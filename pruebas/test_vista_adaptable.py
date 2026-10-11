"""Minimapa y acceso a controles al redimensionar una terminal."""
import subprocess
import sys
import unittest
from pathlib import Path


class PruebasVistaAdaptable(unittest.TestCase):
    def test_minimapa_y_tamanos(self):
        codigo = r'''
import asyncio
from textual.app import App
from textual.widgets import Button, Input
from cripta.controlador.Aplicacion import Aplicacion
from cripta.dto.Partida_dto import CriptaResumen
from cripta.vista.textual.app import CriptaApp
from cripta.vista.textual.screens.juego import JuegoScreen
from cripta.vista.textual.screens.seleccion import SeleccionCriptaScreen
from cripta.vista.textual.widgets.mini_mapa import CeldaMapa
from pruebas.test_partida import FuentePuertas

async def main():
    controlador = Aplicacion(FuentePuertas())
    assert controlador.iniciar_partida('Jugador', '42', 'cripta-01').ok
    for objeto in list(controlador.estado_partida().objetos_suelo):
        assert controlador.recoger(objeto.id).ok
    class Vista(App):
        CSS_PATH = CriptaApp.CSS_PATH
        def on_mount(self):
            self.push_screen(JuegoScreen(controlador))
    vista = Vista()
    async with vista.run_test(size=(130, 50)) as pilot:
        await pilot.pause()
        juego = vista.screen
        norte = juego.query_one('#celda-1', CeldaMapa)
        assert norte.disabled
        antes = controlador.estado_partida().acciones_ejecutadas
        await pilot.click('#celda-1')
        await pilot.click('#celda-4')
        assert controlador.estado_partida().acciones_ejecutadas == antes
        assert controlador.abrir('N').ok
        juego._refrescar()
        await pilot.pause()
        assert not norte.disabled
        await pilot.click('#celda-1')
        await pilot.pause()
        assert controlador.estado_partida().sala_actual_id == 2
        assert controlador.estado_partida().acciones_ejecutadas == antes + 2
        for ancho, alto in [[80, 24], [60, 20], [40, 16], [130, 50]]:
            await pilot.resize_terminal(ancho, alto)
            await pilot.pause()
            assert juego.has_class('-estrecha') == (ancho < 100)
            for id in ['btn-mover', 'btn-terminar', 'celda-7']:
                boton = juego.query_one('#' + id, Button)
                boton.scroll_visible(immediate=True)
                await pilot.pause()
                boton.scroll_visible(immediate=True)
                await pilot.pause()
                assert boton.region.width > 0 and boton.region.height > 0
                assert boton.region.x >= 0 and boton.region.right <= ancho
                assert boton.region.y >= 0 and boton.region.bottom <= alto, [ancho, alto, id, boton.region, boton.parent.region, boton.parent.virtual_size, boton.parent.max_scroll_y]
        vista.push_screen(SeleccionCriptaScreen(controlador, criptas=[
            CriptaResumen('cripta-01', 'Prueba', 2, 1)]))
        await pilot.resize_terminal(40, 16)
        await pilot.pause()
        seleccion = vista.screen
        for id in ['input-nombre', 'input-semilla', 'btn-iniciar', 'btn-salir']:
            widget = seleccion.query_one('#' + id)
            widget.scroll_visible(immediate=True)
            await pilot.pause()
            widget.scroll_visible(immediate=True)
            await pilot.pause()
            assert widget.region.width > 0 and widget.region.right <= 40
            assert widget.region.y >= 0 and widget.region.bottom <= 16, [id, widget.region]

asyncio.run(main())
'''
        resultado = subprocess.run([sys.executable, '-B', '-c', codigo],
                                   cwd=Path(__file__).resolve().parents[1],
                                   capture_output=True, text=True, timeout=60)
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
