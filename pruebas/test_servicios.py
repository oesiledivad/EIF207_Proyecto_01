"""Regresiones de catálogo y precarga sin red ni datos locales."""

import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from cripta.adaptadores.Almacen_Disco import AlmacenDisco
from cripta.estructuras.Cache_Fichas import Cache_Fichas
from cripta.servicio.CriptaService import CriptaService


def fuente_catalogo():
    """Simula respuestas de catálogo con fichas mínimas de llave."""
    return SimpleNamespace(
        catalog=Mock(side_effect=lambda ids: {"entidades": [
            {"id": id_, "nombre": id_, "clase": "llave", "peso": 1, "valor": 1}
            for id_ in ids
        ]}),
        get_catalog_version=Mock(return_value={"version": "1"}),
        reiniciar_partida=Mock(),
    )


class PruebasServicios(unittest.TestCase):
    def test_catalogo_lotes_referencias_y_cache_nueva_al_reiniciar(self):
        fuente = fuente_catalogo()
        servicio = CriptaService(fuente, Cache_Fichas(capacidad=15))
        ids = [f"llave-{i}" for i in range(12)]
        servicio.asegurar_fichas(ids + [ids[0]], fijar=True)
        self.assertEqual([len(c.args[0]) for c in fuente.catalog.call_args_list], [10, 2])
        servicio.liberar_fichas([ids[0]])
        self.assertTrue(servicio._cache_fichas.esta_en_uso(ids[0]))
        servicio.liberar_fichas([ids[0]])
        self.assertFalse(servicio._cache_fichas.esta_en_uso(ids[0]))
        anterior = servicio._cache_fichas
        servicio.reiniciar_partida()
        self.assertIsNot(servicio._cache_fichas, anterior)
        self.assertEqual(servicio.obtener_ficha_garantizada(ids[0]).id, ids[0])
        self.assertEqual(fuente.catalog.call_count, 3)
        self.assertEqual(servicio._cache_fichas.tamano, 1)

    def test_catalogo_recupera_disco_sin_repetir_solicitud(self):
        fuente = fuente_catalogo()
        with tempfile.TemporaryDirectory() as carpeta:
            servicio = CriptaService(fuente, Cache_Fichas(capacidad=1), AlmacenDisco(carpeta))
            servicio.preparar_persistencia(SimpleNamespace(id="cripta", version="1"))
            servicio.asegurar_fichas(["a"])
            servicio.asegurar_fichas(["b"])
            self.assertEqual(servicio.obtener_ficha_garantizada("a").id, "a")
            self.assertEqual(fuente.catalog.call_count, 2)
            self.assertEqual(servicio.lecturas_disco, 1)


if __name__ == "__main__":
    unittest.main()
