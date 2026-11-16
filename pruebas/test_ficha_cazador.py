"""Ficha del cazador y su rango (FR-008, FR-009; contracts/ficha-cazador.md).

    uv run python -m unittest pruebas.test_ficha_cazador
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pruebas.apoyo_cazador import ficha_enemigo
from cripta.dto.FactoryDto_Ficha import parsear_ficha


class FichaCazadorPruebas(unittest.TestCase):
    def test_cazador_valido_conserva_rango(self):
        """FR-008: un cazador con rango entero >= 0 se acepta."""
        self.assertEqual(parsear_ficha(ficha_enemigo("c-1", rango=300)).rango, 300)
        self.assertEqual(parsear_ficha(ficha_enemigo("c-0", rango=0)).rango, 0)

    def test_cazador_sin_rango_o_invalido_se_rechaza(self):
        """FR-009: sin rango, negativo, decimal o booleano la ficha se rechaza nombrando su id."""
        for rango in (None, -1, 2.5, True, "300"):
            with self.assertRaises(ValueError) as contexto:
                parsear_ficha(ficha_enemigo("c-9", rango=rango))
            self.assertIn("c-9", str(contexto.exception))

    def test_otros_comportamientos_no_exigen_rango(self):
        """FR-008: guardián, errante y rastreador no necesitan rango."""
        for comportamiento in ("guardian", "errante", "rastreador"):
            self.assertIsNone(parsear_ficha(ficha_enemigo("x", comportamiento, rango=None)).rango)


if __name__ == "__main__":
    unittest.main()
