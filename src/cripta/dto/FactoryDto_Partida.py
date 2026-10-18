"""Conversión de respuestas de la API a los DTO de partida."""

from cripta.dto.Partida_dto import (
    DetallesCripta, SalaModelo, SalidaVecina, EnemigoPartida,
    ObjetoSuelo, TrampaPartida, ContenidoSala,
)
from cripta.estructuras.Catalogo_Lista import Catalogo_Lista


def buscar_ficha(catalogo: Catalogo_Lista, id_tipo):
    """Busca una ficha resuelta; devuelve None si falta."""
    try:
        return catalogo.obtener(id_tipo)
    except KeyError:
        return None


def parsear_detalles(detalles: dict, cripta_id: str) -> DetallesCripta:
    """Convierte los datos generales conservando los valores predeterminados."""
    if not isinstance(detalles, dict):
        detalles = {}

    jugador = detalles.get("jugador", {})
    if not isinstance(jugador, dict):
        jugador = {}

    return DetallesCripta(
        id=str(detalles.get("id", cripta_id)),
        version=str(detalles.get("version", "offline")),
        salas_total=int(detalles.get("salas_total", 0)),
        sala_inicial=int(detalles.get("sala_inicial", 1)),
        sala_salida=int(detalles.get("sala_salida", 1)),
        llave_salida=str(detalles.get("llave_salida", "—")),
        inventario_max=int(detalles.get("inventario_max", 10)),
        presupuesto_solicitudes=int(detalles.get("presupuesto_solicitudes", 0)),
        jugador_vida_max=int(jugador.get("vida_max", 0)),
        jugador_ataque=int(jugador.get("ataque", 0)),
        jugador_defensa=int(jugador.get("defensa", 0)),
        jugador_velocidad=int(jugador.get("velocidad", 0)),
    )


def parsear_sala(item_sala: dict, sala_salida_id: int) -> SalaModelo:
    """Convierte una sala del esqueleto y sus puertas."""
    s_id = int(item_sala.get("id", 0))
    s_nombre = str(item_sala.get("nombre", ""))
    s_desc = str(item_sala.get("descripcion", ""))

    lista_salidas: list[SalidaVecina] = []
    salidas_brutas = item_sala.get("salidas", {})

    if isinstance(salidas_brutas, dict):
        for direccion, info_salida in salidas_brutas.items():
            vecina_id = int(info_salida.get("sala", 0))
            cerrada = bool(info_salida.get("cerrada", False))
            llave = info_salida.get("llave")
            llave_str = str(llave) if llave is not None else ""
            cierre = info_salida.get("cierre_automatico")

            lista_salidas.append(
                SalidaVecina(
                    direccion=str(direccion),
                    sala_id=vecina_id,
                    nombre=f"Sala {vecina_id}",
                    cerrada=cerrada,
                    llave=llave_str,
                    transitable=not cerrada,
                    es_salida_final=(vecina_id == sala_salida_id),
                    tiene_enemigos=False,
                    tiene_objetos=False,
                    cierre_automatico=int(cierre) if cierre is not None else None,
                )
            )

    return SalaModelo(id=s_id, nombre=s_nombre, descripcion=s_desc, salidas=lista_salidas)


def parsear_contenido(entrada: dict, catalogo: Catalogo_Lista) -> ContenidoSala:
    """Convierte enemigos, objetos y trampas usando las fichas resueltas."""
    enemigos: list[EnemigoPartida] = []
    for e in entrada.get("enemigos", []):
        tipo = str(e.get("tipo", ""))
        ficha = buscar_ficha(catalogo, tipo)
        vida_max = ficha.vida_max if ficha else 0
        vida = e.get("vida")  # puede venir null: entonces empieza con vida_max
        enemigos.append(EnemigoPartida(
            id=str(e.get("instancia", "")),
            nombre=ficha.nombre if ficha else tipo,
            vida=int(vida) if vida is not None else vida_max,
            ataque=ficha.ataque if ficha else 0,
            defensa=ficha.defensa if ficha else 0,
            vida_max=vida_max,
            velocidad=ficha.velocidad if ficha else 100,
            comportamiento=ficha.comportamiento if ficha else "errante",
            regeneracion=getattr(ficha, "regeneracion", None),
            tipo=tipo,
            suelta=list(ficha.suelta or []) if ficha else [],
        ))

    objetos: list[ObjetoSuelo] = []
    for posicion, o in enumerate(entrada.get("objetos", [])):
        ficha = buscar_ficha(catalogo, str(o))
        objetos.append(ObjetoSuelo(
            id=f"sala-{entrada['sala']}-objeto-{posicion}",
            nombre=ficha.nombre if ficha else str(o), tipo_id=str(o),
        ))

    trampas: list[TrampaPartida] = []
    for t in entrada.get("trampas", []):
        tipo = str(t.get("tipo", ""))
        ficha = buscar_ficha(catalogo, tipo)
        trampas.append(TrampaPartida(
            id=str(t.get("instancia", "")),
            tipo=tipo,
            activa=True,
            dano=ficha.daño if ficha else 0,
            rearme=ficha.rearme if ficha else None,
            efecto=getattr(ficha, "efecto", "daño"),
        ))
    return ContenidoSala(enemigos=enemigos, objetos=objetos, trampas=trampas)
