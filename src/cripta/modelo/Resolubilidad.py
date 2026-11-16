"""Verificación de resolubilidad de una cripta (sin red, disco ni vista).

Decide si la cripta se puede ganar usando solo el esqueleto de salas y la
ubicación publicada de las llaves. Es una única exploración en anchura por
rondas con listas de espera por llave: cada sala se encola una vez, cada
salida se examina una vez y cada llave se obtiene una vez.

Complejidad de la exploración: O(S + E + K). El índice de llaves añade un
factor logarítmico en K al construirse y al resolver ids a rangos.

Todas las estructuras son `list` indexadas por entero (sin `dict` ni `set`) y
los ordenamientos usan `ordenar` del proyecto.

Cumple: FR-001, FR-003, FR-004, FR-005, FR-006, FR-007, FR-008, FR-024, FR-027, FR-029.
"""

from __future__ import annotations

from cripta.dto.Partida_dto import DetallesCripta, SalaModelo
from cripta.dto.Verificacion_dto import (
    EstadisticasVerificacion,
    LlaveEnOrden,
    ReporteBloqueo,
    ResultadoVerificacion,
    UbicacionLlave,
)
from cripta.estructuras.Cola_Lista import ColaLista
from cripta.estructuras.Indice_Llaves import IndiceLlaves
from cripta.estructuras.Ordenamientos import ordenar


def _no_verificable(detalles: DetallesCripta, motivo: str, advertencias: list[str]) -> ResultadoVerificacion:
    """Resultado sin veredicto por datos inválidos (FR-001)."""
    return ResultadoVerificacion(
        estado="no_verificable",
        motivo_no_verificable=motivo,
        advertencias=advertencias,
        cripta_id=detalles.id,
        version=detalles.version,
        estadisticas=None,
    )


def _clave_ubicacion(u: UbicacionLlave) -> tuple:
    """Orden de las ubicaciones de una llave: id de sala y luego id de enemigo."""
    return (u.sala, u.enemigo if u.enemigo is not None else "")


def _clave_salida(salida) -> tuple:
    """Orden de las salidas de una sala: id del destino y luego dirección."""
    return (salida.sala_id, salida.direccion)


def verificar(
    detalles: DetallesCripta,
    salas: list[SalaModelo],
    ubicaciones: list[UbicacionLlave],
) -> ResultadoVerificacion:
    """Verifica si la cripta se puede ganar y en qué orden se obtienen las llaves.

    No modifica `salas` ni `ubicaciones`.

    Args:
        detalles: Parámetros de la cripta (sala inicial, sala de salida, llave de salida).
        salas: Esqueleto de salas con sus salidas dirigidas.
        ubicaciones: Ubicaciones publicadas de las llaves.

    Returns:
        `ResultadoVerificacion` con estado `resoluble`, `no_resoluble` o `no_verificable`.
    """
    advertencias: list[str] = []

    # Salas por id, en una lista indexada por el id (la primera gana si hay repetidas).
    max_id = -1
    for s in salas:
        if s.id > max_id:
            max_id = s.id
    total = max_id + 1
    por_id: list[SalaModelo | None] = [None] * total
    for s in salas:
        if s.id < 0:
            advertencias.append(f"Sala {s.id} descartada: id negativo.")
        elif por_id[s.id] is None:
            por_id[s.id] = s
        else:
            advertencias.append(f"Sala {s.id} repetida: se usa la primera.")

    def existe(id_sala: int) -> bool:
        return 0 <= id_sala < total and por_id[id_sala] is not None

    if not existe(detalles.sala_inicial):
        return _no_verificable(
            detalles, f"La sala inicial {detalles.sala_inicial} no existe en el esqueleto.", advertencias)

    # Validación de salidas y recolección de los ids de llave del universo.
    ids_llaves: list[str] = []
    for id_sala in range(total):
        sala = por_id[id_sala]
        if sala is None:
            continue
        for sa in sala.salidas:
            if sa.cerrada and not sa.llave:
                return _no_verificable(
                    detalles,
                    f"La salida {sa.direccion} de la sala {id_sala} está cerrada y no declara llave.",
                    advertencias)
            if not existe(sa.sala_id):
                advertencias.append(
                    f"Salida {sa.direccion} de la sala {id_sala} hacia la sala inexistente {sa.sala_id}: se ignora.")
            elif sa.cerrada:
                ids_llaves.append(sa.llave)

    validas: list[UbicacionLlave] = []
    for u in ubicaciones:
        if not u.llave:
            advertencias.append("Ubicación sin id de llave: se descarta.")
        elif not existe(u.sala):
            advertencias.append(f"Ubicación de la llave {u.llave} en la sala inexistente {u.sala}: se descarta.")
        else:
            validas.append(u)
            ids_llaves.append(u.llave)
    if detalles.llave_salida:
        ids_llaves.append(detalles.llave_salida)

    indice = IndiceLlaves(ids_llaves)
    cantidad_llaves = indice.cantidad()
    rango_salida = indice.rango(detalles.llave_salida) if detalles.llave_salida else -1

    # Ubicaciones por llave (rango) y, por sala, las llaves que se obtienen en ella.
    por_llave: list[list[UbicacionLlave]] = [[] for _ in range(cantidad_llaves)]
    for u in validas:
        por_llave[indice.rango(u.llave)].append(u)
    llaves_sala: list[list[tuple]] = [[] for _ in range(total)]
    for rango in range(cantidad_llaves):
        ordenar(por_llave[rango], key=_clave_ubicacion)
        for u in por_llave[rango]:
            llaves_sala[u.sala].append((rango, u))

    # Salidas planas agrupadas por sala y ordenadas por (destino, dirección).
    s_destino: list[int] = []
    s_llave: list[int] = []
    inicio: list[int] = [0] * total
    fin: list[int] = [0] * total
    for id_sala in range(total):
        sala = por_id[id_sala]
        inicio[id_sala] = len(s_destino)
        if sala is not None:
            alcanzables = [sa for sa in sala.salidas if existe(sa.sala_id)]
            ordenar(alcanzables, key=_clave_salida)
            for sa in alcanzables:
                s_destino.append(sa.sala_id)
                s_llave.append(indice.rango(sa.llave) if sa.cerrada else -1)
        fin[id_sala] = len(s_destino)

    # Exploración en anchura por rondas.
    estadisticas = EstadisticasVerificacion()
    ronda: list[int] = [-1] * total
    obtenida: list[bool] = [False] * cantidad_llaves
    espera: list[list[int]] = [[] for _ in range(cantidad_llaves)]
    orden: list[LlaveEnOrden] = []
    cola = ColaLista()
    gano = False

    ronda[detalles.sala_inicial] = 0
    cola.encolar(detalles.sala_inicial)
    estadisticas.salas_encoladas += 1
    actual = 0

    while not cola.vacia():
        lote: list[int] = []
        while not cola.vacia():
            lote.append(cola.sacar())
        ordenar(lote)   # empate por menor id de sala dentro de la ronda (FR-008)
        for id_sala in lote:
            # Primero las llaves de la sala, en orden de id; cada una libera sus esperas.
            for rango, u in llaves_sala[id_sala]:
                if obtenida[rango]:
                    continue
                obtenida[rango] = True
                estadisticas.llaves_obtenidas += 1
                orden.append(LlaveEnOrden(llave=u.llave, sala=id_sala, enemigo=u.enemigo, ronda=actual))
                for i in espera[rango]:
                    if rango == rango_salida and s_destino[i] == detalles.sala_salida:
                        gano = True
                    destino = s_destino[i]
                    if ronda[destino] == -1:
                        ronda[destino] = actual + 1
                        cola.encolar(destino)
                        estadisticas.salas_encoladas += 1
                espera[rango] = []
            # Luego las salidas, cada una se examina una sola vez.
            for i in range(inicio[id_sala], fin[id_sala]):
                estadisticas.salidas_examinadas += 1
                k = s_llave[i]
                if k != -1 and not obtenida[k]:
                    espera[k].append(i)
                    continue
                destino = s_destino[i]
                if k != -1 and k == rango_salida and destino == detalles.sala_salida:
                    gano = True
                if ronda[destino] == -1:
                    ronda[destino] = actual + 1
                    cola.encolar(destino)
                    estadisticas.salas_encoladas += 1
        actual += 1

    if gano:
        return ResultadoVerificacion(
            estado="resoluble",
            orden_llaves=orden,
            advertencias=advertencias,
            cripta_id=detalles.id,
            version=detalles.version,
            estadisticas=estadisticas,
        )

    obtenida_salida = rango_salida != -1 and obtenida[rango_salida]
    motivo = "puerta_sin_destino" if obtenida_salida else "llave_salida_inobtenible"
    return ResultadoVerificacion(
        estado="no_resoluble",
        reporte=ReporteBloqueo(motivo=motivo),
        advertencias=advertencias,
        cripta_id=detalles.id,
        version=detalles.version,
        estadisticas=estadisticas,
    )
