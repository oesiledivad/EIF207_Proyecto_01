from modelo.Cripta import Cripta

from ensamblador.ensamblar_sala import ensamblar_sala
def ensamblar_cripta(detalles, paginas):
    """
    detalles: Crypta_Details (DTO)
    paginas:  lista de List_rooms (DTO), una por cada página del esqueleto
    """
    salas = []
    for pagina in paginas:
        for dto_sala in pagina.salas:
            salas.append(ensamblar_sala(dto_sala))

    # el esqueleto debe venir completo
    if len(salas) != detalles.salas_total:
        raise ValueError(
            f"Se esperaban {detalles.salas_total} salas y llegaron {len(salas)}"
        )

    return Cripta(
        id=detalles.id,
        version=detalles.version,
        sala_inicial=detalles.sala_inicial,
        sala_salida=detalles.sala_salida,
        llave_salida=detalles.llave_salida,
        presupuesto_solicitudes=detalles.presupuesto_solicitudes,
        inventario_max=detalles.inventario_max,
        salas=salas,
    )