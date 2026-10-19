"""Ventana y entrada del usuario; delega acciones a Aplicacion."""
import sys
from time import monotonic

import arcade

from .escena import Escena, PANEL_X, FONDO
from .lienzo import Lienzo, cargar_fuentes, tamano_ventana_inicial
from .recursos import Recursos
from .musica import Musica
from .sonidos import Sonidos


def _tamano_inicial():
    """Tamaño proporcional a la pantalla de cada computadora (16:9)."""
    try:
        ancho, alto = arcade.get_display_size()
    except Exception:   # sin pantalla detectable (pruebas, escritorio remoto)
        ancho, alto = [1280, 720]
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
        self._accion_sin_dibujar = False
        self.duracion_visual = 0.65
        self.enemigos_muertos = []
        self.accion_visual = ""
        self.enemigo = ""
        self.ultimo_click = None
        self.item = ""
        self.criterio = "real"
        self.descendente = False
        self.modo_mover = False
        self.mensaje = "Haz clic en una puerta, un enemigo o un objeto."
        self._aviso_presupuesto = False
        self.zonas = []
        self.bitacora_desplazamiento = 0
        self.bitacora_limite = 0
        self.inventario_fondo = 0
        self.atacantes = []
        self.cambio_vida = 0
        self.cambios_enemigos = []
        self.set_minimum_size(640, 360)
        self.background_color = FONDO
        self.lienzo = Lienzo()
        self.escena = Escena(Recursos(), self.lienzo)
        self.sonidos = Sonidos(activo=visible)   # en las pruebas (ventana oculta) no suena
        self.musica = Musica(activo=visible)
        self._ultimo_enemigo = -10.0             # para no saltar de pista en cada golpe

    #  Música de ambientación (solo decora: depende de la pantalla y del estado visible)

    def pista_actual(self):
        """Qué pista corresponde: menú, exploración, combate o silencio (pantalla final)."""
        from .carga import PantallaCarga
        from .fin import PantallaFin
        from .menu import MenuPrincipal
        vista = self.current_view
        if isinstance(vista, MenuPrincipal):
            return "menu"
        if isinstance(vista, PantallaCarga):
            return self.musica.actual or "menu"      # se mantiene la que venía sonando
        if isinstance(vista, PantallaFin):
            return ""                                # suenan victoria/derrota
        p = self.controlador.estado_partida()
        if not p.activa:
            return self.musica.actual
        if p.enemigos:
            self._ultimo_enemigo = self.animacion
        return "combate" if self.animacion - self._ultimo_enemigo < 2.5 else "cripta"

    def show_view(self, new_view):
        super().show_view(new_view)
        self.musica.poner(self.pista_actual())

    def hide_view(self):
        super().hide_view()
        self.musica.poner(self.pista_actual())

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
        self._accion_sin_dibujar = False
        self.zonas = self.lienzo.zonas
        self.lienzo.globo_ayuda()
        self.lienzo.bandas(self)

    def volver_menu(self):
        """Termina la partida y carga la selección sin cerrar la ventana."""
        from .menu import MenuPrincipal
        p = self.controlador.estado_partida()
        try:
            self.controlador.preparar_seleccion()
            menu = MenuPrincipal(self, p.cripta_id, p.nombre_jugador)
            self.cargar("Buscando criptas", menu.cargar, lambda _: self.show_view(menu))
        except (OSError, RuntimeError, ValueError) as error:
            self.mensaje = str(error)

    def preparar_partida(self):
        """Limpia selecciones y animaciones antes de mostrar una nueva partida."""
        self.ultimo_click = None
        self._aviso_presupuesto = False
        self.enemigo = self.item = self.accion_visual = ""
        self.atacantes = self.cambios_enemigos = []
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
        self.show_view(PantallaCarga(self, titulo, operacion, terminado, self.current_view))

    def indicador_red(self):
        """Devuelve el modo y las solicitudes usadas frente al presupuesto."""
        p = self.controlador.estado_partida()
        cheats = " · CHEATS" if self.controlador.trucos_activos else ""
        limite = " AGOTADO" if self.controlador.presupuesto_agotado else ""
        return f"{self.modo}{cheats} · RED {self.controlador.solicitudes_usadas()}/{p.presupuesto_solicitudes}{limite}"

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
        if accion == "sentido_orden":
            if self.criterio == "real":
                self.criterio = "peso"
            self.descendente = not self.descendente
            return
        if accion == "ordenar":
            criterios = ["real", "peso", "valor", "nombre"]
            self.criterio = criterios[(criterios.index(self.criterio) + 1) % 4]
            return
        if accion in ["ayuda", "terminar", "informacion", "menu", "cheats"]:
            self.abrir_panel(accion)
            return
        if accion == "seleccionar_item":
            resultado = self.controlador.seleccionar_item(argumento)
            if resultado.ok:
                self.item = argumento
            else:
                self.mensaje = resultado.motivo
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
        acciones = ["mover", "abrir", "recoger", "atacar", "esperar", "retroceder", "usar", "equipar", "soltar"]
        destino_pendiente = False
        if accion == "mover":
            estado = self.controlador.estado_partida()
            vecina = next((v for v in estado.vecindad if v.direccion == argumento), None)
            destino_pendiente = bool(vecina and not vecina.cerrada
                                     and vecina.sala_id not in estado.contenido_cargado)
        if accion in acciones and (destino_pendiente or self.controlador.precarga_pendiente):
            from .panel import Panel
            from .carga import PantallaCarga

            def preparar():
                self.controlador.preparar_accion()
                if accion == "mover":
                    self.controlador.preparar_movimiento(argumento)

            def terminado(_):
                self.hide_view()
                self.ejecutar(accion, argumento)

            retorno = Panel(self, "PREPARAR ACCIÓN", texto="La carga no consume tiempo virtual.")
            self.show_view(PantallaCarga(self, "Preparando sala", preparar, terminado, retorno))
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
                inv = self.controlador.inventario()
                actual = inv.item_actual()
                if not (actual and actual.instancia_id == self.item) and not inv.buscar_por_id(self.item):
                    self.mensaje = "Selecciona un objeto del inventario con un clic o Tab."
                    return
                resultado = getattr(self.controlador, accion)(self.item)
            else:
                return
            self.mensaje = "" if resultado.ok else resultado.motivo
            if resultado.ok:
                self.accion_visual = accion
                despues = self.controlador.estado_partida()
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
                self._accion_sin_dibujar = True
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
            if self.controlador.presupuesto_agotado:
                lineas += ["RED AGOTADA: puedes seguir con los datos disponibles.",
                           "Las acciones que necesiten red se rechazan sin consumir tiempo.",
                           "Esc: guardar partida o volver al menú."]
            lineas += [f"{v.direccion}: {v.nombre} · {'cerrada' if v.cerrada else 'abierta'}"
                       + (f" · llave {v.llave}" if v.llave else "") for v in p.vecindad]
            lineas += [f"Trampa {t.tipo}: {'activa' if t.activa else 'inactiva'} · daño {t.dano}" for t in p.trampas]
            lineas += p.efectos or ["Sin efectos activos."]
            lineas += p.rastro
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
                     "Alt+D: alternar ascendente/descendente\n"
                     "I: información de la sala · Q: terminar · Esc: menú · F11: pantalla completa · F2: sonido · F3: música\n"
                     "Minimapa: dorado = salida, rojo = cerrada.")
            self.show_view(Panel(self, "AYUDA", texto=texto))
            return
        if accion == "terminar":
            self.show_view(Panel(self, "¿TERMINAR LA PARTIDA?", [["Sí, terminar la partida", self.controlador.terminar]]))
            return
        if accion == "cheats":
            self.show_view(Panel(self, "CHEATS · SOLO PRUEBAS", [
                ["Recuperar toda la vida", lambda: self.aplicar_truco("curar")],
                ["Aumentar ataque (+50)", lambda: self.aplicar_truco("ataque")],
                ["Aumentar defensa (+50)", lambda: self.aplicar_truco("defensa")],
                [f"God Mode: {'ON' if self.controlador.truco_activo('god_mode') else 'OFF'} · invulnerabilidad",
                 lambda: self.aplicar_truco("god_mode")],
                [f"Insta Kill: {'ON' if self.controlador.truco_activo('insta_kill') else 'OFF'} · matar de un golpe",
                 lambda: self.aplicar_truco("insta_kill")],
                ["Eliminar veneno", lambda: self.aplicar_truco("antidoto")],
                ["Aumentar vida máxima (+100) y curar", lambda: self.aplicar_truco("vida")],
            ]))
            return
        if accion == "menu":
            self.show_view(Panel(self, "MENÚ", [
                ["Continuar", lambda: None],
                ["Información de la sala (I)", lambda: self.abrir_panel("informacion")],
                ["Guardar partida", self.guardar_partida],                 # <- NUEVA
                ["Cargar partida guardada", self.elegir_guardado],
                ["Cheats (sin puntajes, guardado ni replay)", lambda: self.abrir_panel("cheats")],
                ["Ayuda y controles", lambda: self.abrir_panel("ayuda")],
                ["Configuración: audio y pantalla", self.abrir_configuracion],
                ["Terminar la partida", lambda: self.abrir_panel("terminar")],
                ["Volver al menú principal", self.volver_menu],
            ]))

    def abrir_configuracion(self, retorno=None):
        """Abre los ajustes de vista sin modificar la partida."""
        from .configuracion import Configuracion
        self.show_view(Configuracion(self, retorno=retorno))

    def guardar_partida(self):
        """Guarda la partida activa; no consume tiempo virtual."""
        resultado = self.controlador.guardar()
        self.mensaje = resultado.motivo or "Partida guardada."
        self.sonidos.tocar("recoger" if resultado.ok else "error")

    def aplicar_truco(self, nombre):
        """Aplica una ayuda y comunica que la sesión queda marcada como prueba."""
        resultado = self.controlador.aplicar_truco(nombre)
        if resultado.ok:
            self.preparar_partida()
        self.mensaje = resultado.motivo or "Cheats activos: sin puntajes, guardado ni replay."
        self.sonidos.tocar("recoger" if resultado.ok else "error")

    def elegir_guardado(self):
        """Muestra los guardados identificados por jugador, cripta y progreso."""
        from .panel import Panel
        retorno = self.current_view
        def terminado(guardados):
            """Construye la selección en el hilo gráfico al terminar la lectura."""
            opciones = [[descripcion, lambda ruta=ruta: self.cargar_partida(ruta=ruta)]
                        for ruta, descripcion in guardados]
            self.show_view(Panel(self, "ELEGIR PARTIDA GUARDADA", opciones,
                                 texto="No hay partidas guardadas." if not opciones else "", retorno=retorno))
        self.cargar("Buscando partidas guardadas", self.controlador.listar_guardados, terminado)

    def cargar_partida(self, confirmar=True, ruta=None):
        """Carga desde el menú o solicita permiso para reemplazar una partida activa.

        Args:
            confirmar: Pide confirmación si hay una partida en curso.
            ruta: Archivo elegido en la lista de partidas guardadas.
        """
        if confirmar and self.controlador.estado_partida().activa:
            from .panel import Panel
            self.show_view(Panel(self, "¿REEMPLAZAR LA PARTIDA ACTUAL?", [
                ["Cancelar y seguir jugando", lambda: None],
                ["Sí, cargar la partida guardada", lambda: self.cargar_partida(confirmar=False, ruta=ruta)],
            ]))
            return
        retorno = self.current_view
        def terminado(carga):
            """Aplica el resultado en el hilo gráfico y vuelve a la partida."""
            resultado, controlador = carga
            if resultado.ok:
                self.controlador = controlador
                self.modo = "OFFLINE" if controlador.estado_partida().modo == "offline" else "EN RED"
                self.escena.distribucion.partida = None
                self.preparar_partida()
                actual = self.controlador.inventario().item_actual()
                self.item = actual.instancia_id if actual else ""
                self.mensaje = "Partida cargada."
                self.hide_view()
            else:
                self.mensaje = resultado.motivo
                self.sonidos.tocar("error")
                if retorno is not None:
                    retorno.error = resultado.motivo
                    self.show_view(retorno)
                else:
                    self.hide_view()
        self.cargar("Cargando partida", lambda: self.controlador.cargar_compatible(ruta), terminado)


    def alternar_pantalla_completa(self):
        self.set_fullscreen(not self.fullscreen)

    def on_update(self, delta_time):
        """Avanza solo las animaciones y muestra el resultado cuando terminan."""
        self.animacion += delta_time
        if self.current_view is None and not self._accion_sin_dibujar:
            self.pausa_visual = max(0, self.pausa_visual - delta_time)
        self.musica.poner(self.pista_actual())
        if (self.current_view is None and self.controlador.estado_partida().activa
                and self.controlador.presupuesto_agotado and not self._aviso_presupuesto):
            self._aviso_presupuesto = True
            self.mensaje = "Red agotada: usa datos cargados. Esc: guardar o volver al menú."
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
            for indice in range(len(self.zonas) - 1, -1, -1):  # lo último queda encima
                zona = self.zonas[indice]
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
        if symbol == arcade.key.F3:
            self.mensaje = "Música activada." if self.musica.alternar() else "Música silenciada."
            return
        if self.current_view is not None:
            return
        if symbol == arcade.key.ESCAPE:
            if self.modo_mover:
                self.ejecutar("modo_mover")
            else:
                self.abrir_panel("menu")
        elif modifiers & arcade.key.MOD_ALT:
            if symbol == arcade.key.D:
                self.ejecutar("sentido_orden")
                return
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
