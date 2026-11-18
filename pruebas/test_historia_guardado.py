"""Línea de tiempo y guardado binario (spec 004, US5)."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pruebas.apoyo_linea import FuenteLinea, TIPO_PERGAMINO, armar, contenidos, esqueleto, foto, foto_resumen, jugar
from cripta.controlador.Aplicacion import Aplicacion
from cripta.controlador.guardado.Datos import Cuerpo
from cripta.controlador.guardado.Formato import ID_GLOBAL
from cripta.estructuras.Guardado_Binario import Guardado_Binario
from cripta.estructuras.serializacionBinaria import EscritorBinario


def _consultas(app):
    n = app._linea.linea.acciones()
    fin = app._simulacion.reloj.tiempo_actual
    return [f"#{k}" for k in range(1, n + 2)] + [str(t) for t in range(0, fin + 1, 41)]


def _nueva(k=None):
    return Aplicacion(FuenteLinea(esqueleto(), 1, 6, contenidos()), checkpoint_cada=k)


class TestGuardadoLinea(unittest.TestCase):
    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.ruta = Path(self.carpeta.name) / "partida.bin"

    def tearDown(self):
        self.carpeta.cleanup()

    def test_guardar_y_cargar_conserva_la_linea(self):
        """FR-024: después de cargar, toda consulta da el mismo resumen que antes de guardar."""
        app = jugar(armar(k=4), 50)
        antes = [foto_resumen(app.historia(q).resumen) for q in _consultas(app)]
        self.assertTrue(app.guardar(self.ruta).ok)
        cargada = _nueva()
        self.assertTrue(cargada.cargar(self.ruta).ok)
        despues = [foto_resumen(cargada.historia(q).resumen) for q in _consultas(app)]
        self.assertEqual(despues, antes)

    def test_mapa_conocido_identico(self):
        """FR-025: el mapa conocido cargado es idéntico, incluidas las puertas recordadas."""
        app = jugar(armar(k=4), 50)
        mapa = repr(app.mapa_conocido())
        conocimiento = app._exploracion.conocimiento.instantanea()
        self.assertTrue(app.guardar(self.ruta).ok)
        cargada = _nueva()
        self.assertTrue(cargada.cargar(self.ruta).ok)
        self.assertEqual(repr(cargada.mapa_conocido()), mapa)
        self.assertEqual(cargada._exploracion.conocimiento.instantanea(), conocimiento)

    def test_rechaza_parte_uno(self):
        """FR-026 (Apéndice B, caso 6): un guardado de la Parte I se reporta incompatible y no se carga."""
        w = EscritorBinario()
        w.entero(2)                         # versión de cuerpo de la Parte I
        w.texto("Jugador")
        Guardado_Binario(str(self.ruta)).guardar("v1", [Cuerpo(ID_GLOBAL, w.a_bytes())])
        app = _nueva()
        resultado = app.cargar(self.ruta)
        self.assertFalse(resultado.ok)
        self.assertIn("Parte I", resultado.motivo)
        self.assertIn("incompatible", resultado.motivo)
        self.assertFalse(app.estado_partida().activa)

    def test_continua_y_respeta_k_guardado(self):
        """FR-027: la línea sigue tras cargar, las consultas previas funcionan y manda el K guardado."""
        app = jugar(armar(k=4), 30)
        previas = [foto_resumen(app.historia(q).resumen) for q in _consultas(app)]
        self.assertTrue(app.guardar(self.ruta).ok)
        cargada = _nueva(k=9)
        self.assertTrue(cargada.cargar(self.ruta).ok)
        self.assertEqual(cargada._linea.linea.k, 4)
        avisos = [m.texto for m in cargada.bitacora().ultimos() if m is not None]
        self.assertTrue(any("Se ignora --checkpoint-cada 9" in texto for texto in avisos))
        jugar(cargada, 20, semilla=3)
        n = cargada._linea.linea.acciones()
        self.assertEqual(foto_resumen(cargada.historia(f"#{n + 1}").resumen), foto(cargada))
        self.assertEqual([foto_resumen(cargada.historia(q).resumen) for q in _consultas(app)], previas)
        self.assertLessEqual(cargada._linea.linea.puntos_de_control(), n // 4 + 1)

    def test_retroceso_vacio_al_cargar(self):
        """FR-034: al cargar, el pergamino no revierte acciones anteriores a la carga."""
        app = armar(k=4)
        while sum(1 for i in app.inventario().items() if i.tipo_id == TIPO_PERGAMINO) < 2:
            objeto = next(o for o in app.estado_partida().objetos_suelo if o.tipo_id == TIPO_PERGAMINO)
            self.assertTrue(app.recoger(objeto.id).ok)
        jugar(app, 5)
        self.assertTrue(app.guardar(self.ruta).ok)
        cargada = _nueva()
        self.assertTrue(cargada.cargar(self.ruta).ok)
        n = cargada._linea.linea.acciones()
        self.assertFalse(cargada.usar_pergamino().ok)
        self.assertEqual(cargada._linea.linea.acciones(), n)
        self.assertTrue(cargada.esperar().ok)
        self.assertTrue(cargada.usar_pergamino().ok)
        self.assertEqual(cargada._linea.linea.acciones(), n)
        self.assertEqual(foto_resumen(cargada.historia(f"#{n + 1}").resumen), foto(cargada))


if __name__ == "__main__":
    unittest.main()
