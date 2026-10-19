"""Otra partida: presupuesto renovado y cliente estable durante la ejecución."""
import unittest


class PruebasFin(unittest.TestCase):
    def test_nueva_sesion_conserva_cliente_y_renueva_presupuesto(self):
        from cripta.adaptadores.Network_Adapter import NetworkAdapter
        fuente = NetworkAdapter(timeout=3, max_reintentos_429=1)
        anterior = fuente.client_id
        fuente.fijar_presupuesto(9)
        fuente._requests_made = 9
        fuente.reiniciar_partida()
        self.assertEqual(fuente.client_id, anterior)
        self.assertEqual(NetworkAdapter().client_id, anterior)
        self.assertEqual(fuente.headers["X-Cripta-Client-Id"], fuente.client_id)
        self.assertEqual(fuente.requests_made, 0)
        self.assertIsNone(fuente.solicitudes_restantes())
        self.assertEqual([fuente.timeout, fuente.max_reintentos_429], [3, 1])

    def test_volver_a_seleccion_renueva_presupuesto_antes_de_consultar(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from cripta.adaptadores.AdaptadorOffline import AdaptadorOffline
        from cripta.adaptadores.Network_Adapter import NetworkAdapter
        from cripta.controlador.Aplicacion import Aplicacion

        fuente = NetworkAdapter()
        cliente = fuente.client_id
        fuente.fijar_presupuesto(9)
        fuente._requests_made = 9
        app = Aplicacion(fuente)
        app._jugador = object()
        app._simulacion = object()
        app.estado_partida().activa = True
        app.preparar_seleccion()
        self.assertFalse(app.estado_partida().activa)
        self.assertIsNone(app._jugador)
        self.assertIsNone(app._simulacion)
        self.assertEqual(fuente.requests_made, 0)
        self.assertIsNone(fuente.solicitudes_restantes())
        self.assertEqual(fuente.client_id, cliente)

        datos = AdaptadorOffline('datos_prueba').crypta_details('cripta-02')
        respuesta = SimpleNamespace(status_code=200, json=lambda: datos)
        with patch('requests.get', return_value=respuesta):
            self.assertEqual(app.previsualizar_cripta('cripta-02').id, 'cripta-02')
        self.assertEqual(fuente.requests_made, 1)

    def test_agotar_presupuesto_permite_datos_cargados_y_guardar(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        from cripta.adaptadores.Network_Adapter import NetworkAdapter
        from cripta.controlador.Aplicacion import Aplicacion
        from pruebas.test_inventario import FuentePrueba
        from pruebas.test_replay import firma

        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "partida.bin"
            app = Aplicacion(FuentePrueba(), ruta_guardado=ruta)
            self.assertTrue(app.iniciar_partida("Jugador", "42", "cripta-01").ok)
            red = NetworkAdapter()
            red.fijar_presupuesto(1)
            red._requests_made = 1
            app._cripta_service._data_source = red
            self.assertTrue(app.presupuesto_agotado)
            with patch("requests.get") as solicitar:
                self.assertTrue(app.esperar().ok)
                self.assertTrue(app.mover("N").ok)
                self.assertTrue(app.mover("S").ok)
                # Simula una sala del mapa cuyo contenido aún no se descargó.
                app._salas.obtener(2).contenido_cargado = False
                antes = firma(app)
                resultado = app.mover("N")
                self.assertFalse(resultado.ok)
                self.assertIn("Presupuesto", resultado.motivo)
                self.assertEqual(firma(app), antes)
                self.assertTrue(app.estado_partida().activa)
                self.assertFalse(app.estado_partida().derrota)
                self.assertTrue(app.guardar().ok)
                self.assertTrue(ruta.is_file())
                app.terminar()
                solicitar.assert_not_called()
            self.assertEqual(red.requests_made, 1)

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
