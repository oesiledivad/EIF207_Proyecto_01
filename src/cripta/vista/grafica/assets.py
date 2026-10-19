"""Lectura de imágenes propias y sus animaciones exportadas."""
import json
from pathlib import Path

from PIL import Image

CARPETA = Path(__file__).resolve().parents[1] / "recursos" / "propios"


def imagen(nombre):
    """Carga un PNG independiente del archivo abierto."""
    with Image.open(CARPETA / f"{nombre}.png") as original:
        return original.convert("RGBA")


def animaciones(nombre):
    """Recorta las filas del spritesheet según su índice de cuadros."""
    with (CARPETA / "animaciones.json").open(encoding="utf-8") as archivo:
        indice = json.load(archivo)
    _, ancho, alto, cantidades = next(fila for fila in indice if fila[0] == nombre)
    hoja = imagen(nombre)
    return [[hoja.crop([x * ancho, y * alto, (x + 1) * ancho, (y + 1) * alto])
             for x in range(cantidad)] for y, cantidad in enumerate(cantidades)]
