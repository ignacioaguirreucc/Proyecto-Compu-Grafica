# graphics.py
# Graphics vincula un modelo, su material y el contexto de OpenGL.
# ComputeGraphics extiende Graphics para soportar raytracing en GPU,
# convirtiendo objetos en datos que el compute shader puede procesar.

import numpy as np
import glm  # asegúrate de tener glm para las transformaciones

class Graphics:
    def __init__(self, ctx, model, material):
        self.__ctx = ctx
        self.__model = model
        self.__material = material
        
        # Crear buffers (VBO, IBO, VAO)
        self.__vbo = self.create_buffers()
        self.__ibo = ctx.buffer(model.indices.tobytes())
        self.__vao = ctx.vertex_array(material.shader_program.prog, [*self.__vbo], self.__ibo)
        
        # Cargar texturas en GPU usando diccionario (nombre -> textura_ctx)
        self.__textures = self.load_textures(material.textures_data)
    
    def create_buffers(self):
        # Crear buffers según el vertex layout del modelo
        buffers = []
        shader_attributes = self.__material.shader_program.attributes
        
        for attribute in self.__model.vertex_layout.get_attributes():
            if attribute.name in shader_attributes:
                vbo = self.__ctx.buffer(attribute.array.tobytes())
                buffers.append((vbo, attribute.format, attribute.name))
        
        return buffers
    
    def load_textures(self, textures_data):
        """
        Carga texturas en GPU. Detecta si image_data es float32 (RGBA32F) y crea
        la textura con dtype='f4' si corresponde.
        """
        textures = {}
        for texture in textures_data:
            if not texture.image_data:
                continue

            np_data = texture.image_data.data
            size = texture.size
            channels = texture.channels_amount

            # Determinar tipo de dato
            if np_data.dtype == np.float32:
                texture_ctx = self.__ctx.texture(size, channels, np_data.tobytes(), dtype='f4')
            else:
                texture_ctx = self.__ctx.texture(size, channels, np_data.tobytes())

            # Configurar repetición y mipmaps
            if texture.build_mipmaps:
                texture_ctx.build_mipmaps()
            texture_ctx.repeat_x = texture.repeat_x
            texture_ctx.repeat_y = texture.repeat_y

            textures[texture.name] = (texture, texture_ctx)
        
        return textures
    
    def update_texture(self, texture_name, new_data):
        """Actualiza textura existente con nuevos datos (para raytracing en CPU)."""
        if texture_name not in self.__textures:
            raise ValueError(f"No existe la textura {texture_name}")
        
        texture_obj, texture_ctx = self.__textures[texture_name]
        texture_obj.update_data(new_data)
        texture_ctx.write(texture_obj.get_bytes())

    def bind_to_image(self, name="u_texture", unit=0, read=False, write=True):
        """
        Vincula la textura a una unidad de imagen accesible desde compute shaders.
        """
        if name not in self.__textures:
            raise ValueError(f"No existe la textura {name} para bind_to_image()")
        texture_ctx = self.__textures[name][1]
        texture_ctx.bind_to_image(unit, read, write)

    def render(self, uniforms):
        """Renderiza el modelo aplicando uniforms y texturas."""
        # Actualizar uniforms dinámicos (MVP, etc.)
        for name, value in uniforms.items():
            if name in self.__material.shader_program.prog:
                self.__material.set_uniform(name, value)
        
        # Vincular texturas activas
        for i, (name, (tex, tex_ctx)) in enumerate(self.__textures.items()):
            tex_ctx.use(i)
            self.__material.shader_program.set_uniform(name, i)
        
        # Dibujar el VAO
        self.__vao.render()


class ComputeGraphics(Graphics):
    """Versión extendida de Graphics para compatibilidad con RayTracing GPU."""
    def __init__(self, ctx, model, material):
        self.__ctx = ctx
        self.__model = model
        self.__material = material
        self.textures = material.textures_data
        super().__init__(ctx, model, material)
    
    def create_primitive(self, primitives):
        """Agrega los límites AABB del modelo a la lista de primitivas."""
        amin, amax = self.__model.aabb
        primitives.append({"aabb_min": amin, "aabb_max": amax})
    
    def create_transformation_matrix(self, transformations_matrix, index):
        """Guarda la matriz de transformación del modelo."""
        m = self.__model.get_model_matrix()
        transformations_matrix[index, :] = np.array(m.to_list(), dtype="f4").reshape(16)
    
    def create_inverse_transformation_matrix(self, inverse_transformations_matrix, index):
        """Guarda la matriz inversa de transformación."""
        m = self.__model.get_model_matrix()
        inverse = glm.inverse(m)
        inverse_transformations_matrix[index, :] = np.array(inverse.to_list(), dtype="f4").reshape(16)
    
    def create_material_matrix(self, materials_matrix, index):
        """Guarda color RGB y reflectividad del material."""
        reflectivity = self.__material.reflectivity
        r, g, b = self.__material.color_RGB
        
        # Normalizar valores a [0,1]
        r = r / 255.0 if r > 1.0 else r
        g = g / 255.0 if g > 1.0 else g
        b = b / 255.0 if b > 1.0 else b
        
        materials_matrix[index, :] = np.array([r, g, b, reflectivity], dtype="f4")
