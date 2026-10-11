"""Arranque sin vista y lectura binaria del estado medido."""
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cripta.bootstrap import main
from cripta.estructuras.Guardado_Binario import Guardado_Binario


class PruebasBench(unittest.TestCase):
    def test_bench_no_construye_fuente_ni_vista(self):
        vista_antes = sys.modules.get("cripta.vista.textual.app")
        with patch("cripta.bootstrap._construir_data_source") as fuente:
            with patch("cripta.bootstrap.AlmacenDisco") as almacen:
                with patch("cripta.bootstrap.Aplicacion") as controlador:
                    with patch("cripta.bench.main") as medir:
                        self.assertEqual(main(["--bench"]), 0)
                        medir.assert_called_once_with()
            fuente.assert_not_called()
            almacen.assert_not_called()
            controlador.assert_not_called()
        self.assertIs(sys.modules.get("cripta.vista.textual.app"), vista_antes)

    def test_binario_offsets_con_version_utf8(self):
        salas = [SimpleNamespace(sala_id=3, bytes_=b"primera"),
                 SimpleNamespace(sala_id=90, bytes_=b"segunda")]
        with tempfile.TemporaryDirectory(prefix="cripta-test-") as carpeta:
            guardado = Guardado_Binario(str(Path(carpeta) / "partida.bin"))
            guardado.guardar("version-ñ", salas)
            self.assertEqual(guardado.version_cripta(), "version-ñ")
            for sala in salas:
                self.assertEqual(guardado.cargar_sala(sala.sala_id), sala.bytes_)
            self.assertEqual([s.bytes_ for s in guardado.cargar_todo()],
                             [s.bytes_ for s in salas])
            self.assertIsNone(guardado.cargar_sala(42))


if __name__ == "__main__":
    unittest.main()
