"""Jugador dibujado en código, con el equipo visible (pixel art propio).

El sprite del pack trae una espada pintada en todos los cuadros; para que se
note lo que el jugador lleva puesto, aquí se arma por capas: cuerpo, armadura,
arma en la mano (o puño si no tiene arma) y antorcha encendida en la otra mano.

`animaciones(arma, armadura, antorcha)` devuelve
[reposo, caminar, atacar, herido, muerte] mirando a la DERECHA; todas las
imágenes comparten lienzo y origen. Solo decora: no toca el modelo.
"""
import math

from PIL import Image, ImageDraw

from .monstruos import CONTORNO, _contornear, _mover, _oscurecer, _tenir

ANCHO = 36
ALTO = 32
_PIES = 31                         # fila del suelo
_CX = 14                           # centro del cuerpo

PIEL = (226, 178, 140, 255)
PIEL_SOMBRA = (176, 124, 96, 255)
PELO = (70, 44, 30, 255)
TUNICA = (64, 84, 120, 255)
TUNICA_SOMBRA = (40, 54, 84, 255)
PANTALON = (58, 50, 46, 255)
BOTA = (44, 30, 24, 255)
CUERO = (138, 86, 46, 255)
CUERO_OSCURO = (94, 56, 30, 255)
CUERO_CLARO = (176, 120, 70, 255)
HEBILLA = (232, 186, 72, 255)
ACERO = (150, 160, 176, 255)
ACERO_OSCURO = (88, 96, 112, 255)
ACERO_BRILLO = (220, 228, 240, 255)
ORO = (232, 186, 72, 255)
GEMA = (110, 200, 255, 255)
CAPA = (44, 74, 52, 255)
CAPA_OSCURA = (28, 48, 34, 255)
MALLA = (120, 124, 130, 255)
MADERA = (120, 80, 46, 255)
MADERA_OSCURA = (80, 52, 30, 255)
LLAMA = [(255, 230, 120, 255), (255, 160, 50, 255), (220, 70, 30, 255)]


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


def _arma(d: ImageDraw.ImageDraw, tipo: str, mano, angulo: float) -> None:
    """Dibuja el arma tomada en `mano`; 0° = hacia arriba, 90° = hacia adelante."""
    hx, hy = mano
    rad = math.radians(angulo)
    ux = math.sin(rad)
    uy = -math.cos(rad)

    def p(a, b=0.0):
        return [hx + ux * a - uy * b, hy + uy * a + ux * b]
    if tipo == "daga":
        d.line([p(-1), p(1)], fill=MADERA_OSCURA, width=2)
        d.line([p(1, -2), p(1, 2)], fill=ORO)
        d.polygon([p(2, -1), p(7, 0), p(2, 1)], fill=ACERO)
        d.line([p(2), p(6)], fill=ACERO_BRILLO)
    elif tipo == "espada":
        d.line([p(-2), p(1)], fill=MADERA_OSCURA, width=2)
        d.line([p(1, -3), p(1, 3)], fill=ORO, width=2)
        d.polygon([p(2, -1.2), p(12, -1.2), p(14, 0), p(12, 1.2), p(2, 1.2)], fill=ACERO)
        d.line([p(3), p(12)], fill=ACERO_BRILLO)
    elif tipo == "hacha":
        d.line([p(-3), p(11)], fill=MADERA, width=2)
        d.polygon([p(7, 0), p(6, 5), p(11, 6), p(12, 0)], fill=ACERO)
        d.line([p(7, 5), p(11, 6)], fill=ACERO_BRILLO)
    elif tipo == "lanza":
        d.line([p(-8), p(14)], fill=MADERA, width=2)
        d.polygon([p(14, -2), p(19, 0), p(14, 2)], fill=ACERO)
        d.point([p(15)], fill=ACERO_BRILLO)
    elif tipo == "baston":
        d.line([p(-6), p(12)], fill=MADERA, width=2)
        d.ellipse([p(13)[0] - 2, p(13)[1] - 2, p(13)[0] + 2, p(13)[1] + 2], fill=GEMA)
        d.point([p(13, -1)], fill=(230, 250, 255, 255))
    elif tipo == "maza":
        d.line([p(-2), p(8)], fill=MADERA, width=2)
        d.ellipse([p(10)[0] - 3, p(10)[1] - 3, p(10)[0] + 3, p(10)[1] + 3], fill=ACERO)


def _cuadro(arma="ninguna", armadura="ninguna", antorcha=False, paso=0, respira=0, golpe=0.0,
            llama=0) -> Image.Image:
    """Un cuadro del jugador. golpe: 0 = reposo, 1 = brazo/arma al máximo."""
    img = Image.new("RGBA", [ANCHO, ALTO], (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    y0 = respira
    # Capa (detrás de todo).
    if armadura == "manto":
        d.polygon([[_CX - 4, 13 + y0], [_CX + 2, 13 + y0], [_CX - 1, 28], [_CX - 8, 28 - paso]], fill=CAPA)
        d.line([[_CX - 5, 16 + y0], [_CX - 7, 27 - paso]], fill=CAPA_OSCURA)
    # Brazo de atrás (con la antorcha si está encendida).
    atras = [_CX - 7, 19 + y0] if antorcha else [_CX - 4, 20 + y0]   # la antorcha se aleja del cuerpo
    d.line([[_CX - 2, 15 + y0], atras], fill=PIEL_SOMBRA, width=2)
    if antorcha:
        d.line([[atras[0], atras[1] + 1], [atras[0] - 1, atras[1] - 7]], fill=MADERA, width=2)
        d.rectangle([atras[0] - 2, atras[1] - 9, atras[0], atras[1] - 7], fill=MADERA_OSCURA)
        for i, alto in enumerate([5, 4, 2]):
            color = LLAMA[(i + llama) % 3] if i else LLAMA[2]
            d.ellipse([atras[0] - 2 - (1 if i == 0 else 0), atras[1] - 9 - alto - (llama % 2),
                       atras[0] + (1 if i == 0 else 0), atras[1] - 9], fill=color)
    # Piernas (caminar alterna).
    for dx, adelante in [[-2, False], [2, True]]:
        avance = (paso if adelante else -paso)
        x = _CX + dx + avance
        d.line([[_CX + dx, 21 + y0], [x, 27]], fill=PANTALON, width=3)
        d.point([[x, 25]], fill=BOTA)
        d.rectangle([x - 1, 27, x + 2, _PIES], fill=BOTA)
        d.point([[x + 2, _PIES - 1]], fill=CUERO_OSCURO)
    # Torso.
    d.rectangle([_CX - 4, 13 + y0, _CX + 3, 21 + y0], fill=TUNICA)
    d.line([[_CX - 4, 13 + y0], [_CX - 4, 21 + y0]], fill=TUNICA_SOMBRA)
    if armadura == "cuero":
        d.rectangle([_CX - 4, 14 + y0, _CX + 3, 20 + y0], fill=CUERO)
        d.line([[_CX - 4, 17 + y0], [_CX + 3, 17 + y0]], fill=CUERO_OSCURO)
        d.line([[_CX - 3, 14 + y0], [_CX + 2, 19 + y0]], fill=CUERO_OSCURO)       # correa cruzada
        d.ellipse([_CX - 6, 12 + y0, _CX - 2, 16 + y0], fill=CUERO_CLARO)          # hombrera
        d.ellipse([_CX + 1, 12 + y0, _CX + 5, 16 + y0], fill=CUERO_CLARO)
    elif armadura == "placas":
        d.rectangle([_CX - 4, 13 + y0, _CX + 3, 20 + y0], fill=ACERO)
        d.line([[_CX - 4, 16 + y0], [_CX + 3, 16 + y0]], fill=ACERO_OSCURO)
        d.line([[_CX - 1, 13 + y0], [_CX - 1, 20 + y0]], fill=ACERO_BRILLO)
        d.ellipse([_CX - 7, 11 + y0, _CX - 2, 16 + y0], fill=ACERO_OSCURO)
        d.ellipse([_CX + 1, 11 + y0, _CX + 6, 16 + y0], fill=ACERO)
        d.point([[_CX + 1, 17 + y0]], fill=GEMA)
    elif armadura == "malla":
        for y in range(14, 21, 2):
            d.line([[_CX - 4, y + y0], [_CX + 3, y + y0]], fill=MALLA)
    elif armadura == "manto":
        d.polygon([[_CX - 5, 12 + y0], [_CX + 4, 12 + y0], [_CX + 2, 16 + y0], [_CX - 3, 16 + y0]], fill=CAPA)
    # Cinturón.
    d.line([[_CX - 4, 21 + y0], [_CX + 3, 21 + y0]], fill=CUERO_OSCURO if armadura != "cuero" else BOTA)
    d.point([[_CX, 21 + y0]], fill=HEBILLA)
    # Cabeza.
    d.ellipse([_CX - 3, 4 + y0, _CX + 4, 12 + y0], fill=PIEL)
    d.chord([_CX - 4, 3 + y0, _CX + 4, 10 + y0], 180, 360, fill=PELO)
    d.line([[_CX - 4, 6 + y0], [_CX - 3, 10 + y0]], fill=PELO)
    d.point([[_CX + 2, 8 + y0], [_CX + 2, 7 + y0]], fill=CONTORNO)                       # ojo
    d.point([[_CX + 4, 9 + y0]], fill=PIEL_SOMBRA)                                     # nariz
    d.line([[_CX - 2, 11 + y0], [_CX + 1, 11 + y0]], fill=PIEL_SOMBRA)                 # mandíbula
    d.point([[_CX + 2, 4 + y0], [_CX + 3, 5 + y0]], fill=PELO)                         # flequillo
    if armadura == "placas":
        d.chord([_CX - 4, 2 + y0, _CX + 5, 10 + y0], 180, 360, fill=ACERO)          # yelmo
        d.line([[_CX - 4, 6 + y0], [_CX + 5, 6 + y0]], fill=ACERO_OSCURO)
        d.point([[_CX, 2 + y0]], fill=ORO)
    elif armadura == "manto":
        d.chord([_CX - 5, 2 + y0, _CX + 4, 11 + y0], 180, 360, fill=CAPA)            # capucha
        d.line([[_CX - 5, 7 + y0], [_CX - 4, 12 + y0]], fill=CAPA)
    # Brazo de adelante: el golpe lo estira hacia el frente.
    hombro = [_CX + 2, 15 + y0]
    mano = [_CX + 3 + round(golpe * 7), 19 + y0 - round(golpe * 3)]
    d.line([hombro, mano], fill=PIEL if armadura in ["ninguna", "cuero"] else (ACERO if armadura == "placas" else TUNICA),
           width=2)
    if arma == "ninguna":
        d.rectangle([mano[0], mano[1] - 1, mano[0] + 2, mano[1] + 1], fill=PIEL)    # puño
        d.point([[mano[0] + 2, mano[1] - 1]], fill=PIEL_SOMBRA)
        if golpe > 0.9:                                                                # impacto
            for dx, dy in [[5, 0], [4, -3], [4, 3], [7, -1], [7, 2]]:
                d.point([[mano[0] + dx, mano[1] + dy]], fill=(255, 240, 180, 255))
    else:
        angulo = 20 + golpe * 95 if arma != "lanza" else 70 + golpe * 20
        _arma(d, arma, mano, angulo)
        d.rectangle([mano[0] - 1, mano[1] - 1, mano[0] + 1, mano[1] + 1], fill=PIEL)
    return _contornear(img)


def _caido(img: Image.Image) -> list:
    cuadros = []
    for i, angulo in enumerate([25, 60, 90]):
        girada = img.rotate(angulo, resample=Image.NEAREST, center=[_CX, _PIES])
        caja = girada.getbbox()
        cuadros.append(_oscurecer(_mover(girada, 0, _PIES - caja[3] if caja else 0), 1 - 0.12 * i))
    return cuadros


def animaciones(arma="ninguna", armadura="ninguna", antorcha=False) -> list:
    """[reposo, caminar, atacar, herido, muerte] del jugador con ese equipo."""
    def c(**k):
        return _cuadro(arma, armadura, antorcha, **k)
    reposo = [c(respira=0, llama=0), c(respira=0, llama=1), c(respira=1, llama=2), c(respira=0, llama=1)]
    caminar = [c(paso=p, respira=abs(p) % 2, llama=i) for i, p in enumerate([2, 0, -2, 0])]
    atacar = [c(golpe=0.0), c(golpe=-0.3), c(golpe=0.6), c(golpe=1.0), c(golpe=1.0), c(golpe=0.3)]
    base = c(golpe=-0.2)
    herido = [_tenir(_mover(base, -2), (255, 255, 255), 0.7), _tenir(_mover(base, -2), (220, 30, 30), 0.45),
              _mover(base, -1)]
    muerte = _caido(c())
    return [reposo, caminar, atacar, herido, muerte]
