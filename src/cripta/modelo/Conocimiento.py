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
    entrar: O(4), O(16) con la antorcha encendida
    observar: O(4 + entrantes)
    salida_usable / salidas_conocidas: O(1)
    iniciar: O(S) una vez
    instantanea / restaurar: O(S)
    longitud_registro: O(1)
    reconstruir: O(S + n), n cambios del registro
"""

from __future__ import annotations

DESCONOCIDA = 0
AVISTADA = 1
EXPLORADA = 2

SIN_OBSERVAR = 0
ABIERTA = 1
CERRADA = 2

COSTO_DEFECTO = 100

VERSION_INSTANTANEA = 1

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

    def salidas_conocidas(self, sala: int):
        """Salidas de una sala que el jugador conoce: solo si está explorada; si no, ninguna. O(1).

        Es la única puerta por la que las rutas leen el esqueleto: nada de una sala
        avistada o desconocida sale de aquí (FR-013, FR-014).
        """
        if not self.inicializado or self.estado(sala) != EXPLORADA:
            return []
        modelo = self._salas.obtener(sala)
        return [] if modelo is None else modelo.salidas

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

        `antorcha` es la antorcha tal como estaba al entrar. Si estaba encendida,
        también explora el destino de cada salida de la sala, abierta o cerrada
        (FR-010). Explorar no observa puertas ni toca enemigos, trampas ni
        contenido (FR-011); con la antorcha apagada las vecinas solo quedan
        avistadas (FR-012). Costo O(16).
        """
        self.explorar(sala, historial, tiempo)
        if not antorcha or not self.inicializado or not 0 <= sala < len(self.estado_sala):
            return
        modelo = self._salas.obtener(sala)
        if modelo is None:
            return
        for salida in modelo.salidas:
            self.explorar(salida.sala_destino, historial, tiempo)

    def _asignar_puerta(self, clave: int, valor: int, historial, tiempo: int) -> None:
        """Cambia la memoria de una puerta por el historial y lo anexa al registro."""
        if not 0 <= clave < len(self.puerta) or self.puerta[clave] == valor:
            return
        historial.asignar(self.puerta, clave, valor)
        historial.agregar(self.registro, [tiempo, TIPO_MEMORIA_PUERTA, clave, valor])

    def observar(self, sala: int, historial, tiempo: int) -> None:
        """Recuerda el estado real de las puertas que el jugador ve desde `sala`.

        Cubre las 4 salidas de la sala y las salidas de otras salas que llegan a
        ella (FR-007); solo los cambios reales llegan al registro (FR-037). Se
        llama al terminar cada acción, no al explorar por antorcha (FR-009a).
        Costo O(4 + entrantes).
        """
        if not self.inicializado or not 0 <= sala < len(self.estado_sala):
            return
        modelo = self._salas.obtener(sala)
        if modelo is None:
            return
        for salida in modelo.salidas:
            self._asignar_puerta(salida.clave, CERRADA if salida.cerrada else ABIERTA, historial, tiempo)
        for salida in self._entrantes[sala]:
            self._asignar_puerta(salida.clave, CERRADA if salida.cerrada else ABIERTA, historial, tiempo)

    def salida_usable(self, salida) -> bool:
        """Predicado de las rutas: ¿puede el jugador contar con esta salida? O(1).

        Solo si su sala de origen y su destino están explorados y su memoria de
        puerta es abierta. Nunca consulta el estado real de las puertas (FR-014, FR-022).
        """
        return (self.inicializado
                and self.estado(salida.clave // 4) == EXPLORADA
                and self.estado(salida.sala_destino) == EXPLORADA
                and self.memoria_puerta(salida.clave) == ABIERTA)

    # Interfaz serializable (contracts/conocimiento-serializable.md, FR-015 y FR-017)

    def instantanea(self) -> list[int]:
        """Lista de enteros: versión, n, estado de cada sala y memoria de cada salida.

        Mide `5n + 2` y cada valor cabe en un byte (0 a 2). No guarda entrantes,
        nombres ni costos: se derivan del esqueleto. O(S).
        """
        n = len(self.estado_sala)
        resultado = [VERSION_INSTANTANEA, n]
        resultado.extend(self.estado_sala)
        resultado.extend(self.puerta)
        return resultado

    @staticmethod
    def _validar_instantanea(instantanea: list[int], n_esperado: int | None = None) -> int:
        """Valida versión, `n`, largo y valores; devuelve `n`. Falla con ValueError.

        Con `n_esperado` (el del esqueleto ensamblado) exige que coincida.
        """
        if not isinstance(instantanea, list) or len(instantanea) < 2:
            raise ValueError("Instantánea del conocimiento incompleta.")
        if instantanea[0] != VERSION_INSTANTANEA:
            raise ValueError("Versión de instantánea del conocimiento no admitida.")
        n = instantanea[1]
        if type(n) is not int or n < 0 or (n_esperado is not None and n != n_esperado):
            raise ValueError("La instantánea no coincide con el esqueleto de la cripta.")
        if len(instantanea) != 5 * n + 2:
            raise ValueError("Largo de instantánea del conocimiento incorrecto.")
        for posicion in range(2, len(instantanea)):
            valor = instantanea[posicion]
            if type(valor) is not int or not 0 <= valor <= 2:
                raise ValueError("Valor de instantánea del conocimiento fuera de 0 a 2.")
        return n

    def restaurar(self, instantanea: list[int]) -> None:
        """Reemplaza el conocimiento por el de una instantánea y vacía el registro (FR-015).

        No toca el historial A PROPÓSITO: ocurre al cargar, con el historial
        limpio, y no es un cambio de juego reversible con el pergamino. Valida
        todo antes de cambiar nada. O(S).
        """
        if not self.inicializado:
            raise ValueError("El conocimiento no está iniciado: no hay esqueleto contra el que validar.")
        n = len(self.estado_sala)
        self._validar_instantanea(instantanea, n)
        self.estado_sala = list(instantanea[2:2 + n])
        self.puerta = list(instantanea[2 + n:])
        self.registro = []

    def longitud_registro(self) -> int:
        """Cantidad de cambios del registro cronológico. O(1)."""
        return len(self.registro)

    @staticmethod
    def reconstruir(instantanea_base: list[int], registro: list, n: int) -> "ConocimientoJugador":
        """Conocimiento nuevo tras aplicar los primeros `n` cambios del registro a la base.

        `instantanea_base` es la del instante 0. No modifica el conocimiento vivo
        ni el historial. El resultado es de solo lectura (sirve para `instantanea`,
        `estado`, `memoria_puerta` y para armar un `MapaConocido`). Falla con
        ValueError si `n` está fuera de `0..len(registro)`. O(S + n).
        """
        if type(n) is not int or not 0 <= n <= len(registro):
            raise ValueError("Cantidad de cambios fuera del registro.")
        total = ConocimientoJugador._validar_instantanea(instantanea_base)
        nuevo = ConocimientoJugador()
        nuevo.inicializado = True
        nuevo.estado_sala = list(instantanea_base[2:2 + total])
        nuevo.puerta = list(instantanea_base[2 + total:])
        for posicion in range(n):
            _, tipo, indice, valor = registro[posicion]
            if tipo == TIPO_ESTADO_SALA:
                nuevo.estado_sala[indice] = valor
            else:
                nuevo.puerta[indice] = valor
        return nuevo

    @staticmethod
    def reconstruir_hasta_tiempo(instantanea_base: list[int], registro: list,
                                 t: int) -> "ConocimientoJugador":
        """Aplica los cambios con `tiempo <= t`; exacta solo en fronteras de acción.

        La forma canónica es `reconstruir` por prefijo. El registro está en orden
        cronológico, así que se corta en el primer cambio posterior a `t`. O(S + n).
        """
        cantidad = 0
        while cantidad < len(registro) and registro[cantidad][0] <= t:
            cantidad += 1
        return ConocimientoJugador.reconstruir(instantanea_base, registro, cantidad)
