"""US6 de la spec 003: el bench de terreno y cazador (FR-026, FR-027, FR-028).

    uv run python -m unittest pruebas.test_bench_cazador
"""
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cripta import bench

RAIZ = Path(__file__).resolve().parents[1]


def _estructura(cripta):
    salidas = []
    for i in range(cripta.n_salas):
        for s in cripta.salas.obtener(i).salidas:
            salidas.append([i, s.direccion, s.sala_destino, s.costo, s.cerrada, s.cierre_automatico])
    return [salidas, cripta.jugador, cripta.cazadores]


class BenchCazadorPruebas(unittest.TestCase):
    def test_us6_1_formato_y_sin_vista(self):
        """FR-026, FR-027: H5 reducida imprime los campos del contrato y no importa la vista ni arcade."""
        codigo = (
            "import sys\n"
            "sys.path.insert(0, 'src')\n"
            "from cripta import bench\n"
            "bench.medir_h5(42, 80, (10,), 20)\n"
            "malos = [m for m in sys.modules if m == 'arcade' or m.startswith('arcade.') "
            "or m.startswith('cripta.vista')]\n"
            "assert not malos, malos\n")
        resultado = subprocess.run([sys.executable, "-B", "-c", codigo], cwd=RAIZ,
                                   capture_output=True, text=True, timeout=120)
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        linea = resultado.stdout.strip().splitlines()[-1]
        for campo in ["H5", "cazadores=10", "media_ms=", "maximo_ms=", "limite=20ms"]:
            self.assertIn(campo, linea)
        self.assertTrue(linea.endswith("[CUMPLE]") or linea.endswith("[EXCEDE]"), linea)

    def test_us6_2_determinista_por_semilla(self):
        """FR-026: misma semilla, misma cripta; H4 y H8 reducidas dan los mismos conteos."""
        a = bench.generar_cripta_cazadores(7, 120, 5, 300, puertas_inestables=True)
        b = bench.generar_cripta_cazadores(7, 120, 5, 300, puertas_inestables=True)
        self.assertEqual(_estructura(a), _estructura(b))
        h4a = bench.medir_h4(7, 80, 300, imprimir=False)
        h4b = bench.medir_h4(7, 80, 300, imprimir=False)
        self.assertEqual([h4a.turnos, h4a.coinciden, h4a.recalculos],
                         [h4b.turnos, h4b.coinciden, h4b.recalculos])
        self.assertEqual(h4a.turnos, h4a.coinciden)
        self.assertTrue(bench.medir_h8(7, {"h1_salas": 120, "h1_cantidades": (1, 5), "h4_salas": 60,
                                           "h4_turnos": 200, "h5_salas": 120, "h5_cantidades": (5,),
                                           "h5_ciclos": 15}, imprimir=False).identico)

    def test_generador(self):
        """FR-026, FR-028: ids secuenciales, costos de 1 a 300, nadie en la sala del jugador, cierres automaticos."""
        c = bench.generar_cripta_cazadores(3, 150, 40, 300, puertas_inestables=True)
        self.assertEqual(c.n_salas, 150)
        for i in range(150):
            self.assertEqual(c.salas.obtener(i).id, i)
        costos = [s.costo for i in range(150) for s in c.salas.obtener(i).salidas]
        self.assertTrue(all(1 <= x <= 300 for x in costos))
        self.assertEqual(len(c.cazadores), 40)
        self.assertNotIn(c.jugador, c.cazadores)
        self.assertTrue(any(s.cierre_automatico for i in range(150) for s in c.salas.obtener(i).salidas))
        estable = bench.generar_cripta_cazadores(3, 150, 40, 300)
        self.assertFalse(any(s.cierre_automatico for i in range(150) for s in estable.salas.obtener(i).salidas))


if __name__ == "__main__":
    unittest.main()
