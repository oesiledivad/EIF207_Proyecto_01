"""Replay determinista y limites de entrada, sin red ni TUI."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from pruebas.test_retroceso import FuenteRetroceso
from cripta.bootstrap import main
from cripta.controlador.Aplicacion import Aplicacion
from cripta.replay.reproductor import Cabecera, RegistroPartida, ErrorRegistro, leer_partida, reproducir


class FuenteReplay(FuenteRetroceso):
    def get_catalog_version(self):
        return {"version": "catalogo-prueba-1"}

    def room_content(self, cid, ids):
        respuesta = super().room_content(cid, ids)
        for sala in respuesta["contenido"]:
            if sala["sala"] == 1:
                sala["objetos"].extend(["itm_daga_oxidada", "itm_coraza_cuero"])
        return respuesta


def firma(app):
    sim = app._simulacion
    jugador = app._jugador
    return (
        sim.reloj.tiempo_actual, sim.azar.getstate(), sim.agenda._secuencia_actual,
        jugador.vida, jugador.sala, jugador.velocidad, jugador.ataque, jugador.defensa,
        jugador.fin_veneno, jugador.antorcha_encendida,
        [(i.instancia_id, i.equipado) for i in app.inventario().items()],
        app.inventario().item_actual().instancia_id if app.inventario().item_actual() else None,
        [(s.id, s.ultimo_tiempo_visita,
          [(e.identificador, e.vida, e.sala) for e in s.enemigos],
          [(t.instancia, t.armada) for t in s.trampas],
          [(o.id, o.tipo_id) for o in s.objetos])
         for s in app._salas._datos if s is not None],
        [(e.tiempo_siguiente, e.secuencias, getattr(e.actor, "identificador", getattr(e.actor, "instancia", "")), e.tipo, e.valido)
         for e in sim.agenda._heap],
        len(app._gestor.historial), app.estado_partida().terminada,
        app.estado_partida().acciones_ejecutadas, app.estado_partida().enemigos_derrotados,
    )


class PruebasReplay(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory(prefix="cripta-replay-test-")
        self.addCleanup(self.temporal.cleanup)
        self.carpeta = Path(self.temporal.name)

    def iniciar(self):
        app = Aplicacion(FuenteReplay(), carpeta_logs=self.carpeta)
        resultado = app.iniciar_partida("Jugador", "42", "cripta-01")
        self.assertTrue(resultado.ok, resultado.motivo)
        return app

    def test_partida_completa_combate_inventario_y_dos_retrocesos(self):
        app = self.iniciar()
        for posicion in (0, 1, 8, 9, 10):
            self.assertTrue(app.recoger(f"sala-1-objeto-{posicion}").ok)
        self.assertTrue(app.equipar("sala-1-objeto-9").ok)
        self.assertTrue(app.equipar("sala-1-objeto-10").ok)
        self.assertTrue(app.siguiente_item().ok)
        self.assertTrue(app.anterior_item().ok)
        self.assertTrue(app.mover("N").ok)
        while app.estado_partida().enemigos:
            self.assertTrue(app.atacar("rata").ok)
        self.assertTrue(app.usar("sala-1-objeto-8").ok)
        self.assertTrue(app.mover("S").ok)
        self.assertTrue(app.soltar("sala-1-objeto-9").ok)
        self.assertTrue(app.esperar().ok)
        self.assertTrue(app.esperar().ok)
        self.assertTrue(app.usar_pergamino().ok)
        self.assertTrue(app.usar_pergamino().ok)
        app.terminar()
        replay = reproducir(app._partida.registro.ruta, [FuenteReplay()])
        self.assertEqual(firma(replay), firma(app))
        self.assertEqual(replay.solicitudes_usadas(), 0)
        cabecera, acciones = leer_partida(app._partida.registro.ruta)
        self.assertEqual(cabecera.semilla, 42)
        self.assertEqual(cabecera.version_catalogo, "catalogo-prueba-1")
        self.assertEqual(acciones[-3:], [["retroceder", None], ["retroceder", None], ["terminar", None]])

    def test_version_incompatible_y_copia_local_compatible(self):
        app = self.iniciar()
        vieja = FuenteReplay()
        vieja.get_catalog_version = lambda: {"version": "otra"}
        with patch.object(vieja, "room_content") as contenido:
            with self.assertRaisesRegex(ValueError, "reproduccion fiel"):
                reproducir(app._partida.registro.ruta, [vieja])
            contenido.assert_not_called()
        self.assertEqual(firma(reproducir(app._partida.registro.ruta, [vieja, FuenteReplay()])), firma(app))
        distinta = FuenteReplay()
        original = distinta.crypta_details
        distinta.crypta_details = lambda cid: {**original(cid), "version": "otra-cripta"}
        with self.assertRaisesRegex(ValueError, "reproduccion fiel"):
            reproducir(app._partida.registro.ruta, [distinta])

    def test_registro_append_no_reescribe_y_fallo_no_se_registra(self):
        app = self.iniciar()
        ruta = app._partida.registro.ruta
        anterior = ruta.read_bytes()
        self.assertFalse(app.recoger("no-existe").ok)
        self.assertEqual(ruta.read_bytes(), anterior)
        self.assertTrue(app.esperar().ok)
        self.assertTrue(ruta.read_bytes().startswith(anterior))
        otro = self.iniciar()
        self.assertNotEqual(otro._partida.registro.ruta, ruta)
        self.assertTrue(ruta.read_bytes().startswith(anterior))

    def test_error_disco_revierte_accion_y_detiene_sesion(self):
        app = self.iniciar()
        antes = firma(app)
        with patch.object(app._partida.registro, "anexar", side_effect=OSError("disco lleno")):
            with self.assertRaisesRegex(ErrorRegistro, "disco lleno"):
                app.esperar()
        self.assertEqual(firma(app), antes)
        self.assertFalse(app.estado_partida().activa)

    def test_log_invalido_o_truncado_rechazado_antes_de_iniciar(self):
        registro = RegistroPartida(self.carpeta)
        registro.iniciar(Cabecera("cripta-01", "1", "cat", 42, "Jugador", 25))
        cabecera = registro.ruta.read_text(encoding="utf-8")
        for accion in ('["__dict__", null]', '["mover", "X"]', '["recoger", 1]', '["esperar"'):
            registro.ruta.write_text(cabecera + accion + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "linea 2"):
                leer_partida(registro.ruta)
        registro.ruta.write_text('{}\n', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Encabezado"):
            leer_partida(registro.ruta)

    def test_cli_replay_sin_vista(self):
        app = self.iniciar()
        app.esperar()
        with patch("cripta.bootstrap._construir_data_source", return_value=FuenteReplay()):
            with patch("cripta.bootstrap.AlmacenDisco") as almacen:
                self.assertEqual(main(["--offline", "--replay", str(app._partida.registro.ruta)]), 0)
                almacen.assert_not_called()
        self.assertNotIn("cripta.vista.textual.app", sys.modules)

    def test_cli_con_archivos_offline_reales(self):
        import subprocess
        fuente = FuenteReplay()
        datos = self.carpeta / "datos"
        datos.mkdir()
        for nombre, respuesta in (
            ("cripta_cripta-01.json", fuente.crypta_details("cripta-01")),
            ("cripta_cripta-01_salas_1.json", fuente.list_rooms("cripta-01", 1)),
            ("cripta_cripta-01_contenido.json", fuente.room_content("cripta-01", [1, 2])),
            ("catalogo.json", fuente._leer("catalogo.json")),
            ("catalogo_version.json", fuente.get_catalog_version()),
        ):
            (datos / nombre).write_text(json.dumps(respuesta), encoding="utf-8")
        app = self.iniciar()
        app.mover("N")
        proceso = subprocess.run(
            [sys.executable, "-B", "-m", "cripta", "--offline", "--offline-dir", str(datos),
             "--replay", str(app._partida.registro.ruta)],
            capture_output=True, text=True,
        )
        self.assertEqual(proceso.returncode, 0, proceso.stderr)
        self.assertIn("Replay completado: sala=2", proceso.stdout)

    def test_offline_sin_manifest_version_usa_identidad_de_archivo(self):
        from cripta.adaptadores.AdaptadorOffline import AdaptadorOffline
        archivo = self.carpeta / "catalogo.json"
        archivo.write_text('{"entidades": []}', encoding="utf-8")
        fuente = AdaptadorOffline(self.carpeta)
        primera = fuente.get_catalog_version()
        self.assertEqual(primera, fuente.get_catalog_version())
        archivo.write_text('{"entidades": [{"id": "otra"}]}', encoding="utf-8")
        self.assertNotEqual(primera, fuente.get_catalog_version())

    def test_copia_compatible_si_falla_la_carga_de_red(self):
        app = self.iniciar()
        fuente = FuenteReplay()
        with patch.object(fuente, "room_content", side_effect=RuntimeError("datos no disponibles")):
            replay = reproducir(app._partida.registro.ruta, [fuente, FuenteReplay()])
        self.assertEqual(firma(app), firma(replay))

    def test_nombres_descriptivos_consecutivos_por_cripta(self):
        cabecera = Cabecera("cripta-01", "1", "cat", 42, "Jugador", 25)
        registro = RegistroPartida(self.carpeta)
        registro.iniciar(cabecera)
        primera = registro.ruta
        self.assertEqual(primera.name, "cripta_01_partida_00001.log")
        antes = primera.read_bytes()
        nuevo = RegistroPartida(self.carpeta)
        nuevo.iniciar(cabecera)
        self.assertEqual(nuevo.ruta.name, "cripta_01_partida_00002.log")
        self.assertEqual(primera.read_bytes(), antes)
        cabecera.cripta_id = "otra-cripta"
        nuevo.iniciar(cabecera)
        self.assertEqual(nuevo.ruta.name, "otra_cripta_partida_00001.log")
        cabecera.cripta_id = "../../cripta/externa"
        nuevo.iniciar(cabecera)
        self.assertEqual(nuevo.ruta.parent.resolve(), self.carpeta.resolve())
        self.assertNotIn("..", nuevo.ruta.name)

    def test_colision_de_archivo_no_sobreescribe(self):
        registro = RegistroPartida(self.carpeta)
        cabecera = Cabecera("cripta-01", "1", "cat", 42, "Jugador", 25)
        registro.iniciar(cabecera)
        anterior = registro.ruta
        contenido = anterior.read_bytes()
        siguiente = self.carpeta / "cripta_01_partida_00002.log"
        with patch.object(registro, "_siguiente_ruta", side_effect=[anterior, siguiente]):
            registro.iniciar(cabecera)
        self.assertEqual(registro.ruta, siguiente)
        self.assertEqual(anterior.read_bytes(), contenido)

    def test_puntajes_por_defecto_junto_al_log(self):
        app = self.iniciar()
        app.terminar()
        ruta = self.carpeta / "puntajes.json"
        self.assertTrue(ruta.exists())
        self.assertEqual(len(json.loads(ruta.read_text(encoding="utf-8"))), 1)
        self.assertEqual(app._partida.registro.ruta.parent, ruta.parent)
