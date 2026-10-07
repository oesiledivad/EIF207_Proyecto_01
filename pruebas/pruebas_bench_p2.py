"""Benchmark standalone para el Documento de Decisiones, P2.

No es el --bench oficial del proyecto (ese es un entregable de todo el
equipo, §5.3, y todavía no existe el módulo). Esto mide solo mis 4
problemas (agenda, IA de enemigos, caché) con las clases reales.

Correr con:  uv run python pruebas/bench_p2.py
"""

from __future__ import annotations

import random
import time

from cripta.estructuras.Agenda_Eventos import HeapAgendaEventos
from cripta.estructuras.Salidas import Salidas
from cripta.estructuras.Indice_Salas import IndiceSalas
from cripta.estructuras.Cache_Fichas import Cache_Fichas
from cripta.modelo.Sala import SalaJuego
from cripta.modelo.enemigos.Rastreador import Rastreador


class _ActorFalso:
    """Soporte mínimo para encolar eventos sintéticos sin armar un Actor real."""
    def __init__(self, identificador: str) -> None:
        self.identificador = identificador
        self._proximo_evento = None


# --- 1. Agenda: heap propio vs. lista ordenada por inserción (§4.1) --------

def _bench_agenda_heap(n: int) -> tuple[float, float]:
    agenda = HeapAgendaEventos()
    azar = random.Random(42)
    tiempos = [azar.randint(0, 100_000) for _ in range(n)]

    inicio = time.perf_counter()
    for t in tiempos:
        agenda.insertar(t, _ActorFalso("x"), "accion_actor")
    t_insertar = time.perf_counter() - inicio

    inicio = time.perf_counter()
    while agenda.extraer_siguiente() is not None:
        pass
    t_extraer = time.perf_counter() - inicio
    return t_insertar, t_extraer


class _ListaOrdenada:
    """Alternativa descartada: mantener la lista ordenada al insertar (O(n))."""
    def __init__(self) -> None:
        self._datos: list[tuple[int, int]] = []

    def insertar(self, tiempo: int, secuencia: int) -> None:
        i = 0
        while i < len(self._datos) and self._datos[i][0] < tiempo:
            i += 1
        self._datos.insert(i, (tiempo, secuencia))

    def extraer_siguiente(self):
        return self._datos.pop(0) if self._datos else None


def _bench_lista_ordenada(n: int) -> tuple[float, float]:
    lista = _ListaOrdenada()
    azar = random.Random(42)
    tiempos = [azar.randint(0, 100_000) for _ in range(n)]

    inicio = time.perf_counter()
    for i, t in enumerate(tiempos):
        lista.insertar(t, i)
    t_insertar = time.perf_counter() - inicio

    inicio = time.perf_counter()
    while lista.extraer_siguiente() is not None:
        pass
    t_extraer = time.perf_counter() - inicio
    return t_insertar, t_extraer


# --- 2. decidir_accion vs. tamaño de la cripta (§4.7) -----------------------

def _construir_cripta_sintetica(n_salas: int) -> IndiceSalas:
    salas = IndiceSalas()
    for i in range(n_salas):
        salidas = Salidas()
        if i > 0:
            salidas.agregar("S", i - 1, False)
        if i < n_salas - 1:
            salidas.agregar("N", i + 1, False)
        sala = SalaJuego(id=i, nombre=f"Sala {i}", salidas=salidas,
                          enemigos=[], objetos=[], trampas=[])
        sala.ultimo_tiempo_visita = 0 if i % 2 == 0 else None
        salas.insertar(i, sala)
    return salas


def _bench_decidir_accion(n_salas: int, repeticiones: int) -> float:
    salas = _construir_cripta_sintetica(n_salas)
    rastreador = Rastreador(
        identificador="r-1", vida=10, vida_max=10, ataque=3, defensa=1,
        velocidad=100, sala=n_salas // 2, tiempo_siguiente=None,
    )
    azar = random.Random(1)

    inicio = time.perf_counter()
    for _ in range(repeticiones):
        rastreador.decidir_accion(sala_jugador_id=-1, salas=salas,
                                   tiempo_actual=1000, azar=azar)
    return time.perf_counter() - inicio


# --- 3. Cache_Fichas: acierto vs. fallo (§4.4) ------------------------------

def _bench_cache(n_consultas: int) -> tuple[float, float]:
    cache = Cache_Fichas(capacidad=25)
    cache.insertar("ent_rata_gigante", object())

    inicio = time.perf_counter()
    for _ in range(n_consultas):
        cache.obtener("ent_rata_gigante")
    t_acierto = time.perf_counter() - inicio

    inicio = time.perf_counter()
    for _ in range(n_consultas):
        cache.obtener("id_que_no_existe")
    t_fallo = time.perf_counter() - inicio
    return t_acierto, t_fallo


def main() -> None:
    print("=== Agenda: heap propio vs. lista ordenada (§4.1) ===")
    for n in (100, 500, 2000):
        ih, eh = _bench_agenda_heap(n)
        il, el = _bench_lista_ordenada(n)
        print(f"n={n:5d}  heap: insertar={ih*1000:.2f}ms extraer={eh*1000:.2f}ms"
              f"   |   lista: insertar={il*1000:.2f}ms extraer={el*1000:.2f}ms")

    print("\n=== Rastreador.decidir_accion vs. tamaño de la cripta (§4.7) ===")
    for n_salas in (20, 200, 2000):
        t = _bench_decidir_accion(n_salas, repeticiones=10_000)
        print(f"cripta de {n_salas:5d} salas -> 10000 llamadas en {t*1000:.2f}ms "
              f"({t*1_000_000/10_000:.3f}µs por llamada)")

    print("\n=== Cache_Fichas: acierto vs. fallo (§4.4) ===")
    ta, tf = _bench_cache(50_000)
    print(f"50000 aciertos: {ta*1000:.2f}ms   |   50000 fallos: {tf*1000:.2f}ms")


if __name__ == "__main__":
    main()