# camera.py
# Cámara para ray tracing con soporte para degradado de cielo (skybox gradiente).
# Incluye la obtención de la matriz de vista e inversa, necesaria para compute shaders.

from ray import Ray
import glm


class Camera:
    def __init__(self, position, target, up, fov, aspect, near, far):
        # Define posición y orientación de la cámara
        self.position = glm.vec3(*position)
        self.target = glm.vec3(*target)
        self.up = glm.vec3(*up)
        
        # Parámetros de la proyección
        self.fov = fov
        self.aspect = aspect
        self.near = near
        self.far = far
        
        # Colores del degradado de cielo (superior e inferior)
        self.__sky_color_top = None
        self.__sky_color_bottom = None
    
    # ------------------------------------------------------
    # Degradado de cielo
    # ------------------------------------------------------
    def set_sky_colors(self, top, bottom):
        """Configura los colores del degradado de cielo."""
        self.__sky_color_top = glm.vec3(*top)
        self.__sky_color_bottom = glm.vec3(*bottom)
    
    def get_sky_gradient(self, height):
        """Devuelve el color interpolado según la altura (height entre -1 y 1)."""
        point = pow(0.5 * (height + 1.0), 1.5)
        return (1.0 - point) * self.__sky_color_bottom + point * self.__sky_color_top

    # ------------------------------------------------------
    # Matrices de cámara
    # ------------------------------------------------------
    def get_perspective_matrix(self):
        """Devuelve la matriz de proyección en perspectiva."""
        return glm.perspective(glm.radians(self.fov), self.aspect, self.near, self.far)

    def get_view_matrix(self):
        """Devuelve la matriz de vista (lookAt)."""
        return glm.lookAt(self.position, self.target, self.up)

    def get_inverse_view_matrix(self):
        """Devuelve la matriz inversa de vista (necesaria para el compute shader)."""
        return glm.inverse(self.get_view_matrix())

    # ------------------------------------------------------
    # Generación de rayos
    # ------------------------------------------------------
    def raycast(self, u, v):
        """Convierte coordenadas de pantalla (u, v) a un rayo 3D en el espacio del mundo."""
        fov_adjustment = glm.tan(glm.radians(self.fov) / 2)
        
        ndc_x = (2 * u - 1) * self.aspect * fov_adjustment
        ndc_y = (2 * v - 1) * fov_adjustment

        ray_dir_camera = glm.normalize(glm.vec3(ndc_x, ndc_y, -1.0))
        view = self.get_view_matrix()
        ray_dir_world = glm.vec3(glm.inverse(view) * glm.vec4(ray_dir_camera, 0.0))

        return Ray(self.position, ray_dir_world)
