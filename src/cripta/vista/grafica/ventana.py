"""Ventana y entrada del usuario; delega acciones a Aplicacion."""
import sys
from time import monotonic

import arcade

from .escena import Escena, PANEL_X, FONDO
from .lienzo import Lienzo, cargar_fuentes, tamano_ventana_inicial
from .recursos import Recursos
from .sonidos import Sonidos


def _tamano_inicial():
    """Tamaño proporcional a la pantalla de cada computadora (16:9)."""
    try:
        ancho, alto = arcade.get_display_size()
    except Exception:   # sin pantalla detectable (pruebas, escritorio remoto)
        ancho, alto = 1280, 720
    return tamano_ventana_inicial(ancho, alto)


class VentanaCripta(arcade.Window):
    """Traduce la entrada del usuario en acciones y conserva efectos visuales."""

    def __init__(self, controlador, visible=True, offline=True, tamano=None):
        """Prepara la ventana, los recursos y el estado exclusivo de la vista.

        Args:
            controlador: Aplicación que ejecuta las reglas y guarda la partida.
            visible: Permite ocultar la ventana durante las pruebas.
            offline: Indica el modo mostrado en la barra de conexión.
            tamano: [ancho, alto] fijo; por defecto se calcula según la pantalla.
        """
        ancho, alto = tamano or _tamano_inicial()
        super().__init__(ancho, alto, "Cripta", resizable=True, visible=visible, antialiasing=False)
        cargar_fuentes()
        self.controlador = controlador
        self.modo = "OFFLINE" if offline else "EN RED"
        self.animacion = 0.0
        self.pausa_visual = 0.0
        self.duracion_visual = 0.65
        self.enemigos_muertos = []
        self.accion_visual = ""
        self.enemigo = ""
        self.ultimo_click = None
        self.item = ""
        self.criterio = "real"
        self.modo_mover = False
        self.mensaje = "Haz clic en una puerta, un enemigo o un objeto."
        self.zonas = []
        self.bitacora_desplazamiento = 0
        self.bitacora_limite = 0
        self.inventario_fondo = 0
        self.atacantes = []
        self.dano_visual = 0
        self.cambio_vida = 0
        self.cambios_enemigos = []
        self.set_minimum_size(640, 360)
        self.background_color = FONDO
        self.lienzo = Lienzo()
        self.escena = Escena(Recursos(), self.lienzo)
        self.sonidos = Sonidos(activo=visible)   # en las pruebas (ventana oculta) no suena

    @property
    def raton(self):
        """Cursor en coordenadas virtuales (las mismas que las zonas)."""
        return self.lienzo.raton

    @raton.setter
    def raton(self, valor):
        self.lienzo.raton = list(valor)

    def dibujar_juego(self, interactivo=True):
        """Dibuja la partida en el lienzo (también lo usan los paneles como fondo)."""
        self.lienzo.iniciar(self)
        self.escena.dibujar(
            self, self.controlador.estado_partida(), self.controlador.inventario(),
            [m.texto for m in self.controlador.bitacora().ultimos() if m is not None],
            interactivo=interactivo,
        )

    def on_draw(self):
        """Dibuja el juego cuando ninguna pantalla independiente está activa."""
        if self.current_view is not None:
            return
        self.dibujar_juego()
        self.zonas = self.lienzo.zonas
        self.lienzo.globo_ayuda()
        self.lienzo.bandas(self)

    def volver_menu(self):
        """Termina la partida y carga la selección sin cerrar la ventana."""
        from .menu import MenuPrincipal
        p = self.controlador.estado_partida()
        try:
            self.controlador.terminar()
            menu = MenuPrincipal(self, p.cripta_id, p.nombre_jugador)
            self.cargar("Buscando criptas", menu.cargar, lambda _: self.show_view(menu))
        except (OSError, RuntimeError, ValueError) as error:
            self.mensaje = str(error)

    def preparar_partida(self):
        """Limpia selecciones y animaciones antes de mostrar una nueva partida."""
        self.ultimo_click = None
        self.enemigo = self.item = self.accion_visual = ""
        self.atacantes = self.cambios_enemigos = []
        self.dano_visual = self.cambio_vida = self.pausa_visual = 0
        self.duracion_visual = 0.65
        self.enemigos_muertos = []
        self.bitacora_desplazamiento = 0
        self.modo_mover = False
        self.mensaje = "Haz clic en una puerta, un enemigo o un objeto."

    def cargar(self, titulo, operacion, terminado):
        """Muestra una carga antes de ejecutar trabajo bloqueante.

        Args:
            titulo: Mensaje visible mientras se prepara el resultado.
            operacion: Función sin argumentos ejecutada en otro hilo.
            terminado: Función que recibe el resultado en el hilo gráfico.
        """
        from .carga import PantallaCarga
        self.show_view(PantallaCarga(self, titulo, operacion, terminado))

    def indicador_red(self):
        """Devuelve el modo y las solicitudes usadas frente al presupuesto."""
        p = self.controlador.estado_partida()
        return f"{self.modo} · RED {self.controlador.solicitudes_usadas()}/{p.presupuesto_solicitudes}"

    def iniciar_partida(self, nombre, semilla, cripta_id, retorno):
        """Inicia con pantalla de carga y regresa al origen si la validación falla."""
        def terminado(resultado):
            """Aplica el resultado del inicio y cambia la pantalla desde la ventana."""
            if resultado.ok:
                self.preparar_partida()
                self.hide_view()
            else:
                retorno.error = resultado.motivo
                self.show_view(retorno)
        self.cargar("Preparando incursión", lambda: self.controlador.iniciar_partida(nombre, semilla, cripta_id), terminado)

    def ejecutar(self, accion, argumento=""):
        """Resuelve una interacción y registra cambios para animarlos después.

        Args:
            accion: Nombre de la interacción o acción del controlador.
            argumento: Identificador de entidad o dirección, según la acción.
        """
        if accion != "seleccionar":
            self.ultimo_click = None
        if self.pausa_visual:
            return
        if accion == "modo_mover":
            self.modo_mover = not self.modo_mover
            self.mensaje = ("Elige una puerta abierta (clic o flechas)." if self.modo_mover
                            else "Haz clic en una puerta, un enemigo o un objeto.")
            return
        if accion in ["mover", "abrir", "mover_mapa"]:
            self.modo_mover = False
        if accion == "mover_mapa":
            vecina = next((v for v in self.controlador.estado_partida().vecindad if v.direccion == argumento), None)
            if vecina is None or vecina.cerrada or not vecina.transitable:
                self.mensaje = "Puerta cerrada: ábrela antes de moverte."
                return
            accion = "mover"
        if accion == "ordenar":
            criterios = ["real", "peso", "valor", "nombre"]
            self.criterio = criterios[(criterios.index(self.criterio) + 1) % 4]
            return
        if accion in ["ayuda", "terminar", "informacion", "menu"]:
            self.abrir_panel(accion)
            return
        if accion == "seleccionar_item":
            self.item = argumento
            return
        if accion == "seleccionar":
            self.enemigo = argumento
            enemigo = next((e for e in self.controlador.estado_partida().enemigos if e.id == argumento), None)
            self.mensaje = (f"{enemigo.nombre} ({enemigo.id}) · doble clic o A para atacar" if enemigo
                            else "Enemigo ausente.")
            return
        if accion in ["mover", "abrir", "recoger"] and not argumento:
            argumento = next((z.argumento for z in self.zonas if z.contiene(*self.raton)
                              and z.accion in (["recoger"] if accion == "recoger" else ["mover", "abrir", "mover_mapa"])), "")
            if not argumento:
                self.mensaje = "Apunta al objeto o a la puerta con el cursor."
                return
        if accion == "atacar" and not self.enemigo:
            self.mensaje = "Selecciona un enemigo con un clic y pulsa A."
            return
        try:
            antes = self.controlador.estado_partida()
            sala_antes = antes.sala_actual_id
            self.escena.distribucion.preparar(antes)
            enemigos_antes = list(antes.enemigos)
            vida_antes = antes.jugador_vida
            vidas_enemigos = [[e.id, e.vida] for e in enemigos_antes]
            mensajes_antes = self.controlador.bitacora().ultimos()
            if accion == "atacar":
                resultado = self.controlador.atacar(self.enemigo)
            elif accion == "esperar":
                resultado = self.controlador.esperar()
            elif accion == "retroceder":
                resultado = self.controlador.usar_pergamino()
            elif accion == "mover":
                resultado = self.controlador.mover(argumento)
            elif accion == "abrir":
                resultado = self.controlador.abrir(argumento)
            elif accion == "recoger":
                resultado = self.controlador.recoger(argumento)
            elif accion in ["usar", "equipar", "soltar"]:
                if not self.controlador.inventario().buscar_por_id(self.item):
                    self.mensaje = "Selecciona un objeto del inventario con un clic o Tab."
                    return
                resultado = getattr(self.controlador, accion)(self.item)
            else:
                return
            self.mensaje = "" if resultado.ok else resultado.motivo
            if resultado.ok:
                self.accion_visual = accion
                despues = self.controlador.estado_partida()
                self.dano_visual = max(0, vida_antes - despues.jugador_vida)
                self.cambio_vida = despues.jugador_vida - vida_antes
                self.cambios_enemigos = [[id_, next((e.vida for e in despues.enemigos if e.id == id_), 0) - vida]
                                         for id_, vida in vidas_enemigos] if sala_antes == despues.sala_actual_id else []
                # El motor elimina al enemigo; la vista conserva su figura hasta animar la muerte.
                self.enemigos_muertos = [e for e in enemigos_antes
                                         if not any(vivo.id == e.id for vivo in despues.enemigos)] if sala_antes == despues.sala_actual_id else []
                nuevos = [m for m in self.controlador.bitacora().ultimos()
                          if m is not None and not any(m is anterior for anterior in mensajes_antes)]
                self.atacantes = [e.id for e in enemigos_antes + despues.enemigos
                                  if any(m.texto.startswith(f"{e.nombre} ({e.id}) te ataca por ")
                                         or m.texto.startswith(f"{e.nombre} te ataca por ") for m in nuevos)]
                self.duracion_visual = 1.2 if despues.derrota or self.enemigos_muertos else 0.65
                self.pausa_visual = self.duracion_visual if accion == "atacar" or self.atacantes or self.cambio_vida else 0.18
                self.bitacora_desplazamiento = 0
            self._sonar(accion, resultado.ok)
        except (OSError, RuntimeError, ValueError) as error:
            self.mensaje = str(error)

    def _sonar(self, accion, ok):
        """Elige el efecto según lo que pasó en la acción (solo lee el estado)."""
        if not ok:
            self.sonidos.tocar("error")
            return
        p = self.controlador.estado_partida()
        if p.derrota:
            self.sonidos.tocar("derrota")
            return
        if p.victoria:
            self.sonidos.tocar("victoria")
            return
        if self.enemigos_muertos:
            self.sonidos.tocar("muerte_enemigo")
        else:
            for nombre, efecto in [["mover", "portal"], ["atacar", "golpe"], ["abrir", "puerta"], ["recoger", "recoger"],
                                   ["usar", "usar"], ["retroceder", "retroceso"]]:
                if accion == nombre:
                    self.sonidos.tocar(efecto)
                    break
        if self.cambio_vida < 0:
            self.sonidos.tocar("herido")

    def abrir_panel(self, accion):
        """Muestra información, ayuda, menú o confirmación sin consumir tiempo virtual."""
        from .panel import Panel
        p = self.controlador.estado_partida()
        if accion == "informacion":
            sala = next((s for s in p.salas_conocidas if s.id == p.sala_actual_id), None)
            lineas = [f"{p.sala_actual_nombre}" + (f": {sala.descripcion}" if sala and sala.descripcion else ""),
                      f"Ataque {p.jugador_ataque} · Defensa {p.jugador_defensa} · Velocidad {p.jugador_velocidad}"]
            lineas += [f"{v.direccion}: {v.nombre} · {'cerrada' if v.cerrada else 'abierta'}"
                       + (f" · llave {v.llave}" if v.llave else "") for v in p.vecindad]
            lineas += [f"Trampa {t.tipo}: {'activa' if t.activa else 'inactiva'} · daño {t.dano}" for t in p.trampas]
            lineas += p.efectos or ["Sin efectos activos."]
            item = self.controlador.inventario().buscar_por_id(self.item)
            if item:
                lineas.append(f"{item.nombre} · peso {item.peso} · valor {item.valor} · "
                              f"{'equipado' if item.equipado else 'sin equipar'}")
            self.show_view(Panel(self, f"SALA {p.sala_actual_id}", texto="\n".join(lineas)))
            return
        if accion == "ayuda":
            texto = ("Clic en una puerta: abrir o moverse · Flechas: moverse\n"
                     "Clic en un enemigo: seleccionar · Doble clic o A: atacar\n"
                     "Clic en un objeto del suelo: recoger · M/O/R: mover/abrir/recoger bajo el cursor\n"
                     ". : esperar · P: pergamino de retroceso\n"
                     "Tab: siguiente objeto · U: usar · E: equipar · S/D: soltar\n"
                     "Alt+P/V/N/R: ordenar el inventario por peso/valor/nombre/real\n"
                     "I: información de la sala · Q: terminar · Esc: menú · F11: pantalla completa · F2: sonido\n"
                     "Minimapa: dorado = salida, rojo = cerrada.")
            self.show_view(Panel(self, "AYUDA", texto=texto))
            return
        if accion == "terminar":
            self.show_view(Panel(self, "¿TERMINAR LA PARTIDA?", [["Sí, terminar la partida", self.controlador.terminar]]))
            return
        if accion == "menu":
            self.show_view(Panel(self, "MENÚ", [
                ["Continuar", lambda: None],
                ["Información de la sala (I)", lambda: self.abrir_panel("informacion")],
                ["Guardar partida", self.guardar_partida],                 # <- NUEVA
                ["Cargar partida guardada", self.cargar_partida],
                ["Ayuda y controles", lambda: self.abrir_panel("ayuda")],
                ["Pantalla completa (F11)", self.alternar_pantalla_completa],
                ["Terminar la partida", lambda: self.abrir_panel("terminar")],
                ["Volver al menú principal", self.volver_menu],
            ]))

    def guardar_partida(self):
        """Guarda la partida activa; no consume tiempo virtual."""
        resultado = self.controlador.guardar()
        self.mensaje = resultado.motivo or "Partida guardada."
        self.sonidos.tocar("recoger" if resultado.ok else "error")

    def cargar_partida(self):
        """Reemplaza la partida por la guardada, con pantalla de carga (reconstruye desde la red o la caché)."""
        def terminado(resultado):
            """Aplica el resultado en el hilo gráfico y vuelve a la partida."""
            self.hide_view()
            if resultado.ok:
                self.preparar_partida()
                self.mensaje = "Partida cargada."
            else:
                self.mensaje = resultado.motivo
                self.sonidos.tocar("error")
        self.cargar("Cargando partida", self.controlador.cargar, terminado)


    def alternar_pantalla_completa(self):
        self.set_fullscreen(not self.fullscreen)

    def on_update(self, delta_time):
        """Avanza solo las animaciones y muestra el resultado cuando terminan."""
        self.animacion += delta_time
        self.pausa_visual = max(0, self.pausa_visual - delta_time)
        if self.current_view is None and self.controlador.estado_partida().terminada and not self.pausa_visual:
            from .fin import PantallaFin
            self.show_view(PantallaFin(self))

    def on_mouse_press(self, x, y, button, modifiers):
        """Ejecuta un clic; dos clics rápidos en el mismo enemigo realizan un ataque."""
        anterior = self.ultimo_click
        self.ultimo_click = None
        if self.current_view is not None or self.pausa_visual:
            return
        self.raton = self.lienzo.a_virtual(x, y)
        if button == arcade.MOUSE_BUTTON_LEFT:
            for zona in reversed(self.zonas):     # lo dibujado al final queda encima
                if zona.contiene(*self.raton):
                    self.ejecutar(zona.accion, zona.argumento)
                    if zona.accion == "seleccionar":
                        ahora = monotonic()
                        if anterior and anterior[0] == zona.argumento and 0 <= ahora - anterior[1] <= 0.35:
                            self.ejecutar("atacar")
                        else:
                            self.ultimo_click = [zona.argumento, ahora]
                    break

    def on_mouse_motion(self, x, y, dx, dy):
        """Guarda el cursor (virtual) para resaltados y acciones bajo el cursor."""
        self.raton = self.lienzo.a_virtual(x, y)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        """Recorre la bitácora cuando el cursor está sobre el panel lateral."""
        if self.current_view is not None:
            return
        vx, _ = self.lienzo.a_virtual(x, y)
        if vx >= PANEL_X:
            self.bitacora_desplazamiento = max(0, min(self.bitacora_limite,
                                                      self.bitacora_desplazamiento + int(scroll_y)))

    def on_key_press(self, symbol, modifiers):
        """Resuelve atajos, orden visual, navegación y confirmación de salida."""
        if symbol == arcade.key.F11:
            self.alternar_pantalla_completa()
            return
        if symbol == arcade.key.F2:
            self.mensaje = "Sonido activado." if self.sonidos.alternar() else "Sonido silenciado."
            return
        if self.current_view is not None:
            return
        if symbol == arcade.key.ESCAPE:
            if self.modo_mover:
                self.ejecutar("modo_mover")
            else:
                self.abrir_panel("menu")
        elif modifiers & arcade.key.MOD_ALT:
            for tecla, criterio in [[arcade.key.P, "peso"], [arcade.key.V, "valor"],
                                    [arcade.key.N, "nombre"], [arcade.key.R, "real"]]:
                if symbol == tecla:
                    self.criterio = criterio
                    break
        elif symbol in [arcade.key.M, arcade.key.O, arcade.key.R, arcade.key.Q, arcade.key.F1, arcade.key.SLASH]:
            for tecla, accion in [[arcade.key.M, "mover"], [arcade.key.O, "abrir"],
                                  [arcade.key.R, "recoger"], [arcade.key.Q, "terminar"],
                                  [arcade.key.F1, "ayuda"], [arcade.key.SLASH, "ayuda"]]:
                if symbol == tecla:
                    self.ejecutar(accion)
                    break
        elif symbol == arcade.key.TAB:
            self.controlador.anterior_item() if modifiers & arcade.key.MOD_SHIFT else self.controlador.siguiente_item()
            actual = self.controlador.inventario().item_actual()
            self.item = actual.instancia_id if actual else ""
        elif symbol == arcade.key.I:
            self.ejecutar("informacion")
        elif symbol == arcade.key.A:
            self.ejecutar("atacar")
        elif symbol == arcade.key.PERIOD:
            self.ejecutar("esperar")
        elif symbol == arcade.key.P:
            self.ejecutar("retroceder")
        elif symbol == arcade.key.U:
            self.ejecutar("usar")
        elif symbol == arcade.key.E:
            self.ejecutar("equipar")
        elif symbol in [arcade.key.D, arcade.key.S]:
            self.ejecutar("soltar")
        else:
            for tecla, direccion in [[arcade.key.UP, "N"], [arcade.key.DOWN, "S"],
                                     [arcade.key.LEFT, "O"], [arcade.key.RIGHT, "E"]]:
                if symbol == tecla:
                    self.ejecutar("mover", direccion)
                    break

    def on_close(self):
        """Cierra tras guardar el resultado, evitando interferir con una carga activa."""
        from .carga import PantallaCarga
        if isinstance(self.current_view, PantallaCarga) and self.current_view.futuro is not None and not self.current_view.futuro.done():
            return
        try:
            if self.controlador.estado_partida().activa or self.controlador.estado_partida().terminada:
                self.controlador.terminar()
        except (OSError, RuntimeError, ValueError) as error:
            self.mensaje = str(error)
            print(self.mensaje, file=sys.stderr)
            return
        super().on_close()
