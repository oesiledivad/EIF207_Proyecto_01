"""Escritura: del modelo del juego al archivo binario."""

from __future__ import annotations

import os

from cripta.controlador.guardado.Datos import Cuerpo
from cripta.controlador.guardado.Formato import (
    ACTOR_ENEMIGO,
    ACTOR_JUGADOR,
    ACTOR_SALIDA,
    ACTOR_TRAMPA,
    ID_GLOBAL,
    VERSION_CUERPO,
)
from cripta.estructuras.Guardado_Binario import Guardado_Binario
from cripta.estructuras.Ordenamientos import ordenar
from cripta.estructuras.Salidas import SalidaSimple
from cripta.estructuras.serializacionBinaria import EscritorBinario
from cripta.modelo.Enemigo import Enemigo
from cripta.modelo.Trampa import TrampaJuego


def _escribir_actor(w: EscritorBinario, a) -> None:
    w.texto(a.identificador)
    w.entero(a.vida)
    w.entero(a.vida_max)
    w.entero(a.ataque)
    w.entero(a.defensa)
    w.entero(a.velocidad)
    w.entero(a.velocidad_base)
    w.entero(a.sala)
    w.entero_opcional(a.tiempo_siguiente)
    w.entero(a.dano_veneno)
    w.entero_opcional(a.fin_veneno)
    w.entero(a.regeneracion_cantidad)


def _escribir_enemigo(w: EscritorBinario, e) -> None:
    _escribir_actor(w, e)
    w.texto(e.nombre) 
    w.texto(e.comportamiento)
    w.texto(e.tipo or "")
    w.entero(len(e.suelta))
    for objeto in e.suelta:
        w.texto(objeto)
    w.entero_opcional(e.regeneracion_objetivo)


def _cuerpo_sala(sala) -> bytes:
    w = EscritorBinario()
    w.entero(VERSION_CUERPO)
    w.entero(sala.id)
    w.entero_opcional(sala.ultimo_tiempo_visita)
    w.booleano(sala.contenido_cargado)
    salidas = list(sala.salidas)
    w.entero(len(salidas))
    for s in salidas:
        w.texto(s.direccion)
        w.booleano(s.cerrada)
    w.entero(len(sala.enemigos))
    for e in sala.enemigos:
        _escribir_enemigo(w, e)
    w.entero(len(sala.objetos))
    for o in sala.objetos:
        w.texto(o.id)
        w.texto(o.nombre)
        w.texto(o.tipo_id or "")
    w.entero(len(sala.trampas))
    for t in sala.trampas:
        w.texto(t.instancia)
        w.booleano(t.armada)
        w.entero(t.dano)
        w.entero_opcional(t.rearme)
        w.texto(t.efecto)
        w.texto(t.tipo or "")
    return w.a_bytes()


def _referencia_actor(app, actor) -> tuple[int, int, str]:
    """Identifica al dueño de un evento: (clase, sala, clave). Compara por identidad."""
    if actor is app._jugador:
        return ACTOR_JUGADOR, 0, ""
    for sala_modelo in app._gestor.estado.salas_conocidas:
        sala = app._salas.obtener(sala_modelo.id)
        if sala is None:
            continue
        if isinstance(actor, Enemigo):
            for e in sala.enemigos:
                if e is actor:
                    return ACTOR_ENEMIGO, sala.id, e.identificador
        elif isinstance(actor, TrampaJuego):
            for posicion, t in enumerate(sala.trampas):
                if t is actor:
                    return ACTOR_TRAMPA, sala.id, str(posicion)
        elif isinstance(actor, SalidaSimple):
            for s in sala.salidas:
                if s is actor:
                    return ACTOR_SALIDA, sala.id, s.direccion
    raise ValueError("Hay un evento programado cuyo dueño no está en la partida.")


def _cuerpo_global(app) -> bytes:
    estado = app._gestor.estado
    sim = app._simulacion
    w = EscritorBinario()
    w.entero(VERSION_CUERPO)
    w.texto(estado.nombre_jugador)
    w.texto(estado.cripta_id)
    w.entero(estado.semilla)
    w.texto(estado.modo)
    w.entero(estado.acciones_ejecutadas)
    w.entero(estado.enemigos_derrotados)
    w.entero(estado.sala_actual_id)
    w.entero(sim.reloj.tiempo_actual)
    abiertas = app._partida._salidas_abiertas      
    w.entero(len(abiertas))
    for sala_id, direccion in abiertas:
        w.entero(sala_id)
        w.texto(direccion)


    version, interno, gauss = sim.azar.getstate()
    w.entero(version)
    w.entero(len(interno))
    for numero in interno:
        w.sin_signo(numero)
    w.decimal_opcional(gauss)

    _escribir_actor(w, app._jugador)
    w.entero(app._jugador.inventario_max)
    w.booleano(app._jugador.antorcha_encendida)

    inventario = app._gestor.inventario
    w.entero(inventario.capacidad)
    items = inventario.items()
    w.entero(len(items))
    for it in items:
        w.texto(it.instancia_id)
        w.texto(it.tipo_id)
        w.texto(it.nombre)
        w.texto(it.clase)
        w.entero(it.peso)
        w.entero(it.valor)
        w.booleano(it.equipado)
        w.entero(it.ataque_bonus)
        w.entero(it.defensa_bonus)
    actual = inventario.item_actual()
    w.texto_opcional(actual.instancia_id if actual is not None else None)

    eventos = ordenar(sim.agenda.eventos_validos(), key=lambda ev: ev.clave())
    w.entero(len(eventos))
    for ev in eventos:
        clase, sala_id, clave = _referencia_actor(app, ev.actor)
        w.entero(ev.tiempo_siguiente)
        w.entero(ev.secuencias)
        w.texto(ev.tipo)
        w.entero(clase)
        w.entero(sala_id)
        w.texto(clave)
    return w.a_bytes()


def escribir_partida(app, ruta) -> None:
    """Escribe la partida activa. El archivo se reemplaza de forma atómica."""
    estado = app._gestor.estado
    cuerpos: list[Cuerpo] = []
    for sala_modelo in estado.salas_conocidas:
        sala = app._salas.obtener(sala_modelo.id)
        if sala is not None:
            cuerpos.append(Cuerpo(sala.id, _cuerpo_sala(sala)))
    cuerpos.append(Cuerpo(ID_GLOBAL, _cuerpo_global(app)))
    temporal = f"{ruta}.tmp"
    Guardado_Binario(temporal).guardar(estado.version_cripta, cuerpos)
    os.replace(temporal, ruta)