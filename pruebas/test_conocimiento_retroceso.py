"""Niebla de guerra: el pergamino revierte el conocimiento y el viaje (US6)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pruebas.apoyo_niebla import armar_aplicacion, sala, tiempo
from cripta.estructuras.Inventario import ItemInventario
from cripta.modelo.Conocimiento import AVISTADA, EXPLORADA
from cripta.modelo.Efectos import encender_antorcha


def _pergamino(app, numero=1):
    app._gestor.inventario.agregar(ItemInventario(
        f"perg-{numero}", "itm_pergamino_retroceso", "Pergamino de retroceso",
        "pergamino_retroceso", 1, 0))


def _foto(app):
    """Todo lo que el pergamino debe devolver: estados, memoria, registro y mapa conocido."""
    c = app._exploracion.conocimiento
    return [list(c.estado_sala), list(c.puerta), [list(f) for f in c.registro],
            repr(app.mapa_conocido())]


def _esqueleto():
    """1 a 2 a 3 en línea; 3 tiene además una vecina 5 por el este y una vecina 4 por el norte."""
    return [
        sala(1, [["N", 2]]),
        sala(2, [["S", 1], ["N", 3]]),
        sala(3, [["S", 2], ["N", 4], ["E", 5, {"cerrada": True, "llave": "k"}]]),
        sala(4, [["S", 3]]),
        sala(5, [["O", 3]]),
    ]


class PruebasRetrocesoConocimiento(unittest.TestCase):
    def test_us6_1_apendice_b_retroceso_entrada_con_antorcha(self):
        """FR-016 y SC-006 (Apéndice B, caso 5): el pergamino devuelve las salas exploradas por la
        antorcha, las avistadas y las puertas recordadas, y recorta el registro."""
        app = armar_aplicacion(_esqueleto(), sala_inicial=1, sala_salida=4)
        c = app._exploracion.conocimiento
        _pergamino(app)
        self.assertTrue(app.mover("N").ok)               # entra a 2 sin antorcha
        encender_antorcha(app._jugador, 800, tiempo(app), app._simulacion.agenda)
        antes = _foto(app)
        largo = c.longitud_registro()
        self.assertEqual(c.estado(3), AVISTADA)
        self.assertTrue(app.mover("N").ok)               # entra a 3 con la antorcha encendida
        self.assertEqual(c.estado(4), EXPLORADA)         # vecinas exploradas por la antorcha
        self.assertEqual(c.estado(5), EXPLORADA)
        self.assertGreater(c.longitud_registro(), largo)
        self.assertNotEqual(_foto(app), antes)
        self.assertTrue(app.usar_pergamino().ok)
        self.assertEqual(app._jugador.sala, 2)
        self.assertEqual(_foto(app), antes)
        self.assertEqual(c.estado(4), 0)                 # desconocida otra vez
        self.assertEqual(c.estado(5), 0)
        self.assertEqual(c.estado(3), AVISTADA)
        self.assertEqual(c.longitud_registro(), largo)

    def test_us6_2_apendice_b_retroceso_durante_viaje(self):
        """FR-034 (Apéndice B, caso 6): con un viaje de varios pasos el pergamino revierte solo el
        último paso, el conocimiento vuelve al anterior a ese paso y el viaje no continúa."""
        app = armar_aplicacion(_esqueleto(), sala_inicial=1, sala_salida=4)
        _pergamino(app)
        for direccion in ["N", "N", "N", "S", "S", "S"]:  # explora 1 a 4 y vuelve a 1
            self.assertTrue(app.mover(direccion).ok)
        self.assertEqual(app._jugador.sala, 1)
        # Una puerta de la sala 3 cambia sin que el jugador lo vea: el paso que entra a 3 lo observa.
        app._salas.obtener(3).salidas.obtener("E").cerrada = False
        self.assertTrue(app.ir_a(4).activo)
        self.assertTrue(app.avanzar_viaje().activo)      # 1 a 2
        antes = _foto(app)
        self.assertTrue(app.avanzar_viaje().activo)      # 2 a 3: último paso dado
        self.assertEqual(app._jugador.sala, 3)
        self.assertNotEqual(_foto(app), antes)           # el paso cambió el conocimiento
        self.assertTrue(app.usar_pergamino().ok)
        self.assertEqual(app._jugador.sala, 2)           # solo se revirtió ese paso
        self.assertEqual(_foto(app), antes)
        self.assertFalse(app.viaje_activo)               # el viaje no continúa
        self.assertEqual(app._viaje.motivo, "cancelado")
        mensajes = [m.texto for m in app.bitacora().ultimos() if m is not None and m.tipo == "viaje"]
        self.assertEqual(mensajes, ["Viaje cancelado."])
        self.assertFalse(app.avanzar_viaje().ok)
        self.assertEqual(app._jugador.sala, 2)


if __name__ == "__main__":
    unittest.main()
