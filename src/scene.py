# scene.py
# Escena con soporte para renderizado tradicional y raytracing (CPU/GPU).

from graphics import Graphics, ComputeGraphics
import glm
import math
import numpy as np
from raytracer import RayTracer, RayTracerGPU

class Scene:
    def __init__(self, ctx, camera):
        self.ctx = ctx
        self.objects = []
        self.graphics = {}
        self.camera = camera

        # Inicializamos tiempo y matrices de cámara
        self.time = 0.0
        self.view = self.camera.get_view_matrix()
        self.projection = self.camera.get_perspective_matrix()

    def add_object(self, model, material):
        # Agregar objeto y crear su Graphics con el material
        self.objects.append(model)
        self.graphics[model.name] = Graphics(self.ctx, model, material)
    
    def start(self):
        # Método que se ejecuta una vez cuando la escena está cargada
        print("Start!")

    def on_mouse_click(self, u, v):
        ray = self.camera.raycast(u, v)
        for obj in self.objects:
            if obj.check_hit(ray.origin, ray.direction):
                print(f"¡Golpeaste al objeto!: {obj.name}")

    def render(self):
        # Avanzamos el tiempo en cada frame
        self.time += 0.01  

        # Renderizar cada objeto
        for obj in self.objects:
            # Solo animar objetos con animated=True
            if(obj.animated):
                obj.rotation += glm.vec3(0.8, 0.6, 0.4)
                obj.position.x += math.sin(self.time) * 0.01

            # Obtener matriz modelo del objeto
            model = obj.get_model_matrix()
            
            # MVP = Projection × View × Model
            mvp = self.projection * self.view * model

            # Renderizar pasando uniforms
            self.graphics[obj.name].render({'Mvp': mvp})

    def on_resize(self, width, height):
        self.ctx.viewport = (0, 0, width, height)
        self.camera.aspect = width / height
        self.projection = self.camera.get_perspective_matrix()


# --- Clase RayScene (raytracing en CPU) ---
class RayScene(Scene):
    def __init__(self, ctx, camera, width, height):
        super().__init__(ctx, camera)
        # Instanciamos el RayTracer con el tamaño de pantalla
        self.raytracer = RayTracer(camera, width, height)

    def start(self):
        # Renderizamos con el raytracer y actualizamos la textura del Sprite
        self.raytracer.render_frame(self.objects)
        if "Sprite" in self.graphics:
            self.graphics["Sprite"].update_texture(
                "u_texture", self.raytracer.get_texture()
            )

    def render(self):
        # Reutilizamos el render de la clase base (Scene)
        super().render()

    def on_resize(self, width, height):
        # Ajustamos viewport, cámara y regeneramos el framebuffer
        super().on_resize(width, height)
        self.raytracer = RayTracer(self.camera, width, height)
        self.start()


# --- Clase RaySceneGPU (raytracing en GPU con compute shaders) ---
class RaySceneGPU(Scene):
    def __init__(self, ctx, camera, width, height, output_model, output_material):
        self.ctx = ctx
        self.camera = camera
        self.width = width
        self.height = height
        self.raytracer = None
        
        # Crear Graphics del Quad de salida (se renderiza con pipeline tradicional)
        self.output_graphics = Graphics(ctx, output_model, output_material)
        self.raytracer = RayTracerGPU(self.ctx, self.camera, self.width, self.height, self.output_graphics)
        
        # Llamar al constructor de la clase base
        super().__init__(self.ctx, self.camera)
    
    def add_object(self, model, material):
        # Agregar objeto usando ComputeGraphics (para raytracing en GPU)
        self.objects.append(model)
        self.graphics[model.name] = ComputeGraphics(self.ctx, model, material)
    
    def start(self):
        print("Start Raytracing!")
        self.primitives = []
        n = len(self.objects)
        
        # Crear arrays para matrices de transformación (n x 16 valores cada una)
        self.models_f = np.zeros((n, 16), dtype='f4')
        self.inv_f = np.zeros((n, 16), dtype='f4')
        self.mats_f = np.zeros((n, 4), dtype='f4')
        
        self.__update_matrix()
        self.__matrix_to_ssbo()
    
    def __update_matrix(self):
        # Actualizar matrices y materiales de cada objeto
        self.primitives = []
        
        for i, (name, graphics) in enumerate(self.graphics.items()):
            # Crear primitiva para el objeto
            graphics.create_primitive(self.primitives)
            # Crear matriz de transformación
            graphics.create_transformation_matrix(self.models_f, i)
            # Crear matriz inversa de transformación
            graphics.create_inverse_transformation_matrix(self.inv_f, i)
            # Crear matriz de material (color RGB + reflectividad)
            graphics.create_material_matrix(self.mats_f, i)
    
    def __matrix_to_ssbo(self):
        # Escribir matrices en SSBOs (Shader Storage Buffer Objects)
        self.raytracer.matrix_to_ssbo(self.models_f, 0)
        self.raytracer.matrix_to_ssbo(self.inv_f, 1)
        self.raytracer.matrix_to_ssbo(self.mats_f, 2)
        self.raytracer.primitives_to_ssbo(self.primitives, 3)
    
    def render(self):
        # Avanzar el tiempo y animar objetos
        self.time += 0.01
        
        for obj in self.objects:
            if obj.animated:
                obj.rotation += glm.vec3(0.8, 0.6, 0.4)
                obj.position.x += math.sin(self.time) * 0.01
        
        # Actualizar matrices y buffers en cada frame
        if self.raytracer is not None:
            self.__update_matrix()
            self.__matrix_to_ssbo()
            
            # ✅ EJECUTAR EL COMPUTE SHADER
            self.raytracer.run()
            
            # ✅ RENDERIZAR EL QUAD DE SALIDA
            # Obtener el modelo del quad desde output_graphics
            output_model = self.output_graphics._Graphics__model
            model_matrix = output_model.get_model_matrix()
            mvp = self.projection * self.view * model_matrix
            
            # Renderizar el quad con la textura del raytracer
            self.output_graphics.render({'Mvp': mvp})
    
    def on_resize(self, width, height):
        # Actualizar viewport y aspecto de cámara
        super().on_resize(width, height)
        self.width, self.height = width, height
        self.camera.aspect = width/height