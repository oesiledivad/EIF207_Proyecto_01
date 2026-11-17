"""Cargas sinteticas sin red ni interfaz para --bench."""

from __future__ import annotations

import random
import time
from types import SimpleNamespace

from cripta.estructuras.Agenda_Eventos import HeapAgendaEventos
from cripta.estructuras.Salidas import Salidas
from cripta.estructuras.Historial_Retroceso import Historial_Retroceso
from cripta.modelo.Rutas import BuscadorRutas
from cripta.estructuras.Indice_Salas import IndiceSalas
from cripta.estructuras.Cache_Fichas import Cache_Fichas
from cripta.modelo.Sala import SalaJuego
from cripta.modelo.enemigos.Rastreador import Rastreador


class _ActorFalso:
    """Soporte mínimo para encolar eventos sintéticos sin armar un Actor real."""
    def __init__(self, identificador: str) -> None:
        self.identificador = identificador
        self._proximo_evento = None


# 1. Agenda: heap propio vs. lista ordenada por inserción (4.1)

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


# 2. decidir_accion vs. tamaño de la cripta (4.7)

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


# 3. Cache_Fichas: acierto vs. fallo (4.4)

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
    print("=== Agenda: heap propio vs. lista ordenada (4.1) ===")
    for n in [100, 500, 2000]:
        ih, eh = _bench_agenda_heap(n)
        il, el = _bench_lista_ordenada(n)
        print(f"n={n:5d}  heap: insertar={ih*1000:.2f}ms extraer={eh*1000:.2f}ms"
              f"   |   lista: insertar={il*1000:.2f}ms extraer={el*1000:.2f}ms")

    print("\n=== Rastreador.decidir_accion vs. tamaño de la cripta (4.7) ===")
    for n_salas in [20, 200, 2000]:
        t = _bench_decidir_accion(n_salas, repeticiones=10_000)
        print(f"cripta de {n_salas:5d} salas -> 10000 llamadas en {t*1000:.2f}ms "
              f"({t*1_000_000/10_000:.3f}µs por llamada)")

    print("\n=== Cache_Fichas llena (25 fichas): acierto vs. fallo (4.4) ===")
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


def _bench_ciclo_completo(n_enemigos=500, repeticiones=100):
    """Mide acciones reales con combate, historial y sincronización, sin E/S ni vista."""
    from types import SimpleNamespace
    from cripta.controlador.Aplicacion import Aplicacion
    from cripta.dto.Partida_dto import SalaModelo
    from cripta.modelo.Jugador import Jugador
    from cripta.modelo.Simulacion import Simulacion
    from cripta.modelo.enemigos.Guardian import Guardian

    app = Aplicacion(SimpleNamespace(requests_made=0))
    app._salas = _construir_cripta_sintetica(20)
    app._gestor.reiniciar_inventario(10)
    estado = app.estado_partida()
    estado.activa = True
    estado.salas_conocidas = [SalaModelo(s.id, s.nombre, "") for s in app._salas._datos if s is not None]
    vida = max(1, n_enemigos * repeticiones * 10)
    app._jugador = Jugador("jugador", vida, vida, 6, 100, 100, 0, 0, 10)
    app._simulacion = Simulacion(42, app._gestor.historial)
    app._simulacion.agenda.reprogramar(app._jugador, 0, "accion_actor")
    ficha = SimpleNamespace(id="enemigo-bench", nombre="Guardián sintético")
    app._cripta_service._cache_fichas.insertar(ficha.id, ficha)
    sala = app._salas.obtener(0)
    for i in range(n_enemigos):
        enemigo = Guardian(str(i), 10, 10, 3, 0, 150, 0, None)
        enemigo.tipo = ficha.id
        sala.agregar_enemigo(enemigo)
    app._combate.activar_sala(sala, app._simulacion)
    medidas = []
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        resultado = app.esperar()
        medidas.append((time.perf_counter() - inicio) * 1000)
        assert resultado.ok, resultado.motivo
    peor = max(medidas)
    print(f"ciclo completo: enemigos={n_enemigos} n={repeticiones} "
          f"media={sum(medidas)/len(medidas):.3f}ms maximo={peor:.3f}ms "
          f"limite=20ms {'CUMPLE' if peor < 20 else 'EXCEDE'}")
    return medidas


def _bench_referencia(repeticiones=30):
    """Mide movimiento y combate normales con la cripta de referencia ya cargada."""
    from pathlib import Path
    from cripta.adaptadores.AdaptadorOffline import AdaptadorOffline
    from cripta.controlador.Aplicacion import Aplicacion

    carpeta = Path(__file__).resolve().parents[2] / "datos_offline"
    if not (carpeta / "cripta_cripta-01.json").is_file():
        print("Referencia: no está disponible el paquete datos_offline.")
        return []
    medidas = []

    def medir(accion):
        inicio = time.perf_counter()
        resultado = accion()
        medidas.append((time.perf_counter() - inicio) * 1000)
        assert resultado.ok, resultado.motivo

    for semilla in range(repeticiones):
        app = Aplicacion(AdaptadorOffline(carpeta))
        resultado = app.iniciar_partida("Bench", str(semilla), "cripta-01")
        assert resultado.ok, resultado.motivo
        # La referencia cabe en el primer lote: ninguna acción medida solicita contenido.
        assert not app.estado_partida().contenido_pendiente
        puerta = next(s for s in app.estado_partida().vecindad if not s.cerrada)
        medir(lambda: app.mover(puerta.direccion))
        for _ in range(100):
            estado = app.estado_partida()
            if estado.terminada or not estado.enemigos:
                break
            medir(lambda: app.atacar(estado.enemigos[0].id))
    peor = max(medidas)
    print(f"referencia cripta-01: ciclos={len(medidas)} media={sum(medidas)/len(medidas):.3f}ms "
          f"maximo={peor:.3f}ms limite=20ms {'CUMPLE' if peor < 20 else 'EXCEDE'}")
    return medidas


# Resolubilidad de la cripta (Parte II, 3.5 y 5.4): mediciones M1 a M7.
# Todo es sintetico y determinista por semilla; no usa red, disco de la cripta ni vista.

SEMILLA_PREDETERMINADA = 42
SALAS_SIN_PAQUETE = 500   # Tamano de M7 cuando no esta el paquete datos_offline


def semilla_efectiva(texto) -> int:
    """Semilla de --bench: vacia o None equivale a 42, nunca es aleatoria.

    Raises:
        ValueError: si el texto no es un entero.
    """
    if texto is None or str(texto).strip() == "":
        return SEMILLA_PREDETERMINADA
    try:
        return int(str(texto).strip())
    except ValueError:
        raise ValueError("--semilla debe ser un entero.") from None


class CriptaSintetica:
    """Cripta generada por semilla, lista para `verificar`."""

    def __init__(self, detalles, salas, ubicaciones, n_salidas, n_llaves):
        self.detalles = detalles
        self.salas = salas
        self.ubicaciones = ubicaciones
        self.n_salas = len(salas)
        self.n_salidas = n_salidas
        self.n_llaves = n_llaves


def generar_cripta(semilla: int, salas: int, llaves: int | None = None,
                   con_ciclo: bool = False) -> CriptaSintetica:
    """Genera una cripta sintetica determinista (D8).

    Region base conectada por un arbol aleatorio con salidas abiertas, una cadena
    de K llaves (la puerta j exige la llave j-1 y la llave j esta en la sala que esa
    puerta abre), ramas decorativas y ubicaciones repetidas. Los ids de sala se
    permutan por la semilla. Con `con_ciclo`, la puerta de la penultima sala de la
    cadena exige la ultima llave y se cierra un ciclo.

    Args:
        semilla: Semilla de `random.Random`.
        salas: Cantidad total de salas S.
        llaves: Cantidad K de llaves; por omision S // 10 (al menos 2).
        con_ciclo: Variante no resoluble con ciclo final.

    Raises:
        ValueError: si S es muy pequeno para K llaves.
    """
    from cripta.dto.Partida_dto import DetallesCripta, SalaModelo, SalidaVecina
    from cripta.dto.Verificacion_dto import UbicacionLlave

    azar = random.Random(semilla)
    k = llaves if llaves is not None else max(2, salas // 10)
    if k < 2 or salas < k + 4:
        raise ValueError("La cripta sintetica necesita al menos 2 llaves y K + 4 salas.")
    restantes = salas - k - 1          # Salas de la region base y ramas decorativas
    decorativas = restantes // 10
    base = restantes - decorativas
    primera_cadena = base + decorativas
    salida_final = salas - 1

    ids = list(range(salas))
    azar.shuffle(ids)
    permutacion = list(range(k))
    azar.shuffle(permutacion)
    nombres = [f"llave-{p:06d}" for p in permutacion]

    salidas: list[list] = [[] for _ in range(salas)]    # Por sala logica: [direccion, destino, llave]
    total_salidas = 0

    def conectar(a: int, b: int, llave: str = "") -> None:
        nonlocal total_salidas
        salidas[a].append([f"p{len(salidas[a])}", b, llave])
        total_salidas += 1

    def abrir(a: int, b: int) -> None:
        conectar(a, b)
        conectar(b, a)

    for i in range(1, base):
        abrir(i, azar.randrange(i))
    for _ in range(base // 10):
        a = azar.randrange(base)
        b = azar.randrange(base)
        if a != b:
            abrir(a, b)
    for d in range(decorativas):
        abrir(base + d, azar.randrange(base + d))

    # Cadena: todas las puertas salen de la sala inicial y la puerta j abre la sala j de la
    # cadena, donde esta la llave j. Asi cada llave libera solo la siguiente puerta.
    for j in range(k):
        origen = 0
        if con_ciclo and j == k - 2:
            exigida = k - 1
        else:
            exigida = j - 1
        conectar(origen, primera_cadena + j, nombres[exigida] if exigida >= 0 else "")
    conectar(primera_cadena + k - 1, salida_final, nombres[k - 1])

    ubicaciones: list = []
    for j in range(k):
        enemigo = f"enemigo-{j}" if azar.random() < 0.3 else None
        ubicaciones.append(UbicacionLlave(nombres[j], ids[primera_cadena + j], enemigo))
    for j in range(k):
        if azar.random() < 0.05:
            otra = azar.randrange(j, k)
            if otra != j:
                ubicaciones.append(UbicacionLlave(nombres[j], ids[primera_cadena + otra], None))

    lista = []
    for logica in range(salas):
        vecinas = [
            SalidaVecina(direccion=d, sala_id=ids[destino], nombre="", cerrada=bool(llave),
                         llave=llave, transitable=True, es_salida_final=False,
                         tiene_enemigos=False, tiene_objetos=False)
            for d, destino, llave in salidas[logica]
        ]
        lista.append(SalaModelo(id=ids[logica], nombre=f"s{ids[logica]}", descripcion="", salidas=vecinas))
    detalles = DetallesCripta(
        id="sintetica", version=f"semilla-{semilla}", salas_total=salas, sala_inicial=ids[0],
        sala_salida=ids[salida_final], llave_salida=nombres[k - 1], inventario_max=10,
        presupuesto_solicitudes=0, jugador_vida_max=30, jugador_ataque=6, jugador_defensa=2,
        jugador_velocidad=100)
    return CriptaSintetica(detalles, lista, ubicaciones, total_salidas, k)


def verificar_ingenua(cripta: CriptaSintetica):
    """Alternativa DESCARTADA, solo para medicion: O(K * (S + E)).

    Repite la exploracion completa cada vez que se obtiene una llave nueva. Es
    justo lo que FR-024 prohibe; se conserva como contraste de M1, igual que
    `_ListaOrdenada` en la medicion de la agenda.

    Returns:
        (gano, operaciones): operaciones cuenta salidas recorridas y llaves obtenidas.
    """
    from cripta.estructuras.Indice_Llaves import IndiceLlaves

    detalles = cripta.detalles
    total = 0
    for s in cripta.salas:
        if s.id + 1 > total:
            total = s.id + 1
    ids_llaves = [u.llave for u in cripta.ubicaciones] + [detalles.llave_salida]
    indice = IndiceLlaves(ids_llaves)
    cantidad = indice.cantidad()
    rango_salida = indice.rango(detalles.llave_salida)
    salidas: list[list] = [[] for _ in range(total)]
    for s in cripta.salas:
        for sa in s.salidas:
            salidas[s.id].append((sa.sala_id, indice.rango(sa.llave) if sa.cerrada else -1))
    llaves_sala: list[list] = [[] for _ in range(total)]
    for u in cripta.ubicaciones:
        llaves_sala[u.sala].append(indice.rango(u.llave))

    tengo = [False] * cantidad
    operaciones = 0
    while True:
        visto = [False] * total
        cola = [detalles.sala_inicial]
        visto[detalles.sala_inicial] = True
        cabeza = 0
        nueva = False
        gano = False
        while cabeza < len(cola):
            sala = cola[cabeza]
            cabeza += 1
            for k in llaves_sala[sala]:
                if not tengo[k]:
                    tengo[k] = True
                    nueva = True
                    operaciones += 1
            for destino, k in salidas[sala]:
                operaciones += 1
                if k != -1 and not tengo[k]:
                    continue
                if k != -1 and k == rango_salida and destino == detalles.sala_salida:
                    gano = True
                if not visto[destino]:
                    visto[destino] = True
                    cola.append(destino)
        if gano or not nueva:
            return gano, operaciones


def _mejor_de(repeticiones: int, operacion) -> float:
    """Menor tiempo en segundos de `repeticiones` corridas."""
    mejor = None
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        operacion()
        transcurrido = time.perf_counter() - inicio
        if mejor is None or transcurrido < mejor:
            mejor = transcurrido
    return mejor


def _ms(segundos) -> str:
    return "---" if segundos is None else f"{segundos * 1000:.3f}ms"


def _carpeta_paquete(carpeta=None):
    from pathlib import Path
    if carpeta is not None:
        return Path(carpeta)
    return Path(__file__).resolve().parents[2] / "datos_offline"


def tamano_mayor_esqueleto(carpeta=None) -> int | None:
    """Mayor `salas_total` entre las criptas del paquete; None si el paquete no esta."""
    import json

    carpeta = _carpeta_paquete(carpeta)
    if not carpeta.is_dir():
        return None
    mayor = None
    for ruta in carpeta.glob("cripta_*.json"):
        nombre = ruta.name
        if nombre.endswith(("_contenido.json", "_version.json", "_llaves.json")) or "_salas_" in nombre:
            continue
        try:
            datos = json.loads(ruta.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        total = datos.get("salas_total") if isinstance(datos, dict) else None
        if isinstance(total, int) and (mayor is None or total > mayor):
            mayor = total
    return mayor


def _verificar_cripta(cripta):
    from cripta.modelo.Resolubilidad import verificar
    return verificar(cripta.detalles, cripta.salas, cripta.ubicaciones)


def medir_m1(tamanos=(200, 2000, 20000), tope_ingenua=2000, semilla=SEMILLA_PREDETERMINADA):
    """M1: verificacion O(S + E + K) frente a la ingenua O(K (S + E)). FR-024, FR-026, SC-004."""
    print("M1 verificacion frente a la alternativa ingenua (la ingenua pierde y la brecha crece con K)")
    filas = []
    for salas in tamanos:
        cripta = generar_cripta(semilla, salas)
        resultado = _verificar_cripta(cripta)
        est = resultado.estadisticas
        ops_verificacion = est.salidas_examinadas + est.llaves_obtenidas
        t_verificacion = _mejor_de(5, lambda: _verificar_cripta(cripta))
        t_ingenua = None
        ops_ingenua = None
        if salas <= tope_ingenua:
            inicio = time.perf_counter()
            ops_ingenua = verificar_ingenua(cripta)[1]
            t_ingenua = time.perf_counter() - inicio
        filas.append(SimpleNamespace(
            salas=salas, salidas=cripta.n_salidas, llaves=cripta.n_llaves,
            t_verificacion=t_verificacion, t_ingenua=t_ingenua,
            ops_verificacion=ops_verificacion, ops_ingenua=ops_ingenua))
        if t_ingenua is None:
            comparacion = "ingenua=omitida (supera el tope)"
        else:
            comparacion = (f"ingenua={_ms(t_ingenua)} ({ops_ingenua} ops) "
                           f"ingenua/verificacion={t_ingenua / max(t_verificacion, 1e-9):.1f}x "
                           f"{'PIERDE' if t_ingenua > t_verificacion else 'GANA'}")
        print(f"  S={salas} E={cripta.n_salidas} K={cripta.n_llaves} "
              f"verificacion={_ms(t_verificacion)} ({ops_verificacion} ops) {comparacion}")
    previa = None
    creciente = True
    for fila in filas:
        if fila.t_ingenua is None:
            continue
        brecha = fila.t_ingenua / max(fila.t_verificacion, 1e-9)
        if previa is not None and brecha <= previa:
            creciente = False
        previa = brecha
    print(f"  la brecha crece con K: {'SI' if creciente else 'NO'}")
    return filas


def medir_m2(filas) -> None:
    """M2: escalado al multiplicar por 10 el tamano. FR-024, SC-004."""
    print("M2 escalado de la verificacion al multiplicar por 10 el tamano (limite 15)")
    for anterior, actual in zip(filas, filas[1:]):
        cociente = actual.t_verificacion / max(anterior.t_verificacion, 1e-9)
        cociente_ops = actual.ops_verificacion / max(anterior.ops_verificacion, 1)
        print(f"  S {anterior.salas} -> {actual.salas}: tiempo x{cociente:.2f} operaciones x{cociente_ops:.2f} "
              f"{'menor que 15' if cociente < 15 else 'NO es menor que 15'}")


def medir_m3(carpeta=None) -> None:
    """M3: cripta de referencia del paquete si trae llaves. FR-023, SC-003."""
    from cripta.adaptadores.AdaptadorOffline import AdaptadorOffline
    from cripta.controlador.VerificacionControlador import VerificacionControlador
    from cripta.servicio.CriptaService import CriptaService

    carpeta = _carpeta_paquete(carpeta)
    print("M3 cripta de referencia del paquete (sin red, limite 200 ms)")
    medidas = 0
    if carpeta.is_dir():
        for ruta in carpeta.glob("cripta_*_llaves.json"):
            cripta_id = ruta.name[len("cripta_"):-len("_llaves.json")]
            fuente = AdaptadorOffline(carpeta)
            controlador = VerificacionControlador(CriptaService(fuente))
            inicio = time.perf_counter()
            resultado = controlador.verificar_cripta(cripta_id)
            t = time.perf_counter() - inicio
            medidas += 1
            print(f"  {cripta_id}: {resultado.estado} en {_ms(t)} solicitudes={fuente.requests_made} "
                  f"{'menor que 200 ms' if t < 0.2 else 'EXCEDE 200 ms'}")
    if medidas == 0:
        print("  sin llaves en el paquete")


def medir_m7(semilla=SEMILLA_PREDETERMINADA, carpeta=None) -> None:
    """M7: cripta sintetica de 10 veces el esqueleto mayor del paquete. FR-023, SC-003."""
    mayor = tamano_mayor_esqueleto(carpeta)
    salas = 10 * mayor if mayor else SALAS_SIN_PAQUETE
    origen = f"10 x {mayor}" if mayor else "paquete ausente"
    print(f"M7 cripta sintetica grande sin red ({origen} salas, limite 200 ms)")
    cripta = generar_cripta(semilla, salas)
    resultado = _verificar_cripta(cripta)
    t = _mejor_de(3, lambda: _verificar_cripta(cripta))
    print(f"  S={cripta.n_salas} E={cripta.n_salidas} K={cripta.n_llaves} {resultado.estado} "
          f"en {_ms(t)} {'menor que 200 ms' if t < 0.2 else 'EXCEDE 200 ms'}")


class _TablaHashLlaves:
    """Alternativa medida en M4: tabla hash propia con hash polinomial determinista.

    No usa `hash()` de Python (que cambia entre ejecuciones) ni `dict`.
    """

    def __init__(self, ids: list[str]) -> None:
        tamano = 1
        while tamano < 2 * max(1, len(ids)):
            tamano *= 2
        self._ids = ids
        self._cubetas: list[list[int]] = [[] for _ in range(tamano)]
        self._mascara = tamano - 1
        for rango, id_llave in enumerate(ids):
            self._cubetas[self._hash(id_llave)].append(rango)

    def _hash(self, texto: str) -> int:
        h = 0
        for c in texto:
            h = (h * 131 + ord(c)) & 0xFFFFFFFF
        return h & self._mascara

    def rango(self, id_llave: str) -> int:
        for rango in self._cubetas[self._hash(id_llave)]:
            if self._ids[rango] == id_llave:
                return rango
        return -1


def medir_m4(salas=20000, semilla=SEMILLA_PREDETERMINADA) -> None:
    """M4: indice de llaves, arreglo ordenado con busqueda binaria frente a tabla hash. FR-024, FR-008."""
    from cripta.estructuras.Indice_Llaves import IndiceLlaves

    cripta = generar_cripta(semilla, salas)
    ids = []
    consultas = []
    for s in cripta.salas:
        for sa in s.salidas:
            if sa.cerrada:
                ids.append(sa.llave)
                consultas.append(sa.llave)
    for u in cripta.ubicaciones:
        ids.append(u.llave)
        consultas.append(u.llave)
    ids.append(cripta.detalles.llave_salida)

    def arreglo_completo():
        indice = IndiceLlaves(ids)
        for id_llave in consultas:
            indice.rango(id_llave)

    def hash_completo():
        # El rango sigue exigiendo el orden por id (FR-008), por eso incluye construir el arreglo.
        base = IndiceLlaves(ids).ids()
        tabla = _TablaHashLlaves(base)
        for id_llave in consultas:
            tabla.rango(id_llave)

    indice = IndiceLlaves(ids)
    tabla = _TablaHashLlaves(indice.ids())
    t_arreglo_consultas = _mejor_de(3, lambda: [indice.rango(c) for c in consultas])
    t_hash_consultas = _mejor_de(3, lambda: [tabla.rango(c) for c in consultas])
    t_arreglo = _mejor_de(3, arreglo_completo)
    t_hash = _mejor_de(3, hash_completo)
    ganancia = t_arreglo / max(t_hash, 1e-9)
    print(f"M4 indice de llaves a {salas} salas (K={indice.cantidad()}, {len(consultas)} consultas)")
    print(f"  solo consultas: arreglo={_ms(t_arreglo_consultas)} hash={_ms(t_hash_consultas)}")
    print(f"  construccion + consultas: arreglo={_ms(t_arreglo)} hash={_ms(t_hash)} "
          f"arreglo/hash={ganancia:.2f}x")
    decision = ("se conserva el arreglo ordenado (el hash no gana por mas de 2 veces)"
                if ganancia <= 2 else "gana la tabla hash por mas de 2 veces")
    print(f"  decision: {decision}")


def medir_m5(tamanos=(2000, 20000), semilla=SEMILLA_PREDETERMINADA) -> None:
    """M5: costo del reporte (fase especulativa y ciclos) sobre la verificacion pura. FR-025."""
    print("M5 costo del reporte sobre la verificacion pura (variante con ciclo)")
    anterior = None
    for salas in tamanos:
        pura = generar_cripta(semilla, salas)
        ciclica = generar_cripta(semilla, salas, con_ciclo=True)
        resultado = _verificar_cripta(ciclica)
        est = resultado.estadisticas
        t_pura = _mejor_de(3, lambda: _verificar_cripta(pura))
        t_reporte = _mejor_de(3, lambda: _verificar_cripta(ciclica))
        repite = ("no repite exploraciones" if est.salidas_examinadas <= 2 * ciclica.n_salidas
                  else "REPITE exploraciones")
        escala = ("" if anterior is None
                  else f" tiempo con reporte x{t_reporte / max(anterior, 1e-9):.2f} al multiplicar por 10")
        anterior = t_reporte
        print(f"  S={salas} E={ciclica.n_salidas} {resultado.estado} ciclos={len(resultado.reporte.ciclos)} "
              f"pura={_ms(t_pura)} con reporte={_ms(t_reporte)} "
              f"salidas examinadas={est.salidas_examinadas} de {ciclica.n_salidas} ({repite}){escala}")


def medir_m6(salas=20000, semilla=SEMILLA_PREDETERMINADA) -> None:
    """M6: orden por ronda con `ordenar` frente a orden de cola sin ordenar. FR-008, FR-024."""
    from cripta.estructuras.Ordenamientos import ordenar

    cripta = generar_cripta(semilla, salas)
    # Rondas de una exploracion en anchura que ignora las puertas: el mismo reparto por ronda.
    total = 0
    for s in cripta.salas:
        if s.id + 1 > total:
            total = s.id + 1
    vecinos: list[list[int]] = [[] for _ in range(total)]
    for s in cripta.salas:
        for sa in s.salidas:
            vecinos[s.id].append(sa.sala_id)
    visto = [False] * total
    actual = [cripta.detalles.sala_inicial]
    visto[actual[0]] = True
    lotes: list[list[int]] = []
    while actual:
        lotes.append(actual)
        siguiente = []
        for sala in actual:
            for destino in vecinos[sala]:
                if not visto[destino]:
                    visto[destino] = True
                    siguiente.append(destino)
        actual = siguiente

    def con_orden():
        for lote in lotes:
            ordenar(list(lote))

    def sin_orden():
        for lote in lotes:
            list(lote)

    t_orden = _mejor_de(3, con_orden)
    t_copia = _mejor_de(3, sin_orden)
    t_total = _mejor_de(3, lambda: _verificar_cripta(cripta))
    sobrecosto = (t_orden - t_copia) / max(t_total, 1e-9) * 100
    print(f"M6 orden por ronda a {salas} salas ({len(lotes)} rondas)")
    print(f"  con ordenar={_ms(t_orden)} sin ordenar={_ms(t_copia)} "
          f"verificacion completa={_ms(t_total)} sobrecosto del orden={sobrecosto:.1f}% de la verificacion")


def _bench_resolubilidad(semilla: int = SEMILLA_PREDETERMINADA) -> None:
    """Seccion Resolubilidad: M1 a M7, con la misma semilla en todas."""
    print(f"\n=== Resolubilidad de la cripta (semilla {semilla}) ===")
    filas = medir_m1((200, 2000, 20000), 2000, semilla)
    medir_m2(filas)
    medir_m3()
    medir_m4(20000, semilla)
    medir_m5((2000, 20000), semilla)
    medir_m6(20000, semilla)
    medir_m7(semilla)


# Niebla de guerra e ir a (Parte II, 3.3, 3.4 y 5.3): mediciones K1 a K9.
# Todo es sintetico y determinista por semilla; no usa red, disco ni vista (FR-039, FR-040).

SALAS_REFERENCIA_SINTETICA = 2000   # Tamano de K4 cuando no esta el paquete datos_offline
PARES_POR_MEDICION = 20


class CriptaConocimiento:
    """Esqueleto sintetico para medir el conocimiento y las rutas (sin contenido)."""

    def __init__(self, salas, entrantes, n_salas, n_salidas):
        self.salas = salas
        self.entrantes = entrantes
        self.n_salas = n_salas
        self.n_salidas = n_salidas


def generar_cripta_conocimiento(semilla: int, salas: int) -> CriptaConocimiento:
    """Cuadricula determinista con salidas dirigidas, costos variados y puertas de un solo lado (FR-039, FR-041).

    Cada sala se conecta con sus vecinas de la cuadricula, pero cerca del 3 % de las
    salidas se omite (queda una sola direccion), cerca del 10 % de las salidas hacia el
    este y el sur se declara cerrada solo en ese lado y cerca del 20 % no declara costo
    (vale 100). Los ids son secuenciales.
    """
    from cripta.modelo.Sala import SalaJuego
    from cripta.estructuras.Salidas import indice_direccion

    azar = random.Random(semilla)
    ancho = 1
    while ancho * ancho < salas:
        ancho += 1
    indice = IndiceSalas(max(1, salas))
    entrantes: list[list] = [[] for _ in range(salas)]
    total = 0
    for i in range(salas):
        fila = i // ancho
        columna = i % ancho
        salidas = Salidas()
        vecinas = []
        if fila > 0:
            vecinas.append(["N", i - ancho, False])
        if i + ancho < salas:
            vecinas.append(["S", i + ancho, True])
        if columna + 1 < ancho and i + 1 < salas:
            vecinas.append(["E", i + 1, True])
        if columna > 0:
            vecinas.append(["O", i - 1, False])
        for direccion, destino, puede_cerrar in vecinas:
            if azar.random() < 0.03:
                continue
            cerrada = puede_cerrar and azar.random() < 0.10
            costo = 100 if azar.random() < 0.20 else azar.randint(1, 300)
            salidas.agregar(direccion, destino, cerrada, None, None, costo)
        for salida in salidas:
            salida.clave = i * 4 + indice_direccion(salida.direccion)
            entrantes[salida.sala_destino].append(salida)
            total += 1
        indice.insertar(i, SalaJuego(id=i, nombre=f"Sala {i}", salidas=salidas,
                                     enemigos=[], objetos=[], trampas=[]))
    return CriptaConocimiento(indice, entrantes, salas, total)


def conocimiento_vacio(cripta: CriptaConocimiento):
    """Conocimiento recien iniciado en la sala 0 sobre el esqueleto dado."""
    from cripta.modelo.Conocimiento import ConocimientoJugador

    conocimiento = ConocimientoJugador()
    conocimiento.iniciar(cripta.salas, cripta.entrantes, 0)
    return conocimiento


def conocimiento_completo(cripta: CriptaConocimiento):
    """Conocimiento con todas las salas exploradas y las puertas recordadas tal como son."""
    from cripta.modelo.Conocimiento import EXPLORADA, ABIERTA, CERRADA

    conocimiento = conocimiento_vacio(cripta)
    for i in range(cripta.n_salas):
        conocimiento.estado_sala[i] = EXPLORADA
        for salida in cripta.salas.obtener(i).salidas:
            conocimiento.puerta[salida.clave] = CERRADA if salida.cerrada else ABIERTA
    return conocimiento


def elegir_pares(semilla: int, salas: int, cantidad: int) -> list:
    """Pares (origen, destino) distintos elegidos por semilla."""
    azar = random.Random(semilla)
    pares = []
    if salas < 2:
        return pares
    while len(pares) < cantidad:
        origen = azar.randrange(salas)
        destino = azar.randrange(salas)
        if origen != destino:
            pares.append((origen, destino))
    return pares


def paso_ir_a(cripta, conocimiento, buscador, origen: int, destino: int):
    """Un paso de «ir a»: Dijkstra inverso con parada anticipada y eleccion del primer paso."""
    buscador.distancias_hacia(destino, cripta.entrantes, conocimiento.salida_usable, origen)
    return buscador.elegir_paso(origen, cripta.salas.obtener(origen).salidas, conocimiento.salida_usable)


def tamano_cripta_referencia(carpeta=None) -> int:
    """Mayor esqueleto del paquete (criterio de la spec 001); 2 000 salas si no hay paquete."""
    mayor = tamano_mayor_esqueleto(carpeta)
    return mayor if mayor else SALAS_REFERENCIA_SINTETICA


def medir_k1(tamanos=(200, 2000, 20000), semilla=SEMILLA_PREDETERMINADA, consultas=20000):
    """K1: estado de sala y puerta recordada con listas indexadas frente a busqueda lineal. FR-035, SC-004."""
    from cripta.modelo.Conocimiento import ConocimientoJugador, EXPLORADA, ABIERTA

    print("K1 consulta de estado de sala y de puerta recordada: listas indexadas frente a busqueda lineal "
          "(razon a lo sumo 1,5 con 10 veces el tamano; la lineal crece)")
    filas = []
    for salas in tamanos:
        conocimiento = ConocimientoJugador()
        conocimiento.estado_sala = [EXPLORADA] * salas
        conocimiento.puerta = [ABIERTA] * (4 * salas)
        conocimiento.inicializado = True
        azar = random.Random(semilla)
        ids = [azar.randrange(salas) for _ in range(consultas)]
        claves = [azar.randrange(4 * salas) for _ in range(consultas)]
        # Alternativa descartada: lista de ids explorados y de claves recordadas, con busqueda lineal.
        explorados = list(range(salas))
        recordadas = list(range(4 * salas))
        lineales = 100

        def consultar_estados():
            for sala in ids:
                conocimiento.estado(sala)

        def consultar_puertas():
            for clave in claves:
                conocimiento.memoria_puerta(clave)

        def buscar_lineal():
            for k in range(lineales):
                objetivo = ids[k]
                for valor in explorados:
                    if valor == objetivo:
                        break
                objetivo = claves[k]
                for valor in recordadas:
                    if valor == objetivo:
                        break

        t_estado = _mejor_de(7, consultar_estados) / consultas
        t_puerta = _mejor_de(7, consultar_puertas) / consultas
        t_lineal = _mejor_de(3, buscar_lineal) / (2 * lineales)
        filas.append(SimpleNamespace(salas=salas, t_estado=t_estado, t_puerta=t_puerta, t_lineal=t_lineal))
        print(f"  S={salas}: estado de sala={t_estado * 1e9:.1f}ns puerta recordada={t_puerta * 1e9:.1f}ns "
              f"busqueda lineal={t_lineal * 1e9:.1f}ns por consulta")
    for anterior, actual in zip(filas, filas[1:]):
        print(f"  S {anterior.salas} -> {actual.salas}: estado x{actual.t_estado / max(anterior.t_estado, 1e-12):.2f} "
              f"puerta x{actual.t_puerta / max(anterior.t_puerta, 1e-12):.2f} "
              f"lineal x{actual.t_lineal / max(anterior.t_lineal, 1e-12):.2f}")
    return filas


def _explorar_todo(cripta, antorcha: bool, sin_recolector: bool) -> list:
    """Entra a todas las salas en orden de id; devuelve [reveladas, cambios al registro, segundos]."""
    import gc
    from cripta.modelo.Conocimiento import DESCONOCIDA

    conocimiento = conocimiento_vacio(cripta)
    antes = 0
    for estado in conocimiento.estado_sala:
        if estado != DESCONOCIDA:
            antes += 1
    historial = Historial_Retroceso()
    historial.abrir_intervalo()
    reactivar = sin_recolector and gc.isenabled()
    if reactivar:
        gc.disable()
    try:
        inicio = time.perf_counter()
        for sala in range(cripta.n_salas):
            conocimiento.entrar(sala, antorcha, historial, sala)
        transcurrido = time.perf_counter() - inicio
    finally:
        if reactivar:
            gc.enable()
    despues = 0
    for estado in conocimiento.estado_sala:
        if estado != DESCONOCIDA:
            despues += 1
    return [despues - antes, len(conocimiento.registro), transcurrido]


def medir_k2(tamanos=(200, 2000, 20000), semilla=SEMILLA_PREDETERMINADA):
    """K2: explorar salas nuevas con y sin antorcha, costo por sala revelada. FR-036, SC-004.

    El criterio es el conteo de cambios por sala revelada (no depende de la maquina). El
    tiempo se informa con el recolector de basura activo y, aparte, sin sus pausas: con
    20 000 salas el recolector recorre las miles de entradas del registro y distorsiona
    el tiempo sin que cambie el trabajo del algoritmo.
    """
    print("K2 explorar por sala revelada, con y sin antorcha (razon a lo sumo 1,5 con 10 veces el tamano)")
    filas = []
    for salas in tamanos:
        cripta = generar_cripta_conocimiento(semilla, salas)
        sin = _explorar_todo(cripta, False, False)
        con = _explorar_todo(cripta, True, False)
        sin_gc = _explorar_todo(cripta, False, True)
        con_gc = _explorar_todo(cripta, True, True)
        fila = SimpleNamespace(
            salas=salas, reveladas=sin[0], ops_sin=sin[1] / sin[0], ops_con=con[1] / con[0],
            t_sin=sin[2] / sin[0], t_con=con[2] / con[0],
            t_sin_gc=sin_gc[2] / sin_gc[0], t_con_gc=con_gc[2] / con_gc[0])
        filas.append(fila)
        print(f"  S={salas}: reveladas={fila.reveladas} sin antorcha: {fila.ops_sin:.3f} cambios y "
              f"{fila.t_sin * 1e6:.3f}us por sala, con antorcha: {fila.ops_con:.3f} cambios y "
              f"{fila.t_con * 1e6:.3f}us por sala; sin pausas del recolector: "
              f"{fila.t_sin_gc * 1e6:.3f}us (sin) {fila.t_con_gc * 1e6:.3f}us (con)")
    for anterior, actual in zip(filas, filas[1:]):
        print(f"  S {anterior.salas} -> {actual.salas}: cambios por sala x{actual.ops_sin / anterior.ops_sin:.2f} "
              f"(sin) x{actual.ops_con / anterior.ops_con:.2f} (con); tiempo por sala "
              f"x{actual.t_sin / max(anterior.t_sin, 1e-12):.2f} (sin) x{actual.t_con / max(anterior.t_con, 1e-12):.2f} (con); "
              f"sin recolector x{actual.t_sin_gc / max(anterior.t_sin_gc, 1e-12):.2f} (sin) "
              f"x{actual.t_con_gc / max(anterior.t_con_gc, 1e-12):.2f} (con)")
    return filas


def _invertir(etiqueta, datos) -> None:
    """Inversion de los cambios de lista que usa el conocimiento (igual que `GestorPartida`)."""
    if etiqueta == "lista_asignada":
        lista, posicion, anterior = datos
        lista[posicion] = anterior
    elif etiqueta == "lista_agregada":
        datos[0].pop()


def _valor_alterno(j: int, salas: int) -> int:
    """Valor distinto del anterior para el cambio `j`: alterna explorada y avistada en cada vuelta."""
    from cripta.modelo.Conocimiento import AVISTADA, EXPLORADA
    return EXPLORADA if (j // (salas - 1)) % 2 == 0 else AVISTADA


def medir_k3(tamanos=(200, 20000), cambios=(10, 1000), semilla=SEMILLA_PREDETERMINADA):
    """K3: registrar e invertir con `lista_asignada` frente a copiar el conocimiento en cada cambio. FR-037."""
    print("K3 registrar e invertir con lista_asignada frente a copiar el conocimiento completo en cada cambio "
          "(lineal en los cambios; la copia crece con el mapa)")
    filas = []
    for salas in tamanos:
        cripta = generar_cripta_conocimiento(semilla, salas)
        for k in cambios:
            conocimiento = conocimiento_vacio(cripta)
            antes = list(conocimiento.estado_sala)
            historial = Historial_Retroceso()
            historial.abrir_intervalo()
            inicio = time.perf_counter()
            for j in range(k):
                conocimiento._asignar_estado(j % (salas - 1) + 1, _valor_alterno(j, salas), historial, j)
            registrados = len(conocimiento.registro)
            historial.cerrar_intervalo()
            historial.deshacer(_invertir)
            t_registro = time.perf_counter() - inicio
            revertido = conocimiento.estado_sala == antes
            conocimiento2 = conocimiento_vacio(cripta)
            inicio = time.perf_counter()
            copias = []
            for j in range(k):
                copias.append(conocimiento2.instantanea())
                conocimiento2.estado_sala[j % (salas - 1) + 1] = _valor_alterno(j, salas)
            t_copia = time.perf_counter() - inicio
            ops_copia = len(copias) * len(copias[0])
            filas.append(SimpleNamespace(salas=salas, cambios=k, registrados=registrados, revertido=revertido,
                                         t_registro=t_registro, t_copia=t_copia, ops_copia=ops_copia))
            print(f"  S={salas} cambios={k}: registrar+invertir={_ms(t_registro)} ({registrados} cambios, "
                  f"revertido={'SI' if revertido else 'NO'}) copia completa={_ms(t_copia)} ({ops_copia} valores copiados)")
    return filas


def medir_k4(semilla=SEMILLA_PREDETERMINADA, imprimir=True, carpeta=None):
    """K4: un paso de «ir a» con el mapa completo de la cripta de referencia. FR-038, SC-003."""
    salas = tamano_cripta_referencia(carpeta)
    cripta = generar_cripta_conocimiento(semilla, salas)
    conocimiento = conocimiento_completo(cripta)
    buscador = BuscadorRutas(salas)
    pares = elegir_pares(semilla, salas, PARES_POR_MEDICION)
    resultados = []
    maximo = 0.0
    total = 0.0
    for origen, destino in pares:
        mejor = None
        for _ in range(3):
            inicio = time.perf_counter()
            paso = paso_ir_a(cripta, conocimiento, buscador, origen, destino)
            transcurrido = time.perf_counter() - inicio
            mejor = transcurrido if mejor is None else min(mejor, transcurrido)
        distancia = buscador.distancia_de(origen)
        resultados.append([origen, destino, paso.direccion if paso else "-", -1 if distancia is None else distancia])
        maximo = max(maximo, mejor)
        total += mejor
    cumple = maximo < 0.005
    if imprimir:
        print(f"K4 paso de ir a con el mapa conocido completo de la cripta de referencia (S={salas}, "
              f"{len(pares)} pares por semilla, mejor de 3)")
        print(f"  media={_ms(total / len(pares))} maximo={_ms(maximo)} limite=5ms "
              f"{'CUMPLE' if cumple else 'EXCEDE'}")
    return SimpleNamespace(salas=salas, maximo=maximo, media=total / len(pares), cumple=cumple,
                           resultados=resultados)


def medir_k5(tamanos=(2000, 20000), semilla=SEMILLA_PREDETERMINADA):
    """K5: un paso de «ir a» a 2 000 y 20 000 salas exploradas, informativa. FR-038."""
    import math

    print("K5 paso de ir a con 2000 y 20000 salas exploradas (informativa, esperado O((V + E) log V))")
    filas = []
    for salas in tamanos:
        cripta = generar_cripta_conocimiento(semilla, salas)
        conocimiento = conocimiento_completo(cripta)
        buscador = BuscadorRutas(salas)
        pares = elegir_pares(semilla, salas, PARES_POR_MEDICION)
        maximo = 0.0
        total = 0.0
        for origen, destino in pares:
            inicio = time.perf_counter()
            paso_ir_a(cripta, conocimiento, buscador, origen, destino)
            transcurrido = time.perf_counter() - inicio
            maximo = max(maximo, transcurrido)
            total += transcurrido
        filas.append(SimpleNamespace(salas=salas, salidas=cripta.n_salidas, media=total / len(pares), maximo=maximo))
        print(f"  S={salas} E={cripta.n_salidas}: media={_ms(total / len(pares))} maximo={_ms(maximo)}")
    for anterior, actual in zip(filas, filas[1:]):
        esperado = ((actual.salas + actual.salidas) * math.log(actual.salas)) / (
            (anterior.salas + anterior.salidas) * math.log(anterior.salas))
        print(f"  S {anterior.salas} -> {actual.salas}: media x{actual.media / max(anterior.media, 1e-12):.2f} "
              f"maximo x{actual.maximo / max(anterior.maximo, 1e-12):.2f} "
              f"(el factor (V + E) log V de la cota es x{esperado:.2f})")
    return filas


def _recorrer(cripta, destino: int, origen: int, siguiente_paso) -> list:
    """Viaje paso a paso con una estrategia; devuelve [costo total, pasos]. Se corta a S pasos."""
    actual = origen
    costo = 0
    pasos = 0
    while actual != destino and pasos < cripta.n_salas:
        salida = siguiente_paso(actual)
        if salida is None:
            return [-1, pasos]
        costo += salida.costo
        actual = salida.sala_destino
        pasos += 1
    return [costo, pasos]


def _paso_desde_origen(cripta, conocimiento, estado, origen: int, destino: int):
    """Alternativa K6: Dijkstra desde el origen con padres; devuelve la primera salida de la ruta."""
    estado.generacion += 1
    generacion = estado.generacion
    monticulo = estado.monticulo
    monticulo.vaciar()
    estado.marca[origen] = generacion
    estado.distancia[origen] = 0
    monticulo.insertar(0, origen, origen)
    while not monticulo.esta_vacio():
        prioridad, _, sala = monticulo.extraer_minimo()
        if prioridad != estado.distancia[sala]:
            continue
        if sala == destino:
            break
        for salida in cripta.salas.obtener(sala).salidas:
            if not conocimiento.salida_usable(salida):
                continue
            vecina = salida.sala_destino
            candidata = prioridad + salida.costo
            if estado.marca[vecina] != generacion or candidata < estado.distancia[vecina]:
                estado.marca[vecina] = generacion
                estado.distancia[vecina] = candidata
                estado.padre[vecina] = salida
                monticulo.insertar(candidata, vecina, vecina)
    if estado.marca[destino] != generacion:
        return None
    salida = estado.padre[destino]
    while salida.clave // 4 != origen:
        salida = estado.padre[salida.clave // 4]
    return salida


def medir_k6(salas=2000, semilla=SEMILLA_PREDETERMINADA, imprimir=True):
    """K6: Dijkstra inverso con parada frente al completo, desde el origen y reutilizando distancias. D7, FR-024."""
    from cripta.estructuras.Monticulo_Minimo import MonticuloMinimo

    cripta = generar_cripta_conocimiento(semilla, salas)
    conocimiento = conocimiento_completo(cripta)
    usable = conocimiento.salida_usable
    pares = elegir_pares(semilla, salas, 10)
    buscador = BuscadorRutas(salas)
    estado = SimpleNamespace(distancia=[0] * salas, marca=[0] * salas, padre=[None] * salas,
                             generacion=0, monticulo=MonticuloMinimo())

    def inverso_parada(origen, destino):
        def siguiente(actual):
            return paso_ir_a(cripta, conocimiento, buscador, actual, destino)
        return _recorrer(cripta, destino, origen, siguiente)

    def inverso_completo(origen, destino):
        def siguiente(actual):
            buscador.distancias_hacia(destino, cripta.entrantes, usable, None)
            return buscador.elegir_paso(actual, cripta.salas.obtener(actual).salidas, usable)
        return _recorrer(cripta, destino, origen, siguiente)

    def desde_origen(origen, destino):
        def siguiente(actual):
            return _paso_desde_origen(cripta, conocimiento, estado, actual, destino)
        return _recorrer(cripta, destino, origen, siguiente)

    def reutilizar(origen, destino):
        # Una sola busqueda por viaje: solo es correcta si el conocimiento no cambia entre pasos (FR-026).
        buscador.distancias_hacia(destino, cripta.entrantes, usable, None)

        def siguiente(actual):
            return buscador.elegir_paso(actual, cripta.salas.obtener(actual).salidas, usable)
        return _recorrer(cripta, destino, origen, siguiente)

    estrategias = [["inverso con parada", inverso_parada], ["inverso completo", inverso_completo],
                   ["desde el origen", desde_origen], ["reutilizar distancias", reutilizar]]
    tiempos = []
    resultados = []
    for _, estrategia in estrategias:
        total = 0.0
        costos = []
        for origen, destino in pares:
            inicio = time.perf_counter()
            costos.append(estrategia(origen, destino))
            total += time.perf_counter() - inicio
        tiempos.append(total)
        resultados.append(costos)
    # Las cuatro deben llegar con el mismo costo total (rutas de menor costo); los pasos pueden variar por empates.
    mismo_costo = True
    for i in range(len(pares)):
        for costos in resultados[1:]:
            if costos[i][0] != resultados[0][i][0]:
                mismo_costo = False
    deterministas = [[origen, destino, resultados[0][i][0], resultados[0][i][1]]
                     for i, (origen, destino) in enumerate(pares)]
    if imprimir:
        print(f"K6 Dijkstra inverso con parada frente a alternativas (S={salas}, {len(pares)} viajes completos, "
              f"recalculando en cada paso salvo reutilizar)")
        for (nombre, _), t in zip(estrategias, tiempos):
            print(f"  {nombre}: {_ms(t)} (inverso con parada / esta = {tiempos[0] / max(t, 1e-9):.2f}x)")
        print(f"  mismo costo de ruta en las cuatro: {'SI' if mismo_costo else 'NO'}")
        for (nombre, _), t in zip(estrategias[1:], tiempos[1:]):
            gana = t > 0 and tiempos[0] / t > 2
            print(f"  {nombre} {'gana por mas de 2 veces' if gana else 'no gana por mas de 2 veces'}")
        if tiempos[0] / max(tiempos[3], 1e-9) > 2:
            print("  nota: reutilizar solo es correcta si el conocimiento no cambia entre pasos; "
                  "FR-026 exige recalcular porque la memoria de puertas cambia al observar")
    return SimpleNamespace(salas=salas, t_inverso_parada=tiempos[0], t_inverso_completo=tiempos[1],
                           t_desde_origen=tiempos[2], t_reutilizar=tiempos[3], mismo_costo=mismo_costo,
                           resultados=deterministas)


class _MonticuloIndexado:
    """Alternativa K7: montículo con decremento de clave e indice de posicion por elemento."""

    def __init__(self, tamano: int) -> None:
        self.prioridad: list[int] = []
        self.elemento: list[int] = []
        self.posicion = [-1] * tamano

    def vacio(self) -> bool:
        return not self.elemento

    def _intercambiar(self, i: int, j: int) -> None:
        self.prioridad[i], self.prioridad[j] = self.prioridad[j], self.prioridad[i]
        self.elemento[i], self.elemento[j] = self.elemento[j], self.elemento[i]
        self.posicion[self.elemento[i]] = i
        self.posicion[self.elemento[j]] = j

    def _subir(self, i: int) -> None:
        while i > 0:
            padre = (i - 1) // 2
            if self.prioridad[i] >= self.prioridad[padre]:
                break
            self._intercambiar(i, padre)
            i = padre

    def insertar_o_bajar(self, prioridad: int, elemento: int) -> None:
        i = self.posicion[elemento]
        if i == -1:
            self.prioridad.append(prioridad)
            self.elemento.append(elemento)
            i = len(self.elemento) - 1
            self.posicion[elemento] = i
            self._subir(i)
        elif prioridad < self.prioridad[i]:
            self.prioridad[i] = prioridad
            self._subir(i)

    def extraer(self) -> list:
        resultado = [self.prioridad[0], self.elemento[0]]
        ultimo = len(self.elemento) - 1
        self._intercambiar(0, ultimo)
        self.posicion[self.elemento[ultimo]] = -1
        self.prioridad.pop()
        self.elemento.pop()
        i = 0
        total = len(self.elemento)
        while True:
            izquierdo = 2 * i + 1
            if izquierdo >= total:
                break
            menor = izquierdo
            if izquierdo + 1 < total and self.prioridad[izquierdo + 1] < self.prioridad[izquierdo]:
                menor = izquierdo + 1
            if self.prioridad[menor] >= self.prioridad[i]:
                break
            self._intercambiar(i, menor)
            i = menor
        return resultado


def _distancias_indexado(cripta, usable, destino: int) -> list:
    distancia = [-1] * cripta.n_salas
    fijada = [False] * cripta.n_salas
    monticulo = _MonticuloIndexado(cripta.n_salas)
    distancia[destino] = 0
    monticulo.insertar_o_bajar(0, destino)
    while not monticulo.vacio():
        prioridad, sala = monticulo.extraer()
        fijada[sala] = True
        for salida in cripta.entrantes[sala]:
            origen = salida.clave // 4
            if fijada[origen] or not usable(salida):
                continue
            candidata = prioridad + salida.costo
            if distancia[origen] == -1 or candidata < distancia[origen]:
                distancia[origen] = candidata
                monticulo.insertar_o_bajar(candidata, origen)
    return distancia


def _distancias_lineales(cripta, usable, destino: int) -> list:
    distancia = [-1] * cripta.n_salas
    fijada = [False] * cripta.n_salas
    distancia[destino] = 0
    while True:
        mejor = -1
        for sala in range(cripta.n_salas):
            if not fijada[sala] and distancia[sala] != -1 and (mejor == -1 or distancia[sala] < distancia[mejor]):
                mejor = sala
        if mejor == -1:
            return distancia
        fijada[mejor] = True
        for salida in cripta.entrantes[mejor]:
            origen = salida.clave // 4
            if fijada[origen] or not usable(salida):
                continue
            candidata = distancia[mejor] + salida.costo
            if distancia[origen] == -1 or candidata < distancia[origen]:
                distancia[origen] = candidata


def medir_k7(salas=2000, semilla=SEMILLA_PREDETERMINADA, imprimir=True):
    """K7: montículo perezoso frente a decremento de clave con indice y a seleccion lineal. D8."""
    cripta = generar_cripta_conocimiento(semilla, salas)
    conocimiento = conocimiento_completo(cripta)
    usable = conocimiento.salida_usable
    buscador = BuscadorRutas(salas)
    destino = elegir_pares(semilla, salas, 1)[0][1]

    def perezoso():
        buscador.distancias_hacia(destino, cripta.entrantes, usable, None)

    t_perezoso = _mejor_de(3, perezoso)
    t_indexado = _mejor_de(3, lambda: _distancias_indexado(cripta, usable, destino))
    t_lineal = _mejor_de(1, lambda: _distancias_lineales(cripta, usable, destino))
    indexado = _distancias_indexado(cripta, usable, destino)
    lineal = _distancias_lineales(cripta, usable, destino)
    iguales = True
    for sala in range(salas):
        esperado = -1 if buscador.distancia_de(sala) is None else buscador.distancia[sala]
        if indexado[sala] != esperado or lineal[sala] != esperado:
            iguales = False
    if imprimir:
        razon = t_perezoso / max(t_indexado, 1e-9)
        print(f"K7 monticulo perezoso frente a decremento de clave con indice y a seleccion lineal (S={salas}, "
              f"busqueda completa)")
        print(f"  perezoso={_ms(t_perezoso)} indexado={_ms(t_indexado)} (perezoso/indexado={razon:.2f}x) "
              f"seleccion lineal={_ms(t_lineal)} (lineal/perezoso={t_lineal / max(t_perezoso, 1e-9):.2f}x)")
        print(f"  mismas distancias en las tres: {'SI' if iguales else 'NO'}; "
              f"{'se conserva el perezoso (el indexado no gana por mas de 2 veces)' if razon <= 2 else 'el indexado gana por mas de 2 veces'}")
    return SimpleNamespace(salas=salas, t_perezoso=t_perezoso, t_indexado=t_indexado, t_lineal=t_lineal,
                           iguales=iguales)


def _costo_ruta_bfs(cripta, usable, origen: int, destino: int) -> int:
    """BFS con la cola de la spec 001 (`ColaLista`): costo de la ruta de menos saltos, o -1."""
    from cripta.estructuras.Cola_Lista import ColaLista

    previa = [None] * cripta.n_salas
    visto = [False] * cripta.n_salas
    cola = ColaLista()
    cola.encolar(origen)
    visto[origen] = True
    while not cola.vacia():
        sala = cola.sacar()
        if sala == destino:
            break
        for salida in cripta.salas.obtener(sala).salidas:
            if usable(salida) and not visto[salida.sala_destino]:
                visto[salida.sala_destino] = True
                previa[salida.sala_destino] = salida
                cola.encolar(salida.sala_destino)
    if not visto[destino]:
        return -1
    costo = 0
    actual = destino
    while actual != origen:
        salida = previa[actual]
        costo += salida.costo
        actual = salida.clave // 4
    return costo


def medir_k8(salas=2000, semilla=SEMILLA_PREDETERMINADA, imprimir=True):
    """K8: busqueda por costo frente a BFS (solo valida con costos iguales). D7, FR-023."""
    cripta = generar_cripta_conocimiento(semilla, salas)
    conocimiento = conocimiento_completo(cripta)
    usable = conocimiento.salida_usable
    buscador = BuscadorRutas(salas)
    pares = elegir_pares(semilla, salas, 50)
    mas_caras = mas_baratas = iguales = 0
    t_dijkstra = t_bfs = 0.0
    for origen, destino in pares:
        inicio = time.perf_counter()
        buscador.distancias_hacia(destino, cripta.entrantes, usable, origen)
        optimo = buscador.distancia_de(origen)
        t_dijkstra += time.perf_counter() - inicio
        inicio = time.perf_counter()
        costo_bfs = _costo_ruta_bfs(cripta, usable, origen, destino)
        t_bfs += time.perf_counter() - inicio
        if optimo is None or costo_bfs == -1:
            continue
        if costo_bfs > optimo:
            mas_caras += 1
        elif costo_bfs < optimo:
            mas_baratas += 1
        else:
            iguales += 1
    if imprimir:
        print(f"K8 busqueda por costo frente a BFS con la cola de la spec 001 (S={salas}, {len(pares)} pares, "
              f"costos variados)")
        print(f"  BFS devuelve rutas de mayor costo en {mas_caras} pares, de igual costo en {iguales} y de menor "
              f"costo en {mas_baratas}; tiempo busqueda por costo={_ms(t_dijkstra)} BFS={_ms(t_bfs)}")
    return SimpleNamespace(salas=salas, rutas_mas_caras=mas_caras, rutas_mas_baratas=mas_baratas,
                           rutas_iguales=iguales, t_dijkstra=t_dijkstra, t_bfs=t_bfs)


def medir_k9(semilla=SEMILLA_PREDETERMINADA):
    """K9: K4 y K6 dos veces con la misma semilla dan resultados identicos. FR-039, FR-040, SC-005, SC-008."""
    a4 = medir_k4(semilla, imprimir=False)
    b4 = medir_k4(semilla, imprimir=False)
    a6 = medir_k6(2000, semilla, imprimir=False)
    b6 = medir_k6(2000, semilla, imprimir=False)
    identicos = a4.resultados == b4.resultados and a6.resultados == b6.resultados
    print("K9 determinismo: K4 y K6 dos veces con la misma semilla, sin ventana")
    print(f"  resultados de K4 ({len(a4.resultados)} pares) y de K6 ({len(a6.resultados)} viajes) identicos: "
          f"{'SI' if identicos else 'NO'}")
    return SimpleNamespace(identicos=identicos)


def _bench_conocimiento(semilla: int = SEMILLA_PREDETERMINADA) -> None:
    """Seccion Niebla de guerra e ir a: K1 a K9, con la misma semilla en todas."""
    print(f"\n=== Niebla de guerra e ir a (semilla {semilla}) ===")
    medir_k1((200, 2000, 20000), semilla)
    medir_k2((200, 2000, 20000), semilla)
    medir_k3((200, 20000), (10, 1000), semilla)
    medir_k4(semilla)
    medir_k5((2000, 20000), semilla)
    medir_k6(2000, semilla)
    medir_k7(2000, semilla)
    medir_k8(2000, semilla)
    medir_k9(semilla)


# --- Terreno y cazador (spec 003): FR-025 a FR-028 -----------------------------------------------
LIMITE_CICLO_MS = 20.0
RANGO_SIN_LIMITE = 10 ** 9


def _abierta(salida) -> bool:
    return not salida.cerrada


class CriptaCazadores(CriptaConocimiento):
    """Esqueleto sintetico con la sala del jugador y las salas de los cazadores (FR-026)."""

    def __init__(self, base, jugador, cazadores, rango):
        super().__init__(base.salas, base.entrantes, base.n_salas, base.n_salidas)
        self.jugador = jugador
        self.cazadores = cazadores
        self.rango = rango


def generar_cripta_cazadores(semilla: int, salas: int, cazadores: int, rango: int,
                             puertas_inestables: bool = False) -> CriptaCazadores:
    """Cuadricula de `generar_cripta_conocimiento` con jugador y cazadores colocados por semilla.

    Ningun cazador empieza en la sala del jugador. Con `puertas_inestables`, cerca del 30 % de las
    salidas abiertas declara un cierre automatico corto. Los ids son secuenciales y no hay datos de
    ninguna cripta concreta (FR-028).
    """
    base = generar_cripta_conocimiento(semilla, salas)
    azar = random.Random(semilla)
    jugador = azar.randrange(salas)
    colocados = []
    while len(colocados) < cazadores:
        sala = azar.randrange(salas)
        if sala != jugador:
            colocados.append(sala)
    if puertas_inestables:
        for i in range(salas):
            for salida in base.salas.obtener(i).salidas:
                if not salida.cerrada and azar.random() < 0.30:
                    salida.cierre_automatico = azar.randint(50, 300)
    return CriptaCazadores(base, jugador, colocados, rango)


def _persecucion(cripta):
    from cripta.modelo.Persecucion import Persecucion
    persecucion = Persecucion(HeapAgendaEventos(None))
    persecucion.configurar(cripta.entrantes)
    persecucion.registrar_rango(cripta.rango)
    return persecucion


def _decidir_todos(persecucion, cripta, rango):
    """Decision de cada cazador con la busqueda compartida; devuelve el destino de cada uno."""
    resultado = []
    for sala in cripta.cazadores:
        salida = persecucion.decidir(cripta.jugador, sala, cripta.salas.obtener(sala).salidas, rango)
        resultado.append(-1 if salida is None else salida.sala_destino)
    return resultado


def _decidir_individual(buscador, cripta, rango):
    """Una busqueda por cazador (la alternativa que D5 descarta)."""
    resultado = []
    for sala in cripta.cazadores:
        buscador.distancias_hacia(cripta.jugador, cripta.entrantes, _abierta, None, rango)
        d = buscador.distancia_de(sala)
        if d is None or d == 0 or d > rango:
            resultado.append(-1)
            continue
        salida = buscador.elegir_paso(sala, cripta.salas.obtener(sala).salidas, _abierta)
        resultado.append(-1 if salida is None else salida.sala_destino)
    return resultado


def medir_h1(semilla=SEMILLA_PREDETERMINADA, salas=SALAS_REFERENCIA_SINTETICA, cantidades=(1, 10, 50, 100),
             imprimir=True):
    """H1: decision de C cazadores por ciclo, busqueda compartida frente a una busqueda por cazador."""
    huella = []
    for rango in (300, RANGO_SIN_LIMITE):
        for c in cantidades:
            cripta = generar_cripta_cazadores(semilla, salas, c, rango)
            buscador = BuscadorRutas(salas)
            persecucion = _persecucion(cripta)

            def compartida():
                persecucion.valida = False     # un ciclo nuevo: se busca una vez
                return _decidir_todos(persecucion, cripta, rango)

            t_compartida = _mejor_de(3, compartida)
            t_individual = _mejor_de(3, lambda: _decidir_individual(buscador, cripta, rango))
            decisiones = compartida()
            if decisiones != _decidir_individual(buscador, cripta, rango):
                raise AssertionError("H1: la decision compartida no coincide con la individual")
            huella.append([rango, c, decisiones])
            if imprimir:
                razon = t_individual / t_compartida if t_compartida > 0 else float("inf")
                rango_txt = "sin_limite" if rango == RANGO_SIN_LIMITE else rango
                print(f"H1 salas={salas}: cazadores={c} rango={rango_txt} compartida_ms={t_compartida * 1000:.3f} "
                      f"individual_ms={t_individual * 1000:.3f} razon={razon:.1f} [INFORMATIVA]")
    return SimpleNamespace(huella=huella)


def medir_h2(semilla=SEMILLA_PREDETERMINADA, tamanos=(200, 2000, 20000), rango=300, imprimir=True):
    """H2: un recalculo con y sin corte por rango; criterio de D6 entre los dos tamanos mayores."""
    tiempos = []
    for n in tamanos:
        cripta = generar_cripta_conocimiento(semilla, n)
        buscador = BuscadorRutas(n)
        destino = n // 2

        def con_corte():
            buscador.distancias_hacia(destino, cripta.entrantes, _abierta, None, rango)

        def sin_corte():
            buscador.distancias_hacia(destino, cripta.entrantes, _abierta, None, None)

        def alcanzadas():
            return sum(1 for i in range(n) if buscador.marca[i] == buscador.generacion)

        t_con = _mejor_de(3, con_corte)
        f_con = alcanzadas()
        t_sin = _mejor_de(3, sin_corte)
        f_sin = alcanzadas()
        tiempos.append(t_con)
        if imprimir:
            print(f"H2 salas={n}: con_corte_fijadas={f_con} con_corte_ms={t_con * 1000:.3f} "
                  f"sin_corte_fijadas={f_sin} sin_corte_ms={t_sin * 1000:.3f} [INFORMATIVA]")
    crecimiento = tiempos[-1] / tiempos[-2] if len(tiempos) >= 2 and tiempos[-2] > 0 else 1.0
    cumple = crecimiento < 1.5
    if imprimir:
        print(f"H2 criterio D6: con corte crece {crecimiento:.2f} veces entre {tamanos[-2]} y {tamanos[-1]} salas "
              f"(limite 1.5) [{'CUMPLE' if cumple else 'EXCEDE'}]")
    return SimpleNamespace(crecimiento=crecimiento, cumple=cumple)


def medir_h3(semilla=SEMILLA_PREDETERMINADA, salas=SALAS_REFERENCIA_SINTETICA, cazadores=20, decisiones=200,
             imprimir=True):
    """H3: 200 decisiones del jugador; reutilizar con la clave frente a recalcular por turno o por ciclo."""
    recalculos_de = []
    for inestables in (False, True):
        cripta = generar_cripta_cazadores(semilla, salas, cazadores, 300, puertas_inestables=inestables)
        azar = random.Random(semilla)
        puertas = []
        for _ in range(decisiones):
            origen = azar.randrange(salas)
            abiertas = [s for s in cripta.salas.obtener(origen).salidas]
            puertas.append(abiertas[azar.randrange(len(abiertas))] if abiertas else None)

        def correr(estrategia):
            persecucion = _persecucion(cripta)
            agenda = persecucion.agenda
            inicio = time.perf_counter()
            for k in range(decisiones):
                puerta = puertas[k] if inestables else None
                if puerta is not None and k % 2 == 0:
                    puerta.cerrada = not puerta.cerrada     # una puerta cambia entre decisiones
                    agenda.cambios_puertas += 1
                if estrategia == "ciclo":
                    persecucion.valida = False
                for sala in cripta.cazadores:
                    if estrategia == "turno":
                        persecucion.valida = False
                    persecucion.decidir(cripta.jugador, sala, cripta.salas.obtener(sala).salidas, 300)
                if puerta is not None and k % 2 == 0:
                    puerta.cerrada = not puerta.cerrada     # se restaura: el estado inicial no cambia
                    agenda.cambios_puertas += 1
            return time.perf_counter() - inicio, persecucion.recalculos

        t_clave, recalculos = correr("clave")
        t_turno, _ = correr("turno")
        t_ciclo, _ = correr("ciclo")
        recalculos_de.append(recalculos)
        if imprimir:
            print(f"H3 salas={salas}: puertas={'inestables' if inestables else 'estables'} "
                  f"clave_ms={t_clave * 1000:.3f} por_turno_ms={t_turno * 1000:.3f} "
                  f"por_ciclo_ms={t_ciclo * 1000:.3f} recalculos={recalculos} [INFORMATIVA]")
    return SimpleNamespace(recalculos=recalculos_de)


def medir_h4(semilla=SEMILLA_PREDETERMINADA, salas=300, turnos=10000, imprimir=True):
    """H4: la decision de `Persecucion` coincide con la busqueda completa desde cero en cada turno."""
    cripta = generar_cripta_cazadores(semilla, salas, 1, 300)
    persecucion = _persecucion(cripta)
    persecucion.registrar_rango(1000)
    referencia = BuscadorRutas(salas)
    azar = random.Random(semilla)
    todas = []
    for i in range(salas):
        for salida in cripta.salas.obtener(i).salidas:
            todas.append(salida)
    coinciden = 0
    for _ in range(turnos):
        if todas and azar.random() < 0.05:
            puerta = todas[azar.randrange(len(todas))]
            puerta.cerrada = not puerta.cerrada
            persecucion.agenda.cambios_puertas += 1
        jugador = azar.randrange(salas)
        sala = azar.randrange(salas)
        rango = (0, 100, 300, 1000)[azar.randrange(4)]
        salidas = cripta.salas.obtener(sala).salidas
        obtenida = persecucion.decidir(jugador, sala, salidas, rango)
        referencia.distancias_hacia(jugador, cripta.entrantes, _abierta)
        d = referencia.distancia_de(sala)
        esperada = None
        if d is not None and d != 0 and d <= rango:
            esperada = referencia.elegir_paso(sala, salidas, _abierta)
        if (None if obtenida is None else obtenida.clave) == (None if esperada is None else esperada.clave):
            coinciden += 1
    if imprimir:
        print(f"H4 salas={salas}: turnos={turnos} coinciden={coinciden} "
              f"[{'CUMPLE' if coinciden == turnos else 'EXCEDE'}]")
    return SimpleNamespace(turnos=turnos, coinciden=coinciden, recalculos=persecucion.recalculos)


def _ciclo_cazadores(cripta, semilla, ciclos):
    """Ciclos de eventos con cazadores activos; devuelve los tiempos (ms) y el estado final."""
    from cripta.modelo.Jugador import Jugador
    from cripta.modelo.Simulacion import Simulacion
    from cripta.modelo.enemigos.Cazador import Cazador
    from cripta.util.Costo_Acciones import calcular_intervalo

    sim = Simulacion(semilla)
    sim.persecucion.configurar(cripta.entrantes)
    sim.persecucion.registrar_rango(cripta.rango)
    vida = 10 ** 9
    jugador = Jugador("jugador", vida, vida, 6, 100, 100, cripta.jugador, 0, 10)
    sim.agenda.reprogramar(jugador, 0, "accion_actor")
    for i, sala in enumerate(cripta.cazadores):
        c = Cazador(f"c{i}", 10, 10, 1, 0, 50 + (i * 37) % 151, sala, None, rango=cripta.rango)
        cripta.salas.obtener(sala).agregar_enemigo(c)
        evento = sim.agenda.insertar(i % 100, c, "accion_actor")
        c._proximo_evento = evento
        c.tiempo_siguiente = i % 100
    azar = random.Random(semilla)
    medidas = []
    for _ in range(ciclos):
        abiertas = [s for s in cripta.salas.obtener(jugador.sala).salidas if not s.cerrada]
        if abiertas:
            salida = abiertas[azar.randrange(len(abiertas))]
            jugador.sala = salida.sala_destino
            costo = salida.costo
        else:
            costo = 100
        inicio = time.perf_counter()
        sim.agenda.reprogramar(jugador, sim.reloj.tiempo_actual + calcular_intervalo(costo, 100), "accion_actor")
        sim.avanzar_hasta_turno_jugador(jugador, cripta.salas)
        medidas.append((time.perf_counter() - inicio) * 1000)
    estado = [jugador.sala, sim.reloj.tiempo_actual, sim.persecucion.recalculos,
              sum(c.sala for i in range(cripta.n_salas) for c in cripta.salas.obtener(i).enemigos)]
    return medidas, estado


def medir_h5(semilla=SEMILLA_PREDETERMINADA, salas=None, cantidades=(10, 50, 100), ciclos=200, imprimir=True,
             carpeta=None):
    """H5: ciclo de eventos entre dos decisiones del jugador con cazadores activos (limite 20 ms)."""
    salas = salas or tamano_cripta_referencia(carpeta)
    resultados = []
    for c in cantidades:
        cripta = generar_cripta_cazadores(semilla, salas, c, 300)
        medidas, estado = _ciclo_cazadores(cripta, semilla, ciclos)
        maximo = max(medidas)
        media = sum(medidas) / len(medidas)
        cumple = maximo < LIMITE_CICLO_MS
        resultados.append(SimpleNamespace(cazadores=c, media=media, maximo=maximo, cumple=cumple, estado=estado))
        if imprimir:
            print(f"H5 salas={salas}: cazadores={c} ciclos={ciclos} media_ms={media:.3f} maximo_ms={maximo:.3f} "
                  f"limite=20ms [{'CUMPLE' if cumple else 'EXCEDE'}]")
    return SimpleNamespace(resultados=resultados)


def medir_h6(semilla=SEMILLA_PREDETERMINADA, eventos=2000, cierres=200, imprimir=True):
    """H6 (§5.6): agenda con heap propio frente a lista ordenada con la carga de la parte II."""
    azar = random.Random(semilla)
    tiempos = []
    for _ in range(eventos):
        costo = azar.randint(1, 300)
        velocidad = azar.choice([50, 100, 150, 200])
        tiempos.append(max(1, costo * 100 // velocidad))
    cierres_t = [azar.randint(50, 900) for _ in range(cierres)]
    carga = tiempos + cierres_t

    def con_heap():
        agenda = HeapAgendaEventos()
        actor = _ActorFalso("a")
        for t in carga:
            agenda.insertar(t, actor, "accion_actor")
        while agenda.extraer_siguiente() is not None:
            pass

    def con_lista():
        lista = _ListaOrdenada()
        for secuencia, t in enumerate(carga):
            lista.insertar(t, secuencia)
        for _ in carga:
            lista.extraer_siguiente()

    t_heap = _mejor_de(3, con_heap)
    t_lista = _mejor_de(3, con_lista)
    if imprimir:
        print(f"H6 eventos={len(carga)}: heap_ms={t_heap * 1000:.3f} lista_ms={t_lista * 1000:.3f} [INFORMATIVA]")
    return SimpleNamespace(heap=t_heap, lista=t_lista)


def medir_h7(semilla=SEMILLA_PREDETERMINADA, salas=SALAS_REFERENCIA_SINTETICA, imprimir=True):
    """H7: predicado por arista relajada frente a un arreglo de banderas por clave de salida."""
    cripta = generar_cripta_conocimiento(semilla, salas)
    buscador = BuscadorRutas(salas)
    banderas = [False] * (salas * 4)
    for i in range(salas):
        for salida in cripta.salas.obtener(i).salidas:
            banderas[salida.clave] = not salida.cerrada
    destino = salas // 2
    t_predicado = _mejor_de(3, lambda: buscador.distancias_hacia(destino, cripta.entrantes, _abierta, None, None))
    t_banderas = _mejor_de(3, lambda: buscador.distancias_hacia(
        destino, cripta.entrantes, lambda s: banderas[s.clave], None, None))
    if imprimir:
        print(f"H7 salas={salas}: predicado_ms={t_predicado * 1000:.3f} banderas_ms={t_banderas * 1000:.3f} "
              f"[INFORMATIVA]")
    return SimpleNamespace(predicado=t_predicado, banderas=t_banderas)


def medir_h8(semilla=SEMILLA_PREDETERMINADA, escala=None, imprimir=True):
    """H8: H1, H4 y H5 dos veces con la misma semilla dan las mismas decisiones y conteos."""
    escala = escala or {}
    def una():
        h1 = medir_h1(semilla, escala.get("h1_salas", 300), escala.get("h1_cantidades", (1, 10)), imprimir=False)
        h4 = medir_h4(semilla, escala.get("h4_salas", 100), escala.get("h4_turnos", 500), imprimir=False)
        h5 = medir_h5(semilla, escala.get("h5_salas", 300), escala.get("h5_cantidades", (10,)),
                      escala.get("h5_ciclos", 30), imprimir=False)
        return [h1.huella, [h4.turnos, h4.coinciden, h4.recalculos], [r.estado for r in h5.resultados]]
    identico = una() == una()
    if imprimir:
        print(f"H8 semilla={semilla}: identico={'si' if identico else 'no'} [{'CUMPLE' if identico else 'EXCEDE'}]")
    return SimpleNamespace(identico=identico)


def _bench_cazador(semilla: int = SEMILLA_PREDETERMINADA) -> None:
    """Seccion Terreno y cazador: H1 a H8 con la misma semilla; no abre la vista (FR-026, FR-027)."""
    print(f"\n=== Terreno y cazador (spec 003), semilla {semilla} ===")
    medir_h1(semilla)
    medir_h2(semilla)
    medir_h3(semilla)
    medir_h4(semilla)
    medir_h5(semilla)
    if tamano_cripta_referencia() != SALAS_REFERENCIA_SINTETICA:
        medir_h5(semilla, SALAS_REFERENCIA_SINTETICA)   # el paquete es pequeño: tambien a 2 000 salas
    medir_h6(semilla)
    medir_h7(semilla)
    medir_h8(semilla)


def main(semilla: int = SEMILLA_PREDETERMINADA):
    import tempfile
    _bench_simulacion()
    _bench_referencia()
    print("\n=== Ciclo completo sintético (sin red, disco ni renderizado) ===")
    for enemigos in [20, 200, 500, 1000]:
        _bench_ciclo_completo(enemigos)
    with tempfile.TemporaryDirectory(prefix="cripta-bench-") as carpeta:
        _bench_estructuras_y_persistencia(carpeta)
    _bench_resolubilidad(semilla)
    _bench_conocimiento(semilla)
    _bench_cazador(semilla)


if __name__ == "__main__":
    main()
