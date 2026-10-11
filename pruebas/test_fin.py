"""Otra partida: nueva sesión de red y fichas renovadas."""
import unittest


class PruebasFin(unittest.TestCase):
    def test_nueva_sesion_renueva_cliente_y_presupuesto(self):
        from cripta.adaptadores.Network_Adapter import NetworkAdapter
        fuente = NetworkAdapter(timeout=3, max_reintentos_429=1)
        anterior = fuente.client_id
        fuente.fijar_presupuesto(9)
        fuente._requests_made = 9
        fuente.reiniciar_partida()
        self.assertNotEqual(fuente.client_id, anterior)
        self.assertEqual(fuente.headers["X-Cripta-Client-Id"], fuente.client_id)
        self.assertEqual(fuente.requests_made, 0)
        self.assertIsNone(fuente.solicitudes_restantes())
        self.assertEqual((fuente.timeout, fuente.max_reintentos_429), (3, 1))

    def test_otra_partida_no_reutiliza_fichas_de_version_anterior(self):
        from pruebas.test_replay import FuenteReplay
        from cripta.controlador.Aplicacion import Aplicacion
        fuente = FuenteReplay()
        app = Aplicacion(fuente)
        self.assertTrue(app.iniciar_partida("Jugador", "42", "cripta-01").ok)
        anterior = app._cripta_service._cache_fichas
        app.terminar()
        catalogo_original = fuente.catalog
        def catalogo_actualizado(ids):
            respuesta = catalogo_original(ids)
            for ficha in respuesta["entidades"]:
                ficha["nombre"] = "Ficha renovada"
            return respuesta
        fuente.catalog = catalogo_actualizado
        self.assertTrue(app.iniciar_partida("Jugador", "42", "cripta-01").ok)
        actual = app._cripta_service._cache_fichas
        self.assertIsNot(actual, anterior)
        self.assertEqual(actual.obtener("itm_pergamino_retroceso").nombre, "Ficha renovada")
