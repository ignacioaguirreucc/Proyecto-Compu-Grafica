from graphics import Graphics
import glm

class Scene:
    def __init__(self, ctx, camera):
        self.ctx = ctx
        self.objects = []
        self.graphics = {}
        self.shader_programs = {}  # Guardar referencia a los shaders
        self.camera = camera

    def add_object(self, obj, shader_program=None):
        self.objects.append(obj)
        self.graphics[obj.name] = Graphics(self.ctx, shader_program, obj.vertices, obj.indices)
        self.shader_programs[obj.name] = shader_program  # Guardar el shader program

    def update(self, dt):
        # Actualizar cada objeto (rotación, posición, etc.)
        for obj in self.objects:
            # Rotar el objeto en los ejes Y y X
            obj.rotation.y += 50 * dt  # 50 grados por segundo en Y
            obj.rotation.x += 30 * dt  # 30 grados por segundo en X

    def render(self):
        # Obtener las matrices de la cámara (estas son iguales para todos los objetos)
        view = self.camera.get_view_matrix()
        projection = self.camera.get_perspective_matrix()
        
        # Renderizar cada objeto
        for obj in self.objects:
            # Obtener la matriz modelo del objeto (posición, rotación, escala)
            model = obj.get_model_matrix()
            
            # Calcular la matriz MVP: Projection × View × Model
            mvp = projection * view * model
            
            # Enviar la matriz MVP al shader
            shader_program = self.shader_programs[obj.name]
            shader_program.set_uniform('Mvp', mvp)
            
            # Renderizar el objeto
            self.graphics[obj.name].vao.render()

    def on_resize(self, width, height):
        self.ctx.viewport = (0, 0, width, height)
        self.camera.aspect = width / height
        self.camera.projection = self.camera.get_perspective_matrix()