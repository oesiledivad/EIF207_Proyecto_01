"""Cargas sinteticas sin red ni interfaz para --bench."""

from __future__ import annotations

import random
import time
from types import SimpleNamespace

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


if __name__ == "__main__":
    main()
