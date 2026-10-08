"""Efectos temporales (§2.10): veneno, cambio de velocidad, regeneración."""

INTERVALO_VENENO = 80
DURACION_VENENO = 400
INTERVALO_REGENERACION = 200


def aplicar_veneno(actor, dano_por_pulso: int, tiempo_actual: int, agenda) -> None:
    if actor.evento_veneno is not None:
        agenda.cancelar(actor.evento_veneno)
    agenda.cambiar(actor, "dano_veneno", dano_por_pulso)
    agenda.cambiar(actor, "fin_veneno", tiempo_actual + DURACION_VENENO)
    agenda.cambiar(actor, "evento_veneno", agenda.insertar(tiempo_actual + INTERVALO_VENENO, actor, "veneno"))


def cancelar_veneno(actor, agenda) -> None:
    """Antídoto: cancela pulsos futuros (§2.10, Apéndice B)."""
    if actor.evento_veneno is not None:
        agenda.cancelar(actor.evento_veneno)
        agenda.cambiar(actor, "evento_veneno", None)
        agenda.cambiar(actor, "fin_veneno", None)


def procesar_pulso_veneno(actor, tiempo_actual: int, agenda) -> str:
    from cripta.modelo.Combate import aplicar_danio, esta_vivo

    aplicar_danio(actor, actor.dano_veneno, agenda)
    mensaje = f"{actor.etiqueta} sufre {actor.dano_veneno} de veneno."

    # Pulsos en t0+80, +160, +240, +320 y +400 (400/80 = 5 pulsos).
    if not esta_vivo(actor) or tiempo_actual + INTERVALO_VENENO > actor.fin_veneno:
        agenda.cambiar(actor, "evento_veneno", None)
        agenda.cambiar(actor, "fin_veneno", None)
        return mensaje

    agenda.cambiar(actor, "evento_veneno", agenda.insertar(tiempo_actual + INTERVALO_VENENO, actor, "veneno"))
    return mensaje


def aplicar_cambio_velocidad(actor, nueva_velocidad: int, duracion: int, tiempo_actual: int, agenda) -> None:
    if actor.evento_fin_velocidad is not None:
        agenda.cancelar(actor.evento_fin_velocidad)
    else:
        agenda.cambiar(actor, "velocidad_base", actor.velocidad)

    actor.actualizar_velocidad(nueva_velocidad, tiempo_actual, agenda)
    agenda.cambiar(actor, "evento_fin_velocidad", agenda.insertar(tiempo_actual + duracion, actor, "fin_velocidad"))


def aplicar_modificador_velocidad(actor, modificador: int, duracion: int, tiempo_actual: int, agenda) -> None:
    """Poción de velocidad: suma `modificador` a la velocidad base durante `duracion`.

    Si ya hay un efecto activo, se parte de la velocidad base original
    (no se acumulan), y se reinicia la duración.
    """
    base = actor.velocidad if actor.evento_fin_velocidad is None else actor.velocidad_base
    nueva = max(1, base + modificador)
    aplicar_cambio_velocidad(actor, nueva, duracion, tiempo_actual, agenda)


def curar(actor, cantidad: int, agenda=None) -> int:
    """Cura sin superar vida_max (Apéndice B). Devuelve lo curado realmente."""
    antes = actor.vida
    vida = min(actor.vida_max, actor.vida + cantidad)
    if agenda is None:
        actor.vida = vida
    else:
        agenda.cambiar(actor, "vida", vida)
    return actor.vida - antes


def procesar_fin_velocidad(actor, tiempo_actual: int, agenda) -> str:
    actor.actualizar_velocidad(actor.velocidad_base, tiempo_actual, agenda)
    agenda.cambiar(actor, "evento_fin_velocidad", None)
    return f"El efecto de velocidad de {actor.etiqueta} termina."


def activar_regeneracion(enemigo, cantidad: int, tiempo_actual: int, agenda) -> None:
    agenda.cambiar(enemigo, "regeneracion_cantidad", cantidad)
    agenda.cambiar(enemigo, "evento_regeneracion", agenda.insertar(tiempo_actual + INTERVALO_REGENERACION, enemigo, "regeneracion"))


def procesar_regeneracion(enemigo, tiempo_actual: int, agenda) -> str:
    from cripta.modelo.Combate import esta_vivo

    if not esta_vivo(enemigo):
        return ""
    agenda.cambiar(enemigo, "vida", min(enemigo.vida_max, enemigo.vida + enemigo.regeneracion_cantidad))
    mensaje = f"{enemigo.etiqueta} regenera {enemigo.regeneracion_cantidad}."
    if esta_vivo(enemigo):
        agenda.cambiar(enemigo, "evento_regeneracion", agenda.insertar(tiempo_actual + INTERVALO_REGENERACION, enemigo, "regeneracion"))
    return mensaje

TRAMPA_REARME_DEFECTO = 300


def disparar_trampa(trampa, jugador, tiempo_actual: int, agenda) -> str:
    intervalo = trampa.rearme if trampa.rearme is not None else TRAMPA_REARME_DEFECTO

    if trampa.efecto == "veneno":
        aplicar_veneno(jugador, trampa.dano, tiempo_actual, agenda)
        mensaje = "¡Trampa venenosa! Quedás envenenado."
    else:
        from cripta.modelo.Combate import aplicar_danio
        aplicar_danio(jugador, trampa.dano, agenda)
        mensaje = f"¡Trampa! Pierdes {trampa.dano} de vida."

    agenda.cambiar(trampa, "armada", False)
    agenda.insertar(tiempo_actual + intervalo, trampa, "trampa_rearme")
    return mensaje

def procesar_rearme_trampa(trampa, agenda) -> str:
    agenda.cambiar(trampa, "armada", True)
    return "Una trampa se rearma."

def encender_antorcha(jugador, duracion: int, tiempo_actual: int, agenda) -> str:
    if jugador.evento_antorcha is not None:
        agenda.cancelar(jugador.evento_antorcha)
    agenda.cambiar(jugador, "antorcha_encendida", True)
    agenda.cambiar(jugador, "evento_antorcha", agenda.insertar(tiempo_actual + duracion, jugador, "antorcha_apagar"))
    return "Encendés la antorcha."


def procesar_apagar_antorcha(jugador, agenda) -> str:
    agenda.cambiar(jugador, "antorcha_encendida", False)
    agenda.cambiar(jugador, "evento_antorcha", None)
    return "La antorcha se apaga."
