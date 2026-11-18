"""Mediciones de la línea de tiempo en --bench (spec 004, US7)."""
import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cripta.bench_linea import (SIN_PUNTOS_DE_CONTROL, linea_pesada, medir_l1_pesada, medir_l4, medir_l5)


class TestBenchLinea(unittest.TestCase):
    def test_l1_informa_k_y_sin_puntos_de_control(self):
        """FR-030 (US7, escenario 1): L1 mide memoria y consulta para al menos tres K y sin puntos de control."""
        salida = StringIO()
        with redirect_stdout(salida):
            filas = medir_l1_pesada(valores=(1, 5, 20), acciones=300, ranuras=50, cambios=8, cantidad=40)
        self.assertEqual([f[0] for f in filas], [1, 5, 20, SIN_PUNTOS_DE_CONTROL])
        for k, puntos, celdas, memoria, media, peor, acciones in filas[:3]:
            self.assertLessEqual(acciones, k)                  # FR-015
            self.assertLessEqual(puntos, 300 // k + 1)         # FR-013
        self.assertGreater(filas[0][2], filas[2][2])           # más puntos de control, más memoria
        self.assertIn("sin puntos de control", salida.getvalue())

    def test_partidas_deterministas(self):
        """US7, escenario 4: la misma semilla genera la misma partida sintética."""
        a, b = linea_pesada(200, 30, 5, semilla=9), linea_pesada(200, 30, 5, semilla=9)
        self.assertEqual(a.a_datos(), b.a_datos())
        self.assertNotEqual(a.a_datos(), linea_pesada(200, 30, 5, semilla=10).a_datos())

    def test_l4_y_l5(self):
        """FR-012 y FR-032: el recorte y el historial con observador se miden sin vista."""
        with redirect_stdout(StringIO()):
            recortes = medir_l4(tamanos=(100, 1000), recortes=20)
            sin, con, _ = medir_l5(intervalos=200)
        self.assertEqual([fila[0] for fila in recortes], [100, 1000])
        self.assertGreater(sin, 0)
        self.assertGreater(con, 0)
        self.assertNotIn("cripta.vista.grafica.ventana", sys.modules)   # FR-033


if __name__ == "__main__":
    unittest.main()
