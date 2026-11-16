"""Pruebas de la consulta, el presupuesto y la persistencia de las llaves (historia US5).

Todo ocurre en carpetas temporales con ids genéricos (FR-029): no se toca
`datos_offline` ni se usa la red real.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cripta.adaptadores.AdaptadorOffline import AdaptadorOffline
from cripta.adaptadores.Almacen_Disco import AlmacenDisco
from cripta.adaptadores.Crypt_Data_Source import CryptDataSource, PresupuestoAgotado
from cripta.adaptadores.Guardar_Llamadas_API import Guardar_Llamadas_API
from cripta.adaptadores.Network_Adapter import NetworkAdapter
from cripta.dto.Partida_dto import DetallesCripta
from cripta.servicio.CriptaService import CriptaService, UbicacionLlavesNoDisponible

CRIPTA = "cripta-t"
RESPUESTA = {"llaves": [{"id": "llave-x", "sala": 1}]}


def detalles(version: str = "v1") -> DetallesCripta:
    return DetallesCripta(
        id=CRIPTA, version=version, salas_total=1, sala_inicial=1, sala_salida=1,
        llave_salida="llave-x", inventario_max=10, presupuesto_solicitudes=9,
        jugador_vida_max=30, jugador_ataque=6, jugador_defensa=2, jugador_velocidad=100,
    )


class FuenteContadora(AdaptadorOffline):
    """Cuenta las consultas de llaves y responde `respuesta`."""

    def __init__(self, respuesta=RESPUESTA):
        super().__init__(tempfile.gettempdir())
        self.respuesta = respuesta
        self.consultas = 0

    def key_locations(self, cid):
        self.consultas += 1
        return self.respuesta


class PruebasLlavesAdaptadores(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory(prefix="cripta-llaves-test-")
        self.addCleanup(self.temporal.cleanup)
        self.raiz = Path(self.temporal.name)
        self.almacen = AlmacenDisco(self.raiz / "cache")

    def servicio(self, fuente: CryptDataSource) -> CriptaService:
        return CriptaService(fuente, almacen=self.almacen)

    def test_us5_1_reutiliza_misma_version(self):
        """FR-020, SC-005: con la misma versión la segunda lectura sale de llaves.json sin consultar."""
        fuente = FuenteContadora()
        servicio = self.servicio(fuente)
        servicio.validar_cripta_en_disco(detalles())
        primera = servicio.obtener_ubicaciones_llaves(CRIPTA)
        segunda = servicio.obtener_ubicaciones_llaves(CRIPTA)
        self.assertEqual(fuente.consultas, 1)
        self.assertEqual(primera, segunda)
        self.assertEqual(self.almacen.leer_llaves(CRIPTA), RESPUESTA)

    def test_us5_2_version_distinta_no_reutiliza(self):
        """FR-021: al cambiar la versión se borra llaves.json y se consulta de nuevo."""
        fuente = FuenteContadora()
        servicio = self.servicio(fuente)
        servicio.validar_cripta_en_disco(detalles("v1"))
        servicio.obtener_ubicaciones_llaves(CRIPTA)
        servicio.validar_cripta_en_disco(detalles("v2"))
        self.assertIsNone(self.almacen.leer_llaves(CRIPTA))
        servicio.obtener_ubicaciones_llaves(CRIPTA)
        self.assertEqual(fuente.consultas, 2)

    def test_us5_3_cuenta_en_presupuesto(self):
        """FR-019: la consulta suma una solicitud y con presupuesto agotado no hay veredicto."""
        respuesta = MagicMock(status_code=200)
        respuesta.json.return_value = RESPUESTA
        red = NetworkAdapter()
        red.fijar_presupuesto(1)
        servicio = self.servicio(red)
        with patch("cripta.adaptadores.Network_Adapter.requests.get", return_value=respuesta) as llamada:
            ubicaciones = servicio.obtener_ubicaciones_llaves(CRIPTA)
            self.assertEqual(red.requests_made, 1)
            self.assertEqual(len(ubicaciones), 1)
            with self.assertRaises(PresupuestoAgotado):
                red.key_locations(CRIPTA)
            with self.assertRaises(UbicacionLlavesNoDisponible):
                servicio.obtener_ubicaciones_llaves(CRIPTA)
            self.assertEqual(llamada.call_count, 1)
        self.assertEqual(red.requests_made, 1)

    def test_offline_lee_cache_luego_paquete_y_no_cuenta(self):
        """FR-018: lee de la caché, luego del paquete, falla sin ninguno y nunca cuenta solicitudes."""
        paquete = self.raiz / "paquete"
        paquete.mkdir()
        adaptador = AdaptadorOffline(paquete, almacen=self.almacen)
        with self.assertRaises(FileNotFoundError):
            adaptador.key_locations(CRIPTA)
        (paquete / f"cripta_{CRIPTA}_llaves.json").write_text(
            json.dumps({"llaves": [{"id": "del-paquete", "sala": 1}]}), encoding="utf-8")
        self.assertEqual(adaptador.key_locations(CRIPTA)["llaves"][0]["id"], "del-paquete")
        # Con la cripta en la caché solo cuenta la caché, aunque el paquete tenga llaves.
        self.almacen.guardar_detalles(CRIPTA, {"id": CRIPTA, "version": "v1"})
        with self.assertRaises(FileNotFoundError):
            adaptador.key_locations(CRIPTA)
        self.almacen.guardar_llaves(CRIPTA, RESPUESTA)
        self.assertEqual(adaptador.key_locations(CRIPTA), RESPUESTA)
        self.assertEqual(adaptador.requests_made, 0)

    def test_guardar_llamadas_graba_archivo_de_llaves(self):
        """FR-020: el grabador de respuestas escribe cripta_<id>_llaves.json."""
        carpeta = self.raiz / "grabadas"
        Guardar_Llamadas_API(carpeta).key_locations(CRIPTA, RESPUESTA)
        ruta = carpeta / f"cripta_{CRIPTA}_llaves.json"
        self.assertEqual(json.loads(ruta.read_text(encoding="utf-8")), RESPUESTA)

    def test_llaves_json_danado_equivale_a_none(self):
        """FR-020: un llaves.json dañado se trata como ausente y se vuelve a consultar."""
        fuente = FuenteContadora()
        servicio = self.servicio(fuente)
        servicio.validar_cripta_en_disco(detalles())
        servicio.obtener_ubicaciones_llaves(CRIPTA)
        ruta = self.raiz / "cache" / "criptas" / CRIPTA / "llaves.json"
        ruta.write_text("{ no es json", encoding="utf-8")
        self.assertIsNone(self.almacen.leer_llaves(CRIPTA))
        servicio.obtener_ubicaciones_llaves(CRIPTA)
        self.assertEqual(fuente.consultas, 2)
        self.assertEqual(self.almacen.leer_llaves(CRIPTA), RESPUESTA)

    def test_respuesta_sin_llaves_es_no_disponible_y_lista_vacia_es_valida(self):
        """FR-022: sin la clave `llaves` no hay datos y no se guarda; una lista vacía es legítima."""
        malformada = FuenteContadora({"otra_cosa": []})
        servicio = self.servicio(malformada)
        servicio.validar_cripta_en_disco(detalles())
        with self.assertRaises(UbicacionLlavesNoDisponible):
            servicio.obtener_ubicaciones_llaves(CRIPTA)
        self.assertIsNone(self.almacen.leer_llaves(CRIPTA))

        vacia = FuenteContadora({"llaves": []})
        servicio = self.servicio(vacia)
        servicio.validar_cripta_en_disco(detalles())
        self.assertEqual(servicio.obtener_ubicaciones_llaves(CRIPTA), [])
        self.assertEqual(self.almacen.leer_llaves(CRIPTA), {"llaves": []})

    def test_no_guarda_sin_validar_la_cripta_en_disco(self):
        """FR-021: sin validar la versión de la cripta no se escribe llaves.json."""
        fuente = FuenteContadora()
        servicio = self.servicio(fuente)
        servicio.obtener_ubicaciones_llaves(CRIPTA)
        self.assertIsNone(self.almacen.leer_llaves(CRIPTA))


if __name__ == "__main__":
    unittest.main()
