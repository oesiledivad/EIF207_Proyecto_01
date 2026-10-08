"""Resultado de la partida y tabla local de puntajes."""
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Static


class FinModal(ModalScreen):
    titulo = "SESIÓN TERMINADA"
    estilo = "abandono"
    BINDINGS = [("escape", "otra_partida", "Otra partida")]

    def __init__(self, controlador):
        super().__init__()
        self.controlador = controlador
        self.add_class(self.estilo)

    def compose(self) -> ComposeResult:
        estado = self.controlador.estado_partida()
        with Vertical(id="fin-root"):
            yield Static("LA INCURSIÓN HA TERMINADO", id="fin-epilogo")
            yield Static(self.titulo, id="fin-titulo")
            with VerticalScroll(id="fin-detalle"):
                if estado.derrota:
                    mensajes = [m for m in self.controlador.bitacora().ultimos() if m is not None]
                    causa = "Tu vida llegó a 0."
                    for i in range(len(mensajes) - 1, -1, -1):
                        if mensajes[i].tipo == "combate" and mensajes[i].texto:
                            causa = mensajes[i].texto
                            break
                    yield Static(f"Causa de muerte: {causa}", id="fin-causa", markup=False)
                    recientes = [m.texto for m in mensajes if m.tipo in ("jugador", "combate", "efecto")]
                    yield Static("Últimos acontecimientos:\n" + "\n".join(recientes[-4:]),
                                 id="fin-acontecimientos", markup=False)
                yield Static(f"{estado.nombre_jugador} | {estado.cripta_id} ({estado.version_cripta})\n"
                             f"Acciones: {estado.acciones_ejecutadas} | Enemigos: {estado.enemigos_derrotados}\n"
                             f"Tiempo: {estado.reloj_virtual}\n{self.controlador.resumen_red()}",
                             id="fin-resumen", markup=False)
                if self.controlador.error_puntaje:
                    yield Static(self.controlador.error_puntaje, id="fin-error", markup=False)
                yield DataTable(id="fin-tabla")
            with Horizontal(id="fin-acciones"):
                yield Button("Otra partida", id="fin-otra")
                yield Button("Salir del juego", id="fin-salir")

    def on_mount(self):
        from rich.text import Text
        tabla = self.query_one(DataTable)
        self.query_one("#fin-otra", Button).focus()
        tabla.add_columns("Jugador", "Cripta", "Resultado", "Acciones", "Enemigos", "Tiempo")
        try:
            for puntaje in self.controlador.puntajes():
                tabla.add_row(Text(puntaje.nombre_jugador), Text(puntaje.cripta_id),
                              puntaje.resultado, str(puntaje.acciones),
                              str(puntaje.enemigos_derrotados), str(puntaje.tiempo_final))
        except (OSError, ValueError) as error:
            self.notify(str(error), severity="error")

    def on_button_pressed(self, event):
        self.dismiss(event.button.id == "fin-otra")

    def action_otra_partida(self):
        self.dismiss(True)


class DerrotaModal(FinModal):
    titulo = "HAS MUERTO"
    estilo = "derrota"


class VictoriaModal(FinModal):
    titulo = "VICTORIA"
    estilo = "victoria"
