"""
    src/cripta/controlador/simulacion.py

    Contiene el motor encargado de avanzar la simulación
    mediante la agenda de eventos y el reloj virtual.
"""

from cripta.estructuras.Agenda_Eventos import HeapAgendaEventos
from cripta.util.Reloj import Reloj


class Simulacion:
    """
    Coordina el avance de la simulación mediante eventos.

    Utiliza una agenda de eventos para determinar qué debe ocurrir
    a continuación y un reloj virtual para controlar el tiempo.
    """

    def __init__(self):
        """
        Inicializa una simulación vacía.

        Complejidad temporal: O(1).
        """
        self.agenda = HeapAgendaEventos()
        self.reloj = Reloj()

    def ejecutar_siguiente_evento(self):
        """
        Obtiene y prepara el siguiente evento de la agenda.

        El reloj avanza hasta el tiempo del evento.

        Complejidad temporal: O(log n) en el caso normal.
        """
        evento = self.agenda.extraer_siguiente()

        if evento is None:
            return None

        self.reloj.avanzar_hasta(evento.tiempo_siguiente)

        return evento