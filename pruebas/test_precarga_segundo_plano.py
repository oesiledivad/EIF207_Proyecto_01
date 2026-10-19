"""Precarga en segundo plano (4.2): no congela la ventana y da el mismo resultado."""
import random
import sys
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cripta.adaptadores.AdaptadorOffline import AdaptadorOffline
from cripta.controlador.Aplicacion import Aplicacion
from pruebas.test_replay import firma

DATOS = Path(__file__).resolve().parents[1] / "datos_prueba"
CRIPTA = "cripta-stormlight"


class FuenteLenta(AdaptadorOffline):
    """Simula la latencia del servicio (~400 ms en el enunciado aquí más corta)."""

    def __init__(self, espera=0.0):
        super().__init__(DATOS)
        self.espera = espera

    def room_content(self, cid, ids):
        time.sleep(self.espera)
        return super().room_content(cid, ids)

    def catalog(self, ids):
        time.sleep(self.espera)
        return super().catalog(ids)


def recorrer(app, pasos=40, semilla=7):
    """Camina eligiendo puertas abiertas con un azar propio; devuelve firmas y tiempos de mover."""
    azar = random.Random(semilla)
    firmas, tiempos = [], []
    for _ in range(pasos):
        estado = app.estado_partida()
        if estado.terminada:
            break
        abiertas = sorted(v.direccion for v in estado.vecindad if v.transitable)
        if abiertas:
            inicio = time.perf_counter()
            app.mover(azar.choice(abiertas))
            tiempos.append(time.perf_counter() - inicio)
        else:
            app.esperar()
        # La siguiente acción incorporaría lo pendiente antes de simular; se adelanta
        # aquí solo para poder comparar las salas en el mismo instante.
        app._cripta_service.completar_precarga()
        firmas.append(firma(app))
    app.terminar()
    return [firmas, tiempos]


class PruebasPrecargaSegundoPlano(unittest.TestCase):
    def nueva(self, espera=0.0, segundo_plano=False):
        app = Aplicacion(FuenteLenta(espera))
        if segundo_plano:
            app.activar_precarga_en_segundo_plano()
        self.assertTrue(app.iniciar_partida("Jugador", "42", CRIPTA).ok)
        return app

    def test_mismo_resultado_que_sincronico(self):
        sincronico = recorrer(self.nueva())[0]
        segundo_plano = recorrer(self.nueva(espera=0.01, segundo_plano=True))[0]
        self.assertEqual(sincronico, segundo_plano)

    def test_mover_no_espera_la_precarga(self):
        espera = 0.15
        tiempos = recorrer(self.nueva(espera=espera, segundo_plano=True), pasos=25)[1]
        self.assertTrue(tiempos)
        # Sincrónico, cada precarga congelaría el movimiento ~2*espera (contenido + catálogo).
        lentos = [t for t in tiempos if t >= espera]
        self.assertLessEqual(len(lentos), len(tiempos) // 4, tiempos)


if __name__ == "__main__":
    unittest.main()
