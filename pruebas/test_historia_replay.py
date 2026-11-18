"""Línea de tiempo sin interfaz: --replay partida.log --hasta t (spec 004, US4)."""
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pruebas.apoyo_linea import FuenteLinea, armar, contenidos, esqueleto, jugar
from cripta.bootstrap import main
from cripta.controlador.LineaTiempoControlador import formatear_resumen
from cripta.replay.reproductor import reproducir


class TestReplayHasta(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.carpeta = tempfile.TemporaryDirectory()
        cls.app = armar(k=5, carpeta_logs=cls.carpeta.name, registrar=True)
        jugar(cls.app, 40, inmortal=False)
        cls.log = cls.app._partida.registro.ruta
        cls.final = cls.app._simulacion.reloj.tiempo_actual

    @classmethod
    def tearDownClass(cls):
        cls.carpeta.cleanup()

    def _fuente(self):
        return FuenteLinea(esqueleto(), 1, 6, contenidos())

    def test_hasta_igual_a_historia(self):
        """FR-021: --replay --hasta t imprime el mismo resumen que historia <t>."""
        reproducida = reproducir(self.log, [self._fuente()], checkpoint_cada=11)
        for t in [0, 1, 99, 100, self.final // 3, self.final // 2, self.final]:
            esperado = formatear_resumen(self.app.historia(str(t)).resumen)
            obtenido = formatear_resumen(reproducida._linea.resumen_hasta(t).resumen)
            self.assertEqual(obtenido, esperado, f"t={t}")

    def test_mas_alla_del_final(self):
        """FR-022 (Apéndice B, caso 5): con t posterior al final se muestra el estado final y se indica que la
        partida terminó antes."""
        reproducida = reproducir(self.log, [self._fuente()])
        resultado = reproducida._linea.resumen_hasta(self.final + 5000)
        self.assertTrue(resultado.ok)
        actual = self.app.historia(f"#{self.app._linea.linea.acciones() + 1}").resumen
        self.assertEqual(resultado.resumen.reloj, self.final)
        self.assertIn(f"terminó antes del instante {self.final + 5000}", resultado.resumen.aviso)
        self.assertIn(str(self.final), resultado.resumen.aviso)
        sin_aviso = formatear_resumen(resultado.resumen).rsplit("\n", 1)[0]
        self.assertEqual(sin_aviso, formatear_resumen(actual))

    def test_cli_sin_vista(self):
        """FR-021 y FR-033: la consola imprime el resumen y no se importa la vista."""
        salida = StringIO()
        with patch("cripta.replay.reproductor.reproducir",
                   side_effect=lambda ruta, fuentes, **kw: reproducir(ruta, [self._fuente()], **kw)), \
                redirect_stdout(salida):
            codigo = main(["--offline", "--replay", str(self.log), "--hasta", str(self.final + 1)])
        self.assertEqual(codigo, 0)
        self.assertIn(f"Instante t={self.final}", salida.getvalue())
        self.assertIn("terminó antes", salida.getvalue())
        self.assertNotIn("cripta.vista.grafica.ventana", sys.modules)

    def test_hasta_invalido(self):
        """FR-023: --hasta sin --replay o con un valor que no es entero no negativo termina con error."""
        casos = [["--hasta", "10"], ["--offline", "--replay", str(self.log), "--hasta", "-1"],
                 ["--offline", "--replay", str(self.log), "--hasta", "abc"]]
        for argumentos in casos:
            with redirect_stderr(StringIO()) as error:
                self.assertEqual(main(argumentos), 2, argumentos)
            self.assertIn("--hasta", error.getvalue())


if __name__ == "__main__":
    unittest.main()
