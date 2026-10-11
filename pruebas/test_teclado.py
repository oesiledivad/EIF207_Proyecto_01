"""Navegación de inventario y modales sin consumir tiempo ni importar UI en otras pruebas."""
import subprocess
import sys
import unittest
from pathlib import Path


class PruebasTeclado(unittest.TestCase):
    def test_recorrido_cancelacion_y_seleccion(self):
        codigo = r'''
import asyncio
from textual.app import App
from textual.widgets import Button, DataTable
from cripta.controlador.Aplicacion import Aplicacion
from cripta.vista.textual.app import CriptaApp
from cripta.vista.textual.screens.juego import JuegoScreen
from cripta.vista.textual.modales.elegir_item import ElegirItemModal
from pruebas.test_inventario import FuentePrueba

async def main():
    controlador = Aplicacion(FuentePrueba())
    assert controlador.iniciar_partida('Jugador', '42', 'cripta-01').ok
    for objeto in list(controlador.estado_partida().objetos_suelo):
        assert controlador.recoger(objeto.id).ok
    inv = controlador.inventario()
    orden = [item.instancia_id for item in inv.items()]
    inv.ir_al_frente()
    inicial = inv.item_actual()
    tiempo = controlador.estado_partida().reloj_virtual
    acciones = controlador.estado_partida().acciones_ejecutadas
    historial = len(controlador._gestor.historial)
    class Vista(App):
        CSS_PATH = CriptaApp.CSS_PATH
        def on_mount(self):
            self.push_screen(JuegoScreen(controlador))
    vista = Vista()
    async with vista.run_test(size=(130, 50)) as pilot:
        await pilot.pause()
        juego = vista.screen
        juego.query_one('#btn-esperar', Button).focus()
        await pilot.press('right')
        assert inv.item_actual() is not inicial
        await pilot.press('left')
        assert inv.item_actual() is inicial
        for _ in orden:
            await pilot.press('right')
        assert inv.item_actual().instancia_id == orden[-1]
        for _ in orden:
            await pilot.press('left')
        assert inv.item_actual() is inicial
        await pilot.press('alt+v', 's')
        await pilot.pause()
        assert isinstance(vista.screen, ElegirItemModal)
        tabla = vista.screen.query_one(DataTable)
        assert vista.focused is tabla
        await pilot.press('down', 'right', 'escape')
        await pilot.pause()
        assert vista.screen is juego
        assert inv.item_actual() is inicial
        assert [item.instancia_id for item in inv.items()] == orden
        assert controlador.estado_partida().reloj_virtual == tiempo
        assert controlador.estado_partida().acciones_ejecutadas == acciones
        assert len(controlador._gestor.historial) == historial
        await pilot.press('s')
        await pilot.pause()
        elegido = vista.screen._items[1]
        await pilot.press('down', 'enter')
        await pilot.pause()
        assert vista.screen is juego
        assert inv.buscar_por_id(elegido.instancia_id) is None
        assert controlador.estado_partida().acciones_ejecutadas == acciones + 1

asyncio.run(main())
'''
        resultado = subprocess.run([sys.executable, '-B', '-c', codigo],
                                   cwd=Path(__file__).resolve().parents[1],
                                   capture_output=True, text=True, timeout=60)
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
