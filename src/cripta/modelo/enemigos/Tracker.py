"""

La clase Tracker representa a un enemigo que rastrea al jugador por el laberinto.
Hereda de la clase Enemy y tiene atributos y métodos específicos para su comportamiento en el juego.

"""
from .enemigo import Enemigo
class Rastreador(Enemigo):
    def __init__(self, identificador, vida, vida_max, ataque, defensa, velocidad, sala, tiempo_siguiente, comportamiento) -> None:
        super().__init__(identificador, vida, vida_max, ataque, defensa, velocidad, sala, tiempo_siguiente)
        
    """
    metodos especificos de rastreador
    """