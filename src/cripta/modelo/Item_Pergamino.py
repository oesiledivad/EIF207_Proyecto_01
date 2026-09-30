# modelo/ItemPergamino.py
from .Item import Item


class ItemPergamino(Item):
    def __init__(self, id: str, nombre: str, peso: int, valor: int) -> None:
        super().__init__(id, nombre, peso, valor)