"""Entidad de dominio: un enemigo concreto en la partida (no la ficha de catálogo)."""

from abc import ABC, abstractmethod


class Enemigo(ABC):
    """Clase base: todo lo común a cualquier enemigo, sin importar su comportamiento."""

    def __init__(self, instancia_id: str, tipo_catalogo: str,
                 vida: int, vida_max: int, ataque: int, defensa: int,
                 velocidad: int, suelta: list) -> None:
        self.instancia_id = instancia_id
        self.tipo_catalogo = tipo_catalogo
        self.vida = vida
        self.vida_max = vida_max
        self.ataque = ataque
        self.defensa = defensa
        self.velocidad = velocidad
        self.suelta = suelta

        self.sala_actual_id = None
        self.tiempo_siguiente = None
        self.activo = False
        self.muerto = False

        """"
        aca hacen falta funciones especificas que va a tene run enemigo, como por ejemplo atacar, moverse, etc.
        
        """