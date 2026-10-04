"""
    src/cripta/controlador/simulacion.py
    Contiene el motor encargado de avanzar la simulación
    mediante la agenda de eventos y el reloj virtual.
"""
from cripta.estructuras.Agenda_Eventos import HeapAgendaEventos
from cripta.util.Reloj import Reloj
from cripta.modelo.Combate import calcular_danio, aplicar_danio, esta_vivo
from cripta.util.Costo_Acciones import COSTOS, calcular_intervalo

import random

class Simulacion:
    """
    Coordina el avance de la simulación mediante eventos.
    Utiliza una agenda de eventos para determinar qué debe ocurrir
    a continuación y un reloj virtual para controlar el tiempo.
    """
    def __init__(self, semilla):
        """
        Inicializa una simulación con su agenda, reloj y azar.
        Complejidad temporal: O(1).
        """
        self.agenda = HeapAgendaEventos()
        self.reloj = Reloj()
        self.azar = random.Random(semilla)

    def ejecutar_siguiente_evento(self):
        """
        Obtiene y ejecuta el siguiente evento de la agenda.
        El reloj avanza hasta el tiempo del evento.
        """
        evento = self.agenda.extraer_siguiente()

        if evento is None:
            return None

        self.reloj.avanzar_hasta(evento.tiempo_siguiente)

        self.ejecutar_evento(evento)

        return evento

    def _ejecutar_turno_enemigo(self, enemigo, jugador, salas: dict) -> list[str]:
        if not esta_vivo(enemigo):
            return []

        tiempo_actual = self.reloj.tiempo_actual
        tipo_accion, destino = enemigo.decidir_accion(jugador.sala, salas, tiempo_actual, self.azar)
        mensajes: list[str] = []

        if tipo_accion == "atacar":
            dano = calcular_danio(enemigo, jugador, self.azar)
            aplicar_danio(jugador, dano)
            mensajes.append(f"{enemigo.identificador} te ataca por {dano}.")
            if not esta_vivo(jugador):
                return mensajes  # jugador murió: no reprogramamos nada más
        elif tipo_accion == "mover":
            enemigo.sala = destino

        intervalo = calcular_intervalo(COSTOS[tipo_accion], enemigo.velocidad)
        self.agenda.reprogramar(enemigo, tiempo_actual + intervalo, "accion_actor")
        return mensajes

    def avanzar_hasta_turno_jugador(self, jugador, salas: dict) -> list[str]:
        """Ejecuta eventos (enemigos, efectos) hasta que le toque de nuevo al jugador."""
        mensajes: list[str] = []
        while True:
            siguiente = self.agenda.peek()
            if siguiente is None or siguiente.actor is jugador:
                return mensajes
            evento = self.agenda.extraer_siguiente()
            self.reloj.avanzar_hasta(evento.tiempo_siguiente)
            mensajes.extend(self.ejecutar_evento(evento, jugador, salas))
