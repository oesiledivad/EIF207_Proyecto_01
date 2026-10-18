"""Selección de guardados por jugador sin cambiar el formato binario de P1."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cripta.controlador.Aplicacion import Aplicacion
from cripta.controlador.guardado import leer_partida
from pruebas.test_replay import FuenteReplay


class AdaptadorOffline(FuenteReplay):
    """Fuente local sintética, reconocida por el servicio como modo offline."""

    def crypta_details(self, cid):
        datos = super().crypta_details("cripta-01")
        datos["id"] = cid
        return datos

    def list_rooms(self, cid, pagina):
        return super().list_rooms("cripta-01", pagina)

    def room_content(self, cid, ids):
        return super().room_content("cripta-01", ids)


class PruebasGuardados(unittest.TestCase):
    """Comprueba identidad de archivos y continuidad al volver a guardar."""

    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.raiz = Path(self.temporal.name)
        self.app = Aplicacion(FuenteReplay(), carpeta_logs=self.raiz)
        self.app.ruta_guardado = self.raiz / "partida_guardada.bin"

    def iniciar_y_guardar(self, nombre):
        """Inicia una partida independiente y devuelve su archivo guardado."""
        self.assertTrue(self.app.iniciar_partida(nombre, "42", "cripta-01").ok)
        self.assertTrue(self.app.guardar().ok)
        return self.app._guardado.actual

    def test_cada_partida_tiene_su_archivo(self):
        rutas = [self.iniciar_y_guardar(nombre) for nombre in ["Ana", "Luis", "Ana"]]
        self.assertEqual(len(list((self.raiz / "guardadas").glob("*.bin"))), 3)
        self.assertNotEqual(rutas[0], rutas[2])
        self.assertTrue(all(ruta.parent == self.raiz / "guardadas" for ruta in rutas))
        nombres = [leer_partida(ruta).nombre_jugador for ruta in rutas]
        self.assertEqual(nombres, ["Ana", "Luis", "Ana"])
        descripciones = [descripcion for _, descripcion in self.app.listar_guardados()]
        self.assertTrue(any("Ana" in d and "cripta-01" in d for d in descripciones))
        self.assertTrue(any("Luis" in d and "sala 1" in d for d in descripciones))

    def test_volver_a_guardar_actualiza_la_misma_partida(self):
        ruta = self.iniciar_y_guardar("Ana")
        self.assertTrue(self.app.esperar().ok)
        self.assertTrue(self.app.guardar().ok)
        self.assertEqual(self.app._guardado.actual, ruta)
        self.assertEqual(len(self.app.listar_guardados()), 1)
        self.assertEqual(leer_partida(ruta).tiempo_actual, self.app.estado_partida().reloj_virtual)

    def test_cargar_y_guardar_no_sobrescribe_a_otro_jugador(self):
        ana = self.iniciar_y_guardar("Ana")
        luis = self.iniciar_y_guardar("Luis")
        bytes_luis = luis.read_bytes()
        self.assertTrue(self.app.cargar(ana).ok)
        self.assertTrue(self.app.esperar().ok)
        self.assertTrue(self.app.guardar().ok)
        self.assertEqual(self.app._guardado.actual, ana)
        self.assertEqual(luis.read_bytes(), bytes_luis)
        self.assertEqual(len(self.app.listar_guardados()), 2)

    def test_nueva_partida_reanuda_el_replay_despues_de_cargar(self):
        ruta = self.iniciar_y_guardar("Ana")
        registro_anterior = self.app._partida.registro.ruta
        self.assertTrue(self.app.cargar(ruta).ok)
        self.assertIsNone(self.app._partida.registro)
        self.assertTrue(self.app.iniciar_partida("Luis", "43", "cripta-01").ok)
        self.assertIsNotNone(self.app._partida.registro)
        self.assertNotEqual(self.app._partida.registro.ruta, registro_anterior)
        self.assertTrue(self.app.guardar().ok)
        self.assertNotEqual(self.app._guardado.actual, ruta)
        self.assertTrue(self.app.esperar().ok)
        self.app.terminar()
        self.assertEqual(self.app.puntajes()[0].nombre_jugador, "Luis")

    def test_ruta_anterior_e_ilegibles_aparecen_en_la_lista(self):
        legado = self.raiz / "partida_guardada.bin"
        self.app = Aplicacion(FuenteReplay(), carpeta_logs=self.raiz, ruta_guardado=legado)
        self.assertEqual(self.iniciar_y_guardar("Ana"), legado)
        carpeta = self.raiz / "guardadas"
        carpeta.mkdir()
        ilegible = carpeta / "incompleta.bin"
        ilegible.write_bytes(b"incompleto")
        guardados = self.app.listar_guardados()
        self.assertEqual(len(guardados), 2)
        self.assertTrue(any(ruta == legado and "Ana" in texto for ruta, texto in guardados))
        self.assertTrue(any(ruta == ilegible and "ilegible" in texto for ruta, texto in guardados))

    def test_nombre_del_jugador_no_puede_cambiar_la_carpeta(self):
        ruta = self.iniciar_y_guardar("../../otro/jugador")
        self.assertEqual(ruta.parent.resolve(), (self.raiz / "guardadas").resolve())
        self.assertEqual(leer_partida(ruta).nombre_jugador, "../../otro/jugador")

    def test_guardado_offline_no_consulta_la_cripta_en_red(self):
        local = Aplicacion(AdaptadorOffline(), carpeta_logs=self.raiz / "local")
        self.assertTrue(local.iniciar_partida("Local", "42", "cripta-custom").ok)
        self.assertTrue(local.guardar().ok)
        ruta = local._guardado.actual
        with patch.object(self.app._cripta_service, 'obtener_detalles') as consultar:
            resultado = self.app.cargar(ruta)
            self.assertFalse(resultado.ok)
            self.assertIn("offline", resultado.motivo)
            consultar.assert_not_called()
        with patch('cripta.controlador.GuardadoControlador.AdaptadorOffline', return_value=AdaptadorOffline()), \
             patch('cripta.controlador.GuardadoControlador.NetworkAdapter') as red:
            resultado, nueva = self.app.cargar_compatible(ruta)
            self.assertTrue(resultado.ok, resultado.motivo)
            self.assertIsNot(nueva, self.app)
            self.assertEqual(nueva.estado_partida().modo, "offline")
            self.assertEqual(nueva.estado_partida().cripta_id, "cripta-custom")
            self.assertFalse(self.app.estado_partida().activa)
            red.assert_not_called()

    def test_guardado_de_red_elige_red_desde_sesion_offline(self):
        ruta = self.iniciar_y_guardar("Red")
        local = Aplicacion(AdaptadorOffline(), carpeta_logs=self.raiz / "local")
        with patch('cripta.controlador.GuardadoControlador.NetworkAdapter', return_value=FuenteReplay()) as red:
            resultado, nueva = local.cargar_compatible(ruta)
            self.assertTrue(resultado.ok, resultado.motivo)
            self.assertEqual(nueva.estado_partida().modo, "red")
            self.assertFalse(local.estado_partida().activa)
            red.assert_called_once()

    def test_cambio_de_modo_fallido_conserva_la_partida_actual(self):
        self.iniciar_y_guardar("Original")
        local = Aplicacion(AdaptadorOffline(), carpeta_logs=self.raiz / "local")
        self.assertTrue(local.iniciar_partida("Local", "42", "cripta-custom").ok)
        self.assertTrue(local.guardar().ok)
        fuente = AdaptadorOffline()
        detalles = fuente.crypta_details("cripta-custom")
        detalles["version"] = "incompatible"
        with patch('cripta.controlador.GuardadoControlador.AdaptadorOffline', return_value=fuente), \
             patch.object(fuente, 'crypta_details', return_value=detalles):
            resultado, _ = self.app.cargar_compatible(local._guardado.actual)
        self.assertFalse(resultado.ok)
        self.assertTrue(self.app.estado_partida().activa)
        self.assertEqual(self.app.estado_partida().nombre_jugador, "Original")
