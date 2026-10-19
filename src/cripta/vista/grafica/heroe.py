"""Clasificación del equipo y carga del jugador desde su spritesheet PNG."""
from .assets import animaciones as cargar_animaciones

ANCHO = 36
ALTO = 32


def tipo_arma(texto: str) -> str:
    """Clasifica el arma equipada por su nombre/id (respaldo: espada)."""
    texto = (texto or "").lower()
    if not texto:
        return "ninguna"
    for palabras, tipo in [[["daga", "cuchillo", "puñal"], "daga"], [["hacha"], "hacha"],
                           [["lanza", "pica", "alabarda"], "lanza"], [["baston", "bastón", "vara", "cetro"], "baston"],
                           [["maza", "martillo"], "maza"]]:
        if any(p in texto for p in palabras):
            return tipo
    return "espada"


def tipo_armadura(texto: str) -> str:
    """Clasifica la armadura equipada (respaldo: cota de malla)."""
    texto = (texto or "").lower()
    if not texto:
        return "ninguna"
    for palabras, tipo in [[["cuero", "puentecero"], "cuero"], [["manto", "capa", "túnica", "tunica"], "manto"],
                           [["esquirlada", "placa", "acero", "armadura"], "placas"]]:
        if any(p in texto for p in palabras):
            return tipo
    return "malla"


def animaciones(arma="ninguna", armadura="ninguna", antorcha=False) -> list:
    """Carga [reposo, caminar, atacar, herido, muerte] del equipo indicado."""
    return cargar_animaciones(f"heroe_{arma}_{armadura}_{int(antorcha)}")
