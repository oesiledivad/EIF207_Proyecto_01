"""Pantalla de selección de cripta."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Input, Label, Static

from cripta.controlador.Aplicacion import Aplicacion, CriptaResumen
from cripta.vista.textual.modales.confirmar import ConfirmarModal


def _estrellas(nivel: int) -> str:
    nivel = max(1, min(3, nivel))
    return "★" * nivel


class SeleccionCriptaScreen(Screen):
    BINDINGS = [("escape", "salir", "Salir")]

    def __init__(
        self,
        controlador: Aplicacion,
        criptas: list[CriptaResumen] | None = None,
        error: str = "",
    ) -> None:
        super().__init__()
        self._controlador = controlador
        self._criptas: list[CriptaResumen] = criptas if criptas is not None else []
        self._error_inicial = error
        self._cargado = criptas is not None

    def compose(self) -> ComposeResult:
        with Vertical(id="seleccion-root"):
            yield Static("CRIPTA · Selección de mazmorra", id="titulo")
            yield Static(
                "Elige una cripta para comenzar la incursión.",
                id="subtitulo",
            )

            with Horizontal(id="seleccion-cuerpo"):
                with Vertical(id="seleccion-izq"):
                    yield DataTable(id="tabla-criptas")

                with Vertical(id="seleccion-der", classes="panel-box"):
                    yield Static("PREVISUALIZACIÓN", classes="section-title")
                    yield Static("", id="previsualizacion")

            with Vertical(id="formulario"):
                with Horizontal(classes="form-row"):
                    yield Label("Nombre del jugador", classes="form-label")
                    yield Input(
                        placeholder="p. ej. Ana",
                        id="input-nombre",
                        classes="form-input",
                    )
                with Horizontal(classes="form-row"):
                    yield Label("Semilla (opcional)", classes="form-label")
                    yield Input(
                        placeholder="vacío = se genera una",
                        id="input-semilla",
                        classes="form-input",
                    )

            yield Static("", id="error")

            with Horizontal(id="acciones"):
                yield Button("Iniciar partida", id="btn-iniciar", classes="-primary")
                yield Button("Salir", id="btn-salir", classes="-danger")

        yield Footer()

    def on_mount(self) -> None:
        tabla = self.query_one("#tabla-criptas", DataTable)
        tabla.add_columns("ID", "Nombre", "Salas", "Dificultad")
        tabla.cursor_type = "row"
        tabla.zebra_stripes = True

        # Si las criptas no vinieron precargadas, se piden aquí.
        if not self._cargado:
            try:
                self._criptas = self._controlador.listar_criptas()
            except RuntimeError as e:
                self._error_inicial = str(e)
                self._criptas = []

        if self._error_inicial:
            self.query_one("#error", Static).update(self._error_inicial)

        for c in self._criptas:
            tabla.add_row(
                c.id,
                c.nombre,
                str(c.salas),
                _estrellas(c.dificultad),
                key=c.id,
            )

        if self._criptas:
            tabla.move_cursor(row=0)
            self._actualizar_previsualizacion()

        self.query_one("#input-nombre", Input).focus()

    def on_data_table_row_highlighted(
        self, event: DataTable.RowHighlighted
    ) -> None:
        self._actualizar_previsualizacion()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-iniciar":
            self._intentar_iniciar()
        elif event.button.id == "btn-salir":
            self.app.push_screen(
                ConfirmarModal("¿Desea salir del juego?"),
                self._al_confirmar_salir,
            )

    def _al_confirmar_salir(self, confirmado: bool) -> None:
        if confirmado:
            self.app.exit()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self._intentar_iniciar()

    def action_salir(self) -> None:
        self.app.push_screen(
            ConfirmarModal("¿Desea salir del juego?"),
            self._al_confirmar_salir,
        )

    def _actualizar_previsualizacion(self) -> None:
        tabla = self.query_one("#tabla-criptas", DataTable)
        if tabla.cursor_row < 0 or not self._criptas:
            return

        cripta_id = self._criptas[tabla.cursor_row].id
        try:
            d = self._controlador.previsualizar_cripta(cripta_id)
        except Exception as e:
            self.query_one("#previsualizacion", Static).update(
                f"No se pudo cargar: {e}"
            )
            return

        texto = (
            f"ID:         {d.id}\n"
            f"Versión:    {d.version}\n"
            f"Salas:      {d.salas_total}\n"
            f"Inicial:    {d.sala_inicial}\n"
            f"Salida:     {d.sala_salida}\n"
            f"Llave:      {d.llave_salida}\n"
            f"Inventario: {d.inventario_max}\n"
            f"Presupuesto:{d.presupuesto_solicitudes}\n"
            f"\n"
            f"JUGADOR\n"
            f"  HP:  {d.jugador_vida_max}\n"
            f"  ATQ: {d.jugador_ataque}\n"
            f"  DEF: {d.jugador_defensa}\n"
            f"  VEL: {d.jugador_velocidad}"
        )
        self.query_one("#previsualizacion", Static).update(texto)

    def _intentar_iniciar(self) -> None:
        error = self.query_one("#error", Static)
        error.update("")

        nombre = self.query_one("#input-nombre", Input).value
        semilla = self.query_one("#input-semilla", Input).value

        tabla = self.query_one("#tabla-criptas", DataTable)
        if tabla.cursor_row < 0 or not self._criptas:
            error.update("Selecciona una cripta.")
            return

        cripta_id = self._criptas[tabla.cursor_row].id

        from cripta.vista.textual.screens.cargando import CargandoScreen

        self.app.push_screen(
            CargandoScreen(mensaje="Cargando cripta", modo="modal")
        )

        def _trabajo() -> None:
            try:
                resultado = self._controlador.iniciar_partida(
                    nombre, semilla, cripta_id
                )
            except Exception as e:
                self.app.call_from_thread(self._al_terminar, None, str(e))
            else:
                self.app.call_from_thread(self._al_terminar, resultado, None)

        self.run_worker(_trabajo, thread=True)

    def _al_terminar(self, resultado, error_msg: str | None = None) -> None:
        from cripta.vista.textual.screens.juego import JuegoScreen

        self.app.pop_screen()

        if error_msg is not None:
            self.query_one("#error", Static).update(
                f"Error de conexión: {error_msg}"
            )
            return

        if not resultado.ok:
            self.query_one("#error", Static).update(
                resultado.motivo or "No se pudo iniciar la partida."
            )
            return

        self.app.push_screen(JuegoScreen(self._controlador))