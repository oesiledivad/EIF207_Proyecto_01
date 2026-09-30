# modelo/ItemPocion.py
from .Item import Item


class ItemPocion(Item):
    def __init__(self, id: str, nombre: str, peso: int, valor: int,
                 cura: int = None, modificador_velocidad: int = None, duracion: int = None) -> None:
        super().__init__(id, nombre, peso, valor)
        self.cura = cura
        self.modificador_velocidad = modificador_velocidad
        self.duracion = duracion