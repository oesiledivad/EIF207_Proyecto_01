"""Línea de tiempo y pergamino de retroceso (spec 004, US3)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pruebas.apoyo_linea import TIPO_PERGAMINO, armar, foto, foto_resumen, jugar


def _tiempo(app):
    return app._simulacion.reloj.tiempo_actual


def _con_pergaminos(app):
    """Recoge pergaminos en la sala inicial hasta tener al menos tres."""
    while sum(1 for i in app.inventario().items() if i.tipo_id == TIPO_PERGAMINO) < 3:
        objeto = next(o for o in app.estado_partida().objetos_suelo if o.tipo_id == TIPO_PERGAMINO)
        if not app.recoger(objeto.id).ok:
            raise AssertionError("No se pudo recoger un pergamino.")
    return app


class TestHistoriaRetroceso(unittest.TestCase):
    def test_no_muestra_lo_revertido(self):
        """FR-010 (Apéndice B, caso 2): después de un pergamino, historia no muestra la acción revertida ni
        nada de lo que ocurrió después de ella."""
        app = _con_pergaminos(armar(k=2))
        jugar(app, 6)
        n = app._linea.linea.acciones()
        t_decision = _tiempo(app)
        antes = foto(app)
        self.assertTrue(app.mover("N").ok)                 # la acción que se va a revertir
        movido = foto(app)
        self.assertNotEqual(movido, antes)
        self.assertTrue(app.usar_pergamino().ok)
        self.assertEqual(_tiempo(app), t_decision)
        self.assertEqual(app._linea.linea.acciones(), n)
        actual = foto(app)
        for consulta in [str(t_decision), f"#{n + 1}"]:
            resumen = foto_resumen(app.historia(consulta).resumen)
            self.assertEqual(resumen, actual, consulta)
            self.assertNotEqual(resumen[0], movido[0] if movido[0] != antes[0] else -1)
        self.assertFalse(app.historia(str(t_decision + 1)).ok)   # posterior al reloj: rechazada

    def test_renumera_acciones(self):
        """FR-010 (US3, escenario 2): tras revertir la acción N, #N es el estado actual."""
        app = _con_pergaminos(armar(k=3))
        jugar(app, 7)
        n = app._linea.linea.acciones()
        self.assertTrue(app.esperar().ok)
        self.assertTrue(app.usar_pergamino().ok)
        self.assertEqual(app._linea.linea.acciones(), n)
        self.assertEqual(foto_resumen(app.historia(f"#{n + 1}").resumen), foto(app))
        self.assertFalse(app.historia(f"#{n + 2}").ok)

    def test_accion_nueva_tras_pergamino(self):
        """FR-010 (US3, escenario 3): tras el pergamino y una acción distinta, la línea muestra la nueva."""
        app = _con_pergaminos(armar(k=2))
        jugar(app, 5)
        self.assertTrue(app.esperar().ok)
        self.assertTrue(app.usar_pergamino().ok)
        abierta = next(s for s in app.estado_partida().vecindad if not s.cerrada)
        self.assertTrue(app.mover(abierta.direccion).ok)
        n = app._linea.linea.acciones()
        self.assertEqual(foto_resumen(app.historia(f"#{n + 1}").resumen), foto(app))
        self.assertEqual(app.historia(f"#{n + 1}").resumen.sala_id, abierta.sala_id)

    def test_pergamino_descontado(self):
        """FR-011: el descuento del pergamino queda en el instante al que vuelve el reloj."""
        app = _con_pergaminos(armar(k=4))
        jugar(app, 4)
        pergaminos = sum(1 for i in app.inventario().items() if i.tipo_id == TIPO_PERGAMINO)
        t = _tiempo(app)
        self.assertTrue(app.esperar().ok)
        self.assertTrue(app.usar_pergamino().ok)
        inventario = app.historia(str(t)).resumen.inventario
        self.assertEqual(sum(1 for nombre in inventario if "ergamino" in nombre), pergaminos - 1)
        self.assertEqual(foto_resumen(app.historia(str(t)).resumen), foto(app))

    def test_varios_pergaminos_seguidos(self):
        """FR-010 y FR-012: tres pergaminos seguidos recortan tres acciones y la línea sigue coherente."""
        app = _con_pergaminos(armar(k=2))
        jugar(app, 10)
        n = app._linea.linea.acciones()
        fotos = []
        for _ in range(3):
            fotos.append(foto(app))
            self.assertTrue(app.esperar().ok)
        cambios_antes = app._linea.linea.cambios()
        for _ in range(3):
            self.assertTrue(app.usar_pergamino().ok)
        self.assertEqual(app._linea.linea.acciones(), n)
        self.assertLess(app._linea.linea.cambios(), cambios_antes)
        self.assertEqual(foto_resumen(app.historia(f"#{n + 1}").resumen), foto(app))
        jugar(app, 6)
        self.assertEqual(foto_resumen(app.historia(f"#{app._linea.linea.acciones() + 1}").resumen), foto(app))

    def test_accion_rechazada_no_deja_marca(self):
        """FR-008: una acción rechazada no consume tiempo ni existe en la línea."""
        app = armar(k=2)
        jugar(app, 3)
        n, cambios = app._linea.linea.acciones(), app._linea.linea.cambios()
        self.assertFalse(app.atacar("no-existe").ok)
        self.assertFalse(app.recoger("no-existe").ok)
        self.assertEqual([app._linea.linea.acciones(), app._linea.linea.cambios()], [n, cambios])


if __name__ == "__main__":
    unittest.main()
