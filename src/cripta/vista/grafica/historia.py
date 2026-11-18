"""Entrada de `historia <t>` e `historia #k` (spec 004, FR-028). No consume tiempo del juego."""
import arcade

from .lienzo import ALTO, ANCHO, ORO, TEXTO


class EntradaHistoria(arcade.View):
    """Caja de texto mínima: dígitos, `#` (o Tab), retroceso, Enter para consultar y Esc para salir."""

    ANCHO_CAJA = 460

    def __init__(self, ventana):
        super().__init__(ventana)
        self.texto = ""
        self.error = ""

    def on_draw(self):
        v = self.window
        v.dibujar_juego(interactivo=False)
        l = v.lienzo
        l.zonas = []
        l.rect(0, 0, ANCHO, ALTO, [6, 5, 8, 190])
        alto = 150
        x, y = [(ANCHO - self.ANCHO_CAJA) / 2, (ALTO - alto) / 2]
        l.panel(x, y, self.ANCHO_CAJA, alto)
        l.texto("HISTORIA DE LA PARTIDA", ANCHO / 2, y + alto - 26, 2, ORO, negrita=True, ancla="centro")
        l.texto("Instante t (número) o #k (acción k). Tab o # cambia el modo.", x + 16, y + alto - 50, 1, TEXTO)
        l.texto("Enter: consultar · Retroceso: borrar · Esc: volver", x + 16, y + alto - 64, 1, TEXTO)
        l.texto("historia " + (self.texto or "_"), x + 16, y + alto - 92, 2, ORO)
        if self.error:
            l.texto(self.error, x + 16, y + 30, 1, [220, 120, 110])
        l.boton(x + 16, y + 6, 140, 20, "VOLVER [ESC]", "volver")
        l.bandas(v)

    def on_mouse_press(self, x, y, button, modifiers):
        vx, vy = self.window.lienzo.a_virtual(x, y)
        for zona in self.window.lienzo.zonas:
            if zona.contiene(vx, vy) and zona.accion == "volver":
                self.window.hide_view()
                break

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.window.hide_view()
            return True
        if symbol in [arcade.key.ENTER, arcade.key.NUM_ENTER, arcade.key.RETURN]:
            self._consultar()
            return True
        if symbol == arcade.key.BACKSPACE:
            self.texto = self.texto[:-1]
            return True
        if symbol == arcade.key.TAB:
            self._alternar_modo()
        return True

    def on_text(self, texto):
        """Dígitos y `#` llegan como texto: así funciona con cualquier distribución de teclado."""
        for caracter in texto:
            if caracter == "#":
                self._alternar_modo()
            elif caracter.isdigit() and len(self.texto) < 12:
                self.texto += caracter
        return True

    def _alternar_modo(self):
        self.texto = self.texto[1:] if self.texto.startswith("#") else "#" + self.texto

    def _consultar(self):
        from .panel import Panel
        from cripta.controlador.LineaTiempoControlador import formatear_resumen
        resultado = self.window.controlador.historia(self.texto)
        if not resultado.ok:
            self.error = resultado.motivo
            return
        titulo = f"HISTORIA {self.texto}"
        self.window.show_view(Panel(self.window, titulo, texto=formatear_resumen(resultado.resumen)))
