"""Oscuridad de la sala y radio de la antorcha (spec 002, US9, FR-042 a FR-045, SC-009)."""
import importlib.util
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pruebas.test_grafica import COMUN, _ejecutar


def _fraccion_visible(antorcha):
    from cripta.vista.grafica.escena import (Escena, SALA_X, SALA_Y, SUELO_ALTO, SUELO_ANCHO, SUELO_X,
                                             SUELO_Y)
    px = SUELO_X + SUELO_ANCHO * 0.36 + 16
    py = SUELO_Y + SUELO_ALTO * 0.40
    from cripta.vista.grafica.escena import OPACIDAD_OSCURIDAD
    mascara = Escena.mascara_oscuridad(Escena.radio_visible(antorcha), px - SALA_X, py + 28 - SALA_Y)
    alfa = mascara.getchannel("A")
    visibles = sum(1 for valor in alfa.getdata() if valor < OPACIDAD_OSCURIDAD / 2)
    return visibles / (mascara.width * mascara.height)


SOLO_VISUAL = r'''
from cripta.controlador.Aplicacion import Aplicacion
from cripta.vista.grafica.escena import RADIO_SIN_ANTORCHA, RADIO_CON_ANTORCHA
from pruebas.test_inventario import FuentePrueba
app = Aplicacion(FuentePrueba())
assert app.iniciar_partida('Jugador', '42', 'cripta-01').ok
vista = VentanaCripta(app, visible=False, offline=True, tamano=[640, 360])
try:
    antes = [app.estado_partida().reloj_virtual, app._simulacion.azar.getstate(), len(app._gestor.historial)]
    vista.on_draw()
    assert vista.escena.radio_actual == RADIO_SIN_ANTORCHA
    app._jugador.antorcha_encendida = True
    app._sincronizar_estado()
    vista.on_draw()
    assert vista.escena.radio_actual >= RADIO_CON_ANTORCHA - 4
    app._jugador.antorcha_encendida = False
    app._sincronizar_estado()
    vista.on_draw()
    assert vista.escena.radio_actual == RADIO_SIN_ANTORCHA
    despues = [app.estado_partida().reloj_virtual, app._simulacion.azar.getstate(), len(app._gestor.historial)]
    assert despues == antes
finally:
    vista.close()
'''


@unittest.skipUnless(importlib.util.find_spec("PIL"), "Falta Pillow (uv sync)")
class TestOscuridad(unittest.TestCase):
    def test_radio_de_la_antorcha(self):
        """FR-042 y FR-043: hay un radio mínimo y la antorcha lo amplía al menos al triple, también al parpadear."""
        from cripta.vista.grafica.escena import Escena
        minimo = Escena.radio_visible(False)
        self.assertGreater(minimo, 0)
        for parpadeo in range(3):
            self.assertGreaterEqual(Escena.radio_visible(True, parpadeo), 3 * minimo)

    def test_area_visible(self):
        """SC-009: sin antorcha se ve menos de la quinta parte de la sala; con antorcha, al menos la mitad."""
        self.assertLess(_fraccion_visible(False), 0.2)
        self.assertGreaterEqual(_fraccion_visible(True), 0.5)

    def test_niebla_no_es_negro_total(self):
        """FR-042 y SC-009: fuera del radio la niebla deja ver parte de la imagen (opacidad menor que el 85 %)."""
        from cripta.vista.grafica.escena import Escena
        mascara = Escena.mascara_oscuridad(Escena.radio_visible(False), 100, 100)
        self.assertLess(max(mascara.getchannel("A").getdata()), 0.85 * 255)

    @unittest.skipUnless(importlib.util.find_spec("arcade"), "Falta arcade (uv sync)")
    def test_solo_visual(self):
        """FR-044 (US9, escenarios 3 y 4): dibujar con oscuridad no cambia el estado del juego, y al apagarse la
        antorcha vuelve el radio mínimo."""
        _ejecutar(self, COMUN + SOLO_VISUAL)


if __name__ == "__main__":
    unittest.main()
