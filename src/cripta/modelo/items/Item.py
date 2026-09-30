# modelo/Item.py
"""Base: campos comunes a cualquier objeto del juego."""


class Item:
    def __init__(self, id: str, nombre: str, peso: int, valor: int) -> None:
        self.id = id
        self.nombre = nombre
        self.peso = peso
        self.valor = valor