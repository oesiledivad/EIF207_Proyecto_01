"""Pruebas de `--verificar CRIPTA` desde la consola (historia US4).

Cada prueba arma un paquete offline mínimo en una carpeta temporal con ids
genéricos; no se usa ningún dato de una cripta concreta (FR-029) y no se toca
`datos_offline`.
"""
import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from cripta import bootstrap
from cripta.adaptadores.AdaptadorOffline import AdaptadorOffline
from cripta.adaptadores.Almacen_Disco import AlmacenDisco
from cripta.adaptadores.Crypt_Data_Source import PresupuestoAgotado

CRIPTA = "cripta-t"
LLAVE = "llave-x"
PRESUPUESTO = 9


def escribir(ruta: Path, datos: dict) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(datos), encoding="utf-8")


def detalles() -> dict:
    return {
        "id": CRIPTA, "version": "v1", "salas_total": 2, "paginas": 1, "salas_por_pagina": 50,
        "sala_inicial": 1, "sala_salida": 2, "llave_salida": LLAVE,
        "presupuesto_solicitudes": PRESUPUESTO, "inventario_max": 10,
        "jugador": {"vida_max": 30, "ataque": 6, "defensa": 2, "velocidad": 100},
    }


def salas() -> dict:
    """Sala 1 con una puerta cerrada hacia la sala 2 que exige `LLAVE`."""
    return {"salas": [
        {"id": 1, "nombre": "Inicio", "salidas": {"N": {"sala": 2, "cerrada": True, "llave": LLAVE}}},
        {"id": 2, "nombre": "Salida", "salidas": {"S": {"sala": 1, "cerrada": False}}},
    ], "total_paginas": 1}


def llaves(sala_de_la_llave: int) -> dict:
    return {"llaves": [{"id": LLAVE, "sala": sala_de_la_llave}]}


class PruebasVerificarCli(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory(prefix="cripta-cli-test-")
        self.addCleanup(self.temporal.cleanup)
        self.raiz = Path(self.temporal.name)
        self.paquete = self.raiz / "paquete"
        self.cache = self.raiz / "cache"

    def armar_paquete(self, sala_llave: int | None) -> None:
        """Paquete offline; sala_llave None omite el archivo de llaves."""
        escribir(self.paquete / f"cripta_{CRIPTA}.json", detalles())
        escribir(self.paquete / f"cripta_{CRIPTA}_salas_1.json", salas())
        archivo_llaves = self.paquete / f"cripta_{CRIPTA}_llaves.json"
        if sala_llave is not None:
            escribir(archivo_llaves, llaves(sala_llave))
        elif archivo_llaves.exists():
            archivo_llaves.unlink()

    def argumentos(self, *extra: str) -> list[str]:
        return ["--verificar", CRIPTA, "--offline", "--offline-dir", str(self.paquete),
                "--cache-dir", str(self.cache), *extra]

    def ejecutar(self, argv: list[str]) -> tuple[int, str, str]:
        """Llama a `main` y devuelve (código, salida estándar, salida de errores)."""
        salida, errores = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(errores):
            codigo = bootstrap.main(argv)
        return codigo, salida.getvalue(), errores.getvalue()

    def ejecutar_uso_incorrecto(self, argv: list[str]) -> int:
        """Un error de uso termina con código 2 (argparse o `main`)."""
        try:
            return self.ejecutar(argv)[0]
        except SystemExit as salida:
            return salida.code

    def test_us4_1_imprime_y_no_abre_vista(self):
        """FR-017, FR-028: imprime el resultado y no carga arcade ni abre la vista."""
        self.armar_paquete(1)
        codigo_py = (
            "import sys; sys.path.insert(0, sys.argv[1]);"
            "from cripta.bootstrap import main;"
            "codigo = main(sys.argv[2:]);"
            "print('ARCADE=' + str('arcade' in sys.modules)); sys.exit(codigo)"
        )
        proceso = subprocess.run(
            [sys.executable, "-I", "-c", codigo_py, str(RAIZ / "src"), *self.argumentos()],
            capture_output=True, text=True, encoding="utf-8", timeout=120,
        )
        self.assertEqual(proceso.returncode, 0, proceso.stderr)
        self.assertIn("RESOLUBLE", proceso.stdout)
        self.assertIn("ARCADE=False", proceso.stdout)

    def test_us4_2_offline_sin_red(self):
        """FR-018, SC-006: con caché con llaves no se usa la red y se informan 0 solicitudes."""
        almacen = AlmacenDisco(self.cache)
        almacen.guardar_detalles(CRIPTA, detalles())
        almacen.guardar_pagina_salas(CRIPTA, 1, salas())
        almacen.guardar_llaves(CRIPTA, llaves(1))
        argv = ["--verificar", CRIPTA, "--offline", "--cache-dir", str(self.cache),
                "--offline-dir", str(self.paquete)]
        with patch.object(bootstrap, "NetworkAdapter",
                          side_effect=AssertionError("No debe usarse la red")) as red:
            codigo, salida, _ = self.ejecutar(argv)
        self.assertEqual(codigo, 0, salida)
        self.assertFalse(red.called)
        self.assertIn(f"Solicitudes de red: 0/{PRESUPUESTO}", salida)

    def test_us4_3_codigos_de_salida(self):
        """FR-018a: 0 resoluble, 1 no resoluble, 2 sin ubicación de llaves o mal uso; nunca 0 sin veredicto."""
        self.armar_paquete(1)
        self.assertEqual(self.ejecutar(self.argumentos())[0], 0)
        self.armar_paquete(2)
        codigo, salida, _ = self.ejecutar(self.argumentos())
        self.assertEqual(codigo, 1)
        self.assertIn("NO RESOLUBLE", salida)
        self.armar_paquete(None)
        codigo, salida, _ = self.ejecutar(self.argumentos())
        self.assertEqual(codigo, 2)
        self.assertIn("resolubilidad no verificada", salida)
        self.assertEqual(self.ejecutar(["--verificar", "inexistente", "--offline",
                                        "--offline-dir", str(self.paquete),
                                        "--cache-dir", str(self.cache)])[0], 2)
        self.assertEqual(self.ejecutar_uso_incorrecto(["--verificar"]), 2)
        self.assertEqual(self.ejecutar_uso_incorrecto(
            ["--verificar", CRIPTA, "--replay", "partida.log"]), 2)

    def test_presupuesto_agotado_da_codigo_2(self):
        """FR-018a, FR-019: si el presupuesto se agota en la consulta de llaves el código es 2."""
        self.armar_paquete(1)

        class FuenteAgotada(AdaptadorOffline):
            def key_locations(self, cid):
                raise PresupuestoAgotado("presupuesto agotado")

        with patch.object(bootstrap, "_construir_data_source",
                          return_value=FuenteAgotada(self.paquete)):
            codigo, salida, _ = self.ejecutar(self.argumentos())
        self.assertEqual(codigo, 2)
        self.assertIn("resolubilidad no verificada", salida)

    def test_salida_determinista_y_primera_linea(self):
        """FR-013, SC-002: dos ejecuciones dan la misma salida y la primera línea es el veredicto."""
        for sala_llave, veredicto in ((1, "RESOLUBLE"), (2, "NO RESOLUBLE")):
            with self.subTest(veredicto=veredicto):
                self.armar_paquete(sala_llave)
                _, primera, _ = self.ejecutar(self.argumentos())
                _, segunda, _ = self.ejecutar(self.argumentos())
                self.assertEqual(primera, segunda)
                self.assertTrue(primera.splitlines()[0].endswith(veredicto))

    def test_advertencias_van_a_la_salida_de_errores(self):
        """FR-022: las advertencias salen por la salida de errores con el prefijo `Aviso:`."""
        self.armar_paquete(1)
        escribir(self.paquete / f"cripta_{CRIPTA}_llaves.json",
                 {"llaves": [{"id": LLAVE, "sala": 1}, {"id": "otra", "sala": 99}]})
        codigo, salida, errores = self.ejecutar(self.argumentos())
        self.assertEqual(codigo, 0, salida)
        self.assertTrue(errores.startswith("Aviso:"), errores)
        self.assertNotIn("Aviso:", salida)


if __name__ == "__main__":
    unittest.main()
