"""Lectura: del archivo binario a estructuras intermedias, sin tocar la partida en curso."""

from __future__ import annotations

from cripta.controlador.guardado.Datos import ActorG, DatosGuardado, EnemigoG, EventoG, SalaG
from cripta.controlador.guardado.Formato import (
    ACTOR_JUGADOR,
    ID_GLOBAL,
    ID_LINEA,
    VALOR_BOOLEANO,
    VALOR_ENTERO,
    VALOR_NULO,
    VALOR_TEXTO,
    VALOR_TUPLA,
    comprobar_version,
)
from cripta.estructuras.Guardado_Binario import Guardado_Binario
from cripta.estructuras.Inventario import ItemInventario
from cripta.estructuras.serializacionBinaria import LectorBinario


def _leer_actor(r: LectorBinario) -> ActorG:
    return ActorG(
        identificador=r.texto(), vida=r.entero(), vida_max=r.entero(), ataque=r.entero(),
        defensa=r.entero(), velocidad=r.entero(), velocidad_base=r.entero(), sala=r.entero(),
        tiempo_siguiente=r.entero_opcional(), dano_veneno=r.entero(),
        fin_veneno=r.entero_opcional(), regeneracion_cantidad=r.entero(),
    )


def _leer_enemigo(r: LectorBinario) -> EnemigoG:
    actor = _leer_actor(r)
    nombre = r.texto()                 
    comportamiento = r.texto()
    tipo = r.texto()
    suelta = [r.texto() for _ in range(r.entero())]
    regeneracion = r.entero_opcional()
    rango = r.entero() if comportamiento == "cazador" else None
    return EnemigoG(actor, nombre, comportamiento, tipo, suelta, regeneracion, rango)

def _leer_sala(datos: bytes) -> SalaG:
    r = LectorBinario(datos)
    comprobar_version(r.entero(), "de sala")
    sala = SalaG(r.entero(), r.entero_opcional(), r.booleano(), [], [], [], [])
    for _ in range(r.entero()):
        sala.salidas.append([r.texto(), r.booleano()])
    for _ in range(r.entero()):
        sala.enemigos.append(_leer_enemigo(r))
    for _ in range(r.entero()):
        sala.objetos.append([r.texto(), r.texto(), r.texto()])
    for _ in range(r.entero()):
        sala.trampas.append([r.texto(), r.booleano(), r.entero(), r.entero_opcional(),
                             r.texto(), r.texto()])
    if not r.al_final():
        raise ValueError("Guardado dañado: sobran datos en una sala.")
    return sala


def _leer_global(datos: bytes, version_cripta: str) -> DatosGuardado:
    r = LectorBinario(datos)
    comprobar_version(r.entero(), "global")
    g = DatosGuardado(version_cripta=version_cripta)
    g.nombre_jugador = r.texto()
    g.cripta_id = r.texto()
    g.semilla = r.entero()
    g.modo = r.texto()
    g.acciones_ejecutadas = r.entero()
    g.enemigos_derrotados = r.entero()
    g.sala_actual_id = r.entero()
    g.tiempo_actual = r.entero()

    for _ in range(r.entero()):
        g.salidas_abiertas.append([r.entero(), r.texto()])
    g.azar_version = r.entero()
    g.azar_interno = [r.sin_signo() for _ in range(r.entero())]
    g.azar_gauss = r.decimal_opcional()
    g.jugador = _leer_actor(r)
    g.inventario_max = r.entero()
    g.antorcha_encendida = r.booleano()
    g.capacidad_inventario = r.entero()
    for _ in range(r.entero()):
        g.items.append(ItemInventario(
            instancia_id=r.texto(), tipo_id=r.texto(), nombre=r.texto(), clase=r.texto(),
            peso=r.entero(), valor=r.entero(), equipado=r.booleano(),
            ataque_bonus=r.entero(), defensa_bonus=r.entero(),
        ))
    g.item_actual = r.texto_opcional()
    for _ in range(r.entero()):
        g.eventos.append(EventoG(r.entero(), r.entero(), r.texto(), r.entero(), r.entero(), r.texto()))
    if not r.al_final():
        raise ValueError("Guardado dañado: sobran datos en el estado global.")
    return g


def _leer_valor(r: LectorBinario):
    etiqueta = r.entero()
    if etiqueta == VALOR_NULO:
        return None
    if etiqueta == VALOR_BOOLEANO:
        return r.booleano()
    if etiqueta == VALOR_ENTERO:
        return r.entero()
    if etiqueta == VALOR_TEXTO:
        return r.texto()
    if etiqueta == VALOR_TUPLA:
        return tuple(r.texto() for _ in range(r.entero()))
    raise ValueError("Guardado dañado: valor desconocido en la línea de tiempo.")


def _leer_valores(r: LectorBinario) -> list:
    return [_leer_valor(r) for _ in range(r.entero())]


def _leer_linea(datos: bytes) -> list:
    """Devuelve [instantánea del conocimiento, datos del controlador de la línea]."""
    r = LectorBinario(datos)
    comprobar_version(r.entero(), "de la línea de tiempo")
    conocimiento = _leer_valores(r)
    n = r.entero()
    ids = [r.texto() for _ in range(r.entero())]
    nombres = [r.texto() for _ in range(r.entero())]
    vidas_max = _leer_valores(r)
    ranuras = _leer_valores(r)
    k = r.entero()
    listas = [_leer_valores(r) for _ in range(10)]
    cp_estado = [_leer_valores(r) for _ in range(r.entero())]
    if not r.al_final():
        raise ValueError("Guardado dañado: sobran datos en la línea de tiempo.")
    return [conocimiento, [n, ids, nombres, vidas_max, ranuras, [k] + listas + [cp_estado]]]


def leer_partida(ruta) -> DatosGuardado:
    """Lee y valida el archivo completo sin tocar la partida en curso."""
    contenedor = Guardado_Binario(str(ruta))
    version = contenedor.version_cripta()
    global_g: DatosGuardado | None = None
    salas: list[SalaG] = []
    linea = None
    for cuerpo in contenedor.cargar_todo():
        if cuerpo.sala_id == ID_LINEA:
            linea = _leer_linea(cuerpo.bytes_)
        elif cuerpo.sala_id == ID_GLOBAL:
            global_g = _leer_global(cuerpo.bytes_, version)
        else:
            salas.append(_leer_sala(cuerpo.bytes_))
    if global_g is None:
        raise ValueError("Guardado dañado: falta el estado global.")
    global_g.salas = salas
    if linea is None:
        raise ValueError("Guardado dañado: falta la línea de tiempo.")
    global_g.conocimiento, global_g.linea = linea
    tiene_turno = False
    for ev in global_g.eventos:
        if ev.clase_actor == ACTOR_JUGADOR and ev.tipo == "accion_actor":
            tiene_turno = True
    if not tiene_turno:
        raise ValueError("Guardado dañado: el jugador no tiene acción programada.")
    return global_g