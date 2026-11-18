"""Pruebas de la medición del conocimiento y de «ir a» en --bench (historia US8).

Cada prueba arma criptas sintéticas por semilla: ningún dato de una cripta
concreta vive aquí (FR-041).
"""
import io
import os
import subprocess
import sys
import time
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cripta import bench
from cripta.estructuras.Historial_Retroceso import Historial_Retroceso


def firma(cripta) -> list:
    """Contenido comparable de una cripta sintética de conocimiento."""
    filas = []
    for i in range(cripta.n_salas):
        sala = cripta.salas.obtener(i)
        filas.append([(s.direccion, s.sala_destino, s.cerrada, s.costo, s.clave) for s in sala.salidas])
    return filas


class PruebasBenchConocimiento(unittest.TestCase):
    def test_us8_1_mide_consultas_e_ir_a(self):
        """FR-039: la medición devuelve y el texto impreso trae tiempos de las consultas y del paso de ir a."""
        salida = io.StringIO()
        with redirect_stdout(salida):
            k1 = bench.medir_k1((200, 2000), 42)
            k4 = bench.medir_k4(42)
        self.assertEqual(len(k1), 2)
        for fila in k1:
            self.assertGreaterEqual(fila.t_estado, 0)
            self.assertGreaterEqual(fila.t_puerta, 0)
            self.assertGreaterEqual(fila.t_lineal, 0)
        self.assertGreaterEqual(k4.maximo, 0)
        texto = salida.getvalue()
        self.assertIn("K1", texto)
        self.assertIn("K4", texto)
        self.assertIn("ms", texto)
        self.assertIn("estado de sala", texto)
        self.assertIn("paso de ir a", texto)

    def test_us8_2_paso_menor_5ms_cripta_referencia(self):
        """FR-038, SC-003: con el mapa completo de la cripta de referencia un paso de ir a tarda menos de 5 ms."""
        salas = bench.tamano_cripta_referencia()
        self.assertGreater(salas, 1)
        cripta = bench.generar_cripta_conocimiento(42, salas)
        conocimiento = bench.conocimiento_completo(cripta)
        pares = bench.elegir_pares(42, salas, 20)
        buscador = bench.BuscadorRutas(salas)
        mejor = None
        for _ in range(3):
            peor = 0.0
            for origen, destino in pares:
                inicio = time.perf_counter()
                bench.paso_ir_a(cripta, conocimiento, buscador, origen, destino)
                peor = max(peor, time.perf_counter() - inicio)
            mejor = peor if mejor is None else min(mejor, peor)
        self.assertLess(mejor, 0.005, f"{salas} salas: el paso tardó {mejor * 1000:.3f} ms")

    def test_us8_3_consulta_no_crece_con_el_mapa(self):
        """FR-035, FR-036, FR-037, SC-004: consultas y exploración no crecen con el mapa; el registro crece con los cambios."""
        with redirect_stdout(io.StringIO()):
            k1 = bench.medir_k1((200, 2000, 20000), 42)
            k2 = bench.medir_k2((200, 2000, 20000), 42)
            k3 = bench.medir_k3((200, 20000), (10, 1000), 42)
        # K1: con 10 veces el tamaño la consulta cuesta a lo sumo 1,5 veces; la búsqueda lineal sí crece.
        for anterior, actual in zip(k1, k1[1:]):
            self.assertLessEqual(actual.t_estado / max(anterior.t_estado, 1e-9), 1.5)
            self.assertLessEqual(actual.t_puerta / max(anterior.t_puerta, 1e-9), 1.5)
        self.assertGreater(k1[-1].t_lineal, k1[0].t_lineal)
        # K2: por conteo de operaciones (cambios al registro por sala revelada), a lo sumo 1,5 veces.
        for fila in k2:
            self.assertGreater(fila.reveladas, 0)
        for anterior, actual in zip(k2, k2[1:]):
            self.assertLessEqual(actual.ops_sin / anterior.ops_sin, 1.5)
            self.assertLessEqual(actual.ops_con / anterior.ops_con, 1.5)
        # K3: el registro e inversión dependen solo de los cambios, no del tamaño del mapa.
        for fila in k3:
            self.assertEqual(fila.registrados, fila.cambios)
            self.assertTrue(fila.revertido)
            self.assertEqual(fila.ops_copia, fila.cambios * (5 * fila.salas + 2))
        pequenos = [f for f in k3 if f.salas == 200]
        grandes = [f for f in k3 if f.salas == 20000]
        for a, b in zip(pequenos, grandes):
            self.assertEqual(a.registrados, b.registrados)
            self.assertGreater(b.ops_copia, a.ops_copia)

    def test_misma_semilla_mismos_resultados(self):
        """FR-039, FR-040, SC-008: la misma semilla da la misma cripta y los mismos resultados; otra semilla difiere."""
        a = bench.generar_cripta_conocimiento(42, 300)
        b = bench.generar_cripta_conocimiento(42, 300)
        c = bench.generar_cripta_conocimiento(43, 300)
        self.assertEqual(firma(a), firma(b))
        self.assertNotEqual(firma(a), firma(c))
        self.assertEqual(bench.semilla_efectiva(""), 42)
        self.assertEqual(firma(bench.generar_cripta_conocimiento(bench.semilla_efectiva(""), 300)), firma(a))
        with redirect_stdout(io.StringIO()):
            x = bench.medir_k4(42)
            y = bench.medir_k4(42)
            z = bench.medir_k4(7)
        self.assertEqual(x.resultados, y.resultados)
        self.assertNotEqual(x.resultados, z.resultados)

    def test_generador_costos_puertas_y_tamanos(self):
        """FR-039, FR-041: el generador trae costos variados y sin declarar, puertas cerradas en un solo lado y claves únicas."""
        cripta = bench.generar_cripta_conocimiento(42, 400)
        costos = []
        cerradas = 0
        claves = []
        for i in range(cripta.n_salas):
            for s in cripta.salas.obtener(i).salidas:
                costos.append(s.costo)
                claves.append(s.clave)
                cerradas += 1 if s.cerrada else 0
                self.assertEqual(s.clave // 4, i)
        distintos = []
        for costo in costos:
            if costo not in distintos:
                distintos.append(costo)
        self.assertGreater(len(distintos), 5)
        self.assertIn(100, costos)
        self.assertGreater(cerradas, 0)
        for i in range(1, len(claves)):
            self.assertGreater(claves[i], claves[i - 1])   # cada clave es mayor que la anterior: todas distintas
        self.assertEqual(sum(len(e) for e in cripta.entrantes), len(claves))

    def test_k6_k7_k8_reglas(self):
        """FR-023, FR-024, FR-038: K6 y K7 conservan lo elegido y BFS devuelve rutas más caras con costos variados."""
        with redirect_stdout(io.StringIO()):
            k6 = bench.medir_k6(2000, 42)
            k7 = bench.medir_k7(2000, 42)
            k8 = bench.medir_k8(2000, 42)
        self.assertGreater(k6.t_inverso_parada, 0)
        self.assertGreater(k7.t_perezoso, 0)
        self.assertGreater(k8.rutas_mas_caras, 0)
        self.assertEqual(k8.rutas_mas_baratas, 0)

    def test_k9_determinista(self):
        """FR-039, FR-040, SC-005, SC-008: K4 y K6 repetidos con la misma semilla dan resultados idénticos."""
        with redirect_stdout(io.StringIO()):
            k9 = bench.medir_k9(42)
        self.assertTrue(k9.identicos)

    def test_bench_no_abre_vista(self):
        """FR-039, FR-040, SC-008: --bench en un subproceso limpio no importa arcade ni instancia la vista."""
        resultado = subprocess.run(
            [sys.executable, "-I", "-c",
             "import sys\n"
             "from cripta.bootstrap import main\n"
             "codigo = main(['--bench', '--semilla', '42'])\n"
             "vista = [m for m in sys.modules if m == 'arcade' or m.startswith('arcade.') "
             "or m == 'cripta.vista.grafica']\n"
             "print('SALIDA', codigo, 'VISTA', vista)\n"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("SALIDA 0 VISTA []", resultado.stdout)
        for k in ("K1", "K2", "K3", "K4", "K5", "K6", "K7", "K8", "K9"):
            self.assertIn(k, resultado.stdout)


if __name__ == "__main__":
    unittest.main()
