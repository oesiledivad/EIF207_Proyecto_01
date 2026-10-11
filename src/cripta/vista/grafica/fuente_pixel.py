"""Fuente pixel propia de Cripta (5x7, proporcional, con tildes y ñ).

Los glifos son datos puros: el archivo CriptaPixel.ttf se genera a partir de
ellos con `herramientas/generar_fuente.py`, y la vista usa estas mismas
tablas para medir textos sin depender de cómo cada sistema operativo dibuja
las fuentes. Así el texto ocupa exactamente lo mismo en todas las computadoras.

Celda de 11 filas: 2 para tildes de mayúsculas, 7 de cuerpo y 2 de descenso.
"""

ALTO_CELDA = 11      # filas totales de la celda
FILA_BASE = 9        # la línea base queda debajo de la fila 8 (2 + 7)
ESPACIO = 3          # ancho del espacio en píxeles
SEPARACION = 1       # píxeles entre letras

# Cuerpo de 7 filas (en minúsculas, las 2 primeras son la zona de ascendentes).
_CUERPOS: list[tuple[str, list[str]]] = [
    ("A", [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"]),
    ("B", ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."]),
    ("C", [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."]),
    ("D", ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."]),
    ("E", ["#####", "#....", "#....", "####.", "#....", "#....", "#####"]),
    ("F", ["#####", "#....", "#....", "####.", "#....", "#....", "#...."]),
    ("G", [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"]),
    ("H", ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"]),
    ("I", ["###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"]),
    ("J", ["..###", "...#.", "...#.", "...#.", "#..#.", "#..#.", ".##.."]),
    ("K", ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"]),
    ("L", ["#....", "#....", "#....", "#....", "#....", "#....", "#####"]),
    ("M", ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"]),
    ("N", ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"]),
    ("O", [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."]),
    ("P", ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."]),
    ("Q", [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"]),
    ("R", ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"]),
    ("S", [".####", "#....", "#....", ".###.", "....#", "....#", "####."]),
    ("T", ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."]),
    ("U", ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."]),
    ("V", ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."]),
    ("W", ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."]),
    ("X", ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"]),
    ("Y", ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."]),
    ("Z", ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"]),
    ("0", [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."]),
    ("1", [".#.", "##.", ".#.", ".#.", ".#.", ".#.", "###"]),
    ("2", [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"]),
    ("3", ["####.", "....#", "....#", ".###.", "....#", "....#", "####."]),
    ("4", ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."]),
    ("5", ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."]),
    ("6", ["..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."]),
    ("7", ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."]),
    ("8", [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."]),
    ("9", [".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."]),
    ("a", [".....", ".....", ".###.", "....#", ".####", "#...#", ".####"]),
    ("b", ["#....", "#....", "####.", "#...#", "#...#", "#...#", "####."]),
    ("c", [".....", ".....", ".###.", "#....", "#....", "#...#", ".###."]),
    ("d", ["....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"]),
    ("e", [".....", ".....", ".###.", "#...#", "#####", "#....", ".###."]),
    ("f", ["..##", ".#..", "###.", ".#..", ".#..", ".#..", ".#.."]),
    ("g", [".....", ".....", ".####", "#...#", "#...#", "#...#", ".####"]),
    ("h", ["#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"]),
    ("i", [".#.", "...", "##.", ".#.", ".#.", ".#.", "###"]),
    ("j", ["..#", "...", ".##", "..#", "..#", "..#", "..#"]),
    ("k", ["#...", "#...", "#..#", "#.#.", "##..", "#.#.", "#..#"]),
    ("l", ["##.", ".#.", ".#.", ".#.", ".#.", ".#.", "###"]),
    ("m", [".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#...#"]),
    ("n", [".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"]),
    ("o", [".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."]),
    ("p", [".....", ".....", "####.", "#...#", "#...#", "#...#", "####."]),
    ("q", [".....", ".....", ".####", "#...#", "#...#", "#...#", ".####"]),
    ("r", [".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."]),
    ("s", [".....", ".....", ".####", "#....", ".###.", "....#", "####."]),
    ("t", [".#..", ".#..", "###.", ".#..", ".#..", ".#.#", "..#."]),
    ("u", [".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"]),
    ("v", [".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."]),
    ("w", [".....", ".....", "#...#", "#...#", "#.#.#", "#.#.#", ".#.#."]),
    ("x", [".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"]),
    ("y", [".....", ".....", "#...#", "#...#", "#...#", "#...#", ".####"]),
    ("z", [".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"]),
    (".", [".", ".", ".", ".", ".", ".", "#"]),
    (",", ["..", "..", "..", "..", "..", ".#", ".#"]),
    (":", [".", ".", "#", ".", ".", "#", "."]),
    (";", ["..", "..", ".#", "..", "..", ".#", ".#"]),
    ("!", ["#", "#", "#", "#", "#", ".", "#"]),
    ("¡", ["#", ".", "#", "#", "#", "#", "#"]),
    ("?", [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."]),
    ("¿", ["..#..", ".....", "..#..", ".#...", "#....", "#...#", ".###."]),
    ("-", ["....", "....", "....", "####", "....", "....", "...."]),
    ("–", ["......", "......", "......", "######", "......", "......", "......"]),
    ("—", ["......", "......", "......", "######", "......", "......", "......"]),
    ("_", [".....", ".....", ".....", ".....", ".....", ".....", "#####"]),
    ("+", [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."]),
    ("=", [".....", ".....", "#####", ".....", "#####", ".....", "....."]),
    ("/", ["....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."]),
    ("(", ["..#", ".#.", "#..", "#..", "#..", ".#.", "..#"]),
    (")", ["#..", ".#.", "..#", "..#", "..#", ".#.", "#.."]),
    ("[", ["###", "#..", "#..", "#..", "#..", "#..", "###"]),
    ("]", ["###", "..#", "..#", "..#", "..#", "..#", "###"]),
    ("'", ["#", "#", ".", ".", ".", ".", "."]),
    ('"', ["#.#", "#.#", "...", "...", "...", "...", "..."]),
    ("%", ["##...", "##..#", "...#.", "..#..", ".#...", "#..##", "...##"]),
    ("#", [".#.#.", "#####", ".#.#.", ".#.#.", "#####", ".#.#.", "....."]),
    ("*", [".....", "#.#.#", ".###.", "#####", ".###.", "#.#.#", "....."]),
    ("·", [".", ".", ".", "#", ".", ".", "."]),
    ("|", ["#", "#", "#", "#", "#", "#", "#"]),
    (">", ["#...", ".#..", "..#.", "...#", "..#.", ".#..", "#..."]),
    ("<", ["...#", "..#.", ".#..", "#...", ".#..", "..#.", "...#"]),
    ("…", [".....", ".....", ".....", ".....", ".....", ".....", "#.#.#"]),
    ("°", [".#.", "#.#", ".#.", "...", "...", "...", "..."]),
    ("♥", [".....", ".#.#.", "#####", "#####", ".###.", "..#..", "....."]),
]

# Descendentes (2 filas bajo la línea base).
_DESCENSOS: list[tuple[str, list[str]]] = [
    ("g", ["....#", ".###."]), ("j", ["#.#", ".#."]), ("p", ["#....", "#...."]),
    ("q", ["....#", "....#"]), ("y", ["....#", ".###."]), (",", ["#.", ".."]),
    (";", ["#.", ".."]),
]

# Tildes: patrón de 2 filas centrado sobre la letra base.
_ACENTOS: list[tuple[str, list[str]]] = [
    ("agudo", ["..#", ".#."]), ("tilde", [".#.#", "#.#."]), ("dieresis", ["#.#", "..."]),
]
_COMPUESTOS: list[tuple[str, str, str]] = [
    ("Á", "A", "agudo"), ("É", "E", "agudo"), ("Í", "I", "agudo"), ("Ó", "O", "agudo"),
    ("Ú", "U", "agudo"), ("Ü", "U", "dieresis"), ("Ñ", "N", "tilde"),
    ("á", "a", "agudo"), ("é", "e", "agudo"), ("ó", "o", "agudo"), ("ú", "u", "agudo"),
    ("ü", "u", "dieresis"), ("ñ", "n", "tilde"), ("í", "ı", "agudo"),
]
_CUERPOS.append(("ı", ["...", "...", "##.", ".#.", ".#.", ".#.", "###"]))  # i sin punto (para í)


def _buscar(tabla: list, clave: str):
    """Búsqueda lineal en una tabla de pares; solo se usa al construir la fuente."""
    for k, valor in tabla:
        if k == clave:
            return valor
    return None


def _superponer(filas: list[str], patron: list[str], desde: int) -> list[str]:
    """Copia el patrón de tilde centrado en las filas `desde` y `desde + 1`."""
    ancho = len(filas[0])
    inicio = max(0, (ancho - len(patron[0]) + 1) // 2)
    resultado = list(filas)
    for i, fila_patron in enumerate(patron):
        fila = list(resultado[desde + i].ljust(ancho, "."))
        for j, pixel in enumerate(fila_patron):
            if pixel == "#" and inicio + j < ancho:
                fila[inicio + j] = "#"
        resultado[desde + i] = "".join(fila)
    return resultado


def _construir() -> list[tuple[str, list[str]]]:
    """Arma las celdas completas de 11 filas de cada carácter."""
    glifos: list[tuple[str, list[str]]] = []
    for caracter, cuerpo in _CUERPOS:
        ancho = len(cuerpo[0])
        vacio = "." * ancho
        descenso = _buscar(_DESCENSOS, caracter) or [vacio, vacio]
        glifos.append((caracter, [vacio, vacio] + cuerpo + descenso))
    for caracter, base, acento in _COMPUESTOS:
        celda = _buscar(glifos, base)
        # Mayúsculas: la tilde va en las 2 filas superiores; minúsculas: en la zona de ascendentes.
        celda = _superponer(celda, _buscar(_ACENTOS, acento), 0 if base.isupper() else 2)
        glifos.append((caracter, celda))
    return glifos


GLIFOS: list[tuple[str, list[str]]] = _construir()
_POR_CODIGO: list[list[str] | None] = [None] * 0x2700
for _caracter, _celda in GLIFOS:
    _POR_CODIGO[ord(_caracter)] = _celda


def engrosar(celda: list[str]) -> list[str]:
    """Versión negrita: cada píxel se extiende uno a la derecha (la celda crece 1),
    salvo que eso tape un hueco de un píxel (así la m, la w o el # siguen legibles)."""
    resultado = []
    for linea in celda:
        linea = linea + ".."
        nueva = []
        for i in range(len(linea) - 1):
            extender = i > 0 and linea[i - 1] == "#" and linea[i + 1] != "#"
            nueva.append("#" if linea[i] == "#" or extender else ".")
        resultado.append("".join(nueva))
    return resultado


def glifo(caracter: str) -> list[str]:
    """Celda del carácter; los desconocidos se muestran como '?'. Acceso O(1)."""
    codigo = ord(caracter)
    celda = _POR_CODIGO[codigo] if codigo < len(_POR_CODIGO) else None
    if celda is None:
        celda = _POR_CODIGO[ord("?")]
    return celda


def avance(caracter: str, negrita: bool = False) -> int:
    """Píxeles que avanza el cursor después del carácter."""
    if caracter == " ":
        return ESPACIO + SEPARACION + (1 if negrita else 0)
    return len(glifo(caracter)[0]) + SEPARACION + (1 if negrita else 0)


def ancho_texto(texto: str, escala: float = 1, negrita: bool = False) -> float:
    """Ancho del texto en píxeles virtuales (sin la separación final)."""
    if not texto:
        return 0
    return (sum(avance(c, negrita) for c in texto) - SEPARACION) * escala


def recortar(texto: str, ancho_max: float, escala: float = 1, negrita: bool = False) -> str:
    """Corta el texto con '…' para que no supere `ancho_max`."""
    if ancho_texto(texto, escala, negrita) <= ancho_max:
        return texto
    while texto and ancho_texto(texto + "…", escala, negrita) > ancho_max:
        texto = texto[:-1]
    return texto.rstrip() + "…"


def envolver(texto: str, ancho_max: float, escala: float = 1) -> list[str]:
    """Divide el texto en líneas que caben en `ancho_max` (por palabras)."""
    lineas: list[str] = []
    actual = ""
    for palabra in texto.split(" "):
        candidata = palabra if not actual else actual + " " + palabra
        if ancho_texto(candidata, escala) <= ancho_max:
            actual = candidata
            continue
        if actual:
            lineas.append(actual)
        # Palabra más larga que la línea: se parte por caracteres.
        while ancho_texto(palabra, escala) > ancho_max and len(palabra) > 1:
            corte = len(palabra)
            while corte > 1 and ancho_texto(palabra[:corte], escala) > ancho_max:
                corte -= 1
            lineas.append(palabra[:corte])
            palabra = palabra[corte:]
        actual = palabra
    lineas.append(actual)
    return lineas
