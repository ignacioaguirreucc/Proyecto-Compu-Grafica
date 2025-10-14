# model.py

# ----------------------------
# Clase Vertex
# ----------------------------
# Representa un vértice del modelo 3D.
# Cada vértice tiene un nombre, un formato (por ejemplo, '3f' para 3 floats)
# y un array que contiene los valores asociados (posiciones, colores, normales, etc.).

class Vertex:
    def __init__(self, name, format, array):
        self.__name = name
        self.__format = format
        self.__array = array

    @property
    def name(self):
        return self.__name

    @property
    def format(self):
        return self.__format

    @property
    def array(self):
        return self.__array

# ----------------------------
# Clase VertexLayout
# ----------------------------
# Se encarga de construir y almacenar todos los atributos de un vértice.
# Básicamente, define la estructura del vértice (layout) con sus diferentes atributos.

class VertexLayout:
    def __init__(self):
        self.__attributes = []  # Lista que guarda los atributos del vértice

    def add_attribute(self, name: str, format: str, array):
        # Crea un objeto Vertex y lo agrega al layout
        self.__attributes.append(Vertex(name, format, array))

    def get_attributes(self):
        return self.__attributes


# ----------------------------
# Clase Model
# ----------------------------
# Esta clase será la base de todos los modelos 3D.
# Se encarga de:
#   - Guardar los índices del modelo (definen cómo se conectan los vértices)
#   - Construir el VertexLayout con los atributos disponibles
#   - Organizar posiciones, colores, normales y coordenadas de textura

class Model:
    def __init__(self, vertices=None, indices=None, colors=None, normals=None, texcoords=None):
        self.indices = indices  # Guarda los índices del modelo
        self.vertex_layout = VertexLayout()  # Crea la estructura del vértice

        # Agrega los atributos disponibles al layout
        # Formato ModernGL: '3f' = 3 floats, '2f' = 2 floats
        if vertices is not None:
            self.vertex_layout.add_attribute("in_pos", "3f", vertices)
        if colors is not None:
            self.vertex_layout.add_attribute("in_color", "3f", colors)
        if normals is not None:
            self.vertex_layout.add_attribute("in_norm", "3f", normals)
        if texcoords is not None:
            self.vertex_layout.add_attribute("in_uv", "2f", texcoords)