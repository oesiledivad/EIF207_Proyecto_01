"""Conocimiento del jugador: niebla de guerra (Parte II, §3.3).

Guarda lo que el jugador sabe en cada instante: el estado de cada sala
(desconocida, avistada, explorada) y la memoria de cada puerta (sin observar,
abierta, cerrada). Se eligieron listas planas indexadas por entero: el id de
sala indexa `estado_sala` y la clave de salida (`origen * 4 + dirección`)
indexa `puerta`. Así cada consulta cuesta O(1) sin tabla hash y explorar cuesta
lo que se revela. Todo cambio pasa por `historial.asignar` (reversible con el
pergamino) y se anexa al `registro` cronológico, que la spec 004 usa para
reconstruir cualquier instante.

El modelo no conoce HTTP, archivos ni vista.

Complejidad:
    estado / memoria_puerta: O(1)
    explorar: O(4)
    entrar: O(4)
    iniciar: O(S) una vez
"""

from __future__ import annotations

DESCONOCIDA = 0
AVISTADA = 1
EXPLORADA = 2

SIN_OBSERVAR = 0
ABIERTA = 1
CERRADA = 2

COSTO_DEFECTO = 100

TIPO_ESTADO_SALA = 0
TIPO_MEMORIA_PUERTA = 1


class ConocimientoJugador:
    """Lo que el jugador sabe; es parte del estado del juego (FR-015).

    Mientras `inicializado` es falso (bench y pruebas parciales que arman una
    `Aplicacion` sin iniciar partida) todas las operaciones son inocuas.
    """

    def __init__(self) -> None:
        self.estado_sala: list[int] = []
        self.puerta: list[int] = []
        self.registro: list[list[int]] = []
        self.inicializado = False
        self._salas = None       # IndiceSalas del esqueleto (solo lectura)
        self._entrantes = None   # list de list de SalidaSimple; se deriva, no se guarda

    def iniciar(self, salas, entrantes: list, sala_inicial: int) -> None:
        """Crea el conocimiento del instante 0 (FR-001, FR-002, FR-005, FR-035).

        Explora la sala inicial, avista sus destinos y observa sus puertas.
        Se hace SIN historial a propósito: es la base del instante 0 y no se
        revierte nunca (invariante 6); tampoco se anexa al registro.
        """
        n = len(entrantes)
        self._salas = salas
        self._entrantes = entrantes
        self.estado_sala = [DESCONOCIDA] * n
        self.puerta = [SIN_OBSERVAR] * (4 * n)
        self.registro = []
        self.inicializado = True
        sala = salas.obtener(sala_inicial)
        if sala is None or not 0 <= sala_inicial < n:
            return
        self.estado_sala[sala_inicial] = EXPLORADA
        for salida in sala.salidas:
            if 0 <= salida.sala_destino < n and self.estado_sala[salida.sala_destino] == DESCONOCIDA:
                self.estado_sala[salida.sala_destino] = AVISTADA
        for salida in sala.salidas:
            self.puerta[salida.clave] = CERRADA if salida.cerrada else ABIERTA
        for salida in entrantes[sala_inicial]:
            self.puerta[salida.clave] = CERRADA if salida.cerrada else ABIERTA

    def estado(self, sala: int) -> int:
        """Estado de la sala (0, 1 o 2); un id fuera de rango es desconocida. O(1)."""
        if 0 <= sala < len(self.estado_sala):
            return self.estado_sala[sala]
        return DESCONOCIDA

    def memoria_puerta(self, clave: int) -> int:
        """Última observación de la puerta (0, 1 o 2); fuera de rango es sin observar. O(1)."""
        if 0 <= clave < len(self.puerta):
            return self.puerta[clave]
        return SIN_OBSERVAR

    def _asignar_estado(self, sala: int, valor: int, historial, tiempo: int) -> None:
        """Cambia el estado de una sala por el historial y lo anexa al registro."""
        if self.estado_sala[sala] == valor:
            return
        historial.asignar(self.estado_sala, sala, valor)
        historial.agregar(self.registro, [tiempo, TIPO_ESTADO_SALA, sala, valor])

    def explorar(self, sala: int, historial, tiempo: int) -> None:
        """Marca la sala explorada y avista los destinos aún desconocidos (O(4)).

        No degrada una sala ya explorada ni observa puertas (FR-002, FR-003, FR-012).
        """
        if not self.inicializado or not 0 <= sala < len(self.estado_sala):
            return
        modelo = self._salas.obtener(sala)
        if modelo is None:
            return
        self._asignar_estado(sala, EXPLORADA, historial, tiempo)
        for salida in modelo.salidas:
            destino = salida.sala_destino
            if 0 <= destino < len(self.estado_sala) and self.estado_sala[destino] == DESCONOCIDA:
                self._asignar_estado(destino, AVISTADA, historial, tiempo)

    def entrar(self, sala: int, antorcha: bool, historial, tiempo: int) -> None:
        """El jugador entra a `sala`: la explora (FR-002, FR-036).

        `antorcha` es la antorcha tal como estaba al entrar; su efecto sobre las
        vecinas llega con la historia de la antorcha.
        """
        self.explorar(sala, historial, tiempo)
