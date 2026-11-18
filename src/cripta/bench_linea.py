"""Mediciones de la línea de tiempo (spec 004, research.md D12): L1 a L5.

Todo es determinista por semilla, sin red ni vista. La partida larga se juega en la cripta más
grande del paquete `datos_offline` (sin red); si no está, L1 a L3 se omiten y L4 y L5 siguen.
"""

from __future__ import annotations

import random
import time
import tracemalloc
from pathlib import Path

from cripta.estructuras.Historial_Retroceso import Historial_Retroceso
from cripta.estructuras.Linea_Tiempo import ADELANTE, ATRAS, CERCANO, LineaTiempo

SEMILLA_PREDETERMINADA = 42
VALORES_K = (1, 10, 50, 200)
SIN_PUNTOS_DE_CONTROL = 10 ** 9      # K mayor que cualquier partida: solo el punto de control 0
LIMITE_CONSULTA_MS = 50.0
LIMITE_CICLO_MS = 20.0


def _ms(segundos: float) -> str:
    return f"{segundos * 1000:.3f}ms"


def _carpeta_paquete(carpeta=None) -> Path:
    return Path(carpeta) if carpeta is not None else Path(__file__).resolve().parents[2] / "datos_offline"


def _cripta_mayor(carpeta: Path) -> str | None:
    """Id de la cripta con más salas del paquete (sin datos de cripta en el código)."""
    import json
    mejor, tamano = None, -1
    for ruta in carpeta.glob("cripta_*_salas_1.json"):
        try:
            salas = len(json.loads(ruta.read_text(encoding="utf-8"))["salas"])
        except (OSError, ValueError, KeyError):
            continue
        cripta = ruta.name[len("cripta_"):-len("_salas_1.json")]
        if salas > tamano or (salas == tamano and cripta < mejor):
            mejor, tamano = cripta, salas
    return mejor


def jugar_partida_larga(acciones=5000, semilla=SEMILLA_PREDETERMINADA, k=50, con_linea=True,
                        carpeta=None):
    """Juega `acciones` acciones con una política determinista y devuelve [app, tiempos por acción (s)].

    La vida del jugador se repone fuera de las acciones para que la partida no termine.
    """
    from cripta.adaptadores.AdaptadorOffline import AdaptadorOffline
    from cripta.controlador.Aplicacion import Aplicacion

    carpeta = _carpeta_paquete(carpeta)
    cripta = _cripta_mayor(carpeta)
    if cripta is None:
        return [None, []]
    app = Aplicacion(AdaptadorOffline(carpeta), checkpoint_cada=k)
    resultado = app.iniciar_partida("Bench", str(semilla), cripta, registrar=False, forzar=True)
    if not resultado.ok:
        raise RuntimeError(resultado.motivo)
    if not con_linea:
        app._linea.linea = None          # L3: la misma partida sin línea de tiempo
    azar = random.Random(semilla)
    tiempos: list[float] = []
    intervalos: list[int] = []
    while len(tiempos) < acciones:
        e = app.estado_partida()
        if e.terminada:
            break
        if app._jugador.vida < 1000:
            app._jugador.vida = app._jugador.vida_max = 10 ** 6
        if e.objetos_suelo and azar.random() < 0.3:
            accion = lambda: app.recoger(e.objetos_suelo[0].id)
        elif e.enemigos and azar.random() < 0.3:
            accion = lambda: app.atacar(e.enemigos[0].id)
        else:
            abiertas = [s for s in e.vecindad if not s.cerrada]
            if abiertas and azar.random() < 0.85:
                direccion = abiertas[azar.randrange(len(abiertas))].direccion
                accion = lambda: app.mover(direccion)
            else:
                accion = app.esperar
        inicio = time.perf_counter()
        resultado = accion()
        fin = time.perf_counter()
        if resultado.ok:
            tiempos.append(fin - inicio)
            historial = app._gestor.historial
            if len(historial):
                intervalos.append(len(historial._intervalos[-1].cambios))
    app._bench_intervalos = intervalos
    return [app, tiempos]


def _consultas(linea: LineaTiempo, reloj: int, semilla: int, cantidad: int = 200) -> list[list[int]]:
    """Mitad por número de acción y mitad por instante, deterministas."""
    azar = random.Random(semilla)
    resultado = []
    for i in range(cantidad):
        if i % 2 == 0:
            resultado.append(linea.ubicar_accion(azar.randrange(1, linea.acciones() + 2)))
        else:
            resultado.append(linea.ubicar_tiempo(azar.randrange(0, reloj + 1)))
    return resultado


def _medir_consultas(app, linea: LineaTiempo, consultas, modo=CERCANO) -> list:
    """[media s, peor s, peor acciones recorridas, media cambios recorridos] de la consulta completa."""
    controlador = app._linea
    original = controlador.linea
    controlador.linea = linea
    tiempos = []
    peor_acciones = 0
    cambios = 0
    try:
        for pos, marca in consultas:
            inicio = time.perf_counter()
            controlador._resumen(pos, marca, 0, 0, modo)
            tiempos.append(time.perf_counter() - inicio)
            peor_acciones = max(peor_acciones, linea.acciones_recorridas(pos, marca, modo))
            cambios += linea.costo(pos, marca, modo)[2]
    finally:
        controlador.linea = original
    return [sum(tiempos) / len(tiempos), max(tiempos), peor_acciones, cambios / len(consultas)]


def _bytes_de(fabrica) -> list:
    """[objeto, bytes retenidos] medidos con tracemalloc."""
    tracemalloc.start()
    antes = tracemalloc.get_traced_memory()[0]
    objeto = fabrica()
    despues = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()
    return [objeto, despues - antes]


def medir_l1(app, semilla=SEMILLA_PREDETERMINADA, valores=VALORES_K, imprimir=True) -> list:
    """L1: memoria y tiempo de consulta para varios K y sin puntos de control (FR-029, FR-030)."""
    base = app._linea.linea
    reloj = app._simulacion.reloj.tiempo_actual
    consultas = _consultas(base, reloj, semilla)
    filas = []
    if imprimir:
        print(f"L1 linea de tiempo: {base.acciones()} acciones, {base.cambios()} cambios, "
              f"{len(base._vivo)} ranuras, {len(consultas)} consultas (limite {LIMITE_CONSULTA_MS:.0f} ms)")
    for k in list(valores) + [SIN_PUNTOS_DE_CONTROL]:
        linea, memoria = _bytes_de(lambda: base.con_k(k))
        media, peor, acciones, _ = _medir_consultas(app, linea, consultas)
        _, celdas_cp, celdas = linea.memoria()
        nombre = "sin puntos de control" if k == SIN_PUNTOS_DE_CONTROL else f"K={k}"
        filas.append([k, linea.puntos_de_control(), celdas, memoria, media, peor, acciones])
        if imprimir:
            estado = "CUMPLE" if peor * 1000 <= LIMITE_CONSULTA_MS else "EXCEDE"
            print(f"  {nombre:>22}: puntos={linea.puntos_de_control():>5} celdas={celdas:>8} "
                  f"(control {celdas_cp:>8}) memoria={memoria / 1024:9.1f}KiB "
                  f"consulta media={_ms(media)} peor={_ms(peor)} acciones<={acciones} {estado}")
    return filas


def linea_pesada(acciones=5000, ranuras=1000, cambios=60, semilla=SEMILLA_PREDETERMINADA,
                 k=SIN_PUNTOS_DE_CONTROL) -> LineaTiempo:
    """Carga sintética pesada: `cambios` por acción (decenas de cazadores que se mueven y pierden vida)
    sobre `ranuras` (una cripta grande), con varios cambios por instante. Determinista por semilla."""
    azar = random.Random(semilla)
    linea = LineaTiempo(k, [0] * ranuras)
    t = 0
    for _ in range(acciones):
        linea.marcar(t)
        instante = t
        for _ in range(cambios):
            instante += azar.randrange(0, 3)
            linea.registrar(instante, azar.randrange(ranuras), azar.randrange(1, 10 ** 6))
        t = instante + 1 + azar.randrange(100)
    return linea


def medir_l1_pesada(semilla=SEMILLA_PREDETERMINADA, valores=VALORES_K, acciones=5000, ranuras=1000,
                    cambios=60, cantidad=200, imprimir=True) -> list:
    """L1b: la misma comparación de L1 con carga pesada, solo la estructura (reconstrucción)."""
    base = linea_pesada(acciones, ranuras, cambios, semilla)
    reloj = base._t[-1] if base._t else 0
    consultas = _consultas(base, reloj, semilla, cantidad)
    filas = []
    if imprimir:
        print(f"L1b carga pesada: {acciones} acciones, {base.cambios()} cambios, {ranuras} ranuras, "
              f"{cantidad} consultas")
    for k in list(valores) + [SIN_PUNTOS_DE_CONTROL]:
        linea, memoria = _bytes_de(lambda: base.con_k(k))
        tiempos = []
        peor_acciones = 0
        for pos, marca in consultas:
            inicio = time.perf_counter()
            linea.estado_en(pos, marca)
            tiempos.append(time.perf_counter() - inicio)
            peor_acciones = max(peor_acciones, linea.acciones_recorridas(pos, marca))
        media, peor = sum(tiempos) / len(tiempos), max(tiempos)
        filas.append([k, linea.puntos_de_control(), linea.memoria()[2], memoria, media, peor, peor_acciones])
        if imprimir:
            nombre = "sin puntos de control" if k == SIN_PUNTOS_DE_CONTROL else f"K={k}"
            estado = "CUMPLE" if peor * 1000 <= LIMITE_CONSULTA_MS else "EXCEDE"
            print(f"  {nombre:>22}: puntos={linea.puntos_de_control():>5} celdas={linea.memoria()[2]:>9} "
                  f"memoria={memoria / 1024 / 1024:8.2f}MiB reconstruccion media={_ms(media)} "
                  f"peor={_ms(peor)} acciones<={peor_acciones} {estado}")
        del linea
    return filas


def medir_l2(app, semilla=SEMILLA_PREDETERMINADA, imprimir=True) -> list:
    """L2: reconstrucción hacia adelante, hacia atrás y desde el más cercano (FR-031)."""
    linea = app._linea.linea
    consultas = _consultas(linea, app._simulacion.reloj.tiempo_actual, semilla + 1)
    filas = []
    if imprimir:
        print(f"L2 direccion de reconstruccion con K={linea.k}")
    for modo in [ADELANTE, ATRAS, CERCANO]:
        media, peor, acciones, cambios = _medir_consultas(app, linea, consultas, modo)
        filas.append([modo, media, peor, acciones, cambios])
        if imprimir:
            print(f"  {modo:>9}: media={_ms(media)} peor={_ms(peor)} cambios recorridos (media)={cambios:8.1f} "
                  f"acciones<={acciones}")
    return filas


def medir_l3(tiempos_con: list, tiempos_sin: list, imprimir=True) -> list:
    """L3: costo de la captura por acción, la misma partida con y sin línea de tiempo."""
    con = [sum(tiempos_con) / len(tiempos_con), max(tiempos_con)]
    sin = [sum(tiempos_sin) / len(tiempos_sin), max(tiempos_sin)]
    if imprimir:
        estado = "CUMPLE" if con[1] * 1000 < LIMITE_CICLO_MS else "EXCEDE"
        print(f"L3 accion completa (ciclo de eventos incluido), {len(tiempos_con)} acciones")
        print(f"  con linea: media={_ms(con[0])} peor={_ms(con[1])} limite {LIMITE_CICLO_MS:.0f} ms {estado}")
        print(f"  sin linea: media={_ms(sin[0])} peor={_ms(sin[1])}")
        print(f"  sobrecosto medio: {(con[0] - sin[0]) * 1000:.3f}ms por accion")
    return [con, sin]


def _linea_sintetica(acciones: int, cambios_por_accion: int, k: int = 50) -> LineaTiempo:
    linea = LineaTiempo(k, [0] * 32)
    t = 0
    for a in range(acciones):
        linea.marcar(t)
        for c in range(cambios_por_accion):
            linea.registrar(t, (a + c) % 32, a + c + 1)
        t += 100
    return linea


def medir_l4(tamanos=(1000, 10000), cambios=10, recortes=200, imprimir=True) -> list:
    """L4: recorte por pergamino; debe costar lo recortado, no la longitud de la línea (FR-012)."""
    filas = []
    if imprimir:
        print(f"L4 recorte por pergamino ({cambios} cambios por accion, {recortes} recortes)")
    for n in tamanos:
        linea = _linea_sintetica(n + recortes, cambios)
        inicio = time.perf_counter()
        for _ in range(recortes):
            linea.recortar(linea.acciones())
        media = (time.perf_counter() - inicio) / recortes
        filas.append([n, media])
        if imprimir:
            print(f"  {n:>6} acciones: recorte medio={_ms(media)}")
    return filas


def medir_l5(intervalos=10000, atributos=10, app=None, imprimir=True) -> list:
    """L5 (§5.6): historial de retroceso con la carga nueva, con y sin observador (FR-032)."""

    class Objeto:
        pass

    def correr(observador) -> float:
        historial = Historial_Retroceso(5)
        historial.observador = observador
        objeto = Objeto()
        for i in range(atributos):
            setattr(objeto, f"a{i}", 0)
        inicio = time.perf_counter()
        for n in range(intervalos):
            historial.abrir_intervalo()
            for i in range(atributos):
                historial.cambiar(objeto, f"a{i}", n + 1)
            historial.cerrar_intervalo()
            if n % 2 == 1:
                historial.deshacer(lambda etiqueta, datos: setattr(datos[0], datos[1], datos[2]))
        return time.perf_counter() - inicio

    vistos = []
    sin = min(correr(None) for _ in range(3))
    con = min(correr(lambda etiqueta, datos: vistos.append(etiqueta) if len(vistos) < 0 else None)
              for _ in range(3))
    tamanos = getattr(app, "_bench_intervalos", []) if app is not None else []
    if imprimir:
        print(f"L5 historial de retroceso (5.6): {intervalos} intervalos de {atributos} atributos, "
              f"mitad revertidos")
        print(f"  sin observador={_ms(sin)} con observador de la linea={_ms(con)} "
              f"razon={con / sin:.2f}")
        if tamanos:
            print(f"  cambios por intervalo en la partida larga: media={sum(tamanos) / len(tamanos):.1f} "
                  f"maximo={max(tamanos)} ({len(tamanos)} intervalos)")
    return [sin, con, tamanos]


def bench_linea(semilla=SEMILLA_PREDETERMINADA, acciones=5000, carpeta=None) -> None:
    from cripta.controlador.LineaTiempoControlador import K_POR_DEFECTO

    print(f"\n=== Linea de tiempo y puntos de control (5.5) y retroceso (5.6), semilla {semilla} ===")
    app, tiempos_con = jugar_partida_larga(acciones, semilla, K_POR_DEFECTO, True, carpeta)
    if app is None:
        print("L1 a L3: no esta disponible el paquete datos_offline.")
    else:
        print(f"Partida larga: cripta {app.estado_partida().cripta_id}, "
              f"{app._linea.linea.acciones()} acciones, reloj {app._simulacion.reloj.tiempo_actual}")
        medir_l1(app, semilla)
        medir_l2(app, semilla)
        _, tiempos_sin = jugar_partida_larga(acciones, semilla, K_POR_DEFECTO, False, carpeta)
        medir_l3(tiempos_con, tiempos_sin)
    medir_l1_pesada(semilla)
    medir_l4()
    medir_l5(app=app)
