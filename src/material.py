# material.py
# Material representa la apariencia de un objeto: combina un ShaderProgram con texturas
# y ofrece una interfaz para actualizar uniforms del shader relacionado con ese material.
# Un Material sabe cómo enviar valores al shader y cómo gestionar sus texturas.

from texture import Texture

class Material:
    def __init__(self, shader_program, textures_data = []):
        # ShaderProgram que define cómo se renderiza este material
        self.__shader_program = shader_program
        # Lista de instancias Texture asociadas a este material
        self.__textures_data = textures_data
    
    @property
    def shader_program(self):
        return self.__shader_program
    
    @property
    def textures_data(self):
        return self.__textures_data
    
    def set_uniform(self, name, value):
        # Delegar la actualización del uniform al shader program
        self.__shader_program.set_uniform(name, value)


class StandardMaterial(Material):
    def __init__(self, shader_program, albedo: Texture, reflectivity=0.0):
        # Reflectividad: controla cómo el material refleja la luz
        self.reflectivity = reflectivity
        # Color RGB: tomamos el primer píxel de la textura albedo como color base
        self.color_RGB = albedo.image_data.data[0, 0]  # primer pixel de la textura albedo (color)
        # Llamar al constructor base con el shader y la textura albedo
        super().__init__(shader_program, textures_data=[albedo])