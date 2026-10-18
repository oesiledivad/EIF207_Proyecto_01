"""Enemigos dibujados en código (pixel art propio, sin licencias).

Los packs gratuitos no traen una rata gigante ni un esqueleto, que son los
enemigos de las criptas publicadas, y sus personajes son "chibi". Aquí se
generan monstruos más grandes que el jugador y con aspecto amenazante:
ojos que brillan, dientes, pelaje erizado, huesos.

Cada función devuelve [reposo, ataque, herida, muerte], listas de imágenes
PIL que comparten lienzo y origen (como los spritesheets), mirando a la
DERECHA. Nada de esto toca el modelo ni el azar de la simulación: el azar
de las texturas es propio y fijo.
"""
import math
import random

from PIL import Image, ImageDraw

# Colores RGBA (tuplas porque PIL las exige).
CONTORNO = (10, 8, 9, 255)
PELO_OSCURO = (38, 32, 32, 255)
PELO = (62, 52, 48, 255)
PELO_CLARO = (92, 80, 70, 255)
PELO_PUNTA = (124, 110, 96, 255)
PIEL = (150, 92, 92, 255)          # cola, orejas, patas: piel sin pelo
PIEL_OSCURA = (98, 56, 60, 255)
BOCA = (70, 12, 16, 255)
DIENTE = (226, 210, 160, 255)
DIENTE_SOMBRA = (160, 140, 96, 255)
OJO = (255, 46, 30, 255)
OJO_CENTRO = (255, 214, 120, 255)
SANGRE = (130, 18, 22, 255)
HUESO = (212, 204, 180, 255)
HUESO_SOMBRA = (150, 142, 122, 255)
HUESO_OSCURO = (92, 86, 74, 255)
OXIDO = (122, 64, 40, 255)
OXIDO_CLARO = (168, 96, 56, 255)
HIERRO = (78, 78, 86, 255)
HIERRO_CLARO = (132, 132, 142, 255)
TELA = (34, 26, 40, 255)
TELA_CLARA = (58, 44, 66, 255)
FANTASMA = (255, 255, 255, 255)


def _contornear(img: Image.Image) -> Image.Image:
    """Agrega un contorno oscuro de 1 px alrededor de lo opaco (lectura clara sobre el suelo)."""
    ancho, alto = img.size
    fuente = img.load()
    salida = img.copy()
    destino = salida.load()
    for y in range(alto):
        for x in range(ancho):
            if fuente[x, y][3]:
                continue
            for dx, dy in [[1, 0], [-1, 0], [0, 1], [0, -1]]:
                nx = x + dx
                ny = y + dy
                if 0 <= nx < ancho and 0 <= ny < alto and fuente[nx, ny][3] > 128:
                    destino[x, y] = CONTORNO
                    break
    return salida


def _textura(img: Image.Image, colores, densidad: float, semilla: int, zona=None) -> None:
    """Salpica píxeles de pelaje/grietas sobre lo que ya es opaco."""
    azar = random.Random(semilla)
    px = img.load()
    x0, y0, x1, y1 = zona or [0, 0, img.width, img.height]
    for y in range(y0, y1):
        for x in range(x0, x1):
            if px[x, y][3] and px[x, y] not in [OJO, OJO_CENTRO, DIENTE, BOCA] and azar.random() < densidad:
                px[x, y] = azar.choice(colores)


def _tenir(img: Image.Image, color, fuerza: float) -> Image.Image:
    """Mezcla cada píxel opaco con `color` (destello de golpe)."""
    salida = img.copy()
    px = salida.load()
    for y in range(salida.height):
        for x in range(salida.width):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = (int(r + (color[0] - r) * fuerza), int(g + (color[1] - g) * fuerza),
                            int(b + (color[2] - b) * fuerza), a)
    return salida


def _oscurecer(img: Image.Image, factor: float, alfa: float = 1.0) -> Image.Image:
    salida = img.copy()
    px = salida.load()
    for y in range(salida.height):
        for x in range(salida.width):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = (int(r * factor), int(g * factor), int(b * factor), int(a * alfa))
    return salida


def _mover(img: Image.Image, dx: int = 0, dy: int = 0) -> Image.Image:
    salida = Image.new("RGBA", img.size, (0, 0, 0, 0))
    salida.alpha_composite(img.crop([max(0, -dx), max(0, -dy), img.width - max(0, dx), img.height - max(0, dy)]),
                           [max(0, dx), max(0, dy)])
    return salida


def _caido(img: Image.Image, pasos: int) -> list:
    """Cuadros de muerte: se inclina, cae de lado y se apaga."""
    cuadros = []
    for i in range(pasos):
        t = (i + 1) / pasos
        girada = img.rotate(-90 * t, resample=Image.NEAREST, center=[img.width / 2, img.height - 1])
        cuadros.append(_oscurecer(girada, 1 - 0.45 * t))
    return cuadros


#  Rata gigante (rastreador): encorvada, pelaje erizado, ojos rojos, colmillos

RATA_ANCHO = 60                    # lienzo con margen: cola a la izquierda, embestida a la derecha
RATA_ALTO = 28
_RX = 12                            # dónde va el cuerpo dentro del lienzo
_RY = 2


def _cola(d: ImageDraw.ImageDraw, ondula: float) -> None:
    """Cola larga y escamosa que nace del anca y se arrastra hacia atrás."""
    for i in range(24):
        t = i / 23
        x = _RX + 10 - t * 21
        y = _RY + 18 + t * 5 + math.sin(t * 4.2 + ondula) * 2.2 * t
        r = 2.2 - t * 1.7
        d.ellipse([x - r, y - r, x + r, y + r], fill=PIEL if i % 3 else PIEL_OSCURA)


def _rata(fase: float = 0.0, boca: float = 0.3, cola: float = 0.0, ojo: float = 1.0) -> Image.Image:
    cuerpo = Image.new("RGBA", [46, 26], (0, 0, 0, 0))
    d = ImageDraw.Draw(cuerpo)
    respira = round(math.sin(fase) * 0.8)
    # Pata trasera (anca grande).
    d.ellipse([8, 13 + respira, 20, 25], fill=PELO_OSCURO)
    d.polygon([[12, 22], [18, 22], [19, 25], [11, 25]], fill=PIEL_OSCURA)
    # Cuerpo jorobado.
    d.ellipse([7, 4 + respira, 33, 23], fill=PELO)
    d.ellipse([10, 13 + respira, 32, 23], fill=PELO_OSCURO)          # vientre en sombra
    # Cabeza baja hacia adelante, hocico largo.
    d.polygon([[27, 8 + respira], [35, 9], [43, 15], [42, 17], [33, 20], [26, 18]], fill=PELO)
    d.polygon([[30, 15], [43, 15], [42, 17], [33, 20]], fill=PELO_OSCURO)
    # Mandíbula abierta: boca roja y colmillos.
    abre = round(boca * 4)
    if abre:
        d.polygon([[33, 17], [42, 16], [41, 16 + abre], [34, 18 + abre]], fill=BOCA)
        d.polygon([[33, 18 + abre], [41, 16 + abre], [40, 18 + abre], [34, 20 + abre]], fill=PELO_OSCURO)
    for x in [36, 39]:                                                # colmillos de arriba
        d.line([x, 16, x, 18 + min(abre, 2)], fill=DIENTE)
    d.point([[41, 16], [40, 17]], fill=DIENTE_SOMBRA)
    if abre >= 2:
        d.point([[37, 17 + abre], [37, 16 + abre]], fill=DIENTE)   # colmillo de abajo
    d.point([[43, 15]], fill=PIEL)                                   # nariz
    # Oreja desgarrada.
    d.polygon([[28, 7 + respira], [30, 3 + respira], [33, 4 + respira], [32, 9 + respira]], fill=PIEL_OSCURA)
    d.point([[31, 5 + respira], [30, 6 + respira]], fill=PIEL)
    d.point([[32, 4 + respira]], fill=(0, 0, 0, 0))                  # muesca
    # Pelaje erizado en el lomo (púas).
    for i, x in enumerate(range(9, 30, 3)):
        alto = 3 if i % 2 else 2
        base = 5 + respira + abs(x - 19) // 5
        d.polygon([[x, base + 1], [x + 1, base - alto], [x + 2, base + 1]], fill=PELO_OSCURO)
    # Pata delantera con garras.
    d.polygon([[27, 18], [31, 18], [32, 24], [28, 24]], fill=PELO_OSCURO)
    d.point([[29, 25], [31, 25], [33, 25]], fill=DIENTE_SOMBRA)
    d.point([[13, 25], [15, 25], [17, 25]], fill=DIENTE_SOMBRA)
    _textura(cuerpo, [PELO_CLARO, PELO_OSCURO, PELO_PUNTA], 0.18, 7, [7, 3, 34, 20])
    d.line([19, 8 + respira, 23, 12 + respira], fill=PIEL_OSCURA)    # cicatriz
    # Ojo que brilla, con halo rojo oscuro.
    d.rectangle([34, 10, 37, 13], fill=SANGRE)
    d.rectangle([35, 11, 36, 12], fill=(int(OJO[0] * max(ojo, 0.25)), int(OJO[1] * ojo), OJO[2], 255))
    d.point([[36, 11]], fill=OJO_CENTRO)

    img = Image.new("RGBA", [RATA_ANCHO, RATA_ALTO], (0, 0, 0, 0))
    _cola(ImageDraw.Draw(img), cola)
    img.alpha_composite(cuerpo, [_RX, _RY])
    return _contornear(img)


def _boca_arriba(img: Image.Image, oscuro: float) -> Image.Image:
    """Muerta: patas arriba, apoyada en el suelo, apagándose."""
    volteada = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    caja = volteada.getbbox()
    return _oscurecer(_mover(volteada, 0, img.height - caja[3]), oscuro)


def rata() -> list:
    reposo = [_rata(fase, 0.25, cola, ojo) for fase, cola, ojo in
              [[0, 0, 1], [1.6, 0.6, 0.8], [3.1, 1.2, 1], [4.7, 0.6, 0.7]]]
    ataque = [_rata(0, 0.4), _mover(_rata(0, 0.8), 2), _mover(_rata(0, 1.0), 5),
              _mover(_rata(0, 1.0), 5), _mover(_rata(0, 0.5), 1)]
    golpe = _mover(_rata(0, 0.9, 1.5), -2)
    herida = [_tenir(golpe, (255, 255, 255), 0.7), _tenir(golpe, (200, 20, 20), 0.45), _rata(0, 0.5)]
    final = _rata(0, 1.0, 2.0, 0.0)
    muerte = [_tenir(final, (200, 20, 20), 0.4),
              final.rotate(12, resample=Image.NEAREST, center=[30, 27]),
              _boca_arriba(final, 0.8), _boca_arriba(final, 0.6)]
    return [reposo, ataque, herida, muerte]


#  Guardián óseo (guardián): esqueleto con yelmo oxidado, ojos fríos y mandoble

ESQ_ANCHO = 40
ESQ_ALTO = 42
_PIVOTE = [29, 21]                 # manos sobre la empuñadura


def _espada(d: ImageDraw.ImageDraw, angulo: float, dx: int = 0) -> None:
    """Mandoble oxidado que gira alrededor de las manos (0° = clavado hacia abajo)."""
    px = _PIVOTE[0] + dx
    py = _PIVOTE[1]
    rad = math.radians(angulo)
    ux = math.sin(rad)                             # hacia la punta
    uy = math.cos(rad)
    nx = -uy                                       # perpendicular
    ny = ux
    def punto(a, b):
        return [px + ux * a + nx * b, py + uy * a + ny * b]
    d.polygon([punto(2, -1.6), punto(17, -1.6), punto(19, 0), punto(17, 1.6), punto(2, 1.6)], fill=HIERRO)
    d.line([punto(3, 0.6), punto(17, 0.6)], fill=HIERRO_CLARO)
    for a in [7, 12]:
        d.point([punto(a, -1)], fill=OXIDO_CLARO)
    d.line([punto(1, -4), punto(1, 4)], fill=OXIDO, width=2)          # guarda
    d.line([punto(0, 0), punto(-5, 0)], fill=TELA_CLARA, width=2)     # empuñadura
    d.point([punto(-6, 0)], fill=OXIDO_CLARO)                          # pomo


def _esqueleto(capa: float = 0.0, ojo: float = 1.0, angulo: float = 0.0, dx: int = 0,
               sin_espada: bool = False) -> Image.Image:
    img = Image.new("RGBA", [ESQ_ANCHO, ESQ_ALTO], (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    o = dx
    # Capa desgarrada (detrás).
    borde = []
    for i, x in enumerate(range(6, 27, 3)):
        borde.append([x + o, 33 + (2 if (i + round(capa * 2)) % 2 else -1)])
    d.polygon([[9 + o, 12], [24 + o, 12], [27 + o, 22]] + borde[::-1] + [[5 + o, 22]], fill=TELA)
    d.line([[11 + o, 15], [9 + o, 31]], fill=TELA_CLARA)
    d.line([[22 + o, 15], [24 + o, 30]], fill=TELA_CLARA)
    # Piernas de hueso.
    for x0, x1 in [[13, 12], [19, 20]]:
        d.line([[x0 + o, 28], [x1 + o, 39]], fill=HUESO, width=2)
        d.point([[x0 + o + (x1 - x0) // 2, 33]], fill=HUESO_SOMBRA)
        d.rectangle([x1 + o - 1, 39, x1 + o + 2, 40], fill=HUESO_SOMBRA)
    # Pelvis y columna.
    d.ellipse([11 + o, 25, 21 + o, 29], fill=HUESO)
    d.ellipse([14 + o, 26, 18 + o, 28], fill=HUESO_OSCURO)
    # Caja torácica: hueco oscuro con costillas.
    d.ellipse([10 + o, 13, 22 + o, 24], fill=(24, 18, 20, 255))
    d.line([[16 + o, 12], [16 + o, 26]], fill=HUESO_SOMBRA, width=2)
    for i, y in enumerate([14, 16, 18, 20, 22]):
        media = 6 - abs(i - 1)
        d.arc([16 + o - media, y - 1, 16 + o + media, y + 2], 180, 360, fill=HUESO)
    # Hombreras oxidadas con remaches.
    d.ellipse([6 + o, 10, 13 + o, 16], fill=OXIDO)
    d.ellipse([20 + o, 10, 27 + o, 16], fill=OXIDO)
    d.point([[8 + o, 12], [25 + o, 12]], fill=OXIDO_CLARO)
    # Brazo izquierdo colgando, garra.
    d.line([[8 + o, 15], [6 + o, 22], [8 + o, 27]], fill=HUESO, width=2)
    d.point([[7 + o, 28], [9 + o, 28]], fill=HUESO_SOMBRA)
    # Cráneo con yelmo cornudo.
    d.ellipse([11 + o, 2, 22 + o, 12], fill=HUESO)
    d.line([[12 + o, 9], [12 + o, 10]], fill=HUESO_SOMBRA)                     # pómulos hundidos
    d.line([[21 + o, 9], [21 + o, 10]], fill=HUESO_SOMBRA)
    for x in [13, 18]:                                                        # cuencas profundas
        d.rectangle([x + o, 5, x + o + 2, 8], fill=(6, 8, 12, 255))
    brillo = (int(60 + 140 * ojo), int(150 + 105 * ojo), 255, 255)
    d.point([[14 + o, 7], [15 + o, 6], [18 + o, 6], [19 + o, 7]], fill=brillo)   # mirada inclinada (ceño)
    d.point([[14 + o, 6], [19 + o, 6]], fill=(30, 60, 90, 255))
    # Yelmo cornudo que baja sobre las cejas.
    d.chord([10 + o, -1, 23 + o, 11], 180, 360, fill=HIERRO)
    d.polygon([[12 + o, 5], [16 + o, 6], [17 + o, 6], [21 + o, 5], [21 + o, 4], [12 + o, 4]], fill=HIERRO)
    d.line([[10 + o, 4], [23 + o, 4]], fill=OXIDO)
    d.point([[13 + o, 2], [20 + o, 2]], fill=OXIDO_CLARO)
    d.polygon([[11 + o, 3], [6 + o, -2], [7 + o, 1], [9 + o, 4]], fill=HUESO_SOMBRA)    # cuernos
    d.polygon([[22 + o, 3], [27 + o, -2], [26 + o, 1], [24 + o, 4]], fill=HUESO_SOMBRA)
    d.point([[16 + o, 9], [17 + o, 9]], fill=(6, 8, 12, 255))                 # nariz
    d.rectangle([13 + o, 11, 20 + o, 13], fill=HUESO)                         # mandíbula colgante
    for x in range(13, 21):
        d.point([[x + o, 11 + (x % 2)]], fill=(20, 16, 18, 255))              # dientes en sierra
    d.point([[13 + o, 13], [20 + o, 13]], fill=HUESO_SOMBRA)
    # Brazo derecho hacia la empuñadura.
    d.line([[24 + o, 15], [27 + o, 19], [_PIVOTE[0] + o, _PIVOTE[1]]], fill=HUESO, width=2)
    if not sin_espada:
        _espada(d, angulo, o)
    _textura(img, [HUESO_SOMBRA], 0.06, 3, [10 + o, 2, 23 + o, 13])
    return _contornear(img)


def _pila_de_huesos(oscuro: float) -> Image.Image:
    img = Image.new("RGBA", [ESQ_ANCHO, ESQ_ALTO], (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.line([[4, 39], [34, 40]], fill=HIERRO, width=3)                     # mandoble en el suelo
    d.line([[6, 38], [6, 41]], fill=OXIDO, width=2)
    for x0, y0, x1, y1 in [[10, 36, 20, 39], [14, 38, 27, 36], [18, 40, 28, 40], [8, 40, 16, 38]]:
        d.line([[x0, y0], [x1, y1]], fill=HUESO, width=2)
    d.ellipse([21, 31, 30, 39], fill=HUESO)                               # cráneo
    d.chord([20, 30, 31, 38], 180, 360, fill=HIERRO)
    d.rectangle([23, 35, 24, 36], fill=(8, 10, 14, 255))
    d.rectangle([27, 35, 28, 36], fill=(8, 10, 14, 255))
    return _oscurecer(_contornear(img), oscuro)


def esqueleto() -> list:
    reposo = [_esqueleto(capa, ojo) for capa, ojo in [[0, 1], [1, 0.75], [0, 0.9], [1, 0.6]]]
    ataque = [_esqueleto(0, 1, -40), _esqueleto(0, 1, -150, -1), _esqueleto(0, 1, -150, 1),
              _esqueleto(0, 1, 70, 3), _esqueleto(0, 1, 20, 1)]
    golpe = _esqueleto(1, 0.5, 15, -2)
    herida = [_tenir(golpe, (255, 255, 255), 0.7), _tenir(golpe, (120, 200, 255), 0.35), _esqueleto(0, 1)]
    final = _esqueleto(1, 0.2, 30)
    muerte = [_tenir(final, (255, 255, 255), 0.5),
              _oscurecer(_mover(final.resize([ESQ_ANCHO, ESQ_ALTO - 8], Image.NEAREST)
                                .crop([0, -8, ESQ_ANCHO, ESQ_ALTO - 8]), 0, 0), 0.85),
              _pila_de_huesos(0.9), _pila_de_huesos(0.65)]
    return [reposo, ataque, herida, muerte]


#  Respaldo: espectro encapuchado (cualquier enemigo que no tenga arte propio)

ESP_ANCHO = 32
ESP_ALTO = 40
_COLORES_ESPECTRO = [
    ["rastreador", (255, 60, 40), (60, 22, 26)],
    ["errante", (120, 255, 120), (24, 44, 30)],
    ["guardián", (150, 200, 255), (28, 30, 50)],
    ["guardian", (150, 200, 255), (28, 30, 50)],
]


def _espectro(ojo_color, tela, flota: int = 0, garras: float = 0.0, brillo: float = 1.0) -> Image.Image:
    img = Image.new("RGBA", [ESP_ANCHO, ESP_ALTO], (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    y = flota
    clara = tuple(min(255, c + 22) for c in tela[:3]) + (255,)
    oscura = tuple(max(0, c - 12) for c in tela[:3]) + (255,)
    borde = []
    for i, x in enumerate(range(5, 28, 3)):
        borde.append([x, 36 + y + (3 if i % 2 else 0)])
    d.polygon([[16, 1 + y], [24, 8 + y], [27, 20 + y]] + borde[::-1] + [[5, 20 + y], [8, 8 + y]],
              fill=tela + (255,))
    d.line([[12, 12 + y], [9, 34 + y]], fill=clara)
    d.line([[20, 12 + y], [23, 33 + y]], fill=clara)
    d.ellipse([10, 5 + y, 22, 16 + y], fill=(4, 3, 6, 255))           # rostro en tinieblas
    color = tuple(int(c * brillo) for c in ojo_color) + (255,)
    for x in [13, 18]:
        d.rectangle([x, 9 + y, x + 1, 10 + y], fill=color)
    alcance = round(garras * 5)
    for lado, x in [[-1, 6], [1, 26]]:                                  # brazos y garras
        d.line([[x, 18 + y], [x + lado * (2 + alcance), 25 + y - alcance]], fill=oscura, width=4)
        punta = [x + lado * (2 + alcance), 25 + y - alcance]
        for k in [-1, 0, 1]:
            d.line([punta, [punta[0] + lado * 2, punta[1] + 2 + k]], fill=HUESO_SOMBRA)
    return _contornear(img)


def espectro(comportamiento: str = "") -> list:
    """Respaldo para tipos sin arte: el color de los ojos depende del comportamiento."""
    ojo = (200, 120, 255)          # colores RGB: PIL exige tuplas
    tela = (40, 26, 52)
    for nombre, color_ojo, color_tela in _COLORES_ESPECTRO:
        if nombre == (comportamiento or "").lower():
            ojo = color_ojo
            tela = color_tela
    reposo = [_espectro(ojo, tela, f, 0, b) for f, b in [[0, 1], [-1, 0.8], [-2, 1], [-1, 0.7]]]
    ataque = [_espectro(ojo, tela, -1, 0.3), _mover(_espectro(ojo, tela, -2, 0.8), 2),
              _mover(_espectro(ojo, tela, -2, 1.0), 3), _mover(_espectro(ojo, tela, -1, 0.6), 1)]
    golpe = _mover(_espectro(ojo, tela, 0, 0, 0.4), -2)
    herida = [_tenir(golpe, (255, 255, 255), 0.7), _tenir(golpe, (200, 20, 20), 0.4), reposo[0]]
    muerte = [_oscurecer(reposo[0], 0.9, a) for a in [0.85, 0.55, 0.3, 0.1]]
    return [reposo, ataque, herida, muerte]
