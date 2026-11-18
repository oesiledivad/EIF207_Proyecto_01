"""Mediciones sobre el esqueleto publicado, leído antes de cronometrar."""
import random
import time
from pathlib import Path
from types import SimpleNamespace

from cripta.adaptadores.AdaptadorOffline import AdaptadorOffline
from cripta.controlador.Aplicacion import Aplicacion
from cripta.modelo.Conocimiento import ConocimientoJugador, EXPLORADA, ABIERTA, CERRADA
from cripta.modelo.Resolubilidad import verificar
from cripta.modelo.Rutas import BuscadorRutas


def medir_referencia_publicada(semilla=42, carpeta=None, cazadores=50, ciclos=200):
    from cripta.bench import _ciclo_cazadores, paso_ir_a

    carpeta = Path(carpeta) if carpeta is not None else Path(__file__).resolve().parents[2] / "datos_entrega"
    if not (carpeta / "criptas.json").is_file():
        print("Referencia publicada: NO MEDIDA; falta el paquete datos_entrega.")
        return None
    fuente = AdaptadorOffline(carpeta)
    candidatas = fuente.crypta_list()["criptas"]
    if not candidatas:
        raise ValueError("El paquete de referencia no contiene criptas.")
    resumen = min(candidatas, key=lambda c: (-c["salas"], c["id"]))
    app = Aplicacion(fuente)
    servicio = app._cripta_service
    detalles = servicio.obtener_detalles(resumen["id"])
    esqueleto = servicio.cargar_esqueleto_salas(detalles.id, detalles.sala_salida)
    llaves = servicio.obtener_ubicaciones_llaves(detalles.id)
    app._crear_salas_desde_esqueleto(esqueleto)
    ids = [s.id for s in esqueleto]
    if not ids or len(ids) != resumen["salas"]:
        raise ValueError("El esqueleto de referencia está incompleto.")
    salas = app._salas
    entrantes = app._exploracion.entrantes
    conocimiento = ConocimientoJugador()
    conocimiento.iniciar(salas, entrantes, detalles.sala_inicial)
    for sala_id in ids:
        conocimiento.estado_sala[sala_id] = EXPLORADA
        for salida in salas.obtener(sala_id).salidas:
            conocimiento.puerta[salida.clave] = CERRADA if salida.cerrada else ABIERTA
    azar = random.Random(semilla)
    pares = [[azar.choice(ids), azar.choice(ids)] for _ in range(20)]
    buscador = BuscadorRutas(len(entrantes))

    tiempos_verificacion = []
    for _ in range(20):
        inicio = time.perf_counter()
        resultado = verificar(detalles, esqueleto, llaves)
        tiempos_verificacion.append((time.perf_counter() - inicio) * 1000)
    tiempos_ruta, pasos = [], []
    for origen, destino in pares:
        inicio = time.perf_counter()
        paso = paso_ir_a(SimpleNamespace(salas=salas, entrantes=entrantes), conocimiento,
                         buscador, origen, destino)
        tiempos_ruta.append((time.perf_counter() - inicio) * 1000)
        pasos.append(None if paso is None else paso.clave)

    cripta = SimpleNamespace(salas=salas, entrantes=entrantes, n_salas=len(entrantes), ids=ids,
                             jugador=detalles.sala_inicial,
                             cazadores=[azar.choice(ids) for _ in range(cazadores)],
                             rango=sum(s.costo for i in ids for s in salas.obtener(i).salidas))
    tiempos_ciclo, estado = _ciclo_cazadores(cripta, semilla, ciclos)
    v, r, c = max(tiempos_verificacion), max(tiempos_ruta), max(tiempos_ciclo)
    print(f"\n=== Referencia publicada {detalles.id} version={detalles.version} salas={len(ids)} ===")
    print(f"P1 verificacion={resultado.estado} maximo_ms={v:.3f} limite=200ms "
          f"{'CUMPLE' if v < 200 else 'EXCEDE'}")
    print(f"P2 paso de ir a: pares={len(pares)} maximo_ms={r:.3f} limite=5ms "
          f"{'CUMPLE' if r < 5 else 'EXCEDE'}")
    print(f"P3 mapa real, {cazadores} cazadores activos de prueba, rango={cripta.rango}, "
          f"ciclos={ciclos} maximo_ms={c:.3f} limite=20ms {'CUMPLE' if c < 20 else 'EXCEDE'}")
    return SimpleNamespace(verificacion_ms=v, ruta_ms=r, ciclo_ms=c, salas=len(ids),
                           cripta_id=detalles.id, version=detalles.version,
                           huella=[resultado.estado, pares, pasos, estado])
