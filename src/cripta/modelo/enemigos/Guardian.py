"""
La clase Guardian representa a un enemigo que protege la salida del laberinto.
Hereda de la clase Enemy y tiene atributos y métodos específicos para 
su comportamiento en el juego.

"""
# src/cripta/modelo/enemigos/Guardian.py
from cripta.modelo.Enemigo import Enemigo

class Guardian(Enemigo):
    def __init__(self, identificador, vida, vida_max, ataque, defensa,
                 velocidad, sala, tiempo_siguiente, comportamiento="guardian"):
        super().__init__(identificador, vida, vida_max, ataque, defensa,
                          velocidad, sala, tiempo_siguiente, comportamiento)

    def _decidir_movimiento(self, salas, tiempo_actual, azar):
        return ["esperar", None]