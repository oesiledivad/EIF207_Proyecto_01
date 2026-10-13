"""Lectura: del archivo binario a estructuras intermedias, sin tocar la partida en curso."""

from __future__ import annotations

from cripta.controlador.guardado.Datos import ActorG, DatosGuardado, EnemigoG, EventoG, SalaG
from cripta.controlador.guardado.Formato import ACTOR_JUGADOR, ID_GLOBAL, VERSION_CUERPO
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
    return EnemigoG(actor, nombre, comportamiento, tipo, suelta, r.entero_opcional())  

def _leer_sala(datos: bytes) -> SalaG:
    r = LectorBinario(datos)
    if r.entero() != VERSION_CUERPO:
        raise ValueError("Versión de cuerpo de sala incompatible.")
    sala = SalaG(r.entero(), r.entero_opcional(), r.booleano(), [], [], [], [])
    for _ in range(r.entero()):
        sala.salidas.append((r.texto(), r.booleano()))
    for _ in range(r.entero()):
        sala.enemigos.append(_leer_enemigo(r))
    for _ in range(r.entero()):
        sala.objetos.append((r.texto(), r.texto(), r.texto()))
    for _ in range(r.entero()):
        sala.trampas.append((r.texto(), r.booleano(), r.entero(), r.entero_opcional(),
                             r.texto(), r.texto()))
    if not r.al_final():
        raise ValueError("Guardado dañado: sobran datos en una sala.")
    return sala


def _leer_global(datos: bytes, version_cripta: str) -> DatosGuardado:
    r = LectorBinario(datos)
    if r.entero() != VERSION_CUERPO:
        raise ValueError("Versión de cuerpo global incompatible.")
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


def leer_partida(ruta) -> DatosGuardado:
    """Lee y valida el archivo completo sin tocar la partida en curso."""
    contenedor = Guardado_Binario(str(ruta))
    version = contenedor.version_cripta()
    global_g: DatosGuardado | None = None
    salas: list[SalaG] = []
    for cuerpo in contenedor.cargar_todo():
        if cuerpo.sala_id == ID_GLOBAL:
            global_g = _leer_global(cuerpo.bytes_, version)
        else:
            salas.append(_leer_sala(cuerpo.bytes_))
    if global_g is None:
        raise ValueError("Guardado dañado: falta el estado global.")
    global_g.salas = salas
    tiene_turno = False
    for ev in global_g.eventos:
        if ev.clase_actor == ACTOR_JUGADOR and ev.tipo == "accion_actor":
            tiene_turno = True
    if not tiene_turno:
        raise ValueError("Guardado dañado: el jugador no tiene acción programada.")
    return global_g