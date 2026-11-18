"""Fichas del catálogo: cada entidad del paquete offline se convierte en su DTO (sin red).

Reemplaza a dos scripts manuales (test_datos y test_ensamblador) que consultaban la API en vivo
con `ficha_desde_dict`, función que después pasó a llamarse `parsear_ficha`.
"""
import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from cripta.dto.FactoryDto_Ficha import parsear_ficha


class PruebasFichasCatalogo(unittest.TestCase):
    def test_todas_las_fichas_del_paquete(self):
        """Cada clase del catálogo produce su ficha con el mismo id y nombre."""
        ruta = RAIZ / "datos_offline" / "catalogo.json"
        if not ruta.is_file():
            self.skipTest("No está el paquete datos_offline.")
        entidades = json.loads(ruta.read_text(encoding="utf-8"))["entidades"]
        self.assertTrue(entidades)
        for entidad in entidades:
            ficha = parsear_ficha(dict(entidad))
            self.assertEqual(ficha.id, entidad["id"])
            self.assertEqual(ficha.nombre, entidad["nombre"])

    def test_clase_desconocida(self):
        """Una clase que no existe se rechaza con un mensaje."""
        with self.assertRaises(ValueError):
            parsear_ficha({"id": "x", "clase": "dragon"})


if __name__ == "__main__":
    unittest.main()
