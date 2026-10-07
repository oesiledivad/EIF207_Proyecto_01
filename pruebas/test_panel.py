import asyncio
from pathlib import Path

from textual.app import App

from cripta.adaptadores.AdaptadorOffline import AdaptadorOffline
from cripta.servicio.CriptaService import CriptaService
from cripta.controlador.Aplicacion import Aplicacion
from cripta.dto.Partida_dto import EnemigoPartida, ObjetoSuelo
from cripta.modelo.Jugador import Jugador
from cripta.modelo.Simulacion import Simulacion
from cripta.vista.textual.app import CriptaApp
from cripta.vista.textual.screens.juego import JuegoScreen
from cripta.vista.textual.widgets.panel_sala import PanelSala

DATOS = str(Path(__file__).resolve().parent.parent / "datos_prueba")

servicio = CriptaService(AdaptadorOffline(DATOS))
esqueleto = servicio.cargar_esqueleto_salas("cripta-01", 6)
app_ctrl = Aplicacion(AdaptadorOffline(DATOS))
app_ctrl._crear_salas_desde_esqueleto(esqueleto)
est = app_ctrl._gestor.estado
est.salas_conocidas = esqueleto
est.sala_actual_id = 2
est.sala_salida_id = 6
est.activa = True
est.cripta_id = "cripta-01"
app_ctrl._gestor.reiniciar_inventario(10)
app_ctrl._simulacion = Simulacion(42)
app_ctrl._jugador = Jugador("jugador", 30, 30, 5, 1, 100, 2, 0, 10)
app_ctrl._gestor.refrescar_sala_actual()
app_ctrl._sincronizar_estado()
est.enemigos = [EnemigoPartida(id="e-201", nombre="Rata gigante [x]", vida=12, ataque=5, defensa=1, vida_max=12)]
est.objetos_suelo = [ObjetoSuelo(id="itm_daga_oxidada", nombre="Daga oxidada")]


class Prueba(App):
    CSS_PATH = CriptaApp.CSS_PATH

    def on_mount(self) -> None:
        self.push_screen(JuegoScreen(app_ctrl))


async def main() -> None:
    app = Prueba()
    async with app.run_test(size=(140, 50)) as pilot:
        await pilot.pause()
        panel = app.screen.query_one("#panel-sala", PanelSala)
        texto = str(panel.render())
        print(texto)
        assert "Pasillo de las urnas" in texto
        assert "cerrada, llave: itm_llave_bronce" in texto and "500" in texto
        assert "Rata gigante [x]" in texto and "HP 12/12" in texto
        assert "Daga oxidada" in texto


asyncio.run(main())
print("OK: PanelSala dibuja sala, salidas, enemigos y suelo")