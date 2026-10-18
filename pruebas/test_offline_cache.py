"""--offline juega con lo descargado en la caché persistente (y el paquete solo de respaldo)."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cripta.adaptadores.AdaptadorOffline import AdaptadorOffline
from cripta.adaptadores.Almacen_Disco import AlmacenDisco
from cripta.controlador.Aplicacion import Aplicacion

DATOS = Path(__file__).resolve().parents[1] / "datos_prueba"
CRIPTA = "cripta-stormlight"


class RedSimulada(AdaptadorOffline):
    """Responde como el servicio en línea (usa el paquete por dentro) y cuenta solicitudes."""

    def __init__(self):
        super().__init__(DATOS)
        self.solicitudes = 0

    @property
    def requests_made(self):
        return self.solicitudes

    def _leer(self, nombre):
        self.solicitudes += 1
        return super()._leer(nombre)


class PruebasOfflineDesdeCache(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cache = Path(self.tmp.name) / "cache"
        self.vacio = Path(self.tmp.name) / "sin_paquete"
        self.vacio.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def jugar_en_linea(self):
        app = Aplicacion(RedSimulada(), almacen=AlmacenDisco(self.cache))
        self.assertTrue(app.listar_criptas())
        self.assertTrue(app.iniciar_partida("Jugador", "42", CRIPTA).ok)
        app.terminar()
        return app

    def test_sin_paquete_juega_lo_descargado(self):
        self.jugar_en_linea()
        fuente = AdaptadorOffline(self.vacio, almacen=AlmacenDisco(self.cache))
        app = Aplicacion(fuente)
        self.assertEqual([c.id for c in app.listar_criptas()], [CRIPTA])
        self.assertTrue(app.iniciar_partida("Jugador", "42", CRIPTA).ok)
        self.assertEqual(app.solicitudes_usadas(), 0)
        cargadas = list(app.estado_partida().contenido_cargado)
        self.assertGreater(len(cargadas), 1)
        # Lo que nunca se descargó no se inventa: esas salas quedan sin cargar.
        for sala in app._salas._datos:
            if sala is not None and sala.id not in cargadas:
                self.assertFalse(sala.contenido_cargado)

    def test_sala_no_descargada_no_deja_entrar(self):
        self.jugar_en_linea()
        almacen = AlmacenDisco(self.cache)
        # Se borra una sala vecina de la inicial para simular que nunca se descargó.
        app = Aplicacion(AdaptadorOffline(self.vacio, almacen=almacen))
        self.assertTrue(app.iniciar_partida("Jugador", "42", CRIPTA).ok)
        vecina = next(v for v in app.estado_partida().vecindad if v.transitable)
        app2_cache = self.cache / "criptas" / CRIPTA / "contenido" / f"{vecina.sala_id}.json"
        app2_cache.unlink()
        app = Aplicacion(AdaptadorOffline(self.vacio, almacen=almacen))
        self.assertTrue(app.iniciar_partida("Jugador", "42", CRIPTA).ok)
        resultado = app.mover(vecina.direccion)
        self.assertFalse(resultado.ok)
        self.assertNotEqual(app.estado_partida().sala_actual_id, vecina.sala_id)

    def test_sin_cache_usa_el_paquete_del_curso(self):
        app = Aplicacion(AdaptadorOffline(DATOS, almacen=AlmacenDisco(self.cache)))
        ids = [c.id for c in app.listar_criptas()]
        self.assertIn("cripta-01", ids)
        self.assertTrue(app.iniciar_partida("Jugador", "42", CRIPTA).ok)

    def test_cripta_en_cache_no_mezcla_con_el_paquete(self):
        self.jugar_en_linea()
        fuente = AdaptadorOffline(DATOS, almacen=AlmacenDisco(self.cache))
        detalles = fuente.crypta_details(CRIPTA)
        self.assertEqual(detalles, AlmacenDisco(self.cache).leer_detalles(CRIPTA))
        # Lista: primero lo descargado, luego lo que solo trae el paquete, sin repetir.
        ids = [c["id"] for c in fuente.crypta_list()["criptas"]]
        self.assertEqual(ids[0], CRIPTA)
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
