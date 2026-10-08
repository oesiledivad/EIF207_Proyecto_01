"""Politica LRU, referencias activas y capacidad estricta."""
import unittest
from cripta.estructuras.Cache_Fichas import Cache_Fichas


class PruebasCache(unittest.TestCase):
    def test_recencia_y_reemplazo_sin_duplicar(self):
        cache = Cache_Fichas(2)
        cache.insertar("a", "A")
        cache.insertar("b", "B")
        self.assertEqual(cache.obtener("a"), "A")
        cache.insertar("c", "C")
        self.assertFalse(cache.contiene("b"))
        self.assertTrue(cache.contiene("a"))
        cache.insertar("a", "actualizada")
        self.assertEqual(cache.tamano, 2)
        self.assertEqual(cache.obtener("a"), "actualizada")
        self.assertEqual(cache.desalojos, 1)
        self.assertIsNone(cache.obtener("b"))
        self.assertEqual((cache.aciertos, cache.fallos), (2, 1))

    def test_referencias_multiples_y_desalojo_tras_liberar(self):
        cache = Cache_Fichas(2)
        cache.insertar("a", "A")
        cache.insertar("b", "B")
        cache.marcar_en_uso("a")
        cache.marcar_en_uso("a")
        cache.liberar("a")
        cache.insertar("c", "C")
        self.assertTrue(cache.esta_en_uso("a"))
        self.assertFalse(cache.contiene("b"))
        cache.liberar("a")
        cache.liberar("a")
        cache.insertar("d", "D")
        self.assertFalse(cache.contiene("a"))
        self.assertEqual(cache.tamano, 2)
        self.assertFalse(cache.marcar_en_uso("ausente"))

    def test_cache_totalmente_protegida_no_excede_tope(self):
        cache = Cache_Fichas(1)
        cache.insertar("a", "A")
        cache.marcar_en_uso("a")
        with self.assertRaisesRegex(RuntimeError, "todas las fichas"):
            cache.insertar("b", "B")
        self.assertEqual(cache.tamano, 1)
        self.assertEqual(cache.obtener("a"), "A")
        self.assertFalse(cache.contiene("b"))
        cache.insertar("a", "actualizada")
        self.assertTrue(cache.esta_en_uso("a"))
        cache.liberar("a")
        cache.insertar("b", "B")
        self.assertFalse(cache.contiene("a"))
        self.assertEqual(cache.obtener("b"), "B")

    def test_consulta_no_modifica_recencia(self):
        cache = Cache_Fichas(2)
        cache.insertar("a", "A")
        cache.insertar("b", "B")
        self.assertTrue(cache.contiene("a"))
        self.assertFalse(cache.esta_en_uso("a"))
        cache.insertar("c", "C")
        self.assertFalse(cache.contiene("a"))


if __name__ == "__main__":
    unittest.main()
