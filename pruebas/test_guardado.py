"""Guardado binario: guardar, cargar y seguir jugando da el mismo resultado (sin red ni vista).
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pruebas.test_replay import FuenteReplay
from cripta.controlador.Aplicacion import Aplicacion
from cripta.modelo.Efectos import aplicar_veneno, encender_antorcha
from cripta.modelo.Puertas import abrir_salida


def huella(app):
    """Estado comparable. No incluye números de secuencia ni el historial (no se guardan)."""
    sim = app._simulacion
    j = app._jugador
    est = app.estado_partida()
    return [
        sim.reloj.tiempo_actual, sim.azar.getstate(),
        j.vida, j.vida_max, j.sala, j.velocidad, j.velocidad_base, j.ataque, j.defensa,
        j.fin_veneno, j.dano_veneno, j.antorcha_encendida, j.tiempo_siguiente,
        [[i.instancia_id, i.tipo_id, i.equipado] for i in app.inventario().items()],
        app.inventario().item_actual().instancia_id if app.inventario().item_actual() else None,
        [[s.id, s.ultimo_tiempo_visita, s.contenido_cargado,
          [[sa.direccion, sa.cerrada] for sa in s.salidas],
          [[e.identificador, e.vida, e.sala, e.tiempo_siguiente, e.comportamiento, e.tipo]
           for e in s.enemigos],
          [[t.instancia, t.armada] for t in s.trampas],
          [[o.id, o.tipo_id] for o in s.objetos]]
         for s in app._salas._datos if s is not None],
        # Cada evento válido en orden de ejecución: (tiempo, tipo, dueño).
        [[e.tiempo_siguiente, e.tipo,
          getattr(e.actor, "identificador", getattr(e.actor, "instancia", getattr(e.actor, "direccion", "")))]
         for e in sorted(sim.agenda.eventos_validos(), key=lambda ev: ev.clave())],
        est.acciones_ejecutadas, est.enemigos_derrotados, est.sala_actual_id, est.terminada,
        [list(p) for p in app._partida._salidas_abiertas],
    ]


def preparar_partida(ruta):
    app = Aplicacion(FuenteReplay(), ruta_guardado=ruta)
    resultado = app.iniciar_partida("Jugador", "42", "cripta-01")
    assert resultado.ok, resultado.motivo
    app._jugador.vida = app._jugador.vida_max = 300   # que la prueba no termine en derrota
    for posicion in [0, 1, 8, 9, 10]:
        assert app.recoger(f"sala-1-objeto-{posicion}").ok
    assert app.equipar("sala-1-objeto-9").ok
    # Efectos pendientes en la agenda: veneno, antorcha y una puerta con cierre automático.
    t = app._simulacion.reloj.tiempo_actual
    aplicar_veneno(app._jugador, 1, t, app._simulacion.agenda)
    encender_antorcha(app._jugador, 800, t, app._simulacion.agenda)
    salida = app._salas.obtener(1).salidas.obtener("N")
    salida.cierre_automatico = 900
    abrir_salida(salida, t, app._simulacion.agenda)
    assert app.mover("N").ok                 # dispara la trampa y activa a la rata
    assert app.atacar("rata").ok
    assert app.esperar().ok
    return app


def seguir_jugando(app):
    for _ in range(3):
        app.esperar()
    while app.estado_partida().enemigos:
        assert app.atacar("rata").ok
    assert app.mover("S").ok
    for _ in range(12):
        app.esperar()
    return huella(app)


class PruebasGuardado(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory(prefix="cripta-guardado-test-")
        self.addCleanup(self.temporal.cleanup)
        self.ruta = Path(self.temporal.name) / "partida.bin"

    def test_ida_y_vuelta_y_determinismo(self):
        app = preparar_partida(self.ruta)
        antes = huella(app)
        self.assertTrue(app.guardar().ok)
        self.assertTrue(self.ruta.exists())

        # Lo que pasa si se sigue jugando sin cargar nada.
        esperado = seguir_jugando(app)

        # Cargar en una aplicación nueva: mismo estado al instante...
        otra = Aplicacion(FuenteReplay(), ruta_guardado=self.ruta)
        resultado = otra.cargar()
        self.assertTrue(resultado.ok, resultado.motivo)
        self.assertEqual(huella(otra), antes)
        # ...y la misma continuación (azar, agenda, efectos, cierre de puerta).
        self.assertEqual(seguir_jugando(otra), esperado)

    def test_cargar_sobre_una_partida_en_curso(self):
        app = preparar_partida(self.ruta)
        antes = huella(app)
        self.assertTrue(app.guardar().ok)
        esperado = seguir_jugando(app)       # la misma partida avanza y se aleja de lo guardado
        self.assertNotEqual(huella(app), antes)
        self.assertTrue(app.cargar().ok)     # volver al punto guardado
        self.assertEqual(huella(app), antes)
        self.assertEqual(seguir_jugando(app), esperado)

    def test_salas_se_leen_una_a_una_del_indice(self):
        from cripta.estructuras.Guardado_Binario import Guardado_Binario
        app = preparar_partida(self.ruta)
        self.assertTrue(app.guardar().ok)
        contenedor = Guardado_Binario(str(self.ruta))
        self.assertEqual(contenedor.version_cripta(), app.estado_partida().version_cripta)
        self.assertIsNotNone(contenedor.cargar_sala(1))
        self.assertIsNotNone(contenedor.cargar_sala(2))
        self.assertIsNone(contenedor.cargar_sala(99))

    def test_archivo_dañado_no_toca_la_partida(self):
        app = preparar_partida(self.ruta)
        self.assertTrue(app.guardar().ok)
        antes = huella(app)
        datos = self.ruta.read_bytes()
        self.ruta.write_bytes(datos[:len(datos) // 2])
        self.assertFalse(app.cargar().ok)
        self.assertEqual(huella(app), antes)
        self.ruta.write_bytes(b"no soy un guardado")
        self.assertFalse(app.cargar().ok)
        self.assertEqual(huella(app), antes)
        self.assertFalse(Aplicacion(FuenteReplay()).cargar(self.ruta.with_name("no_existe.bin")).ok)

    def test_no_guarda_sin_partida_o_terminada(self):
        self.assertFalse(Aplicacion(FuenteReplay(), ruta_guardado=self.ruta).guardar().ok)
        app = preparar_partida(self.ruta)
        app.terminar()
        self.assertFalse(app.guardar().ok)
        self.assertFalse(self.ruta.exists())

    def test_no_carga_si_cambio_la_version_de_la_cripta(self):
        app = preparar_partida(self.ruta)
        self.assertTrue(app.guardar().ok)

        class OtraVersion(FuenteReplay):
            def crypta_details(self, cid):
                datos = super().crypta_details(cid)
                datos["version"] = "otra-version"
                return datos

        resultado = Aplicacion(OtraVersion(), ruta_guardado=self.ruta).cargar()
        self.assertFalse(resultado.ok)
        self.assertIn("versi", resultado.motivo)


if __name__ == "__main__":
    unittest.main()