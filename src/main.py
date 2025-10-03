from window import Window
from shader_program import ShaderProgram
from camera import Camera
from scene import Scene
from cube import Cube

# Ventana
window = Window(800, 600, "Basic Graphic Engine")

# Shader
shader_program = ShaderProgram(window.ctx, 'shaders/basic.vert', 'shaders/basic.frag')

# Cámara
camera = Camera((0, 0, 6), (0, 0, 0), (0, 1, 0), 45, window.width/window.height, 0.1, 100.0)

# Objetos
cube1 = Cube((-2, 0, 0), (0, 45, 0), (1, 1, 1), name="Cube1")
cube2 = Cube((2, 0, 0), (0, 45, 0), (1, 1, 1), name="Cube2")

# Escena
scene = Scene(window.ctx, camera)
scene.add_object(cube1, shader_program)
scene.add_object(cube2, shader_program)

# Carga de la escena y ejecución del loop principal
window.set_scene(scene)

# Activar la actualización automática (60 FPS por defecto)
import pyglet
pyglet.clock.schedule_interval(window.update, 1/60.0)

window.run()