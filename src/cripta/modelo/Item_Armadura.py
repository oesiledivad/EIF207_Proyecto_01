# modelo/ItemArmadura.py
from .Item import Item


class ItemArmadura(Item):
    def __init__(self, id: str, nombre: str, peso: int, valor: int, defensa_bonus: int) -> None:
        super().__init__(id, nombre, peso, valor)
        self.defensa_bonus = defensa_bonus