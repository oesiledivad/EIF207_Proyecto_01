"""Pruebas de la verificación de resolubilidad al iniciar una partida (historia US3).

Cada prueba arma su propio esqueleto mínimo con ids genéricos; no se usa ningún
dato de una cripta concreta (FR-029). La fuente falsa solo toma del paquete
`datos_offline` los datos generales (lectura), nunca escribe en él.
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cripta.adaptadores.AdaptadorOffline import AdaptadorOffline
from cripta.adaptadores.Crypt_Data_Source import PresupuestoAgotado
from cripta.controlador.Aplicacion import Aplicacion

CRIPTA = "cripta-01"
LLAVE = "llave-x"


class FuenteVerificable(AdaptadorOffline):
    """Dos salas: la 1 se conecta con la 2 por una puerta que exige `LLAVE`.

    Args:
        llaves: Respuesta de `key_locations`; None hace que la fuente no tenga llaves.
        falla: Excepción que lanza `key_locations` en vez de responder.
    """

    def __init__(self, llaves=None, falla=None):
        super().__init__(Path(__file__).resolve().parents[1] / "datos_offline")
        self.llaves = llaves
        self.falla = falla
        self.consultas_llaves = 0

    def key_locations(self, cid):
        self.consultas_llaves += 1
        if self.falla is not None:
            raise self.falla
        if self.llaves is None:
            raise FileNotFoundError("Sin datos de llaves en la fuente de prueba.")
        return self.llaves

    def crypta_details(self, cid):
        datos = super().crypta_details(cid)
        datos.update(salas_total=2, sala_inicial=1, sala_salida=2, llave_salida=LLAVE)
        return datos

    def list_rooms(self, cid, pagina):
        return {"salas": [
            {"id": 1, "nombre": "Inicio",
             "salidas": {"N": {"sala": 2, "cerrada": True, "llave": LLAVE}}},
            {"id": 2, "nombre": "Salida", "salidas": {"S": {"sala": 1, "cerrada": False}}},
        ], "total_paginas": 1}

    def room_content(self, cid, ids):
        return {"contenido": [
            {"sala": sid, "enemigos": [], "objetos": [], "trampas": []} for sid in ids
        ]}


def llaves_resolubles() -> dict:
    """La llave está en la sala 1: se obtiene sin abrir nada."""
    return {"llaves": [{"id": LLAVE, "sala": 1}]}


def llaves_en_ciclo() -> dict:
    """La llave está detrás de la puerta que ella misma abre."""
    return {"llaves": [{"id": LLAVE, "sala": 2}]}


class PruebasInicioVerificacion(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory(prefix="cripta-inicio-test-")
        self.addCleanup(self.temporal.cleanup)

    def iniciar(self, fuente, **opciones):
        """Inicia con registro en una carpeta temporal y devuelve (app, resultado)."""
        app = Aplicacion(fuente, carpeta_logs=self.temporal.name)
        return app, app.iniciar_partida("Jugador", "42", CRIPTA, **opciones)

    def archivos_registro(self) -> list[str]:
        return [p.name for p in Path(self.temporal.name).iterdir()]

    def textos_bitacora(self, app) -> str:
        texto = ""
        for mensaje in app.bitacora().ultimos():
            texto += mensaje.texto + "\n"
        return texto

    def test_us3_1_apendice_b_bloqueada_sin_forzar(self):
        """FR-015, SC-007: no resoluble sin forzar no inicia, no crea registro y explica."""
        app, resultado = self.iniciar(FuenteVerificable(llaves_en_ciclo()))
        self.assertFalse(resultado.ok)
        self.assertFalse(app.estado_partida().activa)
        self.assertIsNone(app._partida.registro.ruta)
        self.assertEqual(self.archivos_registro(), [])
        self.assertIn("NO RESOLUBLE", resultado.motivo)
        self.assertIn("sala 1 salida N hacia sala 2 exige " + LLAVE, resultado.motivo)

    def test_us3_2_forzada_inicia(self):
        """FR-016: con forzar la partida inicia con el veredicto negativo y el reporte en la bitácora."""
        app, resultado = self.iniciar(FuenteVerificable(llaves_en_ciclo()), forzar=True)
        self.assertTrue(resultado.ok, resultado.motivo)
        self.assertTrue(app.estado_partida().activa)
        self.assertIn("NO RESOLUBLE", resultado.aviso)
        self.assertEqual(resultado.verificacion.estado, "no_resoluble")
        self.assertIn("exige " + LLAVE, self.textos_bitacora(app))

    def test_us3_3_resoluble_muestra_resultado(self):
        """FR-014: una cripta resoluble inicia sola y el aviso trae veredicto y orden de llaves."""
        app, resultado = self.iniciar(FuenteVerificable(llaves_resolubles()))
        self.assertTrue(resultado.ok, resultado.motivo)
        self.assertEqual(resultado.verificacion.estado, "resoluble")
        self.assertIn("RESOLUBLE", resultado.aviso)
        self.assertNotIn("NO RESOLUBLE", resultado.aviso)
        self.assertIn("1. " + LLAVE + " en sala 1", resultado.aviso)

    def test_us3_4_sin_ubicacion_no_verificada(self):
        """FR-022: sin ubicación de llaves no hay veredicto, con y sin forzar."""
        for forzar in (False, True):
            with self.subTest(forzar=forzar):
                app, resultado = self.iniciar(FuenteVerificable(None), forzar=forzar)
                self.assertTrue(resultado.ok, resultado.motivo)
                self.assertEqual(resultado.aviso, "resolubilidad no verificada")
                minusculas = resultado.aviso.lower()
                self.assertNotIn("resoluble", minusculas)
                self.assertEqual(resultado.verificacion.estado, "no_verificable")

    def test_presupuesto_agotado_da_no_verificada(self):
        """FR-019, FR-022: si el presupuesto se agota en la consulta de llaves no hay veredicto."""
        fuente = FuenteVerificable(falla=PresupuestoAgotado("presupuesto agotado"))
        app, resultado = self.iniciar(fuente)
        self.assertTrue(resultado.ok, resultado.motivo)
        self.assertEqual(resultado.aviso, "resolubilidad no verificada")
        self.assertNotIn("resoluble", resultado.aviso.lower())
        self.assertEqual(fuente.consultas_llaves, 1)

    def test_replay_y_carga_no_verifican(self):
        """FR-016 y supuestos: con verificar=False no se consultan llaves ni se bloquea."""
        fuente = FuenteVerificable(llaves_en_ciclo())
        app, resultado = self.iniciar(fuente, verificar=False)
        self.assertTrue(resultado.ok, resultado.motivo)
        self.assertEqual(fuente.consultas_llaves, 0)
        self.assertEqual(resultado.aviso, "")
        self.assertIsNone(resultado.verificacion)


if __name__ == "__main__":
    unittest.main()
