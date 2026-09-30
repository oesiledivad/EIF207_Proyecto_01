# modelo/ItemArmadura.py
from .Item import Item


class ItemArma(Item):
    def __init__(self, id: str, nombre: str, peso: int, valor: int, ataque_bonus: int) -> None:
        super().__init__(id, nombre, peso, valor)
        self.ataque_bonus = ataque_bonus