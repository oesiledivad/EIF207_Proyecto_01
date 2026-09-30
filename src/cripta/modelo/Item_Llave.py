# modelo/ItemLlave.py
from .Item import Item


class ItemLlave(Item):
    def __init__(self, id: str, nombre: str, peso: int, valor: int, abre: str) -> None:
        super().__init__(id, nombre, peso, valor)
        self.abre = abre