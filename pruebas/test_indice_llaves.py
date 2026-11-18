"""Pruebas del índice propio de ids de llave."""
import unittest

from cripta.estructuras.Indice_Llaves import IndiceLlaves


class PruebasIndiceLlaves(unittest.TestCase):
    def test_rango_por_posicion_ordenada(self):
        """FR-008: el rango de cada id es su posición en el orden lexicográfico."""
        indice = IndiceLlaves(["c", "a", "b"])
        self.assertEqual([indice.rango("a"), indice.rango("b"), indice.rango("c")], [0, 1, 2])

    def test_busqueda_inexistente_devuelve_menos_uno(self):
        """FR-024: la búsqueda binaria devuelve -1 si el id no existe."""
        indice = IndiceLlaves(["a", "c"])
        self.assertEqual(indice.rango("b"), -1)
        self.assertEqual(indice.rango("z"), -1)
        self.assertEqual(IndiceLlaves([]).rango("a"), -1)

    def test_duplicados_se_deduplican(self):
        """FR-008: los ids repetidos cuentan una sola vez."""
        indice = IndiceLlaves(["b", "a", "b", "a", "b"])
        self.assertEqual(indice.cantidad(), 2)
        self.assertEqual(indice.rango("b"), 1)

    def test_resultado_igual_para_dos_permutaciones(self):
        """FR-008: el resultado no depende del orden de la entrada."""
        uno = IndiceLlaves(["k3", "k1", "k2", "k5", "k4"])
        otro = IndiceLlaves(["k5", "k4", "k3", "k2", "k1"])
        self.assertEqual(uno.ids(), otro.ids())
        for id_llave in ("k1", "k2", "k3", "k4", "k5"):
            self.assertEqual(uno.rango(id_llave), otro.rango(id_llave))

    def test_ids_se_ordenan_como_cadenas(self):
        """FR-008: un id terminado en 10 tiene menor rango que uno terminado en 2."""
        prefijo = "pfx_"
        indice = IndiceLlaves([prefijo + "2", prefijo + "10", prefijo + "1"])
        self.assertLess(indice.rango(prefijo + "10"), indice.rango(prefijo + "2"))
        self.assertEqual(indice.ids(), [prefijo + "1", prefijo + "10", prefijo + "2"])

    def test_no_modifica_la_entrada(self):
        """FR-024: construir el índice no altera la lista recibida."""
        entrada = ["b", "a", "b"]
        IndiceLlaves(entrada)
        self.assertEqual(entrada, ["b", "a", "b"])


if __name__ == "__main__":
    unittest.main()
