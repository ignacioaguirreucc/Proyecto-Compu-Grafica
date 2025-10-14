import glm

class Ray:
    """
    Clase Ray: Simula el comportamiento de un rayo de luz para ray tracing
    """
    def __init__(self, origin=(0, 0, 0), direction=(0, 0, 1)):
        # Punto de origen del rayo
        self.__origin = glm.vec3(*origin)
        # Vector dirección normalizado
        self.__direction = glm.normalize(glm.vec3(*direction))

    @property
    def origin(self) -> glm.vec3:
        # Retorna punto de origen
        return self.__origin

    @property 
    def direction(self) -> glm.vec3:
        # Retorna vector dirección
        return self.__direction
