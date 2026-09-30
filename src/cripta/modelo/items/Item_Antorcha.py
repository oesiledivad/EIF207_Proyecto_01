# modelo/ItemAntorcha.py
from .Item import Item


class ItemAntorcha(Item):
    def __init__(self, id: str, nombre: str, peso: int, valor: int, duracion: int) -> None:
        super().__init__(id, nombre, peso, valor)
        self.duracion = duracion