"""Constantes del formato de guardado."""

ID_GLOBAL = 0xFFFFFFFF
ID_LINEA = 0xFFFFFFFE      # conocimiento del jugador y línea de tiempo (spec 004, D9)
VERSION_CUERPO = 3         # Parte II; la 2 es la de la Parte I y se rechaza (FR-026)
VERSION_PARTE_UNO = 2

# Etiquetas de los valores de la línea de tiempo.
VALOR_NULO = 0
VALOR_ENTERO = 1
VALOR_TEXTO = 2
VALOR_TUPLA = 3
VALOR_BOOLEANO = 4


def comprobar_version(version: int, que: str) -> None:
    """Rechaza los cuerpos de otra versión; la de la Parte I con un mensaje propio (FR-026)."""
    if version == VERSION_PARTE_UNO:
        raise ValueError("el archivo es un guardado de la Parte I (formato 2), incompatible con "
                         "la Parte II; no se carga.")
    if version != VERSION_CUERPO:
        raise ValueError(f"Versión de cuerpo {que} incompatible.")

# Clase del actor al que pertenece un evento de la agenda.
ACTOR_JUGADOR = 0
ACTOR_ENEMIGO = 1
ACTOR_TRAMPA = 2
ACTOR_SALIDA = 3