"""Restauración: de las estructuras intermedias al modelo del juego."""

from __future__ import annotations

from cripta.controlador.guardado.Datos import ActorG, DatosGuardado, EventoG
from cripta.controlador.guardado.Formato import (
    ACTOR_ENEMIGO,
    ACTOR_JUGADOR,
    ACTOR_SALIDA,
    ACTOR_TRAMPA,
)
from cripta.dto.Partida_dto import EnemigoPartida, ObjetoSuelo
from cripta.modelo.Jugador import Jugador
from cripta.modelo.Simulacion import Simulacion
from cripta.modelo.Trampa import TrampaJuego


def _aplicar_actor(destino, a: ActorG) -> None:
    destino.velocidad_base = a.velocidad_base
    destino.tiempo_siguiente = a.tiempo_siguiente
    destino.dano_veneno = a.dano_veneno
    destino.fin_veneno = a.fin_veneno
    destino.regeneracion_cantidad = a.regeneracion_cantidad


def _buscar_actor(app, ev: EventoG):
    if ev.clase_actor == ACTOR_JUGADOR:
        return app._jugador
    sala = app._salas.obtener(ev.sala_id)
    if sala is None:
        raise ValueError(f"Evento de una sala inexistente: {ev.sala_id}.")
    if ev.clase_actor == ACTOR_ENEMIGO:
        for e in sala.enemigos:
            if e.identificador == ev.clave:
                return e
    elif ev.clase_actor == ACTOR_TRAMPA:
        posicion = int(ev.clave)
        if 0 <= posicion < len(sala.trampas):
            return sala.trampas[posicion]
    elif ev.clase_actor == ACTOR_SALIDA:
        return sala.salidas.obtener(ev.clave)
    raise ValueError("Guardado inconsistente: un evento apunta a algo que no existe.")


def _enlazar_evento(actor, tipo: str, evento) -> None:
    """Reconecta el campo del actor que apunta a su evento pendiente."""
    match tipo:
        case "accion_actor":
            actor._proximo_evento = evento
        case "veneno":
            actor.evento_veneno = evento
        case "fin_velocidad":
            actor.evento_fin_velocidad = evento
        case "regeneracion":
            actor.evento_regeneracion = evento
        case "antorcha_apagar":
            actor.evento_antorcha = evento
        case "cierre_puerta":
            actor.evento_cierre = evento


def restaurar_partida(app, datos: DatosGuardado) -> None:
    """Superpone lo guardado sobre una partida recién iniciada de la misma cripta.

    `iniciar_partida` ya dejó listos el esqueleto, la caché y el estado; aquí se
    reemplaza todo lo que cambia durante el juego.
    """
    # Validar antes de modificar nada.
    for sala_g in datos.salas:
        if app._salas.obtener(sala_g.sala_id) is None:
            raise ValueError(f"La sala {sala_g.sala_id} del guardado no existe en la cripta.")

    # Las fichas protegidas por la partida recién creada se sueltan; se protegen de nuevo al final.
    app._cripta_service.liberar_fichas(app._tipos_activos())

    for sala_g in datos.salas:
        sala = app._salas.obtener(sala_g.sala_id)
        sala.ultimo_tiempo_visita = sala_g.ultimo_tiempo_visita
        sala.contenido_cargado = sala_g.contenido_cargado
        for direccion, cerrada in sala_g.salidas:
            salida = sala.salidas.obtener(direccion)
            if salida is not None:
                salida.cerrada = cerrada
                salida.evento_cierre = None
        sala.enemigos = []
        sala.objetos = []
        sala.trampas = []
        for eg in sala_g.enemigos:
            a = eg.actor
            enemigo = app._combate.crear_enemigo(EnemigoPartida(
                id=a.identificador, nombre=eg.nombre, vida=a.vida, ataque=a.ataque,
                defensa=a.defensa, vida_max=a.vida_max, velocidad=a.velocidad,
                comportamiento=eg.comportamiento, regeneracion=eg.regeneracion_objetivo,
                tipo=eg.tipo, suelta=list(eg.suelta),
            ), sala.id)
            _aplicar_actor(enemigo, a)
            sala.enemigos.append(enemigo)
        for id_, nombre, tipo_id in sala_g.objetos:
            sala.objetos.append(ObjetoSuelo(id=id_, nombre=nombre, tipo_id=tipo_id))
        for instancia, armada, dano, rearme, efecto, tipo in sala_g.trampas:
            sala.trampas.append(TrampaJuego(instancia=instancia, armada=armada, dano=dano,
                                            rearme=rearme, efecto=efecto, tipo=tipo))

    # Simulación nueva: reloj, azar y agenda.
    sim = Simulacion(datos.semilla, app._gestor.historial)
    sim.reloj.tiempo_actual = datos.tiempo_actual
    sim.azar.setstate((datos.azar_version, tuple(datos.azar_interno), datos.azar_gauss))  # random exige tupla
    app._simulacion = sim

    j = datos.jugador
    jugador = Jugador(
        identificador=j.identificador, vida=j.vida, vida_max=j.vida_max, ataque=j.ataque,
        defensa=j.defensa, velocidad=j.velocidad, sala=j.sala, tiempo_siguiente=j.tiempo_siguiente,
        inventario_max=datos.inventario_max,
    )
    _aplicar_actor(jugador, j)
    jugador.antorcha_encendida = datos.antorcha_encendida
    app._jugador = jugador

    # Eventos: ya vienen ordenados por (tiempo, secuencia); reinsertarlos en ese orden conserva el desempate.
    for ev in datos.eventos:
        actor = _buscar_actor(app, ev)
        nuevo = sim.agenda.insertar(ev.tiempo, actor, ev.tipo)
        _enlazar_evento(actor, ev.tipo, nuevo)

    # Inventario: agregar() inserta al frente, así que se recorre al revés para conservar el orden.
    app._gestor.reiniciar_inventario(datos.capacidad_inventario)
    for posicion in range(len(datos.items) - 1, -1, -1):
        app._gestor.inventario.agregar(datos.items[posicion])
    if datos.item_actual is not None:
        app._gestor.inventario.seleccionar(datos.item_actual)

    estado = app._gestor.estado
    estado.acciones_ejecutadas = datos.acciones_ejecutadas
    estado.enemigos_derrotados = datos.enemigos_derrotados
    estado.sala_actual_id = datos.sala_actual_id
    estado.activa = True
    estado.terminada = False
    estado.derrota = False
    estado.victoria = False
    estado.contenido_cargado = [s.sala_id for s in datos.salas if s.contenido_cargado]
    app._partida._salidas_abiertas = [list(p) for p in datos.salidas_abiertas]
    app._gestor.historial.limpiar()
    app._gestor.refrescar_sala_actual()
    app._sincronizar_estado()
    app._cripta_service.fijar_fichas(app._tipos_activos())
