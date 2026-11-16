"""Niebla de guerra: interfaz serializable del conocimiento (US6, spec 004)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pruebas.apoyo_niebla import armar_aplicacion, sala
from cripta.estructuras.Inventario import ItemInventario
from cripta.modelo.Conocimiento import ConocimientoJugador


def _esqueleto():
    """1 a 2 a 3 en línea, 3 con una vecina 4 al norte y una puerta cerrada 5 al este."""
    return [
        sala(1, [["N", 2, {"costo": 30}]]),
        sala(2, [["S", 1], ["N", 3]]),
        sala(3, [["S", 2], ["N", 4], ["E", 5, {"cerrada": True, "llave": "k"}]]),
        sala(4, [["S", 3]]),
        sala(5, [["O", 3]]),
    ]


def _app():
    return armar_aplicacion(_esqueleto(), sala_inicial=1, sala_salida=4)


class PruebasSerializable(unittest.TestCase):
    def test_us6_3_restaurar_identico(self):
        """FR-015 y SC-005: guardar con `instantanea()` y restaurar en otra instancia da un mapa
        idéntico; mide 5n + 2, sus valores van de 0 a 2 y dos conocimientos iguales coinciden."""
        origen = _app()
        for direccion in ["N", "N"]:
            self.assertTrue(origen.mover(direccion).ok)
        c = origen._exploracion.conocimiento
        instantanea = c.instantanea()
        n = len(c.estado_sala)
        self.assertEqual(n, 6)                           # ids 0 a 5
        self.assertEqual(len(instantanea), 5 * n + 2)
        self.assertEqual(instantanea[0], 1)              # versión del formato
        self.assertEqual(instantanea[1], n)
        for valor in instantanea[2:]:
            self.assertIn(valor, [0, 1, 2])
        destino = _app()
        self.assertNotEqual(destino.mapa_conocido(), origen.mapa_conocido())
        destino._exploracion.conocimiento.restaurar(instantanea)
        self.assertEqual(destino.mapa_conocido(), origen.mapa_conocido())
        self.assertEqual(destino._exploracion.conocimiento.instantanea(), instantanea)
        # dos conocimientos iguales producen instantáneas idénticas
        gemela = _app()
        for direccion in ["N", "N"]:
            self.assertTrue(gemela.mover(direccion).ok)
        self.assertEqual(gemela._exploracion.conocimiento.instantanea(), instantanea)
        self.assertEqual(destino._exploracion.conocimiento.registro, [])   # restaurar vacía el registro

    def test_us6_4_reconstruir_instante_pasado(self):
        """FR-017: `reconstruir(base, registro, n)` devuelve el mapa exacto de ese instante sin tocar
        el conocimiento vivo ni el historial; `reconstruir_hasta_tiempo` coincide en las fronteras."""
        app = _app()
        c = app._exploracion.conocimiento
        base = c.instantanea()
        puntos = [[0, 0, app.mapa_conocido(), c.instantanea()]]   # [n, t, mapa, instantánea]
        for direccion in ["N", "N", "N", "S"]:
            self.assertTrue(app.mover(direccion).ok)
            puntos.append([c.longitud_registro(), app._simulacion.reloj.tiempo_actual,
                           app.mapa_conocido(), c.instantanea()])
        self.assertGreater(len(c.registro), 4)
        registro = [list(fila) for fila in c.registro]
        vivo = c.instantanea()
        largo_historial = len(app._gestor.historial)
        for n, _, mapa, instantanea in puntos:
            pasado = ConocimientoJugador.reconstruir(base, registro, n)
            self.assertEqual(pasado.instantanea(), instantanea, n)
            self.assertEqual(app._exploracion.mapa_conocido(pasado), mapa, n)
        self.assertEqual(c.instantanea(), vivo)          # el conocimiento vivo no cambió
        self.assertEqual(c.registro, registro)
        self.assertEqual(len(app._gestor.historial), largo_historial)
        comprobados = 0
        for n, t, mapa, instantanea in puntos[1:]:
            if n < len(registro) and registro[n][0] <= t:
                continue                                  # no es frontera de acción: no es exacta
            pasado = ConocimientoJugador.reconstruir_hasta_tiempo(base, registro, t)
            self.assertEqual(pasado.instantanea(), instantanea, t)
            comprobados += 1
        self.assertGreater(comprobados, 0)

    def test_restaurar_invalida_y_n_fuera_de_rango(self):
        """FR-015 y FR-017: `restaurar` rechaza versión, n, largo o valores inválidos; `reconstruir`
        rechaza n fuera de rango; `longitud_registro` cuenta y un retroceso recorta."""
        app = _app()
        c = app._exploracion.conocimiento
        buena = c.instantanea()
        n = buena[1]

        def con(posicion, valor):
            copia = list(buena)
            copia[posicion] = valor
            return copia

        for mala in [con(0, 2), con(1, n + 1), buena[:-1], buena + [0], con(2, 3), con(2 + n, -1), []]:
            with self.assertRaises(ValueError):
                c.restaurar(mala)
        self.assertEqual(c.instantanea(), buena)         # una restauración inválida no cambia nada
        self.assertEqual(c.longitud_registro(), 0)
        base = c.instantanea()
        app._gestor.inventario.agregar(ItemInventario(
            "p", "itm_pergamino_retroceso", "P", "pergamino_retroceso", 1, 0))
        self.assertTrue(app.mover("N").ok)
        largo = c.longitud_registro()
        self.assertEqual(largo, len(c.registro))
        self.assertGreater(largo, 0)
        for fuera in [-1, largo + 1]:
            with self.assertRaises(ValueError):
                ConocimientoJugador.reconstruir(base, c.registro, fuera)
        self.assertEqual(ConocimientoJugador.reconstruir(base, c.registro, largo).instantanea(),
                         c.instantanea())
        self.assertTrue(app.usar_pergamino().ok)
        self.assertEqual(c.longitud_registro(), 0)        # el retroceso recortó el registro


if __name__ == "__main__":
    unittest.main()
