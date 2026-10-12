"""Pantalla de resultado; reutiliza la sala de fondo y no ejecuta la simulación."""
import arcade

from . import fuente_pixel as fp
from .escena import lineas_bitacora
from .lienzo import ALTO, ANCHO, ORO, ROJO, TEXTO, TEXTO_SUAVE


class PantallaFin(arcade.View):
    """Presenta el resultado, los últimos acontecimientos y los puntajes locales."""

    FILAS = 7

    def __init__(self, ventana):
        """Captura el contexto final y lee la tabla de puntajes una sola vez."""
        super().__init__(ventana)
        self.estado = ventana.controlador.estado_partida()
        self.mensajes = [m.texto for m in ventana.controlador.bitacora().ultimos()
                         if m is not None and m.tipo != "sistema"][-3:]
        self.error = ""
        self.desplazamiento = 0
        self.limite = 0
        try:
            self.puntajes = ventana.controlador.puntajes()
        except (OSError, ValueError) as error:
            self.puntajes = []
            self.error = str(error)

    def on_draw(self):
        """Dibuja el resultado sobre la sala oscurecida y los controles de salida."""
        v, p = self.window, self.estado
        v.dibujar_juego(interactivo=False)
        l = v.lienzo
        l.zonas = []
        l.rect(0, 0, ANCHO, ALTO, (6, 5, 8, 215))
        titulo = "HAS MUERTO" if p.derrota else "HAS ESCAPADO" if p.victoria else "FIN DE LA INCURSIÓN"
        color = ROJO if p.derrota else ORO
        l.texto(titulo, ANCHO / 2, ALTO - 70, 5, color, negrita=True, ancla="centro", sombra=True)
        l.rect(ANCHO / 2 - 220, ALTO - 84, 440, 2, color)
        l.texto(f"Sala {p.sala_actual_id} · {p.acciones_ejecutadas} acciones · {p.enemigos_derrotados} enemigos "
                f"vencidos · t={p.reloj_virtual}", ANCHO / 2, ALTO - 102, 1, TEXTO, ancla="centro")
        contexto = ["La salida queda atrás. Has sobrevivido a la cripta."] if p.victoria else self.mensajes
        for i, linea in enumerate(lineas_bitacora(contexto, 560)[-3:]):
            l.texto(linea, ANCHO / 2, ALTO - 122 - i * 12, 1, TEXTO_SUAVE, ancla="centro")
        self.tabla(ALTO - 170)
        aviso = self.error or v.controlador.error_puntaje
        if aviso:
            l.texto(fp.recortar(aviso, ANCHO - 60), ANCHO / 2, 66, 1, ROJO, ancla="centro")
        for i, (accion, etiqueta) in enumerate([["reintentar", "OTRA PARTIDA [R]"],
                                                ["menu", "MENÚ [M]"], ["salir", "SALIR [ESC]"]]):
            l.boton(ANCHO / 2 - 300 + i * 204, 20, 192, 32, etiqueta, accion)
        l.globo_ayuda()
        l.bandas(v)

    def tabla(self, y):
        """Filas de puntajes que caben sobre los botones (rueda para recorrer)."""
        l = self.window.lienzo
        x0, ancho = 120, 560
        l.panel(x0 - 12, 80, ancho + 24, y - 66)
        l.texto("PUNTAJES", x0, y - 6, 2, ORO, negrita=True)
        l.texto("rueda para recorrer", x0 + ancho, y - 6, 1, TEXTO_SUAVE, ancla="derecha")
        columnas = [["Jugador", 0, 0.22], ["Cripta", 0.22, 0.48], ["Resultado", 0.48, 0.66],
                    ["Acc.", 0.66, 0.78], ["Enem.", 0.78, 0.88], ["Tiempo", 0.88, 1]]
        self.limite = max(0, len(self.puntajes) - self.FILAS)
        self.desplazamiento = min(self.desplazamiento, self.limite)
        for titulo, inicio, _ in columnas:
            l.texto(titulo, x0 + ancho * inicio, y - 24, 1, ORO, negrita=True)
        for i, puntaje in enumerate(self.puntajes[self.desplazamiento:self.desplazamiento + self.FILAS]):
            valores = [puntaje.nombre_jugador, puntaje.cripta_id, puntaje.resultado,
                       puntaje.acciones, puntaje.enemigos_derrotados, puntaje.tiempo_final]
            if i % 2 == 0:
                l.rect(x0 - 4, y - 42 - i * 13 - 3, ancho + 8, 13, (34, 31, 30))
            for valor, (_, inicio, fin) in zip(valores, columnas):
                l.texto(fp.recortar(str(valor), ancho * (fin - inicio) - 6), x0 + ancho * inicio, y - 40 - i * 13, 1, TEXTO)
        if not self.puntajes:
            l.texto("Sin puntajes guardados.", x0, y - 40, 1, TEXTO_SUAVE)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        """Recorre los puntajes sin superar la primera o última fila disponible."""
        self.desplazamiento = max(0, min(self.limite, self.desplazamiento - int(scroll_y)))

    def ejecutar(self, accion):
        """Reintenta, vuelve al menú o cierra, mostrando errores sin perder la vista."""
        v, p = self.window, self.estado
        try:
            if accion == "menu":
                v.volver_menu()
                if v.current_view is self:
                    self.error = v.mensaje
            elif accion == "salir":
                v.on_close()
            elif accion == "reintentar":
                v.iniciar_partida(p.nombre_jugador, str(p.semilla), p.cripta_id, self)
        except (OSError, RuntimeError, ValueError) as error:
            self.error = str(error)

    def on_mouse_motion(self, x, y, dx, dy):
        """Actualiza el resaltado de los controles finales."""
        self.window.raton = self.window.lienzo.a_virtual(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        """Ejecuta la acción del botón pulsado con el botón izquierdo."""
        if button == arcade.MOUSE_BUTTON_LEFT:
            vx, vy = self.window.lienzo.a_virtual(x, y)
            for zona in self.window.lienzo.zonas:
                if zona.contiene(vx, vy):
                    self.ejecutar(zona.accion)
                    break

    def on_key_press(self, symbol, modifiers):
        """Resuelve los atajos de reintento, menú y salida."""
        for tecla, accion in [[arcade.key.R, "reintentar"], [arcade.key.M, "menu"],
                              [arcade.key.ESCAPE, "salir"]]:
            if symbol == tecla:
                self.ejecutar(accion)
                return True
        return None
