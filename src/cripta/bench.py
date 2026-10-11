"""Cargas sinteticas sin red ni interfaz para --bench."""

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

def _bench_agenda_heap(n: int) -> list[float]:
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
    return [t_insertar, t_extraer]


class _ListaOrdenada:
    """Alternativa descartada: mantener la lista ordenada al insertar (O(n))."""
    def __init__(self) -> None:
        self._datos: list[list[int]] = []

    def insertar(self, tiempo: int, secuencia: int) -> None:
        i = 0
        while i < len(self._datos) and self._datos[i][0] < tiempo:
            i += 1
        self._datos.insert(i, [tiempo, secuencia])

    def extraer_siguiente(self):
        return self._datos.pop(0) if self._datos else None


def _bench_lista_ordenada(n: int) -> list[float]:
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
    return [t_insertar, t_extraer]


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

def _bench_cache(n_consultas: int) -> list[float]:
    cache = Cache_Fichas(capacidad=25)
    for i in range(cache.capacidad):
        cache.insertar(f"ficha-{i}", object())

    inicio = time.perf_counter()
    for _ in range(n_consultas):
        cache.obtener("ficha-0")
    t_acierto = time.perf_counter() - inicio

    inicio = time.perf_counter()
    for _ in range(n_consultas):
        cache.obtener("id_que_no_existe")
    t_fallo = time.perf_counter() - inicio
    return [t_acierto, t_fallo]


def _bench_simulacion() -> None:
    print("=== Agenda: heap propio vs. lista ordenada (§4.1) ===")
    for n in [100, 500, 2000]:
        ih, eh = _bench_agenda_heap(n)
        il, el = _bench_lista_ordenada(n)
        print(f"n={n:5d}  heap: insertar={ih*1000:.2f}ms extraer={eh*1000:.2f}ms"
              f"   |   lista: insertar={il*1000:.2f}ms extraer={el*1000:.2f}ms")

    print("\n=== Rastreador.decidir_accion vs. tamaño de la cripta (§4.7) ===")
    for n_salas in [20, 200, 2000]:
        t = _bench_decidir_accion(n_salas, repeticiones=10_000)
        print(f"cripta de {n_salas:5d} salas -> 10000 llamadas en {t*1000:.2f}ms "
              f"({t*1_000_000/10_000:.3f}µs por llamada)")

    print("\n=== Cache_Fichas llena (25 fichas): acierto vs. fallo (§4.4) ===")
    ta, tf = _bench_cache(50_000)
    print(f"50000 aciertos: {ta*1000:.2f}ms   |   50000 fallos: {tf*1000:.2f}ms")



# Mediciones de estructuras y persistencia: operaciones reales, con datos y semilla fijos.
def _medir(nombre, operacion, repeticiones=100):
    inicio = time.perf_counter()
    for _ in range(repeticiones):
        operacion()
    total = time.perf_counter() - inicio
    print(f"{nombre}: n={repeticiones} total={total*1000:.3f}ms "
          f"por_operacion={total*1_000_000/repeticiones:.3f}us")


def _bench_estructuras_y_persistencia(carpeta):
    import json
    from pathlib import Path
    from types import SimpleNamespace
    from cripta.adaptadores.Almacen_Disco import AlmacenDisco
    from cripta.estructuras.Inventario import Inventario, ItemInventario
    from cripta.estructuras.Historial_Retroceso import Historial_Retroceso
    from cripta.estructuras.Ordenamientos import insertion_sort, merge_sort, ordenar
    from cripta.estructuras.Guardado_Binario import Guardado_Binario

    print("\n=== Inventario e historial ===")
    inventario = Inventario(100)
    item = ItemInventario("i", "tipo", "Objeto", "pocion", 1, 1)

    def insertar_soltar():
        assert inventario.agregar(item)
        assert inventario.soltar_actual() is item

    _medir("inventario insertar + soltar", insertar_soltar, 10000)
    for i in range(100):
        inventario.agregar(ItemInventario(str(i), "tipo", "Objeto", "pocion", 1, i))
    _medir("inventario recorrido bidireccional",
           lambda: [inventario.siguiente(), inventario.anterior()], 10000)
    _medir("inventario vista ordenada (100 objetos)", lambda: inventario.vista_ordenada(lambda item: item.valor))

    historial = Historial_Retroceso()
    actor = SimpleNamespace(vida=100)

    def intervalo():
        historial.abrir_intervalo()
        for vida in range(99, 89, -1):
            historial.cambiar(actor, "vida", vida)
        historial.cerrar_intervalo()
        assert historial.deshacer(lambda etiqueta, datos: setattr(*datos))
        assert actor.vida == 100

    _medir("historial registrar + revertir 10 deltas", intervalo, 10000)

    print("\n=== Ordenamientos: mismo conjunto para cada algoritmo ===")
    azar = random.Random(42)
    for n in [16, 128, 512]:
        aleatorios = [azar.randrange(n) for _ in range(n)]
        casi = list(range(n))
        casi[n//2], casi[n//2+1] = [casi[n//2+1], casi[n//2]]
        for escenario, datos in [["aleatorio", aleatorios], ["casi ordenado", casi]]:
            for algoritmo in [insertion_sort, merge_sort, ordenar]:
                for costosa in [False, True]:
                    def clave(valor):
                        if costosa:
                            for _ in range(30):
                                valor + 1
                        return valor

                    def ordenar_copia():
                        copia = datos.copy()
                        algoritmo(copia, key=clave)
                        assert all(a <= b for a, b in zip(copia, copia[1:]))

                    _medir(f"{algoritmo.__name__} n={n} {escenario} "
                           f"clave={'costosa' if costosa else 'simple'}", ordenar_copia, 3)

    print("\n=== Recuperacion de fichas desalojadas desde disco ===")
    almacen = AlmacenDisco(Path(carpeta) / "cache")
    ficha = {"id": "ficha", "nombre": "Ficha sintetica"}
    almacen.guardar_ficha(ficha)
    cache = Cache_Fichas(1)

    def recuperar():
        cache.insertar("ficha", ficha)
        assert cache.marcar_en_uso("ficha")
        cache.liberar("ficha")
        cache.insertar("otra", object())
        assert cache.obtener("ficha") is None
        leida = almacen.leer_ficha("ficha")
        assert leida == ficha
        cache.insertar("ficha", leida)

    _medir("liberar + desalojar + recuperar ficha", recuperar)

    print("\n=== Guardado/carga: mismo estado binario y JSON ===")
    estado = [[i, "sala " + str(i), list(range(100))] for i in range(100)]
    salas = [SimpleNamespace(sala_id=s[0], bytes_=json.dumps(s).encode("utf-8"))
             for s in estado]
    binario = Path(carpeta) / "partida.bin"
    ruta_json = Path(carpeta) / "partida.json"
    guardado = Guardado_Binario(str(binario))

    def guardar_json():
        ruta_json.write_text(json.dumps(["version-sintetica", estado]), encoding="utf-8")

    def cargar_binario():
        assert [json.loads(s.bytes_) for s in guardado.cargar_todo()] == estado

    def cargar_json():
        assert json.loads(ruta_json.read_text(encoding="utf-8")) == ["version-sintetica", estado]

    _medir("guardar binario", lambda: guardado.guardar("version-sintetica", salas), 10)
    _medir("guardar JSON", guardar_json, 10)
    _medir("cargar binario", cargar_binario, 10)
    _medir("cargar JSON", cargar_json, 10)
    _medir("cargar sala especifica binario",
           lambda: _comprobar_sala(guardado, salas[50]), 10)
    print(f"Tamano: binario={binario.stat().st_size}B JSON={ruta_json.stat().st_size}B")


def _comprobar_sala(guardado, sala):
    assert guardado.cargar_sala(sala.sala_id) == sala.bytes_


def main():
    import tempfile
    _bench_simulacion()
    with tempfile.TemporaryDirectory(prefix="cripta-bench-") as carpeta:
        _bench_estructuras_y_persistencia(carpeta)


if __name__ == "__main__":
    main()
