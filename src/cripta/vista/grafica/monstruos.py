"""Animaciones propias cargadas desde spritesheets PNG."""
from .assets import animaciones


def rata() -> list:
    """Carga reposo, ataque, herida y muerte de la rata."""
    return animaciones("rata")


def esqueleto() -> list:
    """Carga reposo, ataque, herida y muerte del esqueleto."""
    return animaciones("esqueleto")


def espectro(comportamiento="") -> list:
    """Carga el espectro del comportamiento, con respaldo genérico."""
    tipo = (comportamiento or "").lower().replace("guardian", "guardián")
    if tipo not in ["rastreador", "errante", "guardián"]:
        tipo = ""
    return animaciones(f"espectro_{tipo}")
