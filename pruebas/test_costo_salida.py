"""Costo de salida: lectura, normalización y compatibilidad de `Salidas.agregar`."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cripta.dto.FactoryDto_Partida import parsear_sala
from cripta.estructuras.Salidas import Salidas


def _sala(salidas):
    return {"id": 1, "nombre": "s", "descripcion": "", "salidas": salidas}


class PruebasCostoSalida(unittest.TestCase):
    def test_parsear_lee_costo_de_cada_salida(self):
        """FR-023: parsear_sala lee `costo` de cada salida."""
        sala = parsear_sala(_sala({"N": {"sala": 2, "costo": 30}, "E": {"sala": 3, "costo": 7}}), 0)
        self.assertEqual([[s.direccion, s.costo] for s in sala.salidas], [["N", 30], ["E", 7]])

    def test_sin_costo_vale_100(self):
        """FR-023: una salida sin costo declarado vale 100."""
        sala = parsear_sala(_sala({"N": {"sala": 2}}), 0)
        self.assertEqual(sala.salidas[0].costo, 100)

    def test_costo_menor_que_1_se_normaliza_y_avisa(self):
        """FR-023, caso límite «costo menor que 1»: se trata como 100 y deja aviso."""
        avisos = []
        sala = parsear_sala(_sala({"N": {"sala": 2, "costo": 0}, "S": {"sala": 3, "costo": -4}}),
                            0, avisos)
        self.assertEqual([s.costo for s in sala.salidas], [100, 100])
        self.assertEqual(len(avisos), 2)

    def test_costo_valido_no_deja_aviso(self):
        """FR-023: un costo válido o ausente no genera aviso."""
        avisos = []
        parsear_sala(_sala({"N": {"sala": 2, "costo": 5}, "S": {"sala": 3}}), 0, avisos)
        self.assertEqual(avisos, [])

    def test_agregar_sin_costo_sigue_funcionando(self):
        """FR-023: las llamadas existentes de `Salidas.agregar` no cambian."""
        salidas = Salidas()
        salidas.agregar("N", 2, False)
        salidas.agregar("S", 3, True, "llave", 50)
        salidas.agregar("E", 4, False, None, None, 12)
        self.assertEqual([s.costo for s in salidas], [100, 100, 12])


if __name__ == "__main__":
    unittest.main()
