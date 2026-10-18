"""
    src/cripta/modelo/Simulacion.py
    Contiene el motor encargado de avanzar la simulación
    mediante la agenda de eventos y el reloj virtual.
"""
from cripta.estructuras.Agenda_Eventos import HeapAgendaEventos
from cripta.estructuras.Indice_Salas import IndiceSalas
from cripta.util.Reloj import Reloj
from cripta.modelo.Combate import calcular_danio, aplicar_danio, esta_vivo
from cripta.util.Costo_Acciones import costo_accion, calcular_intervalo
from cripta.modelo.Efectos import (
    procesar_pulso_veneno,
    procesar_regeneracion,
    procesar_fin_velocidad,
    procesar_apagar_antorcha,
    procesar_rearme_trampa,
)
from cripta.modelo.Puertas import procesar_cierre_puerta
import random
class Simulacion:
    """
    Coordina el avance de la simulación mediante eventos.
    Utiliza una agenda de eventos para determinar qué debe ocurrir
    a continuación y un reloj virtual para controlar el tiempo.
    """
    def __init__(self, semilla, historial=None):
        """
        Inicializa una simulación con su agenda, reloj y azar.
        Complejidad temporal: O(1).
        """
        self.agenda = HeapAgendaEventos(historial)
        self.reloj = Reloj(historial)
        self.azar = random.Random(semilla)

    def _ejecutar_turno_enemigo(self, enemigo, jugador, salas: IndiceSalas) -> list[str]:
        if not esta_vivo(enemigo):
            return []

        tiempo_actual = self.reloj.tiempo_actual
        tipo_accion, destino = enemigo.decidir_accion(jugador.sala, salas, tiempo_actual, self.azar)
        mensajes: list[str] = []

        if tipo_accion == "atacar":
            dano = calcular_danio(enemigo, jugador, self.azar)
            aplicar_danio(jugador, dano, self.agenda)
            mensajes.append(f"{enemigo.etiqueta} te ataca por {dano}.")
            if not esta_vivo(jugador):
                return mensajes  # jugador murió: no reprogramamos nada más
        elif tipo_accion == "mover":
            self._mover_enemigo(enemigo, destino, salas)
            if enemigo.comportamiento == "rastreador" and enemigo.sala == jugador.sala:
                mensajes.append(f"{enemigo.etiqueta} sigue tu rastro y entra en tu sala.")

        intervalo = calcular_intervalo(costo_accion(tipo_accion), enemigo.velocidad)
        self.agenda.reprogramar(enemigo, tiempo_actual + intervalo, "accion_actor")
        return mensajes

    def _mover_enemigo(self, enemigo, destino_id: int, salas: IndiceSalas) -> None:
        """Cambia la pertenencia del enemigo: sale de su sala y entra a la destino.

        El enemigo sigue activo aunque el jugador nunca haya entrado a la
        sala destino (§2.4). O(k) por quitar de la lista de la sala origen.
        """
        sala_origen = salas.obtener(enemigo.sala)
        sala_destino = salas.obtener(destino_id)
        if sala_destino is None:
            return  # no debería pasar: todas las salas del esqueleto existen
        if sala_origen is not None:
            sala_origen.quitar_enemigo(enemigo, self.agenda.historial)
        sala_destino.agregar_enemigo(enemigo, self.agenda.historial)
        self.agenda.cambiar(enemigo, "sala", destino_id)

    def avanzar_hasta_turno_jugador(self, jugador, salas) -> list[str]:
        """Ejecuta eventos en orden (tiempo, secuencia) hasta que le toque al jugador.

        Al encontrar el evento del jugador NO lo extrae: solo adelanta el
        reloj a su instante. Así la siguiente acción del jugador se programa
        desde el tiempo correcto (§2.3). Se detiene si el jugador muere.
        """
        mensajes: list[str] = []
        while True:
            siguiente = self.agenda.peek()
            if siguiente is None:
                return mensajes
            if siguiente.actor is jugador and siguiente.tipo == "accion_actor":
                self.reloj.avanzar_hasta(siguiente.tiempo_siguiente)
                return mensajes
            evento = self.agenda.extraer_siguiente()
            self.reloj.avanzar_hasta(evento.tiempo_siguiente)
            mensajes.extend(self.ejecutar_evento(evento, jugador, salas))
            if not esta_vivo(jugador):
                return mensajes

    def ejecutar_evento(self, evento, jugador, salas) -> list[str]:
        tiempo = self.reloj.tiempo_actual
        match evento.tipo:
            case "accion_actor":
                if evento.actor is jugador:
                    return []
                return self._ejecutar_turno_enemigo(evento.actor, jugador, salas)
            case "veneno":
                return [procesar_pulso_veneno(evento.actor, tiempo, self.agenda)]
            case "regeneracion":
                return [procesar_regeneracion(evento.actor, tiempo, self.agenda)]
            case "fin_velocidad":
                return [procesar_fin_velocidad(evento.actor, tiempo, self.agenda)]
            case "antorcha_apagar":
                return [procesar_apagar_antorcha(evento.actor, self.agenda)]
            case "trampa_rearme":
                return [procesar_rearme_trampa(evento.actor, self.agenda)]
            case "cierre_puerta":
                return [procesar_cierre_puerta(evento.actor, self.agenda)]
        return []
