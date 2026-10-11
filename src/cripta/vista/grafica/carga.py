"""Carga en un hilo separado; solo la ventana aplica el resultado."""
from concurrent.futures import ThreadPoolExecutor

import arcade
from .escena import FONDO, ORO, ROJO


class PantallaCarga(arcade.View):
    """Mantiene la ventana activa mientras se consultan o preparan datos."""

    def __init__(self, ventana, titulo, operacion, terminado):
        """Prepara una operación bloqueante y su respuesta gráfica.

        Args:
            ventana: Ventana donde se mostrará la carga.
            titulo: Mensaje que identifica la operación.
            operacion: Función sin argumentos que se ejecuta en otro hilo.
            terminado: Función que recibe el resultado en el hilo gráfico.
        """
        super().__init__(ventana)
        self.titulo = titulo
        self.operacion = operacion
        self.terminado = terminado
        self.tiempo = 0
        self.error = ""
        self.dibujada = False
        self.futuro = None
        self.executor = ThreadPoolExecutor(max_workers=1)

    def on_draw(self):
        """Dibuja el progreso indeterminado o el error con opción de reintento."""
        self.clear(FONDO)
        e = self.window.escena
        e.texto_actual = 0
        e.zonas = []
        w, h = [self.window.width, self.window.height]
        e.texto(self.titulo, 40, h / 2 + 45, 24, ORO)
        e.texto(self.error[:int((w - 80) / 8)] if self.error else "Cargando" + "." * (int(self.tiempo * 3) % 4),
                40, h / 2, 12, ROJO if self.error else ORO)
        if self.error:
            e.boton(40, 40, 160, 40, "REINTENTAR", "reintentar")
        else:
            e.bloque(40, h / 2 - 30, w - 80, 4, [55, 49, 40])
            e.bloque(40 + (w - 160) * (self.tiempo % 1), h / 2 - 30, 80, 4, ORO)
        e.texto(self.window.modo, w - 100, h - 25, 10)
        self.dibujada = True

    def on_update(self, delta_time):
        """Avanza la animación y entrega el resultado sin bloquear la ventana."""
        self.tiempo += delta_time
        if self.futuro is None:
            # Primero se muestra un cuadro de carga; después comienza el trabajo.
            if self.dibujada:
                self.futuro = self.executor.submit(self.operacion)
            return
        if not self.futuro.done() or self.error:
            return
        self.executor.shutdown(wait=False)
        try:
            resultado = self.futuro.result()
        except (OSError, RuntimeError, ValueError) as error:
            self.error = str(error)
            return
        # Los cambios de vista y OpenGL se realizan únicamente en este hilo.
        self.terminado(resultado)

    def on_mouse_press(self, x, y, button, modifiers):
        """Reintenta la operación al pulsar su botón después de un error."""
        if self.error and button == arcade.MOUSE_BUTTON_LEFT and any(z.contiene(x, y) for z in self.window.escena.zonas):
            self.window.cargar(self.titulo, self.operacion, self.terminado)

    def on_hide_view(self):
        """Libera el ejecutor al abandonar esta pantalla."""
        self.executor.shutdown(wait=False)
