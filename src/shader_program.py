# Carga de shaders
class ShaderProgram:
    def __init__(self, ctx, vertex_shader_path, fragment_shader_path):
        with open(vertex_shader_path) as file:
            vertex_shader = file.read()
        with open(fragment_shader_path) as file:
            fragment_shader = file.read()
        self.prog = ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

    def set_uniform(self, name, value):
        if name in self.prog:
            self.prog[name].write(value.to_bytes())
        else:
            print(f"Warning: Uniform '{name}' not found in shader program.")
