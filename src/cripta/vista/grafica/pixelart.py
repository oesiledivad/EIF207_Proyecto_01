"""Composición de PNG y sombras; el arte se genera fuera del juego."""
from PIL import Image, ImageDraw


def componer(base: Image.Image, imagen: Image.Image, x: int, y: int, ancho=None, alto=None) -> None:
    """Pega `imagen` (escalada sin suavizado si hace falta) respetando la transparencia."""
    if ancho is not None and [ancho, alto] != list(imagen.size):
        imagen = imagen.resize([max(1, ancho), max(1, alto)], Image.NEAREST)
    capa = Image.new("RGBA", base.size, "#00000000")
    capa.paste(imagen, [x, y])
    base.alpha_composite(capa)


def sombra(base: Image.Image, caja, alfa: int) -> None:
    """Rectángulo oscuro semitransparente (caja = x0, y0, x1, y1)."""
    capa = Image.new("RGBA", base.size, "#00000000")
    ImageDraw.Draw(capa).rectangle(caja, fill=f"#080604{alfa:02x}")
    base.alpha_composite(capa)


def sombra_ovalada(base: Image.Image, cx: int, cy: int, ancho: int, alto: int, alfa: int = 90) -> None:
    capa = Image.new("RGBA", base.size, "#00000000")
    ImageDraw.Draw(capa).ellipse([cx - ancho // 2, cy - alto // 2, cx + ancho // 2, cy + alto // 2], fill=f"#000000{alfa:02x}")
    base.alpha_composite(capa)
