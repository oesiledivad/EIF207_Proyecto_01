"""Contadores reversibles, finalizacion y persistencia atomica."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from pruebas.test_retroceso import FuenteRetroceso
from cripta.adaptadores.Puntajes import Puntaje, TablaPuntajes
from cripta.controlador.Aplicacion import Aplicacion


class PruebasPuntajes(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory(prefix="cripta-puntajes-test-")
        self.addCleanup(temporal.cleanup)
        self.ruta = Path(temporal.name) / "puntajes.json"
        self.app = Aplicacion(FuenteRetroceso(), ruta_puntajes=self.ruta)
        self.assertTrue(self.app.iniciar_partida("Jugador", "42", "cripta-01").ok)

    def test_acciones_validas_navegacion_y_retroceso(self):
        app = self.app
        self.assertFalse(app.recoger("no-existe").ok)
        self.assertEqual(app.estado_partida().acciones_ejecutadas, 0)
        self.assertTrue(app.recoger("sala-1-objeto-0").ok)
        self.assertTrue(app.siguiente_item().ok)
        self.assertTrue(app.anterior_item().ok)
        self.assertEqual(app.estado_partida().acciones_ejecutadas, 1)
        self.assertTrue(app.mover("N").ok)
        enemigo = app._salas.obtener(2).enemigos[0]
        enemigo.vida = 1
        self.assertTrue(app.atacar("rata").ok)
        self.assertEqual(app.estado_partida().enemigos_derrotados, 1)
        self.assertEqual(app.estado_partida().acciones_ejecutadas, 3)
        self.assertTrue(app.usar_pergamino().ok)
        self.assertEqual(app.estado_partida().enemigos_derrotados, 0)
        self.assertEqual(app.estado_partida().acciones_ejecutadas, 2)
        self.assertFalse(self.ruta.exists())

    def test_abandono_metadatos_y_no_duplica(self):
        self.app.esperar()
        self.app.terminar()
        self.app.terminar()
        registros = TablaPuntajes(self.ruta).leer()
        self.assertEqual(len(registros), 1)
        p = registros[0]
        self.assertEqual((p.nombre_jugador, p.cripta_id, p.version_cripta),
                         ("Jugador", "cripta-01", self.app.estado_partida().version_cripta))
        self.assertEqual((p.acciones, p.enemigos_derrotados, p.tiempo_final, p.resultado),
                         (1, 0, 100, "abandono"))
        self.assertFalse(self.app.esperar().ok)
        self.assertEqual(self.app.estado_partida().acciones_ejecutadas, 1)

    def test_derrota_por_trampa_registra_una_vez(self):
        self.app._jugador.vida = 1
        self.assertTrue(self.app.mover("N").ok)
        estado = self.app.estado_partida()
        self.assertEqual(estado.jugador_vida, 0)
        self.assertTrue(estado.derrota)
        self.assertTrue(estado.terminada)
        self.assertFalse(estado.activa)
        self.app.terminar()
        registros = TablaPuntajes(self.ruta).leer()
        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0].resultado, "derrota")

    def test_no_declara_victoria_sin_apertura_con_llave(self):
        self.assertTrue(self.app.mover("N").ok)
        self.assertFalse(self.app.estado_partida().victoria)
        self.assertFalse(self.app.estado_partida().terminada)
        self.assertFalse(self.ruta.exists())

    def test_error_no_corrompe_y_permite_reintento(self):
        tabla = TablaPuntajes(self.ruta)
        tabla.registrar(Puntaje("anterior", "Anterior", "otra", "1", 2, 0, 200, "abandono"))
        antes = self.ruta.read_bytes()
        with patch("cripta.adaptadores.Puntajes.os.replace", side_effect=OSError("disco lleno")):
            self.app.terminar()
        self.assertEqual(self.ruta.read_bytes(), antes)
        self.assertIn("disco lleno", self.app.error_puntaje)
        self.assertEqual(list(self.ruta.parent.iterdir()), [self.ruta])
        self.app.terminar()
        self.assertEqual(len(tabla.leer()), 2)
        self.assertEqual(self.app.error_puntaje, "")

    def test_tabla_invalida_no_se_sobreescribe(self):
        for datos in ("incompleto", "{}", '[{"partida_id": 1}]'):
            self.ruta.write_text(datos, encoding="utf-8")
            with self.assertRaises(ValueError):
                TablaPuntajes(self.ruta).registrar(
                    Puntaje("nueva", "Jugador", "cripta", "1", 0, 0, 0, "abandono"))
            self.assertEqual(self.ruta.read_text(encoding="utf-8"), datos)

    def test_ordenamientos_propios_y_idempotencia_por_partida(self):
        tabla = TablaPuntajes(self.ruta)
        a = Puntaje("a", "A", "cripta", "1", 5, 2, 400, "derrota")
        b = Puntaje("b", "B", "cripta", "1", 3, 2, 400, "derrota")
        c = Puntaje("c", "C", "cripta", "1", 8, 1, 700, "victoria")
        for puntaje in (a, b, c, a):
            tabla.registrar(puntaje)
        self.assertEqual([p.partida_id for p in tabla.ordenados()], ["c", "b", "a"])
