"""La partida no continúa con fichas en uso sin protección."""
import unittest

from cripta.controlador.Aplicacion import Aplicacion
from pruebas.test_inventario import FuentePrueba


class FuenteCapacidad(FuentePrueba):
    def room_content(self, cid, ids):
        respuesta = super().room_content(cid, ids)
        for sala in respuesta["contenido"]:
            if sala["sala"] == 2:
                sala["objetos"] = ["itm_antorcha", "itm_antidoto", "itm_llave_bronce"]
        return respuesta


class PruebasLimitesCache(unittest.TestCase):
    def test_inicio_rechaza_capacidad_insuficiente(self):
        app = Aplicacion(FuentePrueba(), capacidad_cache=1)
        resultado = app.iniciar_partida("Jugador", "42", "cripta-01")
        self.assertFalse(resultado.ok)
        self.assertIn("--cache-size", resultado.motivo)
        self.assertFalse(app.estado_partida().activa)
        self.assertFalse(app.esperar().ok)

    def test_inicio_con_capacidad_exacta_protege_todos_los_tipos(self):
        app = Aplicacion(FuentePrueba(), capacidad_cache=3)
        self.assertTrue(app.iniciar_partida("Jugador", "42", "cripta-01").ok)
        for tipo in app._tipos_activos():
            self.assertTrue(app._cripta_service._cache_fichas.esta_en_uso(tipo))

    def test_movimiento_rechazado_conserva_sala_tiempo_y_protecciones(self):
        app = Aplicacion(FuenteCapacidad(), capacidad_cache=3)
        self.assertTrue(app.iniciar_partida("Jugador", "42", "cripta-01").ok)
        self.assertTrue(app.recoger("sala-1-objeto-0").ok)
        tiempo = app.estado_partida().reloj_virtual
        acciones = app.estado_partida().acciones_ejecutadas
        self.assertFalse(app.mover("N").ok)
        self.assertEqual(app.estado_partida().sala_actual_id, 1)
        self.assertEqual(app.estado_partida().reloj_virtual, tiempo)
        self.assertEqual(app.estado_partida().acciones_ejecutadas, acciones)
        for tipo in app._tipos_activos():
            self.assertTrue(app._cripta_service._cache_fichas.esta_en_uso(tipo))


if __name__ == "__main__":
    unittest.main()
