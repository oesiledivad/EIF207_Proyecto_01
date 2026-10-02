"""

La clase Rastreador representa a un enemigo que rastrea al jugador por el laberinto.
Hereda de la clase Enemigo y tiene atributos y métodos específicos para su comportamiento en el juego.

"""
from cripta.modelo.Enemigo import Enemigo

class Rastreador(Enemigo):
    def __init__(self, identificador, vida, vida_max, ataque, defensa,
                 velocidad, sala, tiempo_siguiente, comportamiento="rastreador"):
        super().__init__(identificador, vida, vida_max, ataque, defensa,
                          velocidad, sala, tiempo_siguiente, comportamiento)

    def _decidir_movimiento(self, salas, tiempo_actual, azar):
        sala_actual = salas[self.sala]
        candidatos = []
        for salida in sala_actual.salidas.values():
            if salida.cerrada:
                continue
            vecina = salas[salida.sala_destino]
            if vecina.ultimo_tiempo_visita is None:
                continue
            antiguedad = tiempo_actual - vecina.ultimo_tiempo_visita
            if antiguedad < 400:
                candidatos.append((vecina.ultimo_tiempo_visita, vecina.id))

        if not candidatos:
            return "esperar", None

        candidatos.sort(key=lambda par: (-par[0], par[1]))  # más fresco, empate = menor id
        _, destino = candidatos[0]
        return "mover", destino