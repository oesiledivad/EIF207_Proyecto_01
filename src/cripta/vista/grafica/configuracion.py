"""Preferencias de audio y pantalla para la sesión actual."""
import arcade

from .panel import Panel
from .lienzo import ALTO, ANCHO, ORO, TEXTO, TEXTO_SUAVE


class Configuracion(Panel):
    """Ajustes con sliders accesibles por ratón y teclado."""

    X = 158
    ANCHO_SLIDER = 330

    def __init__(self, ventana, retorno=None):
        super().__init__(ventana, "CONFIGURACIÓN", retorno=retorno)
        self._controles = [["Música", ventana.musica], ["Efectos", ventana.sonidos]]
        self._arrastrando = None
        self._foco = 0

    def on_draw(self):
        """Dibuja valores actuales, barras de volumen y botones de pantalla."""
        v = self.window
        if self.retorno is not None:
            self.retorno.on_draw()
        else:
            v.dibujar_juego(interactivo=False)
        l = v.lienzo
        l.zonas = []
        l.rect(0, 0, ANCHO, ALTO, [6, 5, 8, 190])
        l.panel(130, 58, 540, 330)
        l.texto(self.titulo, ANCHO / 2, 360, 2, ORO, ancla="centro")
        for i, control in enumerate(self._controles):
            nombre, audio = control
            y = 294 - i * 82
            color = ORO if self._foco == i else TEXTO
            l.texto(f"{nombre}: {round(audio.volumen * 100)}%", self.X, y + 27, 2, color)
            l.rect(self.X, y, self.ANCHO_SLIDER, 6, [60, 54, 48])
            l.rect(self.X, y, self.ANCHO_SLIDER * audio.volumen, 6, color)
            l.rect(self.X + self.ANCHO_SLIDER * audio.volumen - 4, y - 5, 8, 16, color)
            l.zona(self.X - 4, y - 10, self.ANCHO_SLIDER + 8, 28, "volumen", str(i),
                   "Arrastra o usa Tab y las flechas para ajustar el volumen")
            l.boton(510, y - 8, 140, 26, "SILENCIAR" if audio.activo else "ACTIVAR", "silencio", str(i))
        l.boton(self.X, 150, 492, 28,
                f"Pantalla completa: {'sí' if v.fullscreen else 'no'} [F11]", "pantalla")
        l.texto("Tab: elegir volumen · Flechas: ajustar · Inicio/Fin: 0/100%",
                self.X, 124, 1, TEXTO_SUAVE)
        l.texto("F2: efectos · F3: música", self.X, 108, 1, TEXTO_SUAVE)
        l.boton(self.X, 76, 160, 22, "VOLVER [ESC]", "volver")
        l.globo_ayuda()
        l.bandas(v)

    def _ajustar(self, x):
        """Convierte la posición virtual del cursor a un volumen limitado."""
        audio = self._controles[self._foco][1]
        audio.cambiar_volumen((x - self.X) / self.ANCHO_SLIDER)

    def on_mouse_press(self, x, y, button, modifiers):
        """Selecciona un slider o aplica un botón sin cerrar los ajustes."""
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        vx, vy = self.window.lienzo.a_virtual(x, y)
        for zona in self.window.lienzo.zonas:
            if not zona.contiene(vx, vy):
                continue
            if zona.accion == "volumen":
                self._foco = self._arrastrando = int(zona.argumento)
                self._ajustar(vx)
            elif zona.accion == "silencio":
                self._controles[int(zona.argumento)][1].alternar()
            elif zona.accion == "pantalla":
                self.window.alternar_pantalla_completa()
            else:
                return super().on_mouse_press(x, y, button, modifiers)
            return True

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """Mantiene el arrastre incluso fuera de los extremos de la barra."""
        self.on_mouse_motion(x, y, dx, dy)
        if self._arrastrando is not None and buttons & arcade.MOUSE_BUTTON_LEFT:
            self._foco = self._arrastrando
            self._ajustar(self.window.lienzo.a_virtual(x, y)[0])

    def on_mouse_release(self, x, y, button, modifiers):
        """Termina el arrastre al soltar el botón izquierdo."""
        if button == arcade.MOUSE_BUTTON_LEFT:
            self._arrastrando = None

    def on_key_press(self, symbol, modifiers):
        """Permite ajustar ambas barras sin ratón; Esc vuelve al origen."""
        audio = self._controles[self._foco][1]
        if symbol in [arcade.key.TAB, arcade.key.UP, arcade.key.DOWN]:
            self._foco = 1 - self._foco
        elif symbol in [arcade.key.LEFT, arcade.key.RIGHT]:
            audio.cambiar_volumen(audio.volumen + (0.05 if symbol == arcade.key.RIGHT else -0.05))
        elif symbol in [arcade.key.HOME, arcade.key.END]:
            audio.cambiar_volumen(0 if symbol == arcade.key.HOME else 1)
        else:
            return super().on_key_press(symbol, modifiers)
        return True
