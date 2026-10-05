"""Efectos temporales (§2.10): veneno, cambio de velocidad, regeneración."""

INTERVALO_VENENO = 80
DURACION_VENENO = 400
INTERVALO_REGENERACION = 200


def aplicar_veneno(actor, dano_por_pulso: int, tiempo_actual: int, agenda) -> None:
    if actor.evento_veneno is not None:
        agenda.cancelar(actor.evento_veneno)
    actor.dano_veneno = dano_por_pulso
    actor.fin_veneno = tiempo_actual + DURACION_VENENO
    actor.evento_veneno = agenda.insertar(tiempo_actual + INTERVALO_VENENO, actor, "veneno")


def cancelar_veneno(actor, agenda) -> None:
    """Antídoto: cancela pulsos futuros (§2.10, Apéndice B)."""
    if actor.evento_veneno is not None:
        agenda.cancelar(actor.evento_veneno)
        actor.evento_veneno = None
        actor.fin_veneno = None


def procesar_pulso_veneno(actor, tiempo_actual: int, agenda) -> str:
    from cripta.modelo.Combate import aplicar_danio, esta_vivo

    aplicar_danio(actor, actor.dano_veneno)
    mensaje = f"{actor.identificador} sufre {actor.dano_veneno} de veneno."

    if not esta_vivo(actor) or tiempo_actual + INTERVALO_VENENO >= actor.fin_veneno:
        actor.evento_veneno = None
        actor.fin_veneno = None
        return mensaje

    actor.evento_veneno = agenda.insertar(tiempo_actual + INTERVALO_VENENO, actor, "veneno")
    return mensaje


def aplicar_cambio_velocidad(actor, nueva_velocidad: int, duracion: int, tiempo_actual: int, agenda) -> None:
    if actor.evento_fin_velocidad is not None:
        agenda.cancelar(actor.evento_fin_velocidad)
    else:
        actor.velocidad_base = actor.velocidad  # guardar la original solo la primera vez

    actor.actualizar_velocidad(nueva_velocidad, tiempo_actual, agenda)
    actor.evento_fin_velocidad = agenda.insertar(tiempo_actual + duracion, actor, "fin_velocidad")


def procesar_fin_velocidad(actor, tiempo_actual: int, agenda) -> str:
    actor.actualizar_velocidad(actor.velocidad_base, tiempo_actual, agenda)
    actor.evento_fin_velocidad = None
    return f"El efecto de velocidad de {actor.identificador} termina."


def activar_regeneracion(enemigo, cantidad: int, tiempo_actual: int, agenda) -> None:
    enemigo.regeneracion_cantidad = cantidad
    enemigo.evento_regeneracion = agenda.insertar(tiempo_actual + INTERVALO_REGENERACION, enemigo, "regeneracion")


def procesar_regeneracion(enemigo, tiempo_actual: int, agenda) -> str:
    from cripta.modelo.Combate import esta_vivo

    enemigo.vida = min(enemigo.vida_max, enemigo.vida + enemigo.regeneracion_cantidad)
    mensaje = f"{enemigo.identificador} regenera {enemigo.regeneracion_cantidad}."
    if esta_vivo(enemigo):
        enemigo.evento_regeneracion = agenda.insertar(tiempo_actual + INTERVALO_REGENERACION, enemigo, "regeneracion")
    return mensaje

TRAMPA_REARME_DEFECTO = 300


def disparar_trampa(trampa, jugador, tiempo_actual: int, agenda) -> str:
    from cripta.modelo.Combate import aplicar_danio

    aplicar_danio(jugador, trampa.dano)
    trampa.armada = False
    intervalo = trampa.rearme if trampa.rearme is not None else TRAMPA_REARME_DEFECTO
    agenda.insertar(tiempo_actual + intervalo, trampa, "trampa_rearme")
    return f"¡Trampa! Pierdes {trampa.dano} de vida."

def procesar_rearme_trampa(trampa) -> str:
    trampa.armada = True
    return "Una trampa se rearma."