"""Carga en un hilo separado; solo la ventana aplica el resultado."""
from concurrent.futures import ThreadPoolExecutor

import arcade

from . import fuente_pixel as fp
from .lienzo import ALTO, ANCHO, ORO, ROJO, TEXTO_SUAVE


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
        v = self.window
        l = v.lienzo
        l.iniciar(v)
        r = v.escena.recursos
        cuadro = int(self.tiempo * 6)
        l.imagen(r.resplandores[int(self.tiempo * 3) % 3], ANCHO / 2 - 64, ALTO / 2 + 10, 128, 128)
        l.imagen(r.antorchas[cuadro % 4], ANCHO / 2 - 24, ALTO / 2 + 50, 48, 48)
        l.texto(self.titulo.upper(), ANCHO / 2, ALTO / 2 + 10, 3, ORO, negrita=True, ancla="centro")
        if self.error:
            l.texto(fp.recortar(self.error, ANCHO - 80), ANCHO / 2, ALTO / 2 - 20, 1, ROJO, ancla="centro")
            l.boton(ANCHO / 2 - 70, ALTO / 2 - 70, 140, 30, "REINTENTAR", "reintentar")
        else:
            l.texto("Cargando" + "." * (int(self.tiempo * 3) % 4), ANCHO / 2, ALTO / 2 - 20, 1,
                    TEXTO_SUAVE, ancla="centro")
            l.rect(ANCHO / 2 - 150, ALTO / 2 - 44, 300, 6, [40, 36, 32])
            l.rect(ANCHO / 2 - 150 + 240 * (self.tiempo % 1), ALTO / 2 - 44, 60, 6, ORO)
        l.texto(v.modo, ANCHO - 10, ALTO - 16, 1, TEXTO_SUAVE, ancla="derecha")
        l.bandas(v)
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

    def on_mouse_motion(self, x, y, dx, dy):
        self.window.raton = self.window.lienzo.a_virtual(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        """Reintenta la operación al pulsar su botón después de un error."""
        vx, vy = self.window.lienzo.a_virtual(x, y)
        if self.error and button == arcade.MOUSE_BUTTON_LEFT and any(z.contiene(vx, vy) for z in self.window.lienzo.zonas):
            self.window.cargar(self.titulo, self.operacion, self.terminado)

    def on_hide_view(self):
        """Libera el ejecutor al abandonar esta pantalla."""
        self.executor.shutdown(wait=False)
