"""Regresiones de catálogo y precarga sin red ni datos locales."""

import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from cripta.adaptadores.Almacen_Disco import AlmacenDisco
from cripta.adaptadores.Crypt_Data_Source import PresupuestoAgotado
from cripta.estructuras.Cache_Fichas import Cache_Fichas
from cripta.estructuras.Indice_Salas import IndiceSalas
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
    def salas(self):
        """Construye dos salas conectadas sin contenido."""
        salas = IndiceSalas()
        salas.insertar(1, SimpleNamespace(id=1, contenido_cargado=False,
                                         salidas=[SimpleNamespace(sala_destino=2)]))
        salas.insertar(2, SimpleNamespace(id=2, contenido_cargado=False,
                                         salidas=[SimpleNamespace(sala_destino=1)]))
        return salas

    def test_precarga_respeta_orden_y_no_repite_salas_cargadas(self):
        fuente = fuente_catalogo()
        fuente.room_content = Mock(return_value={"contenido": [{"sala": 2}, {"sala": 1}]})
        servicio = CriptaService(fuente)
        salas = self.salas()
        incorporadas = []

        def incorporar(sala, contenido):
            incorporadas.append(sala.id)
            sala.contenido_cargado = True

        servicio.cargar_lote("cripta", salas, 2, 1, incorporar)
        self.assertEqual(incorporadas, [1, 2])
        fuente.room_content.assert_called_once_with("cripta", [1, 2])
        servicio.cargar_lote("cripta", salas, 2, 1, incorporar)
        self.assertEqual(fuente.room_content.call_count, 1)
        self.assertEqual(incorporadas, [1, 2])

    def test_precarga_distingue_fallo_necesario_y_opcional(self):
        fuente = fuente_catalogo()
        fuente.room_content = Mock(side_effect=PresupuestoAgotado("Sin presupuesto"))
        servicio = CriptaService(fuente)
        salas = self.salas()
        incorporar = Mock()
        self.assertEqual(servicio.asegurar_sala_cargada("cripta", salas, 2, 1, incorporar),
                         "Sin presupuesto")
        self.assertEqual(servicio.precargar_alrededor("cripta", salas, 2, 1, incorporar),
                         "Precarga omitida: Sin presupuesto")
        self.assertFalse(salas.obtener(1).contenido_cargado)
        incorporar.assert_not_called()

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
