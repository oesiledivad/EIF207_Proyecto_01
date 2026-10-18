"""

La clase Rastreador representa a un enemigo que rastrea al jugador por el laberinto.
Hereda de la clase Enemigo y tiene atributos y métodos específicos para su comportamiento en el juego.

"""
from cripta.modelo.Enemigo import Enemigo
from cripta.estructuras.Ordenamientos import ordenar

DURACION_RASTRO = 400

class Rastreador(Enemigo):
    def __init__(self, identificador, vida, vida_max, ataque, defensa,
                 velocidad, sala, tiempo_siguiente, comportamiento="rastreador"):
        super().__init__(identificador, vida, vida_max, ataque, defensa,
                          velocidad, sala, tiempo_siguiente, comportamiento)

    def _decidir_movimiento(self, salas, tiempo_actual, azar):
        sala_actual = salas.obtener(self.sala)
        candidatos = []
        for s in sala_actual.salidas:  # ya no .values()
            if s.cerrada:
                continue
            vecina = salas.obtener(s.sala_destino)
            if vecina is None or vecina.ultimo_tiempo_visita is None:
                continue
            antiguedad = tiempo_actual - vecina.ultimo_tiempo_visita
            if antiguedad < DURACION_RASTRO:
                candidatos.append((vecina.ultimo_tiempo_visita, vecina.id))

        if not candidatos:
            return "esperar", None

        candidatos = ordenar(candidatos, key=lambda par: (-par[0], par[1]))
        _, destino = candidatos[0]
        return "mover", destino
