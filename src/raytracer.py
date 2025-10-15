# raytracer.py
# RayTracer en CPU y GPU: versión completa con compute shader configurado.

from texture import Texture, ImageData
from shader_program import ComputeShaderProgram
from bvh import BVH
import numpy as np


# ============================================================
# Versión CPU del RayTracer
# ============================================================
class RayTracer:
    def __init__(self, camera, width, height):
        self.camera = camera
        self.width = width
        self.height = height
        self.framebuffer = Texture(width=width, height=height, channels_amount=3)
        
        # Asignar degradado de cielo por defecto
        self.camera.set_sky_colors(top=(16, 190, 222), bottom=(181, 224, 247))
    
    def trace_ray(self, ray, objects):
        """Lanza un rayo y devuelve el color del píxel según intersección o cielo."""
        for obj in objects:
            if obj.check_hit(ray.origin, ray.direction):
                return (255, 0, 0)  # Rojo si intersecta algún objeto
        
        # Si no hay intersección, usar el degradado del cielo
        height = ray.direction.y
        return self.camera.get_sky_gradient(height)
    
    def render_frame(self, objects):
        """Recorre todos los píxeles, genera rayos y calcula el color resultante."""
        for y in range(self.height):
            for x in range(self.width):
                # Normalizar coordenadas de píxel a rango [0, 1]
                u = x / (self.width - 1)
                v = y / (self.height - 1)

                # Generar rayo desde la cámara
                ray = self.camera.raycast(u, v)

                # Calcular color mediante ray tracing
                color = self.trace_ray(ray, objects)

                # Escribir píxel en el framebuffer
                self.framebuffer.set_pixel(x, y, color)
    
    def get_texture(self):
        """Devuelve la textura resultante renderizada."""
        return self.framebuffer.image_data


# ============================================================
# Versión GPU del RayTracer
# ============================================================
class RayTracerGPU:
    def __init__(self, ctx, camera, width, height, output_graphics):
        self.ctx = ctx
        self.width, self.height = width, height
        self.camera = camera
        self.output_graphics = output_graphics
        
        # Crear compute shader para raytracing
        self.compute_shader = ComputeShaderProgram(self.ctx, "shaders/raytracing.comp")
        
        # -------------------------------
        # Crear y vincular textura de salida EN FLOAT32
        # -------------------------------
        self.texture_unit = 0
        
        # CRITICO: Crear textura con datos float32 para rgba32f
        float_data = np.zeros((self.height, self.width, 4), dtype=np.float32)
        image_data_float = ImageData.__new__(ImageData)
        image_data_float.data = float_data
        
        self.output_texture = Texture("u_texture", self.width, self.height, 4, image_data_float, (0, 0, 0, 0))
        
        # Pasar la textura al quad para renderizado
        self.output_graphics.update_texture("u_texture", self.output_texture.image_data)
        
        # Vincular como image2D para escritura del compute shader
        self.output_graphics.bind_to_image("u_texture", self.texture_unit, read=False, write=True)

        # -------------------------------
        # Inicializar uniforms del compute shader
        # -------------------------------
        self.compute_shader.set_uniform("cameraPosition", self.camera.position)
        self.compute_shader.set_uniform("inverseViewMatrix", self.camera.get_inverse_view_matrix())
        self.compute_shader.set_uniform("fieldOfView", self.camera.fov)
    
    def resize(self, width, height):
        """Recalcula el tamaño de la textura al redimensionar la ventana."""
        self.width, self.height = width, height
        
        # Recrear textura float32
        float_data = np.zeros((self.height, self.width, 4), dtype=np.float32)
        image_data_float = ImageData.__new__(ImageData)
        image_data_float.data = float_data
        
        self.output_texture = Texture("u_texture", width, height, 4, image_data_float, (0, 0, 0, 0))
        self.output_graphics.update_texture("u_texture", self.output_texture.image_data)
        self.output_graphics.bind_to_image("u_texture", self.texture_unit, read=False, write=True)

    # -------------------------------
    # Enviar matrices a la GPU (SSBOs)
    # -------------------------------
    def matrix_to_ssbo(self, matrix, binding=0):
        """Envía una matriz (model, view, projection) como SSBO."""
        buffer = self.ctx.buffer(matrix.tobytes())
        buffer.bind_to_storage_buffer(binding=binding)

    # -------------------------------
    # Enviar primitivas (BVH) a la GPU
    # -------------------------------
    def primitives_to_ssbo(self, primitives, binding=3):
        """Genera la jerarquía BVH y la envía a la GPU."""
        self.bvh_nodes = BVH(primitives)
        self.bvh_ssbo = self.bvh_nodes.pack_to_bytes()
        buf_bvh = self.ctx.buffer(self.bvh_ssbo)
        buf_bvh.bind_to_storage_buffer(binding=binding)

    # -------------------------------
    # Ejecutar el compute shader
    # -------------------------------
    def run(self):
        """Ejecuta el compute shader para renderizar en GPU."""
        # Actualizar uniforms de la cámara en cada frame
        self.compute_shader.set_uniform("cameraPosition", self.camera.position)
        self.compute_shader.set_uniform("inverseViewMatrix", self.camera.get_inverse_view_matrix())
        self.compute_shader.set_uniform("fieldOfView", self.camera.fov)
        
        groups_x = (self.width + 15) // 16
        groups_y = (self.height + 15) // 16

        # Ejecutar shader
        self.compute_shader.run(groups_x=groups_x, groups_y=groups_y, groups_z=1)