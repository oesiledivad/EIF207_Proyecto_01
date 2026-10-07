"""
    src/cripta/controlador/simulacion.py
    Contiene el motor encargado de avanzar la simulación
    mediante la agenda de eventos y el reloj virtual.
"""
from cripta.estructuras.Agenda_Eventos import HeapAgendaEventos
from cripta.estructuras.Indice_Salas import IndiceSalas
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

    def _ejecutar_turno_enemigo(self, enemigo, jugador, salas: IndiceSalas) -> list[str]:
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

    def avanzar_hasta_turno_jugador(self, jugador, salas) -> list[str]:
        mensajes: list[str] = []
        while True:
            siguiente = self.agenda.peek()
            if siguiente is None:
                return mensajes
            if siguiente.actor is jugador and siguiente.tipo == "accion_actor":
                return mensajes
            evento = self.agenda.extraer_siguiente()
            self.reloj.avanzar_hasta(evento.tiempo_siguiente)
            mensajes.extend(self.ejecutar_evento(evento, jugador, salas))

    def ejecutar_evento(self, evento, jugador, salas) -> list[str]:
        if evento.tipo == "accion_actor" and evento.actor is not jugador:
            return self._ejecutar_turno_enemigo(evento.actor, jugador, salas)
        if evento.tipo == "veneno":
            from cripta.modelo.Efectos import procesar_pulso_veneno
            return [procesar_pulso_veneno(evento.actor, self.reloj.tiempo_actual, self.agenda)]
        if evento.tipo == "regeneracion":
            from cripta.modelo.Efectos import procesar_regeneracion
            return [procesar_regeneracion(evento.actor, self.reloj.tiempo_actual, self.agenda)]
        if evento.tipo == "fin_velocidad":
            from cripta.modelo.Efectos import procesar_fin_velocidad
            return [procesar_fin_velocidad(evento.actor, self.reloj.tiempo_actual, self.agenda)]
        if evento.tipo == "antorcha_apagar":
            from cripta.modelo.Efectos import procesar_apagar_antorcha
            return [procesar_apagar_antorcha(evento.actor)]
        if evento.tipo == "trampa_rearme":
            from cripta.modelo.Efectos import procesar_rearme_trampa
            return [procesar_rearme_trampa(evento.actor)]
        return []