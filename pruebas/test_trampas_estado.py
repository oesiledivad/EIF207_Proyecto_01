"""La vista recibe las trampas de la sala actual (para dibujarlas) sin tocar la simulación."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cripta.adaptadores.AdaptadorOffline import AdaptadorOffline
from cripta.controlador.Aplicacion import Aplicacion

DATOS = Path(__file__).resolve().parents[1] / "datos_prueba"


class PruebasTrampasEnEstado(unittest.TestCase):
    def test_trampa_de_la_sala_actual_y_veneno(self):
        app = Aplicacion(AdaptadorOffline(DATOS))
        self.assertTrue(app.iniciar_partida("Jugador", "42", "cripta-02").ok)
        self.assertEqual(app.estado_partida().trampas, [])
        while app.estado_partida().sala_actual_id < 10 and not app.estado_partida().terminada:
            estado = app.estado_partida()
            if estado.enemigos:
                app.atacar(estado.enemigos[0].id)
            else:
                app.mover("N")
        estado = app.estado_partida()
        self.assertEqual(estado.sala_actual_id, 10)
        self.assertEqual([[t.id, t.tipo] for t in estado.trampas], [["t-cripta-02-3", "trp_dardos"]])
        self.assertFalse(estado.trampas[0].activa)                 # se disparó al entrar
        self.assertTrue(any(e.startswith("Envenenado") for e in estado.efectos))
        self.assertTrue(all(e.tipo for e in estado.enemigos))      # la vista elige sprite por tipo


if __name__ == "__main__":
    unittest.main()
