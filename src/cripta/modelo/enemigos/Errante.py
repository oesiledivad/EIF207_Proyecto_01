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

    def _decidir_movimiento(self, salas, tiempo_actual, azar, persecucion=None, sala_jugador_id=None):
        # Mismo orden y cantidad que antes, así azar.choice elige el mismo destino (FR-022).
        abiertas = [s for s in salas.obtener(self.sala).salidas if not s.cerrada]
        if not abiertas:
            return ["esperar", None, None]
        salida = azar.choice(abiertas)
        return ["mover", salida.sala_destino, salida.costo]
