"""Lienzo virtual de 800x450 que se escala igual en cualquier pantalla.

Todo se dibuja en coordenadas virtuales y el lienzo las convierte a píxeles
de la ventana con una sola escala (y bandas negras si la proporción no es
16:9). Así la interfaz ocupa la misma proporción en una laptop con escalado
de Windows al 150 % que en un monitor grande: nada queda "gigante" ni
diminuto. Cuando la escala es casi entera se usa la entera, para que el pixel
art se vea nítido.
"""
from dataclasses import dataclass
from pathlib import Path

import arcade

from . import fuente_pixel as fp
from .medidas import ALTO, ANCHO, calcular_escala, tamano_ventana_inicial  # noqa: F401

FONDO = [18, 17, 22]
TEXTO = [226, 214, 180]
TEXTO_SUAVE = [150, 140, 120]
ORO = [214, 170, 82]
ROJO = [196, 52, 46]
VERDE = [100, 210, 120]

_FUENTES = Path(__file__).resolve().parents[1] / "recursos" / "fuente"
_FAMILIA = "Cripta Pixel"
_FAMILIA_NEGRITA = "Cripta Pixel Negrita"
_fuentes_cargadas = False


def cargar_fuentes() -> None:
    """Registra las fuentes pixel del proyecto (una sola vez)."""
    global _fuentes_cargadas
    if not _fuentes_cargadas:
        arcade.load_font(_FUENTES / "CriptaPixel.ttf")
        arcade.load_font(_FUENTES / "CriptaPixelNegrita.ttf")
        _fuentes_cargadas = True


@dataclass
class Zona:
    """Rectángulo clickeable en coordenadas virtuales; no ejecuta nada."""
    x: float
    y: float
    ancho: float
    alto: float
    accion: str
    argumento: str = ""
    ayuda: str = ""

    def contiene(self, x, y):
        """Indica si el punto pertenece al rectángulo, incluidos sus bordes."""
        return self.x <= x <= self.x + self.ancho and self.y <= y <= self.y + self.alto


class Lienzo:
    """Convierte coordenadas virtuales a la ventana y dibuja primitivas."""

    def __init__(self):
        self.escala = 1.0
        self.ox = 0
        self.oy = 0
        self.zonas: list[Zona] = []
        self.raton = [-1.0, -1.0]          # en coordenadas virtuales
        self.textos: list = []              # etiquetas reutilizadas por posición en el cuadro
        self.texto_actual = 0
        self.ayuda = ""                     # texto emergente del elemento bajo el cursor

    #  Escala

    def ajustar(self, ancho_ventana: float, alto_ventana: float) -> None:
        """Calcula escala y márgenes para el tamaño actual de la ventana."""
        self.escala, self.ox, self.oy = calcular_escala(ancho_ventana, alto_ventana)

    def a_virtual(self, x: float, y: float) -> list[float]:
        """Ventana -> virtual (para el ratón)."""
        return [(x - self.ox) / self.escala, (y - self.oy) / self.escala]

    def a_ventana(self, x: float, y: float) -> list[float]:
        """Virtual -> ventana (útil en pruebas para simular clics)."""
        return [self.ox + x * self.escala, self.oy + y * self.escala]

    def _caja(self, x, y, ancho, alto):
        """Rectángulo virtual -> rectángulo de ventana alineado a píxeles."""
        x0 = round(self.ox + x * self.escala)
        y0 = round(self.oy + y * self.escala)
        x1 = round(self.ox + (x + ancho) * self.escala)
        y1 = round(self.oy + (y + alto) * self.escala)
        return [x0, y0, x1 - x0, y1 - y0]

    #  Cuadro

    def iniciar(self, ventana, color=FONDO) -> None:
        """Empieza un cuadro: ajusta la escala, limpia zonas y pinta el fondo."""
        self.ajustar(ventana.width, ventana.height)
        self.zonas = []
        self.texto_actual = 0
        self.ayuda = ""
        ventana.clear(color=color)

    #  Primitivas

    def rect(self, x, y, ancho, alto, color) -> None:
        x0, y0, w, h = self._caja(x, y, ancho, alto)
        if w > 0 and h > 0:
            arcade.draw_lbwh_rectangle_filled(x0, y0, w, h, color)

    def marco(self, x, y, ancho, alto, color, grosor=1) -> None:
        """Borde rectangular hacia adentro."""
        self.rect(x, y, ancho, grosor, color)
        self.rect(x, y + alto - grosor, ancho, grosor, color)
        self.rect(x, y + grosor, grosor, alto - 2 * grosor, color)
        self.rect(x + ancho - grosor, y + grosor, grosor, alto - 2 * grosor, color)

    def panel(self, x, y, ancho, alto, resaltado=False, fondo=[24, 23, 28]) -> None:
        """Caja con doble borde como en el diseño de referencia."""
        self.rect(x, y, ancho, alto, [8, 8, 10])
        self.rect(x + 1, y + 1, ancho - 2, alto - 2, ORO if resaltado else [62, 58, 52])
        self.rect(x + 2, y + 2, ancho - 4, alto - 4, [12, 12, 15])
        self.rect(x + 3, y + 3, ancho - 6, alto - 6, fondo)

    def imagen(self, textura, x, y, ancho=None, alto=None) -> None:
        """Dibuja una textura sin suavizado (pixel art nítido)."""
        ancho = textura.width if ancho is None else ancho
        alto = textura.height if alto is None else alto
        x0, y0, w, h = self._caja(x, y, ancho, alto)
        if w > 0 and h > 0:
            arcade.draw_texture_rect(textura, arcade.LBWH(x0, y0, w, h), pixelated=True)

    def elipse(self, cx, cy, ancho, alto, color, borde=0) -> None:
        x, y = self.a_ventana(cx, cy)
        if borde:
            arcade.draw_ellipse_outline(x, y, ancho * self.escala, alto * self.escala, color,
                                        max(1, borde * self.escala))
        else:
            arcade.draw_ellipse_filled(x, y, ancho * self.escala, alto * self.escala, color)

    #  Texto

    def texto(self, texto, x, y, tam=1, color=TEXTO, negrita=False, ancla="izquierda", sombra=False) -> float:
        """Escribe con la fuente pixel. `y` es la línea base; `tam` multiplica el píxel.

        Returns:
            Ancho del texto en coordenadas virtuales.
        """
        texto = str(texto)
        ancho = fp.ancho_texto(texto, tam, negrita)
        if ancla == "centro":
            x -= ancho / 2
        elif ancla == "derecha":
            x -= ancho
        if sombra:
            self._etiqueta(texto, x + tam, y - tam, tam, [10, 9, 12], negrita)
        self._etiqueta(texto, x, y, tam, color, negrita)
        return ancho

    def _etiqueta(self, texto, x, y, tam, color, negrita):
        """Reutiliza objetos arcade.Text (crearlos en cada cuadro es lento)."""
        vx = round(self.ox + x * self.escala)
        vy = round(self.oy + y * self.escala)
        # Una fila de la fuente = tam píxeles virtuales; la celda mide 11 filas.
        # arcade usa puntos a 96 ppp: px = pt * 96 / 72.
        puntos = fp.ALTO_CELDA * tam * self.escala * 72 / 96
        familia = _FAMILIA_NEGRITA if negrita else _FAMILIA
        if self.texto_actual == len(self.textos):
            self.textos.append(arcade.Text(texto, vx, vy, color, puntos, font_name=familia))
        etiqueta = self.textos[self.texto_actual]
        try:
            for atributo, valor in [["text", texto], ["x", vx], ["y", vy], ["font_size", puntos],
                                    ["font_name", familia], ["color", color]]:
                actual = getattr(etiqueta, atributo)
                if atributo == "color":
                    actual = list(actual)[:len(color)]
                    valor = list(valor)
                if actual != valor:
                    setattr(etiqueta, atributo, valor)
        except (AttributeError, TypeError):
            # Por si alguna versión de arcade no permite cambiar una propiedad: se recrea.
            etiqueta = arcade.Text(texto, vx, vy, color, puntos, font_name=familia)
            self.textos[self.texto_actual] = etiqueta
        etiqueta.draw()
        self.texto_actual += 1

    #  Interacción

    def zona(self, x, y, ancho, alto, accion, argumento="", ayuda="") -> Zona:
        """Registra un área clickeable; si el cursor está encima, guarda su ayuda."""
        zona = Zona(x, y, ancho, alto, accion, argumento, ayuda)
        self.zonas.append(zona)
        if ayuda and zona.contiene(*self.raton):
            self.ayuda = ayuda
        return zona

    def bajo_raton(self, x, y, ancho, alto) -> bool:
        return x <= self.raton[0] <= x + ancho and y <= self.raton[1] <= y + alto

    def boton(self, x, y, ancho, alto, etiqueta, accion, argumento="", icono=None, activo=False,
              tam=1, ayuda="", color=TEXTO, negrita=True) -> Zona:
        """Botón con borde doble, icono opcional y resaltado al pasar el cursor."""
        encima = self.bajo_raton(x, y, ancho, alto)
        self.panel(x, y, ancho, alto, resaltado=encima or activo,
                   fondo=[44, 38, 30] if (encima or activo) else [28, 27, 32])
        margen = 0
        if icono is not None:
            lado = min(alto - 10, icono.height * 2)
            escala_icono = lado / icono.height
            ancho_icono = icono.width * escala_icono
            if etiqueta:
                self.imagen(icono, x + 9, y + (alto - lado) / 2, ancho_icono, lado)
                margen = ancho_icono + 6
            else:
                self.imagen(icono, x + (ancho - ancho_icono) / 2, y + (alto - lado) / 2, ancho_icono, lado)
        if etiqueta:
            alto_letra = 7 * tam
            relleno = 4 if tam == 1 else 7
            disponible = ancho - margen - 2 * relleno
            etiqueta = fp.recortar(etiqueta, disponible, tam, negrita)
            ancho_texto = fp.ancho_texto(etiqueta, tam, negrita)
            inicio = x + margen + relleno + max(0, (disponible - ancho_texto) / 2) if icono is not None else \
                x + (ancho - ancho_texto) / 2
            self.texto(etiqueta, inicio, y + (alto - alto_letra) / 2, tam,
                       ORO if (encima or activo) else color, negrita=negrita)
        return self.zona(x, y, ancho, alto, accion, argumento, ayuda)

    def globo_ayuda(self) -> None:
        """Dibuja el texto emergente del elemento bajo el cursor (al final del cuadro)."""
        if not self.ayuda:
            return
        ancho = fp.ancho_texto(self.ayuda) + 10
        x = min(ANCHO - ancho - 2, max(2, self.raton[0] + 10))
        y = min(ALTO - 18, max(2, self.raton[1] + 12))
        self.rect(x, y, ancho, 15, [8, 8, 10])
        self.rect(x + 1, y + 1, ancho - 2, 13, [36, 33, 30])
        self.texto(self.ayuda, x + 5, y + 4, 1, TEXTO)

    def bandas(self, ventana) -> None:
        """Cubre lo que quede fuera del lienzo (cuando la ventana no es 16:9)."""
        ancho_lienzo = ANCHO * self.escala
        alto_lienzo = ALTO * self.escala
        if self.ox > 0:
            arcade.draw_lbwh_rectangle_filled(0, 0, self.ox, ventana.height, [0, 0, 0])
            arcade.draw_lbwh_rectangle_filled(self.ox + ancho_lienzo, 0, ventana.width, ventana.height, [0, 0, 0])
        if self.oy > 0:
            arcade.draw_lbwh_rectangle_filled(0, 0, ventana.width, self.oy, [0, 0, 0])
            arcade.draw_lbwh_rectangle_filled(0, self.oy + alto_lienzo, ventana.width, ventana.height, [0, 0, 0])
