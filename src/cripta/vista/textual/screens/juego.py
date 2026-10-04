"""Pantalla de juego."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Static

from cripta.controlador.Aplicacion import Aplicacion
from cripta.vista.textual.modales.ayuda import AyudaModal
from cripta.vista.textual.modales.confirmar import ConfirmarModal
from cripta.vista.textual.modales.elegir_item import ElegirItemModal
from cripta.vista.textual.widgets.barra_acciones import BarraAcciones
from cripta.vista.textual.widgets.barra_superior import BarraSuperior
from cripta.vista.textual.widgets.mini_mapa import MiniMapa
from cripta.vista.textual.widgets.panel_bitacora import PanelBitacora
from cripta.vista.textual.widgets.panel_inventario import PanelInventario
from cripta.vista.textual.widgets.panel_jugador import PanelJugador


class JuegoScreen(Screen):
    BINDINGS = [
        ("escape", "volver", "Volver"),
        ("q", "terminar", "Terminar"),
        ("r", "refrescar", "Refrescar"),
        ("p", "vista_peso", "Peso"),
        ("v", "vista_valor", "Valor"),
        ("n", "vista_nombre", "Nombre"),
        ("o", "vista_real", "Real"),
        ("?", "ayuda", "Ayuda"),
    ]

    def __init__(self, controlador: Aplicacion) -> None:
        super().__init__()
        self._controlador = controlador
        self._anim = 0
        self._timer = None

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
                    yield Static("SALIDAS", classes="section-title")
                    yield Static("", id="salidas")
                    yield Static("ENEMIGOS", classes="section-title")
                    yield Static("", id="enemigos")
                    yield Static("SUELO", classes="section-title")
                    yield Static("", id="suelo")

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

        # Salidas
        if p.vecindad:
            lineas = []
            for v in p.vecindad:
                if v.cerrada:
                    estado = f"[llave] {v.llave or '?'}"
                    color = "#c9a227"
                else:
                    estado = "abierta"
                    color = "#d6cfc4"
                final = "  [salida]" if v.es_salida_final else ""
                lineas.append(
                    f"[{color}]{v.direccion} -> {v.sala_id}  "
                    f"{v.nombre}  ({estado}){final}[/]"
                )
            self.query_one("#salidas", Static).update("\n".join(lineas))
        else:
            self.query_one("#salidas", Static).update("(sin salidas)")

        # Enemigos
        if p.enemigos:
            lineas = []
            for e in p.enemigos:
                nombre = getattr(e, "nombre", "?")
                vida = getattr(e, "vida", "?")
                lineas.append(f"! {nombre}  HP {vida}")
            self.query_one("#enemigos", Static).update("\n".join(lineas))
        else:
            self.query_one("#enemigos", Static).update("(sin enemigos)")

        # Suelo
        if p.objetos_suelo:
            lineas = [f"* {o.nombre}" for o in p.objetos_suelo]
            self.query_one("#suelo", Static).update("\n".join(lineas))
        else:
            self.query_one("#suelo", Static).update("(nada)")

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
        elif btn == "btn-recoger":
            # Recoger se hace sobre el suelo, no sobre el inventario.
            # Hasta que exista el modal de objetos del suelo (P1),
            # se reporta como no implementado.
            self.notify("Recoger aún no implementado.", title="Cripta")
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
        else:
            # Botones de P1 y P2 aún sin implementar.
            self.notify("Acción aún no implementada.", title="Cripta")

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
        if accion == "usar":
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
            self.app.exit()

    def _ejecutar(self, resultado) -> None:
        if not resultado.ok:
            self.notify(resultado.motivo or "Acción rechazada.", title="Cripta")
        self._refrescar()

    #  Acciones de teclado

    def action_volver(self) -> None:
        if self._timer:
            self._timer.stop()
        self.app.pop_screen()

    def action_terminar(self) -> None:
        if self._timer:
            self._timer.stop()
        self._controlador.terminar()
        self.app.exit()

    def action_refrescar(self) -> None:
        self._refrescar()

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