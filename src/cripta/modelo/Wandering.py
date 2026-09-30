"""
Wndering es una clase que hereda de la clase ENEMY, y representa a un enemigo que se mueve de manera aleatoria por el laberinto.
"""
from .enemigo import Enemigo
class Errante(Enemigo):
    def __init__(self, identificador, vida, vida_max, ataque, defensa, velocidad, sala, tiempo_siguiente, comportamiento) -> None:
        super().__init__(identificador, vida, vida_max, ataque, defensa, velocidad, sala, tiempo_siguiente)
        
    """
    metodos especificos de errante
    """