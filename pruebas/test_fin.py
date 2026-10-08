"""Flujo de otra partida sin contaminar las pruebas de replay con imports de UI."""
import subprocess
import sys
import unittest
from pathlib import Path


class PruebasFin(unittest.TestCase):
    def test_derrota_otra_partida_y_variantes(self):
        codigo = r'''
import asyncio
import tempfile
from pathlib import Path
from textual.app import App
from textual.widgets import Button, Input, Static
from pruebas.test_replay import FuenteReplay
from cripta.controlador.Aplicacion import Aplicacion
from cripta.dto.Partida_dto import CriptaResumen
from cripta.vista.textual.app import CriptaApp
from cripta.vista.textual.screens.seleccion import SeleccionCriptaScreen
from cripta.vista.textual.screens.juego import JuegoScreen
from cripta.vista.textual.modales.fin import DerrotaModal, VictoriaModal

async def main():
    with tempfile.TemporaryDirectory(prefix="cripta-fin-test-") as carpeta:
        controlador = Aplicacion(FuenteReplay(), carpeta_logs=Path(carpeta) / "logs",
                                 ruta_puntajes=Path(carpeta) / "puntajes.json")
        class Vista(App):
            CSS_PATH = CriptaApp.CSS_PATH
            def on_mount(self):
                self.push_screen(SeleccionCriptaScreen(controlador, criptas=[
                    CriptaResumen("cripta-01", "Cripta de prueba", 2, 1)]))
        vista = Vista()
        async with vista.run_test(size=(130, 50)) as pilot:
            await pilot.pause()
            seleccion = vista.screen
            seleccion.query_one("#input-nombre", Input).value = "Jugador"
            seleccion.query_one("#input-semilla", Input).value = "42"
            referencia_inicial = None
            for intento in range(3):
                await pilot.click("#btn-iniciar")
                await vista.workers.wait_for_complete()
                await pilot.pause()
                assert isinstance(vista.screen, JuegoScreen)
                assert controlador.estado_partida().activa
                assert controlador.estado_partida().acciones_ejecutadas == 0
                assert controlador.inventario().tamano == 0
                assert len(controlador._gestor.historial) == 0
                cache = controlador._cripta_service._cache_fichas
                referencias = cache._buscar("itm_pergamino_retroceso").referencias
                if referencia_inicial is None:
                    referencia_inicial = referencias
                assert referencias == referencia_inicial
                controlador._jugador.vida = 1
                vista.screen._ejecutar(controlador.mover("N"))
                assert isinstance(vista.screen, JuegoScreen)
                await pilot.pause(0.2)
                assert isinstance(vista.screen, JuegoScreen)
                await pilot.pause(1.2)
                assert isinstance(vista.screen, DerrotaModal)
                assert str(vista.screen.query_one("#fin-titulo", Static).content) == "HAS MUERTO"
                ultimo = [m.texto for m in controlador.bitacora().ultimos() if m.tipo == "combate"][-1]
                assert ultimo in str(vista.screen.query_one("#fin-causa", Static).content)
                assert ultimo in str(vista.screen.query_one("#fin-acontecimientos", Static).content)
                assert vista.screen.query_one("#fin-titulo", Static).styles.color.hex == "#CF554C"
                assert len(controlador.puntajes()) == intento + 1
                assert vista.focused.id == "fin-otra"
                if intento == 0:
                    await pilot.resize_terminal(80, 24)
                    boton = vista.screen.query_one("#fin-otra", Button)
                    assert boton.region.bottom <= vista.size.height
                    assert await pilot.click("#fin-otra")
                elif intento == 1:
                    await pilot.press("escape")
                else:
                    await pilot.press("enter")
                await pilot.pause()
                assert vista.screen is seleccion
                assert len(vista.screen_stack) == 2
                await pilot.resize_terminal(130, 50)
            assert len(list((Path(carpeta) / "logs").glob("*.log"))) == 3
            vista.push_screen(VictoriaModal(controlador))
            await pilot.pause()
            assert str(vista.screen.query_one("#fin-titulo", Static).content) == "VICTORIA"
            assert vista.screen.query_one("#fin-titulo", Static).styles.color.hex == "#E8C878"
            await pilot.click("#fin-salir")
asyncio.run(main())
'''
        resultado = subprocess.run([sys.executable, "-B", "-c", codigo],
                                   cwd=Path(__file__).resolve().parents[1],
                                   capture_output=True, text=True, timeout=45)
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)

    def test_estilos_fuera_de_python(self):
        raiz = Path(__file__).resolve().parents[1] / "src/cripta/vista/textual"
        self.assertTrue((raiz / "estilos/fin.tcss").exists())
        for archivo in raiz.rglob("*.py"):
            self.assertNotIn("DEFAULT_CSS =", archivo.read_text(encoding="utf-8"))

    def test_nueva_sesion_renueva_cliente_y_presupuesto(self):
        from cripta.adaptadores.Network_Adapter import NetworkAdapter
        fuente = NetworkAdapter(timeout=3, max_reintentos_429=1)
        anterior = fuente.client_id
        fuente.fijar_presupuesto(9)
        fuente._requests_made = 9
        fuente.reiniciar_partida()
        self.assertNotEqual(fuente.client_id, anterior)
        self.assertEqual(fuente.headers["X-Cripta-Client-Id"], fuente.client_id)
        self.assertEqual(fuente.requests_made, 0)
        self.assertIsNone(fuente.solicitudes_restantes())
        self.assertEqual((fuente.timeout, fuente.max_reintentos_429), (3, 1))

    def test_otra_partida_no_reutiliza_fichas_de_version_anterior(self):
        from pruebas.test_replay import FuenteReplay
        from cripta.controlador.Aplicacion import Aplicacion
        fuente = FuenteReplay()
        app = Aplicacion(fuente)
        self.assertTrue(app.iniciar_partida("Jugador", "42", "cripta-01").ok)
        anterior = app._cripta_service._cache_fichas
        app.terminar()
        catalogo_original = fuente.catalog
        def catalogo_actualizado(ids):
            respuesta = catalogo_original(ids)
            for ficha in respuesta["entidades"]:
                ficha["nombre"] = "Ficha renovada"
            return respuesta
        fuente.catalog = catalogo_actualizado
        self.assertTrue(app.iniciar_partida("Jugador", "42", "cripta-01").ok)
        actual = app._cripta_service._cache_fichas
        self.assertIsNot(actual, anterior)
        self.assertEqual(actual.obtener("itm_pergamino_retroceso").nombre, "Ficha renovada")
