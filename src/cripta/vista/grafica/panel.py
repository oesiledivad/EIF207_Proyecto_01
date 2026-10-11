"""Selección y ayuda gráficas; abrirlas no consume tiempo del juego."""
import arcade
from .escena import FONDO, ORO, lineas_bitacora


class Panel(arcade.View):
    """Muestra ayuda, información de sala o la confirmación para terminar."""

    def __init__(self, ventana, titulo, opciones=None, texto=""):
        """Prepara contenido informativo y botones opcionales.

        Args:
            ventana: Ventana de la partida.
            titulo: Encabezado del panel.
            opciones: Lista de pares [etiqueta, función sin argumentos].
            texto: Contenido informativo que admite desplazamiento.
        """
        super().__init__(ventana)
        self.titulo = titulo
        self.opciones = opciones or []
        self.texto = texto
        self.inicio = 0

    def on_draw(self):
        """Dibuja el contenido visible y el botón para regresar al juego."""
        self.clear(FONDO)
        e = self.window.escena
        e.texto_actual = 0
        e.zonas = []
        w, h = [self.window.width, self.window.height]
        e.texto(self.titulo, 30, h - 55, 24, ORO)
        cantidad = max(1, int((h - 160) / 40))
        for i, opcion in enumerate(self.opciones[self.inicio:self.inicio + cantidad]):
            e.boton(30, h - 115 - i * 40, w - 60, 34, opcion[0][:int((w - 80) / 7)], "elegir", str(self.inicio + i))
        if self.texto:
            for i, linea in enumerate(lineas_bitacora(self.texto.splitlines(), int((w - 60) / 8))[self.inicio:self.inicio + cantidad * 2]):
                e.texto(linea, 30, h - 95 - i * 19, 12)
        e.boton(30, 25, 180, 36, "VOLVER [ESC]", "volver")
        e.texto("Rueda: más opciones", w - 200, 38, 10)

    def on_mouse_motion(self, x, y, dx, dy):
        """Actualiza el resaltado de los botones."""
        self.window.escena.raton = [x, y]

    def on_mouse_press(self, x, y, button, modifiers):
        """Cierra el panel y ejecuta la opción elegida, mostrando posibles errores."""
        if button == arcade.MOUSE_BUTTON_LEFT:
            for zona in self.window.escena.zonas:
                if zona.contiene(x, y):
                    self.window.hide_view()
                    if zona.accion == "elegir":
                        try:
                            self.opciones[int(zona.argumento)][1]()
                        except (OSError, RuntimeError, ValueError) as error:
                            self.window.show_view(Panel(self.window, "NO SE PUDO COMPLETAR", texto=str(error)))
                    break

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        """Desplaza opciones o texto dentro de los límites del contenido."""
        cantidad = max(1, int((self.window.height - 160) / 40))
        total = len(self.opciones)
        if self.texto:
            cantidad *= 2
            total = len(lineas_bitacora(self.texto.splitlines(), int((self.window.width - 60) / 8)))
        self.inicio = max(0, min(max(0, total - cantidad), self.inicio - int(scroll_y)))

    def on_key_press(self, symbol, modifiers):
        """Cierra con Esc y consume el evento para evitar salir también del juego."""
        if symbol == arcade.key.ESCAPE:
            self.window.hide_view()
            return True
