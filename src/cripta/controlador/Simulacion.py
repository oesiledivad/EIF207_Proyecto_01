"""
    src/cripta/controlador/simulacion.py
    Contiene el motor encargado de avanzar la simulación
    mediante la agenda de eventos y el reloj virtual.
"""
from cripta.estructuras.Agenda_Eventos import HeapAgendaEventos
from cripta.util.Reloj import Reloj

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

    def ejecutar_evento(self, evento):
        """
        Ejecuta un evento según su tipo.
        """
        if evento.tipo == "accion_actor":
            actor = evento.actor
            pass
