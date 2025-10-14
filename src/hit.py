# hit.py
# Este archivo define las clases para detectar colisiones (intersecciones) entre rayos y objetos en la escena.
# Esencial para ray tracing: permite saber si un rayo "toca" un objeto y en qué punto.
# Incluye cajas alineadas (AABB) y cajas orientadas (OBB).

import glm

class Hit:
    def __init__(self, get_model_matrix, hittable=True):
        # Guardamos la función que devuelve la matriz de modelo
        self.__model_matrix = get_model_matrix
        # Atributo que determina si el objeto puede ser golpeado/seleccionado
        self.hittable = hittable

    @property
    def model_matrix(self):
        # Cada vez que se accede, se calcula la matriz actual del objeto
        return self.__model_matrix()

    @property
    def position(self):
        # La posición está en la última columna de la matriz (índice 3)
        m = self.model_matrix
        return glm.vec3(m[3].x, m[3].y, m[3].z)

    @property
    def scale(self):
        # El scale se calcula como la longitud de los vectores base (columnas 0, 1 y 2)
        m = self.model_matrix
        return glm.vec3(
            glm.length(glm.vec3(m[0])),
            glm.length(glm.vec3(m[1])),
            glm.length(glm.vec3(m[2]))
        )

    def check_hit(self, origin, direction):
        # Método base que debe ser implementado por las subclases
        raise NotImplementedError("Subclasses should implement this method.")


class HitBox(Hit):
    def __init__(self, get_model_matrix, hittable=True):
        # Llamamos al constructor de la clase padre
        super().__init__(get_model_matrix, hittable)

    def check_hit(self, origin, direction):
        # Si el objeto no es "golpeable", retornamos False inmediatamente
        if not self.hittable:
            return False

        # Convertimos origen y dirección a vectores glm
        origin = glm.vec3(origin)
        direction = glm.normalize(glm.vec3(direction))

        # Calcular límites mínimos y máximos de la caja alineada con los ejes (AABB)
        min_bounds = self.position - self.scale
        max_bounds = self.position + self.scale

        # Calcular intersección en cada eje (x, y, z)
        tmin = (min_bounds - origin) / direction
        tmax = (max_bounds - origin) / direction

        # Asegurar que tmin < tmax en cada eje
        t1 = glm.min(tmin, tmax)
        t2 = glm.max(tmin, tmax)

        # Calcular el punto de entrada (t_near) y salida (t_far) del rayo en la caja
        t_near = max(t1.x, t1.y, t1.z)
        t_far = min(t2.x, t2.y, t2.z)

        # True si el rayo intersecta la caja (entrada antes que salida y no detrás del origen)
        return t_near <= t_far and t_far >= 0


class HitBoxOBB(Hit):
    def __init__(self, get_model_matrix, hittable=True):
        # Llamamos al constructor de la clase padre
        super().__init__(get_model_matrix, hittable)

    def check_hit(self, origin, direction):
        # Si el objeto no es "golpeable", retornamos False inmediatamente
        if not self.hittable:
            return False

        # Convertimos origen y dirección a vectores glm
        origin = glm.vec3(origin)
        direction = glm.normalize(glm.vec3(direction))

        # Transformar el rayo al espacio local del objeto (OBB = Oriented Bounding Box)
        inv_model = glm.inverse(self.model_matrix)
        local_origin = inv_model * glm.vec4(origin, 1.0)
        local_dir = inv_model * glm.vec4(direction, 0.0)

        # Convertir a vec3 y normalizar la dirección local
        local_origin = glm.vec3(local_origin)
        local_dir = glm.normalize(glm.vec3(local_dir))

        # Límites de la caja en espacio local (cubo unitario de -1 a 1 en cada eje)
        min_bounds = glm.vec3(-1, -1, -1)
        max_bounds = glm.vec3(1, 1, 1)

        # Calcular intersección en cada eje en el espacio local
        tmin = (min_bounds - local_origin) / local_dir
        tmax = (max_bounds - local_origin) / local_dir

        # Ordenar valores para asegurar t1 < t2
        t1 = glm.min(tmin, tmax)
        t2 = glm.max(tmin, tmax)

        # Determinar entrada (t_near) y salida (t_far)
        t_near = max(t1.x, t1.y, t1.z)
        t_far = min(t2.x, t2.y, t2.z)

        # True si hay colisión (entrada antes que salida y no detrás del origen)
        return t_near <= t_far and t_far >= 0
