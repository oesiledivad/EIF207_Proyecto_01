"""Pantalla de juego."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Static

from cripta.controlador.Aplicacion import Aplicacion
from cripta.estructuras.Inventario import ItemInventario
from cripta.vista.textual.modales.fin import FinModal, DerrotaModal, VictoriaModal
from cripta.vista.textual.modales.ayuda import AyudaModal
from cripta.vista.textual.modales.confirmar import ConfirmarModal
from cripta.vista.textual.modales.elegir_item import ElegirItemModal
from cripta.vista.textual.widgets.barra_acciones import BarraAcciones
from cripta.vista.textual.widgets.barra_superior import BarraSuperior
from cripta.vista.textual.widgets.mini_mapa import MiniMapa
from cripta.vista.textual.widgets.panel_bitacora import PanelBitacora
from cripta.vista.textual.widgets.panel_inventario import PanelInventario
from cripta.vista.textual.widgets.panel_jugador import PanelJugador


from cripta.vista.textual.widgets.panel_sala import PanelSala          

from cripta.vista.textual.modales.elegir_enemigo import ElegirEnemigoModal
from cripta.vista.textual.modales.elegir_direccion import ElegirDireccionModal

class JuegoScreen(Screen):
    BINDINGS = [
        Binding("escape", "volver", "Volver"),
        Binding("q", "terminar", "Terminar"),
        Binding("m", "pulsar('btn-mover')", "Mover"),
        Binding("a", "pulsar('btn-atacar')", "Atacar"),
        Binding("full_stop", "pulsar('btn-esperar')", "Esperar"),
        Binding("o", "pulsar('btn-abrir')", "Abrir"),
        Binding("r", "pulsar('btn-recoger')", "Recoger"),
        Binding("u", "pulsar('btn-usar')", "Usar"),
        Binding("e", "pulsar('btn-equipar')", "Equipar"),
        Binding("s", "pulsar('btn-soltar')", "Soltar"),
        Binding("p", "pulsar('btn-pergamino')", "Pergamino"),
        Binding("g", "pulsar('btn-guardar')", "Guardar"),
        Binding("c", "pulsar('btn-cargar')", "Cargar"),
        Binding("alt+p", "vista_peso", "Peso"),
        Binding("alt+v", "vista_valor", "Valor"),
        Binding("alt+n", "vista_nombre", "Nombre"),
        Binding("alt+r", "vista_real", "Real"),
        Binding("left", "item_anterior", "Item anterior", priority=True),
        Binding("right", "item_siguiente", "Item siguiente", priority=True),
        Binding("?", "ayuda", "Ayuda"),
    ]

    def __init__(self, controlador: Aplicacion) -> None:
        super().__init__()
        self._controlador = controlador
        self._anim = 0
        self._timer = None
        self._fin_mostrado = False
        self._timer_fin = None

    def compose(self) -> ComposeResult:
        with Vertical(id="juego-root"):
            yield BarraSuperior(id="barra-superior")

            with Horizontal(id="juego-columnas"):
                with Vertical(id="col-izq", classes="panel-col"):
                    yield Static("JUGADOR", classes="section-title")
                    yield PanelJugador(id="panel-jugador")
                    yield Static("EFECTOS", classes="section-title")
                    yield Static("", id="efectos")

                with Vertical(id="col-centro", classes="panel-col"):
                    yield Static("SALA", classes="section-title")
                    yield MiniMapa(id="mini-mapa")
                    yield PanelSala(id="panel-sala")                    # <- NUEVO (reemplaza las 6 líneas de SALIDAS, ENEMIGOS y SUELO)

                with Vertical(id="col-der", classes="panel-col"):
                    yield Static("INVENTARIO", classes="section-title")
                    yield PanelInventario(id="panel-inventario")
                    yield Static("BITÁCORA", classes="section-title")
                    yield PanelBitacora(id="panel-bitacora")

            yield BarraAcciones(id="barra-acciones")

        yield Footer()

    def on_mount(self) -> None:
        self._refrescar()
        self._timer = self.set_interval(0.4, self._tick_cargando)

    #  Refresco

    def _refrescar(self) -> None:
        p = self._controlador.estado_partida()
        inv = self._controlador.inventario()
        item_actual = inv.item_actual() if inv is not None else None

        self.query_one("#barra-superior", BarraSuperior).actualizar(
            p, self._controlador.solicitudes_usadas()
        )
        self.query_one("#panel-jugador", PanelJugador).actualizar(p)
        self.query_one("#mini-mapa", MiniMapa).actualizar(p)
        self.query_one("#panel-inventario", PanelInventario).actualizar(
            inv, item_actual
        )
        self.query_one("#panel-bitacora", PanelBitacora).actualizar(
            self._controlador.bitacora()
        )
        # Efectos
        if p.efectos:
            lineas_efectos = [f"[#c9a227]{texto}[/]" for texto in p.efectos]
            self.query_one("#efectos", Static).update("\n".join(lineas_efectos))
        else:
            self.query_one("#efectos", Static).update("(sin efectos)")

        # Sala: salidas, enemigos y suelo
        self.query_one("#panel-sala", PanelSala).actualizar(p)          

        # Efectos
        if p.efectos:
            lineas = [f"* {e}" for e in p.efectos]
            self.query_one("#efectos", Static).update("\n".join(lineas))
        else:
            self.query_one("#efectos", Static).update("(sin efectos)")

    def _tick_cargando(self) -> None:
        p = self._controlador.estado_partida()
        if not p.contenido_pendiente:
            return
        self._anim = (self._anim + 1) % 4
        self.query_one("#barra-superior", BarraSuperior).actualizar(
            p,
            self._controlador.solicitudes_usadas(),
            animacion=self._anim,
        )

    #  Botones

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn = event.button.id

        if btn == "btn-terminar":
            self.app.push_screen(
                ConfirmarModal("¿Desea salir del juego?"),
                self._al_confirmar_salir,
            )
        elif btn == "btn-esperar":
            self._ejecutar(self._controlador.esperar())
        elif btn == "btn-atacar":
            self._modal_elegir_enemigo()
        elif btn == "btn-recoger":
            objetos = self._controlador.estado_partida().objetos_suelo
            if not objetos:
                self.notify("No hay objetos en el suelo.", title="Cripta")
                return
            items = [ItemInventario(o.id, o.tipo_id or o.id, o.nombre, "", 0, 0)
                     for o in objetos]
            self.app.push_screen(ElegirItemModal(items, "recoger"),
                                 lambda item: self._al_elegir_item("recoger", item))
        elif btn == "btn-usar":
            self._modal_elegir("usar")
        elif btn == "btn-equipar":
            self._modal_elegir("equipar")
        elif btn == "btn-soltar":
            self._modal_elegir("soltar")
        elif btn == "btn-pergamino":
            self._ejecutar(self._controlador.usar_pergamino())
        elif btn == "btn-ayuda":
            self.app.push_screen(AyudaModal())
        elif btn == "btn-guardar":
            self.app.push_screen(
                ConfirmarModal("¿Guardar partida?"), self._al_confirmar
            )
        elif btn == "btn-cargar":
            self.app.push_screen(
                ConfirmarModal("¿Cargar partida?"), self._al_confirmar
            )
        elif btn == "btn-atacar":
            self._modal_elegir_enemigo()
        elif btn == "btn-mover":
            self._modal_elegir_direccion()
        elif btn == "btn-abrir":                       # NUEVO
            self._modal_abrir_puerta()
        else:
            # Botones pendientes de integracion.
            self.notify("Acción aún no implementada.", title="Cripta")

    def _modal_elegir_enemigo(self) -> None:
        enemigos = [e for e in self._controlador.estado_partida().enemigos if e.vida > 0]
        if not enemigos:
            self.notify("No hay enemigos para atacar.", title="Cripta")
            return
        self.app.push_screen(ElegirEnemigoModal(enemigos), self._al_elegir_enemigo)

    def _al_elegir_enemigo(self, enemigo) -> None:
        if enemigo is None:
            return
        self._ejecutar(self._controlador.atacar(enemigo.id))

    def _modal_elegir_direccion(self) -> None:
        p = self._controlador.estado_partida()
        salidas = [v for v in (p.vecindad or []) if not v.cerrada]
        if not salidas:
            self.notify("No hay salidas abiertas.", title="Cripta")
            return
        self.app.push_screen(ElegirDireccionModal(salidas), self._al_elegir_direccion)

    def _al_elegir_direccion(self, direccion: str | None) -> None:
        if direccion is None:
            return
        self._ejecutar(self._controlador.mover(direccion))


    def _modal_abrir_puerta(self) -> None:                                       # <- NUEVO
        p = self._controlador.estado_partida()
        cerradas = [v for v in (p.vecindad or []) if v.cerrada]
        if not cerradas:
            self.notify("No hay puertas cerradas.", title="Cripta")
            return
        self.app.push_screen(ElegirDireccionModal(cerradas), self._al_elegir_puerta)

    def _al_elegir_puerta(self, direccion: str | None) -> None:
        if direccion is None:
            return
        self._ejecutar(self._controlador.abrir(direccion))







    def _modal_elegir(self, accion: str, filtro: str | None = None) -> None:
        inv = self._controlador.inventario()
        if inv is None or inv.esta_vacio():
            self.notify("Inventario vacío.", title="Cripta")
            return
        self.app.push_screen(
            ElegirItemModal(inv, accion, filtro),
            lambda item: self._al_elegir_item(accion, item),
        )

    def _al_elegir_item(self, accion: str, item) -> None:
        if item is None:
            return
        if accion == "recoger":
            self._ejecutar(self._controlador.recoger(item.instancia_id))
        elif accion == "usar":
            self._ejecutar(self._controlador.usar(item.instancia_id))
        elif accion == "equipar":
            self._ejecutar(self._controlador.equipar(item.instancia_id))
        elif accion == "soltar":
            self._ejecutar(self._controlador.soltar(item.instancia_id))

    def _al_confirmar(self, valor: bool) -> None:
        if valor:
            self.notify("Confirmado.", title="Cripta")

    def _al_confirmar_salir(self, confirmado: bool) -> None:
        if confirmado:
            self.action_terminar()

    def _ejecutar(self, resultado) -> None:
        if not resultado.ok:
            self.notify(resultado.motivo or "Acción rechazada.", title="Cripta")
        self._refrescar()
        estado = self._controlador.estado_partida()
        if estado.terminada:
            if estado.derrota:
                if self._timer_fin is None:
                    if self._timer:
                        self._timer.stop()
                    self._timer_fin = self.set_timer(1.2, self._mostrar_fin)
            else:
                self._mostrar_fin()

    def _mostrar_fin(self):
        if self._fin_mostrado:
            return
        self._fin_mostrado = True
        if self._timer_fin:
            self._timer_fin.stop()
        if self._timer:
            self._timer.stop()
        estado = self._controlador.estado_partida()
        pantalla = VictoriaModal if estado.victoria else DerrotaModal if estado.derrota else FinModal
        self.app.push_screen(pantalla(self._controlador), self._al_finalizar)

    def on_unmount(self):
        if self._timer:
            self._timer.stop()
        if self._timer_fin:
            self._timer_fin.stop()

    def _al_finalizar(self, otra_partida: bool):
        if otra_partida:
            self.app.pop_screen()  # Regresa a la seleccion ya abierta.
        else:
            self.app.exit()

    #  Acciones de teclado

    def action_volver(self) -> None:
        if self._timer:
            self._timer.stop()
        self._controlador.terminar()
        self.app.pop_screen()

    def action_terminar(self) -> None:
        if self._timer:
            self._timer.stop()
        self._controlador.terminar()
        self._mostrar_fin()

    def action_pulsar(self, boton_id: str) -> None:
        self.query_one("#" + boton_id, Button).press()

    def action_item_anterior(self) -> None:
        self._ejecutar(self._controlador.anterior_item())

    def action_item_siguiente(self) -> None:
        self._ejecutar(self._controlador.siguiente_item())

    def action_vista_peso(self) -> None:
        self.query_one("#panel-inventario", PanelInventario).set_criterio("peso")
        self._refrescar()

    def action_vista_valor(self) -> None:
        self.query_one("#panel-inventario", PanelInventario).set_criterio("valor")
        self._refrescar()

    def action_vista_nombre(self) -> None:
        self.query_one("#panel-inventario", PanelInventario).set_criterio("nombre")
        self._refrescar()

    def action_vista_real(self) -> None:
        self.query_one("#panel-inventario", PanelInventario).set_criterio("real")
        self._refrescar()

    def action_ayuda(self) -> None:
        self.app.push_screen(AyudaModal())
