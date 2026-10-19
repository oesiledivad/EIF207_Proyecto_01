"""Carga en un hilo separado; solo la ventana aplica el resultado."""
from concurrent.futures import ThreadPoolExecutor

import arcade

from cripta.adaptadores.Crypt_Data_Source import PresupuestoAgotado
from . import fuente_pixel as fp
from .lienzo import ALTO, ANCHO, ORO, ROJO, TEXTO_SUAVE


class PantallaCarga(arcade.View):
    """Mantiene la ventana activa mientras se consultan o preparan datos."""

    def __init__(self, ventana, titulo, operacion, terminado, retorno=None):
        """Prepara una operación bloqueante y su respuesta gráfica.

        Args:
            ventana: Ventana donde se mostrará la carga.
            titulo: Mensaje que identifica la operación.
            operacion: Función sin argumentos que se ejecuta en otro hilo.
            terminado: Función que recibe el resultado en el hilo gráfico.
            retorno: Vista a la que se puede regresar si falla la carga.
        """
        super().__init__(ventana)
        self.titulo = titulo
        self.operacion = operacion
        self.terminado = terminado
        self.retorno = retorno
        self.tiempo = 0
        self.error = ""
        self.reintentable = True
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
            acciones = [["REINTENTAR", "reintentar"]] if self.reintentable else []
            if self.retorno is not None:
                acciones.append(["VOLVER", "volver"])
            acciones.append(["SALIR", "salir"])
            inicio = (ANCHO - (len(acciones) * 150 - 10)) / 2
            for i, [etiqueta, accion] in enumerate(acciones):
                l.boton(inicio + i * 150, ALTO / 2 - 70, 140, 30, etiqueta, accion)
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
            self.reintentable = not isinstance(error, PresupuestoAgotado)
            return
        # Los cambios de vista y OpenGL se realizan únicamente en este hilo.
        self.terminado(resultado)

    def on_mouse_motion(self, x, y, dx, dy):
        self.window.raton = self.window.lienzo.a_virtual(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        """Permite reintentar, volver o salir una vez finalizada la operación."""
        if not self.error or button != arcade.MOUSE_BUTTON_LEFT:
            return
        vx, vy = self.window.lienzo.a_virtual(x, y)
        for zona in self.window.lienzo.zonas:
            if zona.contiene(vx, vy):
                self.ejecutar(zona.accion)
                return

    def ejecutar(self, accion):
        """Conserva la vista de retorno entre reintentos, sin reiniciar el presupuesto."""
        if not self.error:
            return
        if accion == "reintentar" and self.reintentable:
            self.window.show_view(PantallaCarga(self.window, self.titulo, self.operacion,
                                               self.terminado, self.retorno))
        elif accion == "volver" and self.retorno is not None:
            self.window.show_view(self.retorno)
        elif accion == "salir":
            self.window.on_close()

    def on_key_press(self, symbol, modifiers):
        """Esc vuelve a la vista anterior; en el arranque permite salir."""
        if symbol == arcade.key.ESCAPE:
            self.ejecutar("volver" if self.retorno is not None else "salir")
        elif symbol in [arcade.key.ENTER, arcade.key.RETURN]:
            self.ejecutar("reintentar")

    def on_hide_view(self):
        """Libera el ejecutor al abandonar esta pantalla."""
        self.executor.shutdown(wait=False)
