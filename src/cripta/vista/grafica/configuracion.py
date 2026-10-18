"""Preferencias de audio y pantalla para la sesión actual."""
import arcade

from .panel import Panel


class Configuracion(Panel):
    """Reutiliza el panel sin cerrarlo al modificar un ajuste."""

    def __init__(self, ventana, retorno=None):
        super().__init__(ventana, "CONFIGURACIÓN", retorno=retorno)

    def on_draw(self):
        """Actualiza las etiquetas también cuando se usan F2, F3 o F11."""
        v = self.window
        self.opciones = []
        for nombre, audio in [["Música", v.musica], ["Efectos", v.sonidos]]:
            self.opciones.extend([
                [f"{nombre}: {round(audio.volumen * 100)}% · bajar (-10%)",
                 lambda audio=audio: audio.cambiar_volumen(audio.volumen - 0.1)],
                [f"{nombre}: {round(audio.volumen * 100)}% · subir (+10%)",
                 lambda audio=audio: audio.cambiar_volumen(audio.volumen + 0.1)],
                [f"{nombre}: {'activados' if audio.activo else 'silenciados'} · cambiar",
                 audio.alternar],
            ])
        self.opciones.append([f"Pantalla completa: {'sí' if v.fullscreen else 'no'} · cambiar",
                              v.alternar_pantalla_completa])
        super().on_draw()

    def on_mouse_press(self, x, y, button, modifiers):
        """Aplica el ajuste inmediatamente y mantiene el panel abierto."""
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        vx, vy = self.window.lienzo.a_virtual(x, y)
        for zona in self.window.lienzo.zonas:
            if zona.contiene(vx, vy) and zona.accion == "elegir":
                self.opciones[int(zona.argumento)][1]()
                return True
        return super().on_mouse_press(x, y, button, modifiers)
