"""Registro de la partida y reproducción de «ir a» (US7)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pruebas.apoyo_niebla import FuenteNiebla, sala
from cripta.controlador.Aplicacion import Aplicacion
from cripta.replay.reproductor import Cabecera, ErrorRegistro, RegistroPartida, leer_partida, reproducir


class FuenteRegistro(FuenteNiebla):
    """La fuente de las pruebas de niebla con versión de catálogo, que el registro exige."""

    def get_catalog_version(self):
        return {"version": "catalogo-niebla-1"}


def _esqueleto():
    """1 a 2 a 3 a 4 en línea, con una vecina 5 al este de 3."""
    return [
        sala(1, [["N", 2]]),
        sala(2, [["S", 1], ["N", 3]]),
        sala(3, [["S", 2], ["N", 4], ["E", 5]]),
        sala(4, [["S", 3]]),
        sala(5, [["O", 3]]),
    ]


def _fuente():
    return FuenteRegistro(_esqueleto(), sala_inicial=1, sala_salida=4)


def _lineas(ruta):
    return Path(ruta).read_text(encoding="utf-8").splitlines()


class PruebasRegistroIrA(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory(prefix="cripta-registro-ir-a-")
        self.addCleanup(self.temporal.cleanup)
        self.carpeta = Path(self.temporal.name)

    def _partida(self):
        """Partida con registro que explora 1 a 4 y vuelve a 1 (seis movimientos ordinarios)."""
        app = Aplicacion(_fuente(), carpeta_logs=self.carpeta)
        resultado = app.iniciar_partida("Jugador", "42", "cripta-01")
        self.assertTrue(resultado.ok, resultado.motivo)
        for direccion in ["N", "N", "N", "S", "S", "S"]:
            self.assertTrue(app.mover(direccion).ok)
        return app

    def test_us7_1_pasos_individuales_y_comentario(self):
        """FR-033: un viaje deja `# ir_a <sala>` antes del primer paso y un `mover` por paso;
        una orden rechazada no escribe nada."""
        app = self._partida()
        ruta = app._partida.registro.ruta
        antes = _lineas(ruta)
        for orden in [99, "x", 1, 5]:      # no existe, no entero, sala actual, no explorada
            self.assertFalse(app.ir_a(orden).ok)
        self.assertEqual(_lineas(ruta), antes)
        resultado = app.ir_a_completo(4)
        self.assertEqual(resultado.motivo, "llegada")
        nuevas = _lineas(ruta)[len(antes):]
        self.assertEqual(nuevas, ["# ir_a 4", '["mover", "N"]', '["mover", "N"]', '["mover", "N"]'])
        self.assertEqual(nuevas.count("# ir_a 4"), 1)      # una sola vez por orden aceptada
        # el comentario se escribe al aceptar la orden, antes de avanzar
        app.ir_a(1)
        self.assertEqual(_lineas(ruta)[-1], "# ir_a 1")

    def test_us7_2_reproduccion_ignora_comentarios(self):
        """FR-033 y SC-005: reproducir llega al mismo mapa conocido y al mismo estado final con y
        sin los comentarios."""
        app = self._partida()
        self.assertEqual(app.ir_a_completo(4).motivo, "llegada")
        self.assertEqual(app.ir_a_completo(2).motivo, "llegada")
        app.terminar()
        ruta = app._partida.registro.ruta
        lineas = _lineas(ruta)
        self.assertEqual(len([t for t in lineas if t.startswith("#")]), 2)
        sin = self.carpeta / "sin_comentarios.log"
        sin.write_text("\n".join(t for t in lineas if not t.startswith("#")) + "\n", encoding="utf-8")

        def estado(replay):
            c = replay._exploracion.conocimiento
            return [replay.mapa_conocido(), c.instantanea(), replay._jugador.sala,
                    replay._simulacion.reloj.tiempo_actual, replay._jugador.vida,
                    replay.estado_partida().acciones_ejecutadas]

        con_comentarios = reproducir(ruta, [_fuente()])
        sin_comentarios = reproducir(sin, [_fuente()])
        self.assertEqual(estado(con_comentarios), estado(app))
        self.assertEqual(estado(sin_comentarios), estado(app))
        self.assertEqual(estado(con_comentarios), estado(sin_comentarios))

    def test_comentar_y_lector(self):
        """FR-033: `comentar` antepone `# ` y aplana saltos; el lector omite comentarios, cuenta
        sus líneas y sigue rechazando líneas vacías o inválidas."""
        registro = RegistroPartida(self.carpeta)
        with self.assertRaises(RuntimeError):      # sin encabezado, igual que `anexar`
            registro.comentar("ir_a 3")
        with self.assertRaises(RuntimeError):
            registro.anexar("esperar")
        registro.iniciar(Cabecera("cripta-01", "v1", "c1", 7, "Ana", 25))
        registro.anexar("esperar")
        registro.comentar("ir_a 3")
        registro.comentar("uno\ndos\ntres")
        registro.anexar("esperar")
        lineas = _lineas(registro.ruta)
        self.assertEqual(lineas[2], "# ir_a 3")
        self.assertEqual(lineas[3], "# uno dos tres")
        cabecera, acciones = leer_partida(registro.ruta)
        self.assertEqual(acciones, [["esperar", None], ["esperar", None]])
        # comentario con espacios iniciales y un comentario manual de evidencia
        with registro.ruta.open("a", encoding="utf-8") as archivo:
            archivo.write("   # indentado\n# FR-028 escenario: sala con enemigos dormidos\n")
        self.assertEqual(len(leer_partida(registro.ruta)[1]), 2)
        # el número de línea de un error cuenta los comentarios
        with registro.ruta.open("a", encoding="utf-8") as archivo:
            archivo.write('["volar", null]\n')
        with self.assertRaisesRegex(ValueError, f"linea {len(_lineas(registro.ruta))}"):
            leer_partida(registro.ruta)
        # una línea vacía sigue siendo inválida
        vacia = self.carpeta / "vacia.log"
        vacia.write_text(_lineas(registro.ruta)[0] + "\n# nota\n\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "linea 3"):
            leer_partida(vacia)
        # `ir_a` no es una acción válida: solo existe como comentario
        accion = self.carpeta / "accion.log"
        accion.write_text(_lineas(registro.ruta)[0] + '\n["ir_a", "3"]\n', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "linea 2"):
            leer_partida(accion)

    def test_registrar_comentario_falla_como_una_accion(self):
        """FR-033: un error de disco al comentar detiene la sesión como `registrar_accion`."""
        app = self._partida()
        with patch.object(app._partida.registro, "comentar", side_effect=OSError("disco")):
            with self.assertRaises(ErrorRegistro):
                app._partida.registrar_comentario("ir_a 4")
        self.assertFalse(app.estado_partida().activa)
        sin_registro = Aplicacion(_fuente())
        sin_registro.iniciar_partida("Jugador", "42", "cripta-01", registrar=False, verificar=False)
        sin_registro._partida.registrar_comentario("ir_a 4")     # sin registro: no hace nada


if __name__ == "__main__":
    unittest.main()
