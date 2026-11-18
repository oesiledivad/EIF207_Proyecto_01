"""Interfaz de la línea de tiempo con ventana oculta (spec 004, FR-028)."""
import importlib.util
import unittest

from pruebas.test_grafica import COMUN, _ejecutar


class TestHistoriaVista(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec("arcade"), "Falta arcade (uv sync)")
    def test_tecla_h_consulta_y_rechaza(self):
        """FR-028: H abre la entrada; #1 y Enter muestran el resumen; un instante futuro muestra el motivo y no
        consume tiempo."""
        _ejecutar(self, COMUN + r'''
from cripta.controlador.Aplicacion import Aplicacion
from cripta.vista.grafica.historia import EntradaHistoria
from cripta.vista.grafica.panel import Panel
from pruebas.test_inventario import FuentePrueba
app = Aplicacion(FuentePrueba())
assert app.iniciar_partida('Jugador', '42', 'cripta-01').ok
assert app.esperar().ok
vista = VentanaCripta(app, visible=False, offline=True, tamano=[640, 360])
try:
    reloj = app.estado_partida().reloj_virtual
    vista.on_key_press(arcade.key.H, 0)
    entrada = vista.current_view
    assert isinstance(entrada, EntradaHistoria)
    entrada.on_draw()
    entrada.on_key_press(arcade.key.TAB, 0)
    entrada.on_text('1')
    assert entrada.texto == '#1'
    entrada.on_text('#')
    assert entrada.texto == '1'
    entrada.on_text('#x')
    assert entrada.texto == '#1'
    entrada.on_key_press(arcade.key.ENTER, 0)
    assert isinstance(vista.current_view, Panel)
    assert 'Instante t=0' in vista.current_view.texto
    vista.current_view.on_draw()
    vista.hide_view()
    vista.on_key_press(arcade.key.H, 0)
    entrada = vista.current_view
    entrada.on_text('99999')
    entrada.on_key_press(arcade.key.ENTER, 0)
    assert vista.current_view is entrada
    assert 'posterior al reloj actual' in entrada.error
    entrada.on_draw()
    entrada.on_key_press(arcade.key.ESCAPE, 0)
    assert vista.current_view is None
    assert app.estado_partida().reloj_virtual == reloj
finally:
    vista.close()
''')


if __name__ == "__main__":
    unittest.main()
