"""Búsqueda compartida de los cazadores (spec 003, Parte II §3.2, §5.1 y §5.2).

Todos los cazadores persiguen al mismo jugador y el costo de una salida es el mismo en ambos
sentidos, así que UNA búsqueda inversa desde la sala del jugador da `dist(v, jugador)` para toda
sala `v` dentro del costo de interés. Cada cazador aplica entonces el desempate de FR-014 con
`BuscadorRutas.elegir_paso`, sin buscar por su cuenta.

Las distancias se reutilizan mientras no cambie nada que pueda alterar la respuesta (FR-017):

    clave = (sala del jugador, agenda.cambios_puertas, historial.reversiones)

Eventos que invalidan (D8):
    * el jugador cambia de sala            -> cambia `sala_jugador`
    * una puerta se abre o se cierra       -> sube `agenda.cambios_puertas`
    * se revierte un intervalo o un pergamino (mueve actores, puertas y la sala del jugador)
                                           -> sube `historial.reversiones`
    * un cazador activo con un rango mayor que el usado -> `limite_usado < rango`
Eventos que NO invalidan: la muerte, el movimiento o los cambios de velocidad de otros actores,
porque los actores no bloquean salas y los costos no dependen de la velocidad (FR-018).

La búsqueda se corta al superar el mayor rango activo (FR-025), así que cuesta según la región que
queda dentro del rango y no según el tamaño de la cripta.

Este módulo solo lee `entrantes` (el esqueleto completo), `SalidaSimple.cerrada` y
`SalidaSimple.costo`. NO conoce el conocimiento del jugador ni abre puertas (FR-015, FR-016).

Complejidad:
    distancias: O(1) si la clave coincide; si no, O((V_R + A_R) log V_R) con la región R del límite
    paso: O(4)
"""

from __future__ import annotations

from cripta.modelo.Rutas import BuscadorRutas


def _abierta(salida) -> bool:
    """Una salida entra en la búsqueda del cazador solo si está abierta ahora (FR-011)."""
    return not salida.cerrada


class Persecucion:
    """Distancias compartidas hacia el jugador. No es estado del juego (no se guarda)."""

    def __init__(self, agenda=None) -> None:
        self.agenda = agenda
        self.buscador: BuscadorRutas | None = None
        self.entrantes: list | None = None
        self.rango_maximo = 0
        self.valida = False
        self.clave_sala = -1
        self.clave_puertas = 0
        self.clave_reversiones = 0
        self.limite_usado = 0
        self.recalculos = 0   # diagnóstico: cuántas búsquedas se hicieron (--bench y pruebas)

    def configurar(self, entrantes: list) -> None:
        """Enlaza con las salidas entrantes del esqueleto de la cripta. O(S)."""
        self.entrantes = entrantes
        self.buscador = BuscadorRutas(len(entrantes))
        self.valida = False

    def registrar_rango(self, rango: int) -> None:
        """Un cazador activo declara su rango; el máximo solo crece (D7). O(1)."""
        if rango > self.rango_maximo:
            self.rango_maximo = rango

    def distancias(self, sala_jugador: int, agenda, historial, rango: int) -> bool:
        """Deja listas las distancias hacia `sala_jugador`; False si no hay con qué buscar."""
        if self.buscador is None:
            return False
        reversiones = historial.reversiones if historial is not None else 0
        if (not self.valida or sala_jugador != self.clave_sala
                or agenda.cambios_puertas != self.clave_puertas
                or reversiones != self.clave_reversiones
                or self.limite_usado < rango):
            limite = self.rango_maximo if self.rango_maximo > rango else rango
            self.buscador.distancias_hacia(sala_jugador, self.entrantes, _abierta, None, limite)
            self.valida = True
            self.clave_sala = sala_jugador
            self.clave_puertas = agenda.cambios_puertas
            self.clave_reversiones = reversiones
            self.limite_usado = limite
            self.recalculos += 1
        return True

    def paso(self, sala: int, salidas, rango: int):
        """La salida que da el cazador desde `sala`, o nada si espera (FR-012, FR-013, FR-014).

        Debe llamarse tras `distancias`. Espera si no hay ruta abierta, si d > rango o si ya está
        en la sala del jugador (d == 0; ahí ataca, FR-010).
        """
        d = self.buscador.distancia_de(sala)
        if d is None or d == 0 or d > rango:
            return None
        return self.buscador.elegir_paso(sala, salidas, _abierta)

    def decidir(self, sala_jugador: int, sala: int, salidas, rango: int):
        """`distancias` más `paso` con la agenda de la simulación (lo usa el cazador)."""
        if not self.distancias(sala_jugador, self.agenda, self.agenda.historial, rango):
            return None
        return self.paso(sala, salidas, rango)
