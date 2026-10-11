"""Carga opcional de spritesheets locales, sin descargar durante el juego."""
from PIL import Image
from pathlib import Path
import arcade

LOCAL = Path(__file__).resolve().parents[1] / "recursos" / "local"


def animacion(nombre, accion):
    """Recorta una animación local manteniendo un marco común entre acciones.

    Args:
        nombre: Personaje según el nombre original del archivo.
        accion: Acción del spritesheet, como Idle, Hurt o Death.

    Returns:
        list: Texturas de los cuadros; vacía si falta el archivo o está vacío.
    """
    ruta = LOCAL / f"{nombre}_{accion}.png"
    if not ruta.is_file():
        return []
    with Image.open(ruta) as imagen:
        imagen = imagen.convert("RGBA")
        cuadros = [imagen.crop([x, 0, x + 100, 100]) for x in range(0, imagen.width, 100)]
    # Todas las acciones comparten marco y origen, incluso cuando el arma se extiende.
    cajas = [c.getbbox() for c in cuadros if c.getbbox()]
    for otra in ["Idle", "Walk", "Attack01", "Hurt", "Death"]:
        archivo = LOCAL / f"{nombre}_{otra}.png"
        if archivo.is_file():
            with Image.open(archivo) as hoja:
                hoja = hoja.convert("RGBA")
                cajas += [c.getbbox() for x in range(0, hoja.width, 100)
                          if (c := hoja.crop([x, 0, x + 100, 100])).getbbox()]
    if not cajas:
        return []
    borde = [min(c[0] for c in cajas), min(c[1] for c in cajas),
             max(c[2] for c in cajas), max(c[3] for c in cajas)]
    return [arcade.Texture(c.crop(borde)) for c in cuadros]


def armas():
    """Devuelve los cinco iconos de armas de Willibab, o [] si falta el pack."""
    ruta = LOCAL / "willibab.png"
    if not ruta.is_file():
        return []
    # Celdas de 32 px del spritesheet ALL original: espada, hacha, daga, bastón, lanza.
    with Image.open(ruta) as imagen:
        imagen = imagen.convert("RGBA")
        return [arcade.Texture(imagen.crop([x, y, x + 32, y + 32]))
                for x, y in [[0, 544], [0, 1152], [0, 2688], [0, 1696], [0, 2272]]]
