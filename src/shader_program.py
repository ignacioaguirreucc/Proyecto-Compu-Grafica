# shader_program.py
# Esta clase encapsula programas de shaders (vertex/fragment o compute).
# Permite administrar atributos y uniforms, y ejecutar compute shaders en GPU.

from moderngl import Attribute, Uniform
import glm


class ShaderProgram:
    def __init__(self, ctx, vertex_shader_path, fragment_shader_path):
        # Leer y compilar los shaders desde archivos con UTF-8
        with open(vertex_shader_path, encoding='utf-8') as file:
            vertex_shader = file.read()
        with open(fragment_shader_path, encoding='utf-8') as file:
            fragment_shader = file.read()
        
        # Crear el programa de shaders
        self.prog = ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
        
        # Detectar automáticamente atributos y uniforms
        attributes = []
        uniforms = []
        for name in self.prog:
            member = self.prog[name]
            if type(member) is Attribute:
                attributes.append(name)
            if type(member) is Uniform:
                uniforms.append(name)
        
        self.attributes = list(attributes)
        self.uniforms = uniforms

    def set_uniform(self, name, value):
        # Modificar un uniform si existe en el shader
        if name in self.uniforms:
            uniform = self.prog[name]
            if isinstance(value, glm.mat4):
                # Matrices deben enviarse en formato de bytes
                uniform.write(value.to_bytes())
            elif hasattr(uniform, "value"):
                # Otros tipos (escalars, tuples, ints, floats)
                uniform.value = value


class ComputeShaderProgram:
    def __init__(self, ctx, compute_shader_path):
        # Leer el compute shader desde archivo con UTF-8
        with open(compute_shader_path, encoding='utf-8') as file:
            compute_source = file.read()
        
        # Crear el programa de compute shader
        self.prog = ctx.compute_shader(compute_source)
        
        # Detectar uniforms disponibles
        uniforms = []
        for name in self.prog:
            member = self.prog[name]
            if type(member) is Uniform:
                uniforms.append(name)
        
        self.uniforms = uniforms

    def set_uniform(self, name, value):
        # Modificar un uniform si existe
        if name in self.uniforms:
            uniform = self.prog[name]
            if isinstance(value, glm.mat4):
                uniform.write(value.to_bytes())
            elif hasattr(uniform, "value"):
                uniform.value = value

    def run(self, groups_x=1, groups_y=1, groups_z=1):
        """
        Ejecuta el compute shader en la GPU.
        Los grupos determinan cuántas invocaciones paralelas se lanzan.
        """
        self.prog.run(group_x=groups_x, group_y=groups_y, group_z=groups_z)