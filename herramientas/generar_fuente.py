"""Genera recursos/fuente/CriptaPixel.ttf a partir de grafica/fuente_pixel.py.

Solo hace falta al cambiar los glifos (requiere fontTools, no es dependencia
del juego):  uv run --with fonttools python herramientas/generar_fuente.py
"""
import importlib.util
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

RAIZ = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "fuente_pixel", RAIZ / "src" / "cripta" / "vista" / "grafica" / "fuente_pixel.py")
fp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fp)

U = 100                                   # unidades por píxel
ASCENSO = fp.FILA_BASE * U                # 900
DESCENSO = (fp.ALTO_CELDA - fp.FILA_BASE) * U


def contorno(celda):
    pen = TTGlyphPen(None)
    for fila, linea in enumerate(celda):
        y1 = (fp.FILA_BASE - fila) * U
        y0 = y1 - U
        col = 0
        while col < len(linea):
            if linea[col] != "#":
                col += 1
                continue
            inicio = col
            while col < len(linea) and linea[col] == "#":
                col += 1
            x0, x1 = inicio * U, col * U
            pen.moveTo((x0, y0)); pen.lineTo((x0, y1)); pen.lineTo((x1, y1)); pen.lineTo((x1, y0))
            pen.closePath()
    return pen.glyph()


def generar(familia, archivo, negrita):
    orden = [".notdef", "space"]
    mapa = {32: "space"}
    glifos = {".notdef": TTGlyphPen(None).glyph(), "space": TTGlyphPen(None).glyph()}
    metricas = {".notdef": 4 * U, "space": (fp.ESPACIO + fp.SEPARACION + (1 if negrita else 0)) * U}
    for caracter, celda in fp.GLIFOS:
        if negrita:
            celda = fp.engrosar(celda)
        nombre = f"uni{ord(caracter):04X}"
        orden.append(nombre)
        mapa[ord(caracter)] = nombre
        glifos[nombre] = contorno(celda)
        metricas[nombre] = (len(celda[0]) + fp.SEPARACION) * U

    fb = FontBuilder(ASCENSO + DESCENSO, isTTF=True)
    fb.setupGlyphOrder(orden)
    fb.setupCharacterMap(mapa)
    fb.setupGlyf(glifos)
    fb.setupHorizontalMetrics({n: (a, 0) for n, a in metricas.items()})
    fb.setupHorizontalHeader(ascent=ASCENSO, descent=-DESCENSO)
    fb.setupNameTable({"familyName": familia, "styleName": "Regular",
                       "copyright": "Fuente original del proyecto Cripta (EIF207, 2026).",
                       "uniqueFontIdentifier": familia.replace(" ", "") + "-Regular",
                       "fullName": familia, "psName": familia.replace(" ", "") + "-Regular"})
    fb.setupOS2(sTypoAscender=ASCENSO, sTypoDescender=-DESCENSO, sTypoLineGap=0,
                usWinAscent=ASCENSO, usWinDescent=DESCENSO, sCapHeight=7 * U, sxHeight=5 * U)
    fb.setupPost()
    destino = RAIZ / "src" / "cripta" / "vista" / "recursos" / "fuente" / archivo
    fb.save(str(destino))
    print("Fuente generada:", destino.name, destino.stat().st_size, "bytes")


generar("Cripta Pixel", "CriptaPixel.ttf", False)
generar("Cripta Pixel Negrita", "CriptaPixelNegrita.ttf", True)
