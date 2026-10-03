"""Pantalla de juego."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Static

from cripta.controlador.Aplicacion import Aplicacion
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

            with Horizontal(id="acciones-juego"):
                yield Button("Mover [M]", id="btn-mover")
                yield Button("Atacar [A]", id="btn-atacar")
                yield Button("Esperar [.]", id="btn-esperar")
                yield Button("Terminar [Q]", id="btn-terminar", classes="-danger")

        yield Footer()

    def on_mount(self) -> None:
        self._refrescar()
        self._timer = self.set_interval(0.4, self._tick_cargando)

    def _tick_cargando(self) -> None:
        """Refresca la barra superior mientras hay contenido pendiente.

        Anima los puntos suspensivos para dar feedback de carga sin
        congelar la interfaz.
        """
        p = self._controlador.estado_partida()
        if not p.contenido_pendiente:
            return
        self._anim = (self._anim + 1) % 4
        self.query_one("#barra-superior", BarraSuperior).actualizar(
            p,
            self._controlador.solicitudes_usadas(),
            animacion=self._anim,
        )

    def _refrescar(self) -> None:
        p = self._controlador.estado_partida()

        self.query_one("#barra-superior", BarraSuperior).actualizar(
            p, self._controlador.solicitudes_usadas()
        )
        self.query_one("#panel-jugador", PanelJugador).actualizar(p)
        self.query_one("#mini-mapa", MiniMapa).actualizar(p)
        self.query_one("#panel-inventario", PanelInventario).actualizar(p)
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
                nombre = e.get("tipo", "?")
                vida = e.get("vida", "?")
                lineas.append(f"! {nombre}  HP {vida}")
            self.query_one("#enemigos", Static).update("\n".join(lineas))
        else:
            self.query_one("#enemigos", Static).update("(sin enemigos)")

        # Suelo
        if p.objetos_suelo:
            lineas = [f"* {getattr(o, 'nombre', '?')}" for o in p.objetos_suelo]
            self.query_one("#suelo", Static).update("\n".join(lineas))
        else:
            self.query_one("#suelo", Static).update("(nada)")

        # Efectos
        if p.efectos:
            lineas = [
                f"* {e.get('tipo', '?')}  {e.get('restante', '?')}"
                for e in p.efectos
            ]
            self.query_one("#efectos", Static).update("\n".join(lineas))
        else:
            self.query_one("#efectos", Static).update("(sin efectos)")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-terminar":
            self.action_terminar()
        elif event.button.id == "btn-esperar":
            self._controlador.esperar()
            self._refrescar()

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