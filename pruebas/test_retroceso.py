"""Retroceso integrado por deltas, sin red ni archivos generados."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pruebas.test_inventario import FuentePrueba
from cripta.controlador.Aplicacion import Aplicacion
from cripta.controlador.GestorPartida import GestorPartida
from cripta.estructuras.Agenda_Eventos import HeapAgendaEventos
from cripta.estructuras.Ordenamientos import ordenar
from cripta.modelo.Efectos import aplicar_veneno, aplicar_cambio_velocidad, encender_antorcha
from cripta.modelo.Trampa import TrampaJuego


class FuenteRetroceso(FuentePrueba):
    def crypta_details(self, cid):
        datos = super().crypta_details(cid)
        datos["inventario_max"] = 20
        return datos

    def room_content(self, cid, ids):
        return {"contenido": [
            {"sala": sid,
             "enemigos": [{"instancia": "rata", "tipo": "ent_rata_gigante"}] if sid == 2 else [],
             "objetos": ["itm_pergamino_retroceso"] * 8 + ["itm_pocion_menor"] if sid == 1 else [],
             "trampas": [{"instancia": "trampa", "tipo": "trp_dardos"}] if sid == 2 else []}
            for sid in ids
        ]}


def eventos(agenda):
    return ordenar([(e.tiempo_siguiente, e.secuencias, e.actor, e.tipo, e.valido)
                    for e in agenda._heap], key=lambda e: (e[0], e[1]))


def estado(app):
    """Comparación de prueba; no se almacena en el historial de producción."""
    jugador = app._jugador
    sim = app._simulacion
    return (
        sim.reloj.tiempo_actual, sim.azar.getstate(), sim.agenda._secuencia_actual,
        jugador.vida, jugador.sala, jugador.velocidad, jugador.ataque, jugador.defensa,
        jugador.evento_veneno, jugador.fin_veneno, jugador.evento_fin_velocidad,
        jugador.antorcha_encendida, jugador.evento_antorcha, jugador._proximo_evento,
        eventos(sim.agenda),
        [(s.id, s.ultimo_tiempo_visita,
          [(e, e.vida, e.sala, e._proximo_evento, e.tiempo_siguiente) for e in s.enemigos],
          [(t, t.armada) for t in s.trampas],
          [(o.id, o.tipo_id) for o in s.objetos if o.tipo_id != "itm_pergamino_retroceso"])
         for s in app._salas._datos if s is not None],
        [(i.instancia_id, i.equipado) for i in app.inventario().items()
         if i.clase != "pergamino_retroceso"],
    )


class RetrocesoPruebas(unittest.TestCase):
    def setUp(self):
        self.app = Aplicacion(FuenteRetroceso())
        self.assertTrue(self.app.iniciar_partida("Jugador", "42", "cripta-01").ok)
        for objeto in list(self.app.estado_partida().objetos_suelo)[:6]:
            self.assertTrue(self.app.recoger(objeto.id).ok)
        self.app._gestor.historial.limpiar()

    def pergaminos(self):
        return [i for i in self.app.inventario().items() if i.clase == "pergamino_retroceso"]

    def test_movimiento_activacion_trampa_combate_reloj_azar_y_agenda(self):
        antes = estado(self.app)
        self.assertTrue(self.app.mover("N").ok)
        self.assertLess(self.app._jugador.vida, antes[3])
        self.assertFalse(self.app._salas.obtener(2).trampas[0].armada)
        self.assertTrue(self.app.usar_pergamino().ok)
        self.assertEqual(estado(self.app), antes)
        self.assertEqual(len(self.pergaminos()), 5)
        self.assertEqual(self.app._cripta_service.requests_made, 0)

    def test_muerte_botin_y_repeticion_determinista(self):
        self.assertTrue(self.app.mover("N").ok)
        enemigo = self.app._salas.obtener(2).enemigos[0]
        enemigo.vida = 1
        antes = estado(self.app)
        self.assertTrue(self.app.atacar("rata").ok)
        despues = estado(self.app)
        self.assertEqual(self.app._salas.obtener(2).enemigos, [])
        self.assertTrue(self.app.estado_partida().objetos_suelo)
        self.assertTrue(self.app.usar_pergamino().ok)
        self.assertEqual(estado(self.app), antes)
        self.assertTrue(self.app.atacar("rata").ok)
        # Eventos nuevos son objetos distintos, pero deben tener las mismas claves y efectos.
        self.assertEqual(self.app._jugador.vida, despues[3])
        self.assertEqual(self.app._simulacion.reloj.tiempo_actual, despues[0])
        self.assertEqual(self.app._simulacion.azar.getstate(), despues[1])
        self.assertEqual(self.app._simulacion.agenda._secuencia_actual, despues[2])

    def test_dos_pergaminos_no_generan_acciones(self):
        antes = estado(self.app)
        self.assertTrue(self.app.esperar().ok)
        intermedio = estado(self.app)
        self.assertTrue(self.app.esperar().ok)
        self.assertTrue(self.app.usar_pergamino().ok)
        self.assertEqual(estado(self.app), intermedio)
        self.assertTrue(self.app.usar_pergamino().ok)
        self.assertEqual(estado(self.app), antes)
        self.assertEqual(len(self.app._gestor.historial), 0)
        self.assertEqual(len(self.pergaminos()), 4)
        self.assertFalse(self.app.usar_pergamino().ok)
        self.assertEqual(len(self.pergaminos()), 4)

    def test_recoger_otro_pergamino_no_lo_devuelve_al_suelo(self):
        objeto = self.app.estado_partida().objetos_suelo[0]
        tiempo = self.app._simulacion.reloj.tiempo_actual
        self.assertTrue(self.app.recoger(objeto.id).ok)
        self.assertEqual(len(self.pergaminos()), 7)
        self.assertTrue(self.app.usar_pergamino().ok)
        self.assertEqual(len(self.pergaminos()), 6)
        self.assertFalse(any(o.id == objeto.id for o in self.app.estado_partida().objetos_suelo))
        self.assertEqual(self.app._simulacion.reloj.tiempo_actual, tiempo)

    def test_soltar_pergamino_no_se_revierte(self):
        item = self.pergaminos()[0]
        self.assertTrue(self.app.soltar(item.instancia_id).ok)
        self.assertTrue(self.app.usar_pergamino().ok)
        self.assertIsNone(self.app.inventario().buscar_por_id(item.instancia_id))
        self.assertTrue(any(o.id == item.instancia_id for o in self.app.estado_partida().objetos_suelo))
        self.assertEqual(len(self.pergaminos()), 4)

    def test_limite_cinco_y_accion_rechazada(self):
        antes = estado(self.app)
        self.assertFalse(self.app.atacar("inexistente").ok)
        self.assertEqual(estado(self.app), antes)
        self.assertEqual(len(self.app._gestor.historial), 0)
        for _ in range(6):
            self.assertTrue(self.app.esperar().ok)
        self.assertEqual(len(self.app._gestor.historial), 5)
        for _ in range(5):
            self.assertTrue(self.app.usar_pergamino().ok)
        self.assertFalse(self.app.usar_pergamino().ok)
        self.assertEqual(self.app._simulacion.reloj.tiempo_actual, antes[0] + 100)
        self.assertEqual(len(self.pergaminos()), 1)

    def test_efectos_que_terminan_y_rearme(self):
        app = self.app
        agenda, jugador = app._simulacion.agenda, app._jugador
        tiempo = app._simulacion.reloj.tiempo_actual
        aplicar_veneno(jugador, 2, tiempo, agenda)
        encender_antorcha(jugador, 30, tiempo, agenda)
        aplicar_cambio_velocidad(jugador, 150, 20, tiempo, agenda)
        trampa = TrampaJuego("extra", False, 1, 300)
        app._salas.obtener(1).trampas.append(trampa)
        agenda.insertar(tiempo + 10, trampa, "trampa_rearme")
        antes = estado(app)
        self.assertTrue(app.esperar().ok)
        self.assertTrue(trampa.armada)
        self.assertFalse(jugador.antorcha_encendida)
        self.assertEqual(jugador.velocidad, 100)
        self.assertTrue(app.usar_pergamino().ok)
        self.assertEqual(estado(app), antes)

    def test_consumible_vuelve_y_protege_su_ficha(self):
        objeto = next(o for o in self.app.estado_partida().objetos_suelo
                      if o.tipo_id == "itm_pocion_menor")
        self.assertTrue(self.app.recoger(objeto.id).ok)
        self.app._jugador.vida = 10
        antes = estado(self.app)
        self.assertTrue(self.app.usar(objeto.id).ok)
        self.assertTrue(self.app.usar_pergamino().ok)
        self.assertEqual(estado(self.app), antes)
        cache = self.app._cripta_service._cache_fichas
        self.assertEqual(cache._buscar("itm_pocion_menor").referencias, 1)

    def test_movimiento_enemigo_y_regeneracion(self):
        sala = self.app._salas.obtener(2)
        enemigo = sala.enemigos[0]
        enemigo.vida = 1
        enemigo.ataque = 1
        enemigo.regeneracion_objetivo = 2
        self.app._combate.activar_sala(sala, self.app._simulacion)
        # Un movimiento concreto permite comprobar pertenencia sin depender del RNG.
        with patch.object(enemigo, "decidir_accion", return_value=("mover", 1)):
            antes = estado(self.app)
            self.assertTrue(self.app.esperar().ok)
            self.assertEqual(enemigo.sala, 1)
            self.assertIn(enemigo, self.app._salas.obtener(1).enemigos)
            self.assertTrue(self.app.usar_pergamino().ok)
            self.assertEqual(estado(self.app), antes)
        self.assertTrue(self.app.esperar().ok)
        antes = estado(self.app)
        vida = enemigo.vida
        self.assertTrue(self.app.esperar().ok)
        self.assertGreater(enemigo.vida, vida)
        self.assertTrue(self.app.usar_pergamino().ok)
        self.assertEqual(estado(self.app), antes)

    def test_error_durante_eventos_revierte_todo_el_intervalo(self):
        self.assertTrue(self.app.mover("N").ok)
        antes = estado(self.app)
        original = self.app._simulacion.ejecutar_evento
        def falla(evento, jugador, salas):
            original(evento, jugador, salas)
            raise RuntimeError("fallo en evento")
        with patch.object(self.app._simulacion, "ejecutar_evento", side_effect=falla):
            with self.assertRaisesRegex(RuntimeError, "fallo en evento"):
                self.app.esperar()
        self.assertEqual(estado(self.app), antes)
        self.assertFalse(self.app._gestor.historial.hay_intervalo_abierto())

    def test_error_de_accion_revierte_los_deltas(self):
        antes = estado(self.app)
        def falla():
            self.app._simulacion.agenda.cambiar(self.app._jugador, "vida", 1)
            raise RuntimeError("fallo sintético")
        with self.assertRaisesRegex(RuntimeError, "fallo sintético"):
            self.app._accion_jugador("esperar", falla)
        self.assertEqual(estado(self.app), antes)
        self.assertFalse(self.app._gestor.historial.hay_intervalo_abierto())


class AgendaReversiblePruebas(unittest.TestCase):
    def test_heap_reversible_con_cancelados_y_empates(self):
        gestor = GestorPartida()
        agenda = HeapAgendaEventos(gestor.historial)
        originales = [agenda.insertar(n % 11, None, "prueba") for n in range(200)]
        for evento in originales[::3]:
            agenda.cancelar(evento)
        antes = eventos(agenda)
        secuencia = agenda._secuencia_actual
        gestor.abrir_intervalo()
        for n in range(100):
            agenda.insertar(n % 7, None, "nuevo")
            agenda.extraer_siguiente()
        gestor.cerrar_intervalo()
        self.assertTrue(gestor.deshacer())
        self.assertEqual(eventos(agenda), antes)
        self.assertEqual(agenda._secuencia_actual, secuencia)
        for indice, evento in enumerate(agenda._heap):
            self.assertEqual(evento.indice, indice)
        claves = []
        while (evento := agenda.extraer_siguiente()) is not None:
            claves.append(evento.clave())
        self.assertEqual(claves, ordenar(claves.copy()))


if __name__ == "__main__":
    unittest.main()
