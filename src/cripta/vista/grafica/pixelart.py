"""Arte pixel propio de Cripta, generado en memoria con PIL.

Cada dibujo es una lista de cadenas: cada letra es un color de la paleta y
"." es transparente. Así el arte queda legible en el código, no depende de
archivos externos y no tiene problemas de licencia. Nada de esto toca el
modelo ni el azar de la simulación.
"""
import random

from PIL import Image, ImageDraw

# Paleta piedra arenisca / oliva (como el diseño de referencia).
_PALETA: list[tuple[str, tuple[int, int, int, int]]] = [
    ("K", (14, 12, 12, 255)),     # contorno
    ("k", (34, 28, 24, 255)),     # sombra muy oscura
    ("W", (238, 232, 214, 255)),  # brillo
    ("w", (196, 188, 170, 255)),  # gris claro
    ("g", (128, 124, 120, 255)),  # gris
    ("G", (84, 82, 84, 255)),     # gris oscuro / hierro
    ("R", (204, 52, 46, 255)),    # rojo
    ("r", (138, 30, 32, 255)),    # rojo oscuro
    ("P", (255, 150, 140, 255)),  # brillo rojo
    ("Y", (232, 186, 72, 255)),   # oro
    ("y", (168, 118, 40, 255)),   # oro oscuro
    ("O", (246, 156, 52, 255)),   # naranja fuego
    ("B", (70, 140, 220, 255)),   # azul
    ("b", (36, 74, 140, 255)),    # azul oscuro
    ("V", (110, 196, 92, 255)),   # verde
    ("v", (50, 112, 52, 255)),    # verde oscuro
    ("U", (160, 90, 200, 255)),   # violeta
    ("u", (92, 44, 128, 255)),    # violeta oscuro
    ("M", (140, 92, 54, 255)),    # madera
    ("m", (92, 58, 34, 255)),     # madera oscura
    ("C", (226, 206, 160, 255)),  # pergamino
    ("c", (170, 146, 102, 255)),  # pergamino oscuro
    ("S", (150, 134, 98, 255)),   # piedra clara
    ("s", (104, 92, 66, 255)),    # piedra
    ("d", (66, 58, 42, 255)),     # piedra oscura
    ("n", (20, 16, 13, 255)),     # hueco negro
]
_COLOR_POR_LETRA: list = [None] * 128
for _letra, _color in _PALETA:
    _COLOR_POR_LETRA[ord(_letra)] = _color


def dibujo(filas: list[str], reemplazos: list[tuple[str, str]] | None = None) -> Image.Image:
    """Convierte un dibujo ASCII en imagen RGBA. `reemplazos` cambia letras (p.ej. R->B)."""
    alto, ancho = len(filas), max(len(f) for f in filas)
    imagen = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
    for y, fila in enumerate(filas):
        for x, letra in enumerate(fila):
            for origen, destino in reemplazos or []:
                if letra == origen:
                    letra = destino
                    break
            color = _COLOR_POR_LETRA[ord(letra)] if ord(letra) < 128 else None
            if color is not None:
                imagen.putpixel((x, y), color)
    return imagen


#  Interfaz

CORAZON = [
    ".KKK...KKK.",
    "KRRWK.KRRRK",
    "KRWRRKRRRRK",
    "KRRRRRRRRrK",
    "KRRRRRRRRrK",
    ".KRRRRRRrK.",
    "..KRRRRrK..",
    "...KRRrK...",
    "....KrK....",
    ".....K.....",
]
CANDADO = [
    "..KKK..",
    ".KwgwK.",
    ".Kg.gK.",
    "KKKKKKK",
    "KYYYYyK",
    "KYYKYyK",
    "KYYKYyK",
    "KYyyyyK",
    "KKKKKKK",
]
CRUCETA = [
    "....KKKK....",
    "....KwWK....",
    "....KwWK....",
    "....KwwK....",
    "KKKKKwwKKKKK",
    "KwwwwwwwwwWK",
    "KgwwwwwwwwwK",
    "KKKKKwwKKKKK",
    "....KgwK....",
    "....KgwK....",
    "....KggK....",
    "....KKKK....",
]
ESPADA = [
    "..........KK",
    ".........KWK",
    "........KWwK",
    ".......KWwK.",
    "......KWwK..",
    ".KK..KWwK...",
    ".KyKKWwK....",
    "..KyWwK.....",
    "..KKyK......",
    ".KmKKyK.....",
    "KmK..KK.....",
    "KK..........",
]
RELOJ = [
    "KKKKKKKKKK",
    "KMMMMMMMMK",
    ".KWYYYYwK.",
    "..KYYYYK..",
    "...KYYK...",
    "....KK....",
    "....KK....",
    "...KwYK...",
    "..KwYYYK..",
    ".KYYYYYYK.",
    "KMMMMMMMMK",
    "KKKKKKKKKK",
]
PERGAMINO = [
    ".KKKKKKKKK..",
    "KcCCCCCCCcK.",
    "KcKKKKKKKCcK",
    ".KCCCCCCCCK.",
    ".KCkkkkkkCK.",
    ".KCCCCCCCCK.",
    ".KCkkkkkCCK.",
    ".KCCCCCCCCK.",
    "KcKKKKKKKCcK",
    "KcCCCCCCCcK.",
    ".KKKKKKKKK..",
]
LUPA = [
    "..KKKK......",
    ".KwWWwK.....",
    "KwW..wwK....",
    "KW....wK....",
    "Kw....wK....",
    "Kww..wwK....",
    ".KwwwwKK....",
    "..KKKKKmK...",
    "......KmmK..",
    ".......KmmK.",
    "........KmK.",
    ".........K..",
]
PUERTA_SALIR = [
    "..KKKKKK....",
    "..KMMMMK....",
    "..KMmMMK....",
    "..KMmMMK..K.",
    "..KMmMMK.KK.",
    "..KMmYMKKwKK",
    "..KMmMMKwwwK",
    "..KMmMMK.KK.",
    "..KMmMMK..K.",
    "..KMmMMK....",
    "..KMMMMK....",
    "..KKKKKK....",
]


#  Objetos

POCION = [
    "....KKKK....",
    "....KmMK....",
    ".....KwK....",
    ".....KwK....",
    "....KwwwK...",
    "...KRPRRRK..",
    "..KRPWRRRrK.",
    "..KRPRRRRrK.",
    "..KRRRRRRrK.",
    "..KRRRRRrrK.",
    "...KRRrrrK..",
    "....KKKKK...",
]
LLAVE = [
    "....KKKK....",
    "...KYYYYK...",
    "..KYyKKyYK..",
    "..KYK..KYK..",
    "..KYyKKyYK..",
    "...KYYYYK...",
    "....KYyK....",
    "....KYyK....",
    "....KYyKK...",
    "....KYYYK...",
    "....KYyKK...",
    "....KYYYK...",
    ".....KKK....",
]
ANTORCHA = [
    ".....KK.....",
    "....KOYK....",
    "...KOYWOK...",
    "...KOYYOK...",
    "....KOOK....",
    "....KmMK....",
    "....KmMK....",
    "....KmMK....",
    "....KmMK....",
    "....KmMK....",
    "....KmMK....",
    ".....KK.....",
]
ARMADURA = [
    ".KKK....KKK.",
    "KgwwKKKKwwgK",
    "KgwwwwwwwwgK",
    ".KgwWwwWwgK.",
    ".KgwwwwwwgK.",
    ".KgwwKKwwgK.",
    ".KgwwwwwwgK.",
    ".KggwwwwggK.",
    "..KgggggggK.",
    "...KKKKKK...",
]
GEMA = [
    "...KKKKK....",
    "..KPWRRRK...",
    ".KPWRRRRrK..",
    "KRPRRRRRRrK.",
    "KRRRRRRRRrK.",
    ".KRRRRRRrK..",
    "..KRRRRrK...",
    "...KRRrK....",
    "....KrK.....",
    ".....K......",
]
COFRE = [
    "..KKKKKKKK..",
    ".KMMMMMMMMK.",
    "KMmmmmmmmmMK",
    "KKKKKYYKKKKK",
    "KMMMMyYMMMMK",
    "KMmmmmmmmmMK",
    "KMMMMMMMMMMK",
    "KKKKKKKKKKKK",
]

#  Decoración

BARRIL = [
    "..KKKKKKKK..",
    ".KMMMMMMMMK.",
    "KMmMMMMMMmMK",
    "KGGGGGGGGGGK",
    "KMmMMMMMMmMK",
    "KMmMMMMMMmMK",
    "KMmMMMMMMmMK",
    "KGGGGGGGGGGK",
    "KMmMMMMMMmMK",
    ".KmmmmmmmmK.",
    "..KKKKKKKK..",
]
VASIJA = [
    "...KKKK...",
    "..KSsssK..",
    "...KssK...",
    "..KSSssK..",
    ".KSSsssdK.",
    "KSSssssddK",
    "KSsssssddK",
    "KSsssssddK",
    ".KssssddK.",
    "..KKKKKK..",
]
ROCAS = [
    "....KKK.......",
    "..KKSssK..KK..",
    ".KSSsssdKKSsK.",
    "KSSssssddKsddK",
    "KsssssddKKKKK.",
    ".KKKKKKKK.....",
]
CALAVERA = [
    ".KKKKK.",
    "KwWWWwK",
    "KWKwKwK",
    "KwwKwwK",
    ".KwwwK.",
    ".KwKwK.",
    "..KKK..",
]


def con_color(filas: list[str], liquido: str) -> Image.Image:
    """Poción/gema con otro color de líquido (R por B, U, V, Y...)."""
    oscuros = [("R", "r"), ("B", "b"), ("U", "u"), ("V", "v"), ("Y", "y"), ("O", "y")]
    oscuro = next(o for c, o in oscuros if c == liquido)
    return dibujo(filas, [("R", liquido), ("r", oscuro)])


#  Sala: suelo, paredes, puertas

def _variar(color, azar, rango=6):
    d = azar.randint(-rango, rango)
    return tuple(max(0, min(255, c + d)) for c in color[:3]) + (255,)


def baldosa(semilla: int) -> Image.Image:
    """Baldosa de piedra 16x16 con bisel, y a veces grieta o musgo."""
    azar = random.Random(semilla)
    base = (100, 84, 56)
    img = Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            img.putpixel((x, y), _variar(base, azar, 5))
    for i in range(16):
        img.putpixel((i, 0), (44, 37, 26, 255))           # junta superior
        img.putpixel((0, i), (44, 37, 26, 255))           # junta izquierda
        if i > 0:
            img.putpixel((i, 1), (124, 106, 74, 255))     # brillo
            img.putpixel((1, i), (116, 99, 69, 255))
            img.putpixel((i, 15), (74, 62, 42, 255))      # sombra
            img.putpixel((15, i), (78, 66, 45, 255))
    tipo = azar.random()
    if tipo < 0.25:                                        # grieta
        x, y = azar.randint(3, 12), azar.randint(3, 6)
        for _ in range(azar.randint(5, 9)):
            if 1 < x < 15 and 1 < y < 15:
                img.putpixel((x, y), (60, 51, 36, 255))
            x += azar.choice([-1, 0, 1])
            y += 1
    elif tipo < 0.4:                                       # musgo
        cx, cy = azar.randint(4, 11), azar.randint(4, 11)
        for _ in range(azar.randint(8, 14)):
            x, y = cx + azar.randint(-2, 2), cy + azar.randint(-2, 2)
            if 1 < x < 15 and 1 < y < 15:
                img.putpixel((x, y), azar.choice([(76, 98, 46, 255), (96, 116, 56, 255), (62, 82, 40, 255)]))
    elif tipo < 0.6:                                       # piedritas
        for _ in range(3):
            x, y = azar.randint(3, 13), azar.randint(3, 13)
            img.putpixel((x, y), (126, 112, 82, 255))
            img.putpixel((x, y + 1), (70, 60, 42, 255))
    return img


def ladrillos(semilla: int) -> Image.Image:
    """Pared frontal 16x16: ladrillos de 8x4 desplazados por fila."""
    azar = random.Random(semilla)
    img = Image.new("RGBA", (16, 16), (32, 28, 21, 255))
    for fila in range(4):
        desplazamiento = 0 if fila % 2 == 0 else 4
        for col in range(-1, 3):
            x0 = col * 8 + desplazamiento
            color = _variar((76, 66, 46), azar, 7)
            for y in range(fila * 4 + 1, fila * 4 + 4):
                for x in range(x0 + 1, x0 + 8):
                    if 0 <= x < 16:
                        img.putpixel((x, y), color)
            for x in range(x0 + 1, x0 + 8):
                if 0 <= x < 16:
                    img.putpixel((x, fila * 4 + 1), _variar((98, 86, 61), azar, 4))
    return img


def bloque_muro(semilla: int, ancho=16, alto=16) -> Image.Image:
    """Piedra del borde superior y de los muros laterales (vista desde arriba)."""
    azar = random.Random(semilla)
    img = Image.new("RGBA", (ancho, alto), (46, 41, 31, 255))
    for y0 in range(0, alto, 8):
        x_ini = -4 if (y0 // 8) % 2 else 0
        for x0 in range(x_ini, ancho, 8):
            color = _variar((102, 90, 64), azar, 6)
            for y in range(y0 + 1, min(alto, y0 + 8)):
                for x in range(max(0, x0 + 1), min(ancho, x0 + 8)):
                    img.putpixel((x, y), color)
            for x in range(max(0, x0 + 1), min(ancho, x0 + 8)):
                if y0 + 1 < alto:
                    img.putpixel((x, y0 + 1), _variar((128, 114, 84), azar, 4))
                if y0 + 7 < alto:
                    img.putpixel((x, y0 + 7), (72, 63, 45, 255))
    return img


def pilar(alto: int = 40) -> Image.Image:
    """Columna adosada al muro del fondo: capitel, fuste estriado y base."""
    img = Image.new("RGBA", (12, alto), (0, 0, 0, 0))
    for y in range(alto):
        for x in range(12):
            if y < 4 or y >= alto - 4:                         # capitel y base
                color = (140, 126, 92) if x not in (0, 11) else (60, 53, 39)
                if y in (0, alto - 1):
                    color = (60, 53, 39)
                if y == 1 or y == alto - 4:
                    color = (166, 150, 112)
            elif 1 <= x <= 10:                                  # fuste
                color = [(70, 62, 45), (128, 114, 84), (142, 128, 96), (128, 114, 84),
                         (104, 92, 68), (128, 114, 84), (142, 128, 96), (120, 106, 78),
                         (104, 92, 68), (96, 85, 62)][x - 1]
            else:
                continue
            img.putpixel((x, y), color + (255,))
    return img


def _arco(img, cx, arriba, abajo, medio_ancho, color_hueco, marco=True):
    """Hueco con remate en arco de medio punto (y crece hacia abajo)."""
    for y in range(arriba, abajo):
        for x in range(cx - medio_ancho, cx + medio_ancho):
            dy = y - (arriba + medio_ancho)
            dx = x - cx + 0.5
            if dy < 0 and dx * dx + dy * dy > medio_ancho * medio_ancho:
                continue
            img.putpixel((x, y), color_hueco)


def puerta_norte(cerrada: bool, salida: bool) -> Image.Image:
    """Arco en el muro del fondo (32x40): escalera hacia arriba o puerta de madera."""
    img = Image.new("RGBA", (32, 40), (0, 0, 0, 0))
    azar = random.Random(7)
    piedra = (132, 118, 86)
    for y in range(40):
        for x in range(32):
            dx, dy = x - 15.5, y - 13
            dentro = abs(x - 15.5) <= 15 and (y >= 13 or dx * dx + dy * dy <= 15.5 ** 2)
            if dentro:
                img.putpixel((x, y), _variar(piedra, azar, 7))
    # juntas de los bloques del marco
    for y in range(0, 40, 6):
        for x in range(32):
            if img.getpixel((x, y))[3]:
                img.putpixel((x, y), (70, 62, 45, 255))
    _arco(img, 16, 6, 40, 9, (64, 56, 40, 255))
    _arco(img, 16, 7, 40, 8, (16, 12, 10, 255))
    if cerrada:
        _arco(img, 16, 7, 40, 8, (112, 72, 40, 255))
        for x in range(8, 24, 4):                                # tablones
            for y in range(7, 40):
                if img.getpixel((x, y))[:3] == (112, 72, 40):
                    img.putpixel((x, y), (74, 46, 26, 255))
        for y in (16, 30):                                       # herrajes
            for x in range(8, 24):
                if img.getpixel((x, y))[:3] in [(112, 72, 40), (74, 46, 26)]:
                    img.putpixel((x, y), (60, 60, 66, 255))
        img.putpixel((20, 24), (200, 170, 80, 255))
    else:
        for i, y in enumerate(range(26, 40, 3)):                  # escalones
            claro = 40 + i * 14
            for x in range(9, 23):
                img.putpixel((x, y), (claro, claro - 6, claro - 12, 255))
                if y + 1 < 40:
                    img.putpixel((x, y + 1), (claro - 20, claro - 24, claro - 28, 255))
    if salida:
        for x in range(12, 20):                                  # piedra angular dorada
            img.putpixel((x, 1), (232, 186, 72, 255))
            img.putpixel((x, 2), (200, 150, 60, 255))
    return img


def puerta_sur(cerrada: bool, salida: bool) -> Image.Image:
    """Arco en el muro de abajo (32x22), visto desde dentro de la sala."""
    img = Image.new("RGBA", (32, 22), (0, 0, 0, 0))
    azar = random.Random(11)
    for y in range(22):
        for x in range(32):
            if x < 7 or x > 24 or y < 4:
                img.putpixel((x, y), _variar((132, 118, 86), azar, 7))
    for x in range(32):
        img.putpixel((x, 0), (160, 144, 108, 255))
    for y in range(4, 22):
        for x in range(7, 25):
            claro = max(10, 60 - (y - 4) * 3)
            img.putpixel((x, y), (claro, claro - 4, claro - 8, 255))
    if cerrada:
        for y in range(5, 22):
            for x in range(8, 24):
                img.putpixel((x, y), (112, 72, 40, 255) if (x - 8) % 4 else (74, 46, 26, 255))
        for x in range(8, 24):
            img.putpixel((x, 10), (60, 60, 66, 255))
    if salida:
        for x in range(12, 20):
            img.putpixel((x, 1), (232, 186, 72, 255))
    return img


def puerta_lateral(cerrada: bool, salida: bool) -> Image.Image:
    """Puerta en el muro izquierdo (16x34). La del muro derecho es su reflejo."""
    img = Image.new("RGBA", (16, 34), (0, 0, 0, 0))
    azar = random.Random(13)
    for y in range(34):
        for x in range(16):
            img.putpixel((x, y), _variar((132, 118, 86), azar, 7))
    for y in range(4, 30):
        for x in range(0, 11):
            claro = 14 + x * 4
            img.putpixel((x, y), (claro, claro - 3, claro - 6, 255))
    for y in (0, 33):
        for x in range(16):
            img.putpixel((x, y), (70, 62, 45, 255))
    if cerrada:
        for y in range(5, 29):
            for x in range(8, 14):
                img.putpixel((x, y), (112, 72, 40, 255) if (y - 5) % 4 else (74, 46, 26, 255))
        for y in (10, 22):
            for x in range(8, 14):
                img.putpixel((x, y), (60, 60, 66, 255))
    if salida:
        for y in range(10, 24):
            img.putpixel((15, y), (232, 186, 72, 255))
    return img


def resplandor(radio: int, color=(255, 170, 70), fuerza: float = 1.0) -> Image.Image:
    """Halo radial (para antorchas y la puerta de salida)."""
    tam = radio * 2
    img = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    for y in range(tam):
        for x in range(tam):
            d = ((x - radio + 0.5) ** 2 + (y - radio + 0.5) ** 2) ** 0.5 / radio
            if d < 1:
                img.putpixel((x, y), color + (int(70 * fuerza * (1 - d) ** 2),))
    return img


def componer(base: Image.Image, imagen: Image.Image, x: int, y: int, ancho=None, alto=None) -> None:
    """Pega `imagen` (escalada sin suavizado si hace falta) respetando la transparencia."""
    if ancho is not None and (ancho, alto) != imagen.size:
        imagen = imagen.resize((max(1, ancho), max(1, alto)), Image.NEAREST)
    capa = Image.new("RGBA", base.size, (0, 0, 0, 0))
    capa.paste(imagen, (x, y))
    base.alpha_composite(capa)


def sombra(base: Image.Image, caja, alfa: int) -> None:
    """Rectángulo oscuro semitransparente (caja = x0, y0, x1, y1)."""
    capa = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(capa).rectangle(caja, fill=(8, 6, 4, alfa))
    base.alpha_composite(capa)


def sombra_ovalada(base: Image.Image, cx: int, cy: int, ancho: int, alto: int, alfa: int = 90) -> None:
    capa = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(capa).ellipse([cx - ancho // 2, cy - alto // 2, cx + ancho // 2, cy + alto // 2], fill=(0, 0, 0, alfa))
    base.alpha_composite(capa)


def tenir(imagen: Image.Image, oscuro, claro) -> Image.Image:
    """Mapea la luminancia de una imagen a un degradado (recolorear assets grises)."""
    resultado = imagen.convert("RGBA").copy()
    datos = []
    for r, g, b, a in resultado.getdata():
        t = (0.3 * r + 0.59 * g + 0.11 * b) / 255
        t = min(1, t * 1.35)
        datos.append(tuple(int(oscuro[i] + (claro[i] - oscuro[i]) * t) for i in range(3)) + (a,))
    resultado.putdata(datos)
    return resultado
