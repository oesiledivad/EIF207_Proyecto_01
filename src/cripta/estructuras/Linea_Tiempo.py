"""Línea de tiempo con bitácora de cambios y puntos de control (Parte II, §3.6 y §5.5).

El estado se ve como un vector de ranuras: cada ranura es un valor simple (entero, texto, tupla).
La partida se guarda como una bitácora de cambios `[tiempo, ranura, antes, después]` en cuatro
listas paralelas, anexada por evento. Cada acción del jugador deja una marca `[instante,
posición]` y cada K marcas se copia el vector completo (punto de control).

Una consulta ubica la marca con búsqueda binaria propia, toma el punto de control anterior o el
siguiente (índice directo `a // K`) y aplica o invierte los cambios de a lo sumo K acciones.
Guardar el valor anterior permite reconstruir en las dos direcciones y recortar con el pergamino
restaurando el vector vivo.

Esta estructura no conoce el juego: el controlador decide qué es cada ranura (spec 004, D1 y D2).

Complejidad:
    registrar: O(1) amortizado
    marcar: O(1); O(R) si toma punto de control (R = ranuras)
    ubicar_tiempo: O(log N + c), N marcas, c cambios de una acción
    ubicar_accion: O(1)
    estado_en: O(R + cambios de a lo sumo K acciones)
    recortar: O(cambios recortados + puntos de control quitados)
    memoria: O(cambios + R * N / K)
"""

from __future__ import annotations

ADELANTE = "adelante"
ATRAS = "atras"
CERCANO = "cercano"


class LineaTiempo:
    """Bitácora de cambios con marcas por acción y puntos de control cada K marcas.

    Args:
        k: Acciones del jugador entre dos puntos de control (entero mayor o igual que 1).
        inicial: Valores iniciales de las ranuras fijas.
    """

    def __init__(self, k: int, inicial: list | None = None) -> None:
        if type(k) is not int or k < 1:
            raise ValueError("K debe ser un entero mayor o igual que 1.")
        self.k = k
        self._vivo: list = list(inicial or [])
        self._base: list = list(self._vivo)
        # Bitácora de cambios, listas paralelas.
        self._t: list[int] = []
        self._ranura: list[int] = []
        self._antes: list = []
        self._despues: list = []
        # Marcas: estado justo antes de la acción m + 1 del jugador.
        self._marca_t: list[int] = []
        self._marca_pos: list[int] = []
        self._marca_extra: list = []
        # Puntos de control: el 0 es el estado de creación (posición 0); el i >= 1, la marca i*K.
        self._cp_pos: list[int] = [0]
        self._cp_estado: list[list] = [list(self._vivo)]

    #  Escritura

    def nueva_ranura(self, valor) -> int:
        """Agrega una ranura con su valor vigente y la devuelve.

        El valor queda como base: es el que la ranura tuvo desde el instante 0 hasta su primer
        cambio. Los puntos de control más viejos que la ranura se completan con la base.
        """
        self._vivo.append(valor)
        self._base.append(valor)
        return len(self._vivo) - 1

    def valor(self, ranura: int):
        """Valor vigente de una ranura. O(1)."""
        return self._vivo[ranura]

    def registrar(self, t: int, ranura: int, valor) -> bool:
        """Anexa un cambio si el valor es distinto del vigente. Devuelve si lo anexó."""
        anterior = self._vivo[ranura]
        if anterior == valor:
            return False
        if self._t and t < self._t[-1]:
            raise ValueError("La bitácora no admite tiempos que retroceden.")
        self._t.append(t)
        self._ranura.append(ranura)
        self._antes.append(anterior)
        self._despues.append(valor)
        self._vivo[ranura] = valor
        return True

    def marcar(self, t: int, extra=None) -> int:
        """Anexa la marca de la próxima acción del jugador y devuelve su número (desde 1).

        `extra` es un dato del llamador que se devuelve al recortar (por ejemplo, un cursor).
        """
        if self._marca_t and t <= self._marca_t[-1]:
            raise ValueError("Las marcas deben tener instantes estrictamente crecientes.")
        m = len(self._marca_t)
        self._marca_t.append(t)
        self._marca_pos.append(len(self._t))
        self._marca_extra.append(extra)
        if m > 0 and m % self.k == 0:
            self._cp_pos.append(len(self._t))
            self._cp_estado.append(list(self._vivo))
        return m + 1

    def recortar(self, numero: int):
        """Quita la acción `numero` (desde 1) y todo lo posterior; devuelve el `extra` de su marca.

        Invierte en el vector vivo los cambios quitados, en orden inverso. Cuesta lo recortado,
        no la longitud de la línea (FR-012).
        """
        m = numero - 1
        if not 0 <= m < len(self._marca_t):
            raise ValueError("No existe esa acción en la línea de tiempo.")
        destino = self._marca_pos[m]
        for i in range(len(self._t) - 1, destino - 1, -1):
            self._vivo[self._ranura[i]] = self._antes[i]
            self._t.pop()
            self._ranura.pop()
            self._antes.pop()
            self._despues.pop()
        extra = self._marca_extra[m]
        while len(self._marca_t) > m:
            self._marca_t.pop()
            self._marca_pos.pop()
            self._marca_extra.pop()
        # Sobreviven el 0 y los tomados en marcas i*K < m.
        conservar = 1 + (m - 1) // self.k if m > 0 else 1
        while len(self._cp_pos) > conservar:
            self._cp_pos.pop()
            self._cp_estado.pop()
        return extra

    #  Consultas

    def acciones(self) -> int:
        """Cantidad de acciones del jugador registradas (marcas)."""
        return len(self._marca_t)

    def cambios(self) -> int:
        return len(self._t)

    def puntos_de_control(self) -> int:
        return len(self._cp_pos)

    def tiempo_de_accion(self, numero: int) -> int:
        """Instante de decisión de la acción `numero` (desde 1)."""
        return self._marca_t[numero - 1]

    def _ultima_marca_hasta(self, t: int) -> int:
        """Índice de la última marca con instante <= t, o -1. Búsqueda binaria propia."""
        izquierda, derecha = 0, len(self._marca_t) - 1
        resultado = -1
        while izquierda <= derecha:
            medio = (izquierda + derecha) // 2
            if self._marca_t[medio] <= t:
                resultado = medio
                izquierda = medio + 1
            else:
                derecha = medio - 1
        return resultado

    def ubicar_tiempo(self, t: int) -> list[int]:
        """Posición de la bitácora del estado en t y la marca que la contiene: `[posicion, marca]`.

        Estado en t: todos los cambios con tiempo <= t; si en t hay una decisión del jugador, el
        estado justo antes de tomarla (FR-001). `marca` es -1 antes de la primera acción.
        """
        m = self._ultima_marca_hasta(t)
        if m >= 0 and self._marca_t[m] == t:
            return [self._marca_pos[m], m]
        pos = self._marca_pos[m] if m >= 0 else 0
        fin = self._marca_pos[m + 1] if m + 1 < len(self._marca_pos) else len(self._t)
        while pos < fin and self._t[pos] <= t:
            pos += 1
        return [pos, m]

    def ubicar_accion(self, numero: int) -> list[int]:
        """Posición del estado justo antes de la acción `numero` (1 a N+1): `[posicion, marca]`."""
        if numero == len(self._marca_t) + 1:
            return [len(self._t), len(self._marca_t) - 1]
        if not 1 <= numero <= len(self._marca_t):
            raise ValueError("Número de acción fuera de la línea de tiempo.")
        return [self._marca_pos[numero - 1], numero - 1]

    def _completar(self, estado: list) -> list:
        """Agrega con su base las ranuras creadas después de ese punto de control."""
        for ranura in range(len(estado), len(self._base)):
            estado.append(self._base[ranura])
        return estado

    def costo(self, pos: int, marca: int, modo: str = CERCANO) -> list:
        """`[direccion, origen, cambios]` que usaría `estado_en` (para medir y probar)."""
        indice = (marca // self.k) if marca >= 0 else 0
        anterior = self._cp_pos[indice]
        if indice + 1 < len(self._cp_pos):
            siguiente = self._cp_pos[indice + 1]
        else:
            siguiente = len(self._t)
            indice = -1   # el vivo
        adelante = [ADELANTE, (marca // self.k) if marca >= 0 else 0, pos - anterior]
        atras = [ATRAS, indice + 1 if indice >= 0 else -1, siguiente - pos]
        if modo == ADELANTE:
            return adelante
        if modo == ATRAS:
            return atras
        return adelante if adelante[2] <= atras[2] else atras

    def estado_en(self, pos: int, marca: int, modo: str = CERCANO) -> list:
        """Vector de ranuras en la posición `pos` (copia nueva; no modifica la línea)."""
        direccion, origen, _ = self.costo(pos, marca, modo)
        if direccion == ADELANTE:
            estado = self._completar(list(self._cp_estado[origen]))
            for i in range(self._cp_pos[origen], pos):
                estado[self._ranura[i]] = self._despues[i]
            return estado
        if origen == -1:
            estado = list(self._vivo)
            desde = len(self._t)
        else:
            estado = self._completar(list(self._cp_estado[origen]))
            desde = self._cp_pos[origen]
        for i in range(desde - 1, pos - 1, -1):
            estado[self._ranura[i]] = self._antes[i]
        return estado

    def acciones_recorridas(self, pos: int, marca: int, modo: str = CERCANO) -> int:
        """Acciones del jugador cuyos cambios aplica o deshace `estado_en` (FR-015: a lo sumo K)."""
        direccion, origen, _ = self.costo(pos, marca, modo)
        if marca < 0:
            return 0 if direccion == ADELANTE else (len(self._marca_t) if origen == -1 else origen * self.k)
        if direccion == ADELANTE:
            parcial = 1 if pos > self._marca_pos[marca] else 0
            return marca - origen * self.k + parcial
        fin = len(self._marca_t) if origen == -1 else origen * self.k
        return fin - marca

    def memoria(self) -> list[int]:
        """`[cambios, celdas de puntos de control, celdas totales]` (4 celdas por cambio)."""
        celdas_cp = 0
        for estado in self._cp_estado:
            celdas_cp += len(estado)
        return [len(self._t), celdas_cp, 4 * len(self._t) + celdas_cp + 3 * len(self._marca_t)]

    def con_k(self, k: int) -> "LineaTiempo":
        """La misma partida con otro K (las marcas y cambios se vuelven a alimentar)."""
        nueva = LineaTiempo(k, list(self._cp_estado[0]))
        for ranura in range(len(self._cp_estado[0]), len(self._base)):
            nueva.nueva_ranura(self._base[ranura])
        marca = 0
        for i in range(len(self._t) + 1):
            while marca < len(self._marca_pos) and self._marca_pos[marca] == i:
                nueva.marcar(self._marca_t[marca], self._marca_extra[marca])
                marca += 1
            if i < len(self._t):
                nueva.registrar(self._t[i], self._ranura[i], self._despues[i])
        return nueva

    #  Persistencia: listas simples que cualquier formato puede escribir

    def a_datos(self) -> list:
        return [self.k, list(self._vivo), list(self._base), list(self._t), list(self._ranura),
                list(self._antes), list(self._despues), list(self._marca_t), list(self._marca_pos),
                list(self._marca_extra), list(self._cp_pos), [list(e) for e in self._cp_estado]]

    @staticmethod
    def desde_datos(datos: list) -> "LineaTiempo":
        (k, vivo, base, tiempos, ranuras, antes, despues, marca_t, marca_pos, marca_extra,
         cp_pos, cp_estado) = datos
        linea = LineaTiempo(k)
        largos = [len(ranuras), len(antes), len(despues)]
        if any(largo != len(tiempos) for largo in largos) or len(marca_t) != len(marca_pos) \
                or len(marca_extra) != len(marca_t) or len(cp_pos) != len(cp_estado) or not cp_pos \
                or len(vivo) != len(base):
            raise ValueError("Línea de tiempo dañada: largos inconsistentes.")
        esperados = 1 + (len(marca_t) - 1) // k if marca_t else 1
        if len(cp_pos) != esperados:
            raise ValueError("Línea de tiempo dañada: puntos de control inconsistentes.")
        linea._vivo, linea._base = list(vivo), list(base)
        linea._t, linea._ranura = list(tiempos), list(ranuras)
        linea._antes, linea._despues = list(antes), list(despues)
        linea._marca_t, linea._marca_pos = list(marca_t), list(marca_pos)
        linea._marca_extra = list(marca_extra)
        linea._cp_pos = list(cp_pos)
        linea._cp_estado = [list(e) for e in cp_estado]
        return linea
