import moderngl
import pyglet

class Window(pyglet.window.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)
        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.DEPTH_TEST)  # Habilitar depth test
        self.scene = None

    def set_scene(self, scene):
        self.scene = scene
        scene.start()  # Llamar a start() cuando se asigna la escena

    def on_draw(self):  # se ejecuta por cada frame
        self.clear()
        self.ctx.clear()
        if self.scene:
            self.scene.render()

    def run(self):  # activar el loop de la ventana
        pyglet.app.run()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.scene is None:
            return
        # Convertir posición del mouse a u,v [0,1]
        u = x / self.width
        v = y / self.height
        self.scene.on_mouse_click(u, v)