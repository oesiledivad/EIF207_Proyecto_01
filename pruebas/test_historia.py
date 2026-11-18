"""Línea de tiempo: consultas `historia <t>` e `historia #k` (spec 004, US1, US2 y US6)."""
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pruebas.apoyo_linea import Anotador, armar, foto, foto_resumen, jugar
from cripta.bootstrap import main


def _tiempo(app):
    return app._simulacion.reloj.tiempo_actual


class TestConsulta(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = armar(k=4)
        cls.anotador = Anotador(cls.app)
        jugar(cls.app, 200, anotador=cls.anotador)

    def test_rechaza_t_futuro(self):
        """FR-004 (Apéndice B, caso 1): historia con t mayor que el reloj se rechaza y nada cambia."""
        app = self.app
        antes = [_tiempo(app), foto(app), app._linea.linea.acciones()]
        resultado = app.historia(str(_tiempo(app) + 1))
        self.assertFalse(resultado.ok)
        self.assertIn("posterior al reloj actual", resultado.motivo)
        self.assertEqual([_tiempo(app), foto(app), app._linea.linea.acciones()], antes)

    def test_eventos_mismo_instante(self):
        """FR-001 (Apéndice B, caso 3): con varios eventos en el mismo instante t, historia <t> muestra el
        estado después de todos ellos."""
        decisiones = [t for t, _ in self.anotador.decisiones]
        ultimo = []          # [t, foto tras el último evento de t, cuántos eventos]
        for t, f in self.anotador.eventos:
            if ultimo and ultimo[-1][0] == t:
                ultimo[-1][1] = f
                ultimo[-1][2] += 1
            else:
                ultimo.append([t, f, 1])
        varios = [fila for fila in ultimo if fila[2] >= 2 and fila[0] not in decisiones]
        self.assertTrue(varios, "la partida de prueba debe tener instantes con varios eventos")
        for t, f, _ in varios:
            self.assertEqual(foto_resumen(self.app.historia(str(t)).resumen), f, f"t={t}")

    def test_coincide_con_lo_anotado(self):
        """FR-006 y SC-002: cada estado anotado antes de decidir y tras cada evento coincide con historia."""
        decisiones = [t for t, _ in self.anotador.decisiones]
        for k, (t, f) in enumerate(self.anotador.decisiones, 1):
            self.assertEqual(foto_resumen(self.app.historia(f"#{k}").resumen), f, f"#{k}")
            self.assertEqual(foto_resumen(self.app.historia(f"historia {t}").resumen), f, f"t={t}")
        revisados = 0
        for indice, (t, f) in enumerate(self.anotador.eventos):
            ultimo_de_t = indice + 1 == len(self.anotador.eventos) or self.anotador.eventos[indice + 1][0] != t
            if ultimo_de_t and t not in decisiones:
                self.assertEqual(foto_resumen(self.app.historia(str(t)).resumen), f, f"t={t}")
                revisados += 1
        self.assertGreater(revisados, 10)

    def test_entre_eventos(self):
        """FR-001 (US1, escenario 3): un instante sin eventos muestra lo ocurrido hasta él y nada posterior."""
        eventos = self.anotador.eventos
        decisiones = [t for t, _ in self.anotador.decisiones]
        probados = 0
        for indice in range(len(eventos) - 1):
            t, f = eventos[indice]
            siguiente = eventos[indice + 1][0]
            hay_decision = any(t <= d <= siguiente for d in decisiones)
            if siguiente - t >= 2 and not hay_decision:
                self.assertEqual(foto_resumen(self.app.historia(str(t + 1)).resumen), f)
                probados += 1
        self.assertGreater(probados, 0)

    def test_consulta_sin_efectos(self):
        """FR-007 (Apéndice B, caso 4): historia no consume tiempo, no se registra en partida.log y no modifica
        el historial de retroceso ni el azar."""
        with tempfile.TemporaryDirectory() as carpeta:
            app = armar(k=3, carpeta_logs=carpeta, registrar=True)
            jugar(app, 25)
            log = app._partida.registro.ruta
            antes = [_tiempo(app), log.read_bytes(), len(app._gestor.historial),
                     app._gestor.historial.reversiones, app._simulacion.azar.getstate(), foto(app),
                     app.estado_partida().acciones_ejecutadas, app._linea.linea.acciones()]
            for consulta in ["0", "#1", "#5", str(_tiempo(app)), "#26", "#99", "abc", str(_tiempo(app) + 5)]:
                app.historia(consulta)
            despues = [_tiempo(app), log.read_bytes(), len(app._gestor.historial),
                       app._gestor.historial.reversiones, app._simulacion.azar.getstate(), foto(app),
                       app.estado_partida().acciones_ejecutadas, app._linea.linea.acciones()]
            self.assertEqual(despues, antes)

    def test_historia_cero(self):
        """FR-002 (US1, escenario 6): historia 0 es el estado inicial, con la sala inicial explorada."""
        resumen = self.app.historia("0").resumen
        self.assertEqual(resumen.reloj, 0)
        self.assertEqual(resumen.acciones, 0)
        self.assertEqual(resumen.sala_id, 1)
        self.assertEqual([s.id for s in resumen.mapa.exploradas], [1])
        self.assertEqual(resumen.mapa.avistadas, [2, 4])

    def test_numeros_de_accion(self):
        """FR-003 y FR-004 (US2): #1 es el inicio, #N+1 el estado actual; #0, #N+2 y textos inválidos se rechazan."""
        app = self.app
        n = app._linea.linea.acciones()
        self.assertEqual(foto_resumen(app.historia("#1").resumen), self.anotador.decisiones[0][1])
        actual = app.historia(f"#{n + 1}").resumen
        self.assertEqual(foto_resumen(actual), foto(app))
        self.assertEqual(actual.reloj, _tiempo(app))
        for malo in ["#0", f"#{n + 2}", "#", "#x", "-5", "", "historia", "1.5"]:
            self.assertFalse(app.historia(malo).ok, malo)

    def test_consulta_tras_terminar(self):
        """FR-009: la consulta se permite después de terminar la partida."""
        app = armar(k=5)
        jugar(app, 12)
        app.terminar()
        self.assertTrue(app.estado_partida().terminada)
        self.assertTrue(app.historia("#3").ok)
        self.assertTrue(app.historia(str(_tiempo(app))).ok)


class TestK(unittest.TestCase):
    def test_mismo_resultado_con_distinto_k(self):
        """FR-015 (US6, escenario 3): la misma partida con K=1 y K=50 da resúmenes idénticos."""
        a = jugar(armar(k=1), 60)
        b = jugar(armar(k=50), 60)
        self.assertEqual(_tiempo(a), _tiempo(b))
        for k in range(1, 62):
            self.assertEqual(foto_resumen(a.historia(f"#{k}").resumen),
                             foto_resumen(b.historia(f"#{k}").resumen), f"#{k}")
        for t in range(0, _tiempo(a) + 1, 37):
            self.assertEqual(foto_resumen(a.historia(str(t)).resumen),
                             foto_resumen(b.historia(str(t)).resumen), f"t={t}")

    def test_puntos_de_control_y_limite_k(self):
        """FR-013 y FR-015 (US6, escenarios 1 y 2): a lo sumo un punto de control cada K acciones y ninguna
        consulta aplica o deshace más de K acciones."""
        for k in [1, 3, 7, 50]:
            app = jugar(armar(k=k), 70)
            linea = app._linea.linea
            n = linea.acciones()
            self.assertLessEqual(linea.puntos_de_control(), n // k + 1)
            for numero in range(1, n + 2):
                pos, marca = linea.ubicar_accion(numero)
                for modo in ["adelante", "atras", "cercano"]:
                    self.assertLessEqual(linea.acciones_recorridas(pos, marca, modo), k, f"K={k} #{numero} {modo}")
            for t in range(0, _tiempo(app) + 1, 13):
                pos, marca = linea.ubicar_tiempo(t)
                for modo in ["adelante", "atras", "cercano"]:
                    self.assertLessEqual(linea.acciones_recorridas(pos, marca, modo), k, f"K={k} t={t} {modo}")

    def test_k_por_defecto(self):
        """FR-018 (US6, escenario 5): sin --checkpoint-cada se usa K_POR_DEFECTO."""
        from cripta.controlador.LineaTiempoControlador import K_POR_DEFECTO
        self.assertEqual(armar()._linea.linea.k, K_POR_DEFECTO)

    def test_k_invalido(self):
        """FR-017 (US6, escenario 4): K inválido termina con error antes de iniciar la partida."""
        for valor in ["0", "-3", "abc", "2.5"]:
            with redirect_stderr(StringIO()) as error:
                self.assertEqual(main(["--checkpoint-cada", valor, "--offline"]), 2, valor)
            self.assertIn("--checkpoint-cada", error.getvalue())


if __name__ == "__main__":
    unittest.main()
