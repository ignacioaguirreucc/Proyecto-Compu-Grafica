# texture.py
# Clase Texture encapsula una textura 2D con datos modificables (para CPU y GPU).

import numpy as np

class ImageData:
    """Contiene los datos de imagen como matriz NumPy para manipular píxeles."""
    def __init__(self, height, width, channels, color=(0, 0, 0)):
        self.data = np.full((height, width, channels), color, dtype=np.uint8)

    def set_pixel(self, x, y, color):
        """Establece un píxel en la posición (x, y)."""
        self.data[y, x] = color

    def tobytes(self):
        """Devuelve los datos en formato de bytes plano."""
        return self.data.tobytes()


class Texture:
    """Representa una textura con su información de imagen y parámetros de uso."""
    def __init__(self, name="u_texture", width=1, height=1, channels_amount=3,
                 image_data: ImageData = None, color=(0, 0, 0), repeat_x=False,
                 repeat_y=False, build_mipmaps=False):
        self.name = name
        self.size = (width, height)
        self.channels_amount = channels_amount
        self.repeat_x = repeat_x
        self.repeat_y = repeat_y
        self.build_mipmaps = build_mipmaps

        self.width = width
        self.height = height

        # Si se da una imagen, usarla; si no, crear una vacía del color indicado
        if image_data is not None:
            self.__image_data = image_data
        else:
            self.__image_data = ImageData(height, width, channels_amount, color)

    @property
    def image_data(self):
        """Devuelve el objeto ImageData asociado a esta textura."""
        return self.__image_data

    def update_data(self, new_data: ImageData):
        """Reemplaza los datos actuales por otros nuevos."""
        self.__image_data = new_data

    def set_pixel(self, x, y, color):
        """Modifica un píxel específico."""
        self.__image_data.set_pixel(x, y, color)

    def get_bytes(self):
        """Devuelve los bytes listos para subir a GPU."""
        return self.__image_data.tobytes()
