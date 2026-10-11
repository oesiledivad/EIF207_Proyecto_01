"""Pantallas de resultado; reutilizan la sala y no ejecutan la simulación."""
import arcade

from .escena import ORO, ROJO, TEXTO, lineas_bitacora


class PantallaFin(arcade.View):
    """Presenta el resultado, los últimos acontecimientos y los puntajes locales."""

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
        v, p = [self.window, self.estado]
        e = v.escena
        self.clear()
        e.dibujar(v, p, v.controlador.inventario(), self.mensajes)
        ancho, alto = [v.width, v.height]
        e.bloque(0, 0, ancho, alto, [8, 7, 12, 235])
        e.zonas = []
        titulo = "HAS MUERTO" if p.derrota else "HAS ESCAPADO" if p.victoria else "FIN DE LA INCURSIÓN"
        color = ROJO if p.derrota else ORO
        tamano = min(52, ancho / 20)
        e.bloque(ancho * 0.12, alto - 110, ancho * 0.76, 2, color)
        e.texto(titulo, (ancho - len(titulo) * tamano * 0.6) / 2, alto - 90, tamano, color)
        e.texto(f"Sala {p.sala_actual_id} · {p.acciones_ejecutadas} acciones · {p.enemigos_derrotados} enemigos vencidos",
                ancho * 0.12, alto - 140, 12, TEXTO)
        contexto = ["La salida queda atrás. Has sobrevivido a la cripta."] if p.victoria else self.mensajes
        for i, linea in enumerate(lineas_bitacora(contexto, int(ancho * 0.76 / 8))[-4:]):
            e.texto(linea, ancho * 0.12, alto - 175 - i * 20, 12)
        self.tabla(ancho, alto - 265)
        e.texto((self.error or v.controlador.error_puntaje)[:int((ancho - 60) / 8)], 30, 155, 11, ROJO)
        for accion, etiqueta, y in [["reintentar", "OTRA PARTIDA [R]", 110],
                                    ["menu", "VOLVER AL MENÚ [M]", 65], ["salir", "SALIR [ESC]", 20]]:
            e.boton(ancho / 2 - 140, y, 280, 36, etiqueta, accion, color=color)
        e.texto(v.indicador_red(), ancho - 220, alto - 22, 10)

    def tabla(self, ancho, y):
        """Dibuja las filas de puntajes que caben sobre los botones.

        Args:
            ancho: Anchura de la ventana usada para distribuir columnas.
            y: Altura del encabezado de la tabla.
        """
        e = self.window.escena
        e.texto("PUNTAJES · rueda para recorrer", ancho * 0.08, y, 12, ORO)
        columnas = [["Jugador", 0, 0.22], ["Cripta", 0.22, 0.48], ["Resultado", 0.48, 0.66],
                    ["Acc.", 0.66, 0.78], ["Enem.", 0.78, 0.88], ["Tiempo", 0.88, 1]]
        cantidad = max(1, int((y - 185) / 20))
        self.limite = max(0, len(self.puntajes) - cantidad)
        self.desplazamiento = min(self.desplazamiento, self.limite)
        for titulo, inicio, fin in columnas:
            e.texto(titulo, ancho * (0.08 + inicio * 0.84), y - 22, 10, ORO)
        for i, puntaje in enumerate(self.puntajes[self.desplazamiento:self.desplazamiento + cantidad]):
            valores = [puntaje.nombre_jugador, puntaje.cripta_id, puntaje.resultado,
                       puntaje.acciones, puntaje.enemigos_derrotados, puntaje.tiempo_final]
            for valor, columna in zip(valores, columnas):
                inicio, fin = columna[1:]
                e.texto(str(valor)[:max(1, int(ancho * 0.84 * (fin - inicio) / 8) - 1)],
                        ancho * (0.08 + inicio * 0.84), y - 42 - i * 20, 10)
        if not self.puntajes:
            e.texto("Sin puntajes guardados.", ancho * 0.08, y - 42, 10)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        """Recorre los puntajes sin superar la primera o última fila disponible."""
        self.desplazamiento = max(0, min(self.limite, self.desplazamiento - int(scroll_y)))

    def ejecutar(self, accion):
        """Reintenta, vuelve al menú o cierra, mostrando errores sin perder la vista."""
        v, p = [self.window, self.estado]
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
        self.window.escena.raton = [x, y]

    def on_mouse_press(self, x, y, button, modifiers):
        """Ejecuta la acción del botón pulsado con el botón izquierdo."""
        if button == arcade.MOUSE_BUTTON_LEFT:
            for zona in self.window.escena.zonas:
                if zona.contiene(x, y):
                    self.ejecutar(zona.accion)
                    break

    def on_key_press(self, symbol, modifiers):
        """Resuelve los atajos de reintento, menú y salida."""
        for tecla, accion in [[arcade.key.R, "reintentar"], [arcade.key.M, "menu"],
                               [arcade.key.ESCAPE, "salir"]]:
            if symbol == tecla:
                self.ejecutar(accion)
                break
