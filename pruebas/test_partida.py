"""Inicio y puertas en el flujo de partida, sin red ni cambios a datos offline."""
import tempfile
import unittest

from cripta.controlador.Aplicacion import Aplicacion
from cripta.controlador.PartidaControlador import PartidaControlador
from cripta.replay.reproductor import reproducir
from pruebas.test_replay import FuenteReplay, firma


class FuentePuertas(FuenteReplay):
    def list_rooms(self, cid, pagina):
        datos = super().list_rooms(cid, pagina)
        datos["salas"][0]["salidas"]["N"].update(
            cerrada=True, llave="itm_llave_bronce", cierre_automatico=300)
        return datos

    def room_content(self, cid, ids):
        datos = super().room_content(cid, ids)
        for sala in datos["contenido"]:
            sala["enemigos"] = []
            sala["trampas"] = []
            if sala["sala"] == 1:
                sala["objetos"] = ["itm_llave_bronce", "itm_pergamino_retroceso",
                                   "itm_pergamino_retroceso"]
        return datos


class PruebasPartida(unittest.TestCase):
    def test_validar_inicio(self):
        self.assertEqual(PartidaControlador.validar_inicio(" Jugador ", " 0 ", "cripta"),
                         ["Jugador", 0])
        for nombre, semilla, cripta in ((" ", "1", "c"), ("J", "1", ""),
                                       ("J", "-1", "c"), ("J", "²", "c"),
                                       ("J", "abc", "c")):
            with self.subTest(semilla=semilla), self.assertRaises(ValueError):
                PartidaControlador.validar_inicio(nombre, semilla, cripta)
        self.assertGreater(PartidaControlador.validar_inicio("J", "", "c")[1], 0)

    def test_puertas_retroceso_y_replay(self):
        with tempfile.TemporaryDirectory() as carpeta:
            app = Aplicacion(FuentePuertas(), carpeta_logs=carpeta)
            self.assertTrue(app.iniciar_partida("Jugador", "42", "cripta-01").ok)
            for objeto in list(app.estado_partida().objetos_suelo):
                self.assertTrue(app.recoger(objeto.id).ok)
            puerta = app._salas.obtener(1).salidas.obtener("N")
            self.assertTrue(app.abrir("N").ok)
            self.assertFalse(puerta.cerrada)
            self.assertTrue(app.usar_pergamino().ok)
            self.assertTrue(puerta.cerrada)
            self.assertIsNone(puerta.evento_cierre)
            self.assertTrue(app.abrir("N").ok)
            cierre = puerta.evento_cierre
            for _ in range(3):
                self.assertTrue(app.esperar().ok)
            self.assertTrue(puerta.cerrada)
            self.assertTrue(app.usar_pergamino().ok)
            self.assertFalse(puerta.cerrada)
            self.assertIs(puerta.evento_cierre, cierre)
            self.assertTrue(app.esperar().ok)
            self.assertTrue(puerta.cerrada)
            replay = reproducir(app._partida.registro.ruta, [FuentePuertas()])
            self.assertEqual(firma(replay), firma(app))
            otra = replay._salas.obtener(1).salidas.obtener("N")
            self.assertEqual((otra.cerrada, otra.evento_cierre),
                             (puerta.cerrada, puerta.evento_cierre))
            self.assertIsNotNone(cierre)
