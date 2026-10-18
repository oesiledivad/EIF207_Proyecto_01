"""
La clase Errante representa a un enemigo que se mueve de manera aleatoria por el laberinto.
"""
# src/cripta/modelo/enemigos/Errante.py
from cripta.modelo.Enemigo import Enemigo

class Errante(Enemigo):
    def __init__(self, identificador, vida, vida_max, ataque, defensa,
                 velocidad, sala, tiempo_siguiente, comportamiento="errante"):
        super().__init__(identificador, vida, vida_max, ataque, defensa,
                          velocidad, sala, tiempo_siguiente, comportamiento)

    def _decidir_movimiento(self, salas, tiempo_actual, azar):
        transitables = [s.sala_destino for s in salas.obtener(self.sala).salidas if not s.cerrada]
        if not transitables:
            return ["esperar", None]
        return ["mover", azar.choice(transitables)]
