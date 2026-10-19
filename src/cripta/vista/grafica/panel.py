"""Ventanas emergentes (ayuda, sala, menú, confirmación); no consumen tiempo del juego."""
import arcade

from .escena import lineas_bitacora
from . import fuente_pixel as fp
from .lienzo import ALTO, ANCHO, ORO, TEXTO


class Panel(arcade.View):
    """Caja centrada sobre la partida oscurecida, con texto u opciones."""

    ANCHO_CAJA = 460

    def __init__(self, ventana, titulo, opciones=None, texto="", retorno=None):
        """Prepara contenido informativo y botones opcionales.

        Args:
            ventana: Ventana de la partida.
            titulo: Encabezado del panel.
            opciones: Lista de pares [etiqueta, función sin argumentos].
            texto: Contenido informativo que admite desplazamiento.
            retorno: Pantalla a la que se regresa al cerrar; None vuelve al juego.
        """
        super().__init__(ventana)
        self.titulo = titulo
        self.opciones = opciones or []
        self.texto = texto
        self.inicio = 0
        self.retorno = retorno

    def _lineas(self):
        return lineas_bitacora(self.texto.splitlines(), self.ANCHO_CAJA - 32) if self.texto else []

    def _capacidad(self):
        return 9 if self.opciones else 18

    def on_draw(self):
        """Dibuja la partida de fondo, la caja y el botón para regresar."""
        v = self.window
        if self.retorno is not None:
            self.retorno.on_draw()
        else:
            v.dibujar_juego(interactivo=False)
        l = v.lienzo
        l.zonas = []
        l.rect(0, 0, ANCHO, ALTO, [6, 5, 8, 190])
        filas = min(self._capacidad(), max(1, len(self.opciones) or len(self._lineas())))
        alto_contenido = filas * (30 if self.opciones else 12)
        alto = 78 + alto_contenido
        x, y = [(ANCHO - self.ANCHO_CAJA) / 2, (ALTO - alto) / 2 + 10]
        l.panel(x, y, self.ANCHO_CAJA, alto)
        l.texto(self.titulo, ANCHO / 2, y + alto - 26, 2, ORO, negrita=True, ancla="centro")
        l.rect(x + 16, y + alto - 34, self.ANCHO_CAJA - 32, 2, [70, 64, 56])
        arriba = y + alto - 46
        for i, opcion in enumerate(self.opciones[self.inicio:self.inicio + self._capacidad()]):
            l.boton(x + 16, arriba - (i + 1) * 30 + 4, self.ANCHO_CAJA - 32, 26,
                    fp.recortar(opcion[0], self.ANCHO_CAJA - 48), "elegir", str(self.inicio + i),
                    ayuda=fp.recortar(opcion[0], ANCHO - 30))
        for i, linea in enumerate(self._lineas()[self.inicio:self.inicio + self._capacidad()]):
            l.texto(linea, x + 16, arriba - 10 - i * 12, 1, TEXTO)
        l.boton(x + 16, y + 10, 140, 22, "VOLVER [ESC]", "volver")
        if len(self.opciones) > self._capacidad() or len(self._lineas()) > self._capacidad():
            l.texto("rueda: más", x + self.ANCHO_CAJA - 16, y + 17, 1, [150, 140, 120], ancla="derecha")
        l.globo_ayuda()
        l.bandas(v)

    def on_mouse_motion(self, x, y, dx, dy):
        """Actualiza el resaltado de los botones."""
        self.window.raton = self.window.lienzo.a_virtual(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        """Cierra el panel y ejecuta la opción elegida, mostrando posibles errores."""
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        vx, vy = self.window.lienzo.a_virtual(x, y)
        for zona in self.window.lienzo.zonas:
            if zona.contiene(vx, vy):
                self.window.show_view(self.retorno) if self.retorno is not None else self.window.hide_view()
                if zona.accion == "elegir":
                    try:
                        self.opciones[int(zona.argumento)][1]()
                    except (OSError, RuntimeError, ValueError) as error:
                        self.window.show_view(Panel(self.window, "NO SE PUDO COMPLETAR", texto=str(error)))
                break

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        """Desplaza opciones o texto dentro de los límites del contenido."""
        total = len(self.opciones) or len(self._lineas())
        self.inicio = max(0, min(max(0, total - self._capacidad()), self.inicio - int(scroll_y)))

    def on_key_press(self, symbol, modifiers):
        """Cierra con Esc y consume el evento para evitar salir también del juego."""
        if symbol == arcade.key.ESCAPE:
            self.window.show_view(self.retorno) if self.retorno is not None else self.window.hide_view()
            return True
        return None

