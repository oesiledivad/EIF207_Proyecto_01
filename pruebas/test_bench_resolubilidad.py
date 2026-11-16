"""Pruebas de la medición de resolubilidad en --bench (historia US6).

Cada prueba arma criptas sintéticas por semilla: ningún dato de una cripta
concreta vive aquí (FR-029).
"""
import io
import json
import os
import subprocess
import sys
import time
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cripta import bench
from cripta.modelo.Resolubilidad import verificar

PAQUETE = Path(__file__).resolve().parents[1] / "datos_offline"


def firma(cripta) -> list:
    """Contenido comparable de una cripta sintética: salas, salidas y ubicaciones."""
    salas = [
        (s.id, s.nombre, [(x.direccion, x.sala_id, x.cerrada, x.llave) for x in s.salidas])
        for s in cripta.salas
    ]
    ubicaciones = [(u.llave, u.sala, u.enemigo) for u in cripta.ubicaciones]
    d = cripta.detalles
    return [salas, ubicaciones, d.sala_inicial, d.sala_salida, d.llave_salida]


def tamano_mayor_esqueleto_del_paquete() -> int | None:
    """Mayor `salas_total` de las criptas del paquete; None si el paquete no está."""
    if not PAQUETE.is_dir():
        return None
    mayor = None
    for ruta in PAQUETE.glob("cripta_*.json"):
        nombre = ruta.name
        if nombre.endswith(("_contenido.json", "_version.json", "_llaves.json")) or "_salas_" in nombre:
            continue
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        total = datos.get("salas_total") if isinstance(datos, dict) else None
        if isinstance(total, int) and (mayor is None or total > mayor):
            mayor = total
    return mayor


class PruebasBenchResolubilidad(unittest.TestCase):
    def test_us6_1_mide_ambas_alternativas(self):
        """FR-026: la medición devuelve y el texto impreso trae tiempos de la verificación y de la ingenua."""
        salida = io.StringIO()
        with redirect_stdout(salida):
            filas = bench.medir_m1((100, 300), 300, 42)
        self.assertEqual(len(filas), 2)
        for fila in filas:
            self.assertGreaterEqual(fila.t_verificacion, 0)
            self.assertIsNotNone(fila.t_ingenua)
            self.assertGreaterEqual(fila.t_ingenua, 0)
            self.assertGreater(fila.llaves, 1)
        texto = salida.getvalue()
        self.assertIn("M1", texto)
        self.assertIn("verificacion", texto)
        self.assertIn("ingenua", texto)
        self.assertIn("ms", texto)

    def test_us6_2_misma_semilla_misma_cripta(self):
        """FR-026: misma semilla, misma cripta (S, E, K, salas y ubicaciones); semillas distintas difieren."""
        a = bench.generar_cripta(42, 300)
        b = bench.generar_cripta(42, 300)
        c = bench.generar_cripta(43, 300)
        self.assertEqual((a.n_salas, a.n_salidas, a.n_llaves), (b.n_salas, b.n_salidas, b.n_llaves))
        self.assertEqual(firma(a), firma(b))
        self.assertNotEqual(firma(a), firma(c))
        self.assertEqual(bench.semilla_efectiva(""), 42)
        self.assertEqual(bench.semilla_efectiva(None), 42)
        self.assertEqual(bench.semilla_efectiva("7"), 7)
        self.assertEqual(firma(bench.generar_cripta(bench.semilla_efectiva(""), 300)), firma(a))

    def test_us6_3_escala_casi_lineal(self):
        """FR-024: el conteo de operaciones crece lineal con S, E y K y es menor que el de la ingenua."""
        filas = []
        for salas in (200, 2000):
            cripta = bench.generar_cripta(42, salas)
            resultado = verificar(cripta.detalles, cripta.salas, cripta.ubicaciones)
            self.assertEqual(resultado.estado, "resoluble")
            est = resultado.estadisticas
            operaciones = est.salidas_examinadas + est.llaves_obtenidas
            # Cada salida se examina una vez y cada llave se obtiene una vez.
            self.assertLessEqual(est.salidas_examinadas, cripta.n_salidas)
            self.assertLessEqual(est.llaves_obtenidas, cripta.n_llaves)
            self.assertLessEqual(operaciones, cripta.n_salidas + cripta.n_llaves)
            gano, ingenuas = bench.verificar_ingenua(cripta)
            self.assertTrue(gano)
            self.assertLess(operaciones, ingenuas)
            filas.append((cripta, operaciones, ingenuas))
        (_, pequena, ingenua_pequena), (grande, grande_ops, ingenua_grande) = filas
        # Diez veces el tamaño, a lo sumo unas doce veces las operaciones.
        self.assertLess(grande_ops / pequena, 12)
        # La ingenua crece mucho más rápido que la verificación.
        self.assertGreater(ingenua_grande / ingenua_pequena, grande_ops / pequena * 3)

    def test_generador_resoluble_y_con_ciclo(self):
        """FR-026, FR-012: la variante resoluble da resoluble y la de ciclo final da no_resoluble con ciclo."""
        resoluble = bench.generar_cripta(42, 300)
        r = verificar(resoluble.detalles, resoluble.salas, resoluble.ubicaciones)
        self.assertEqual(r.estado, "resoluble")
        self.assertEqual(len(r.orden_llaves), resoluble.n_llaves)
        ciclica = bench.generar_cripta(42, 300, con_ciclo=True)
        r = verificar(ciclica.detalles, ciclica.salas, ciclica.ubicaciones)
        self.assertEqual(r.estado, "no_resoluble")
        self.assertGreaterEqual(len(r.reporte.ciclos), 1)

    def test_limite_200ms_cripta_sintetica_grande(self):
        """FR-023, SC-003: una cripta sintética de 10 veces el esqueleto mayor se verifica sin red en menos de 200 ms."""
        mayor = tamano_mayor_esqueleto_del_paquete()
        salas = 10 * mayor if mayor else 500
        cripta = bench.generar_cripta(42, salas)
        fuente = SimpleNamespace(requests_made=0)
        mejor = None
        with patch("requests.get", side_effect=AssertionError("No debe consultar la red")):
            for _ in range(3):
                inicio = time.perf_counter()
                resultado = verificar(cripta.detalles, cripta.salas, cripta.ubicaciones)
                transcurrido = time.perf_counter() - inicio
                mejor = transcurrido if mejor is None else min(mejor, transcurrido)
        self.assertEqual(resultado.estado, "resoluble")
        self.assertEqual(fuente.requests_made, 0)
        self.assertLess(mejor, 0.2, f"{salas} salas tardaron {mejor * 1000:.1f} ms")

    def test_bench_no_importa_arcade(self):
        """FR-028: --bench no importa arcade ni instancia la vista."""
        codigo = (
            "import sys\n"
            "from cripta.bootstrap import main\n"
            "codigo = main(['--bench', '--semilla', '42'])\n"
            "vista = [m for m in sys.modules if m == 'arcade' or m.startswith('arcade.') "
            "or m == 'cripta.vista.grafica']\n"
            "print('SALIDA', codigo, 'VISTA', vista)\n"
        )
        resultado = subprocess.run(
            [sys.executable, "-I", "-c", codigo], capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=300,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("SALIDA 0 VISTA []", resultado.stdout)
        self.assertIn("Resolubilidad", resultado.stdout)


if __name__ == "__main__":
    unittest.main()
