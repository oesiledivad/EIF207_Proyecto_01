"""Recortes del tileset original de Szadi art, cargados una sola vez."""
from pathlib import Path
from PIL import Image
import arcade


def cargar(recursos):
    """Carga suelos, paredes, antorchas y alternativas estáticas de Catacombs.

    Args:
        recursos: Contenedor donde se asignan las texturas recortadas.
    """
    carpeta = Path(__file__).resolve().parents[1] / "recursos" / "catacombs"
    with Image.open(carpeta / "mainlevbuild.png") as hoja:
        hoja = hoja.convert("RGBA")
        suelos = [hoja.crop([736 + x, 208 + y, 752 + x, 224 + y])
                  for y in range(0, 48, 16) for x in range(0, 32, 16)]
        recursos.suelos = [arcade.Texture(tile) for tile in suelos if tile.getchannel("A").getextrema()[0] == 255]
        recursos.pared = arcade.Texture(hoja.crop([80, 128, 96, 160]))
        recursos.borde = arcade.Texture(hoja.crop([80, 48, 96, 64]))
        recursos.pared_izquierda = arcade.Texture(hoja.crop([32, 80, 48, 112]))
        recursos.pared_derecha = arcade.Texture(hoja.crop([272, 80, 288, 112]))
        recursos.esquina_izquierda = arcade.Texture(hoja.crop([64, 48, 80, 64]))
        recursos.esquina_derecha = arcade.Texture(hoja.crop([240, 48, 256, 64]))
        recursos.reja = arcade.Texture(hoja.crop([520, 32, 568, 96]))
    recursos.antorchas = [arcade.load_texture(carpeta / f"torch_{i}.png") for i in range(1, 5)]
    with Image.open(carpeta / "decorative.png") as hoja:
        hoja = hoja.convert("RGBA")
        for nombre, caja in [["estatua", [85, 125, 107, 160]], ["objeto", [144, 128, 160, 144]],
                             ["antidoto", [144, 176, 160, 192]], ["cofre", [128, 72, 144, 112]],
                             ["caja", [4, 68, 44, 96]], ["espada", [132, 16, 140, 46]]]:
            setattr(recursos, nombre, arcade.Texture(hoja.crop(caja)))
    recursos.hacha = recursos.daga = recursos.baston = recursos.lanza = recursos.espada
