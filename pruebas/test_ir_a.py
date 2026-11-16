"""Comando «ir a»: rechazos, no abre puertas y viaje hasta la llegada (US3)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pruebas.apoyo_niebla import FuenteNiebla, armar_aplicacion, sala, tiempo
from cripta.controlador.Aplicacion import Aplicacion
from cripta.estructuras.Inventario import ItemInventario
from cripta.modelo.Puertas import abrir_salida

NO_EXPLORADA = "Solo puedes ir a una sala que ya exploraste."
NO_EXISTE = "La sala indicada no existe."
SIN_RUTA = "No hay ruta conocida hacia esa sala."


def _grabar(app):
    """Anota cada acción que llega a `partida.log` sin escribir archivos."""
    acciones = []
    original = app._partida.registrar_accion

    def registrar(nombre, argumento=None):
        acciones.append([nombre, argumento])
        return original(nombre, argumento)

    app._partida.registrar_accion = registrar
    return acciones


def _mensajes_viaje(app):
    return [m.texto for m in app.bitacora().ultimos() if m is not None and m.tipo == "viaje"]


def _lineal():
    """1 (inicial) a 2 a 3; 4 queda desconocida."""
    return [
        sala(1, [["N", 2]]),
        sala(2, [["S", 1], ["N", 3]]),
        sala(3, [["S", 2], ["N", 4]]),
        sala(4, [["S", 3]]),
    ]


def _diamante():
    """Dos rutas de 1 a 4: por 2 (costo 400) y por 3 (costo 100)."""
    return [
        sala(1, [["N", 2, {"costo": 200}], ["E", 3, {"costo": 50}]]),
        sala(2, [["S", 1, {"costo": 200}], ["E", 4, {"costo": 200}]]),
        sala(3, [["O", 1, {"costo": 50}], ["N", 4, {"costo": 50}]]),
        sala(4, [["S", 3, {"costo": 50}], ["O", 2, {"costo": 200}]]),
    ]


class PruebasIrARechazos(unittest.TestCase):
    def test_us3_1_apendice_b_sala_no_explorada(self):
        """FR-020 (Apéndice B, caso 1): ir a una avistada o desconocida se rechaza igual y sin tiempo."""
        app = armar_aplicacion(_lineal(), sala_inicial=1, sala_salida=4)
        acciones = _grabar(app)
        conocimiento = app._exploracion.conocimiento
        self.assertEqual(conocimiento.estado(2), 1)   # avistada
        self.assertEqual(conocimiento.estado(3), 0)   # desconocida
        antes = tiempo(app)
        avistada = app.ir_a(2)
        desconocida = app.ir_a(3)
        for resultado in [avistada, desconocida]:
            self.assertFalse(resultado.ok)
            self.assertFalse(resultado.activo)
        self.assertEqual(avistada.mensaje, NO_EXPLORADA)
        self.assertEqual(avistada.mensaje, desconocida.mensaje)
        self.assertEqual(_mensajes_viaje(app), [NO_EXPLORADA, NO_EXPLORADA])
        self.assertEqual(tiempo(app), antes)
        self.assertEqual(acciones, [])

    def test_us3_4_no_abre_puertas_con_llave(self):
        """FR-032: con la llave en el inventario el viaje ni atraviesa ni abre la puerta cerrada."""
        esqueleto = [
            sala(1, [["N", 2, {"cerrada": True, "llave": "itm_llave_bronce", "costo": 10}],
                     ["E", 3, {"costo": 100}]]),
            sala(2, [["S", 1], ["E", 3]]),
            sala(3, [["O", 1], ["N", 2]]),
        ]
        app = armar_aplicacion(esqueleto, sala_inicial=1, sala_salida=2)
        app._gestor.inventario.agregar(
            ItemInventario("i-1", "itm_llave_bronce", "Llave de bronce", "desconocido", 1, 0))
        conocimiento = app._exploracion.conocimiento
        puerta = app._salas.obtener(1).salidas.obtener("N")
        conocimiento.explorar(2, app._gestor.historial, 0)
        antes = tiempo(app)
        rechazo = app.ir_a(2)                       # sin otra ruta conocida: se rechaza
        self.assertFalse(rechazo.ok)
        self.assertEqual(rechazo.mensaje, SIN_RUTA)
        self.assertEqual(tiempo(app), antes)
        self.assertTrue(puerta.cerrada)
        # con otra ruta conocida (por 3) el viaje la usa y deja la puerta cerrada
        self.assertTrue(app.mover("E").ok)
        self.assertTrue(app.mover("O").ok)
        acciones = _grabar(app)
        resultado = app.ir_a_completo(2)
        self.assertTrue(resultado.ok, resultado.mensaje)
        self.assertEqual(resultado.motivo, "llegada")
        self.assertEqual(acciones, [["mover", "E"], ["mover", "N"]])
        self.assertEqual(app._jugador.sala, 2)
        self.assertTrue(puerta.cerrada)
        self.assertEqual(app._gestor.inventario.tamano, 1)

    def test_us3_6_sala_actual_rechazada(self):
        """FR-021: ir a la sala actual se rechaza sin consumir tiempo."""
        app = armar_aplicacion(_lineal(), sala_inicial=1, sala_salida=4)
        antes = tiempo(app)
        resultado = app.ir_a(1)
        self.assertFalse(resultado.ok)
        self.assertEqual(resultado.mensaje, "Ya estás en esa sala.")
        self.assertEqual(_mensajes_viaje(app), ["Ya estás en esa sala."])
        self.assertEqual(tiempo(app), antes)

    def test_rechazos_sin_tiempo(self):
        """FR-020, FR-021 y FR-030: cada rechazo usa su mensaje del contrato y no gasta tiempo."""
        app = armar_aplicacion(_lineal(), sala_inicial=1, sala_salida=4)
        acciones = _grabar(app)
        antes = tiempo(app)
        for valor in ["abc", 2.5, None, -1, 99, True]:
            resultado = app.ir_a(valor)
            self.assertFalse(resultado.ok, valor)
            self.assertEqual(resultado.mensaje, NO_EXISTE, valor)
        # destino explorado sin ruta: la puerta intermedia está sin observar
        conocimiento = app._exploracion.conocimiento
        conocimiento.explorar(2, app._gestor.historial, 0)
        conocimiento.explorar(3, app._gestor.historial, 0)
        sin_observar = app.ir_a(3)
        self.assertFalse(sin_observar.ok)
        self.assertEqual(sin_observar.mensaje, SIN_RUTA)
        self.assertFalse(app.ir_a_completo(3).ok)
        self.assertEqual(tiempo(app), antes)
        self.assertEqual(acciones, [])
        self.assertEqual(_mensajes_viaje(app)[-1], SIN_RUTA)
        # puerta recordada cerrada
        esqueleto = [sala(1, [["E", 2, {"cerrada": True, "llave": "k"}]]), sala(2, [["O", 1]])]
        cerrada = armar_aplicacion(esqueleto, sala_inicial=1, sala_salida=2)
        cerrada._exploracion.conocimiento.explorar(2, cerrada._gestor.historial, 0)
        self.assertEqual(cerrada.ir_a(2).mensaje, SIN_RUTA)
        # partida no activa
        sin_partida = Aplicacion(FuenteNiebla(_lineal()))
        resultado = sin_partida.ir_a(2)
        self.assertFalse(resultado.ok)
        self.assertEqual(resultado.mensaje, "La partida no está activa.")


class PruebasIrAViaje(unittest.TestCase):
    def _recorrido(self):
        """Explora las cuatro salas del diamante y vuelve a la sala 1."""
        app = armar_aplicacion(_diamante(), sala_inicial=1, sala_salida=4)
        for direccion in ["N", "E", "S", "O"]:
            self.assertTrue(app.mover(direccion).ok)
        self.assertEqual(app._jugador.sala, 1)
        return app

    def test_us3_7_llegada_detiene_viaje(self):
        """FR-025 (enmendado) y FR-027: llega por la ruta de menor costo, cada paso avanza el reloj
        lo mismo que un movimiento ordinario y corren los eventos del reloj entre pasos."""
        referencia = self._recorrido()
        ordinarios = []
        for direccion in ["E", "N"]:
            antes_ref = tiempo(referencia)
            self.assertTrue(referencia.mover(direccion).ok)
            ordinarios.append(tiempo(referencia) - antes_ref)
        app = self._recorrido()
        # una puerta abierta a mano que se cierra sola durante el viaje (evento del reloj)
        cierre = app._salas.obtener(2).salidas.obtener("S")
        cierre.cierre_automatico = 150
        abrir_salida(cierre, tiempo(app), app._simulacion.agenda)
        self.assertFalse(cierre.cerrada)
        acciones = _grabar(app)
        relojes = []
        original = app._ciclo.consumir_tiempo

        def medir(nombre):
            antes = tiempo(app)
            original(nombre)
            relojes.append(tiempo(app) - antes)

        app._ciclo.consumir_tiempo = medir
        inicio = tiempo(app)
        resultado = app.ir_a_completo(4)
        self.assertTrue(resultado.ok, resultado.mensaje)
        self.assertFalse(resultado.activo)
        self.assertEqual(resultado.motivo, "llegada")
        self.assertEqual(acciones, [["mover", "E"], ["mover", "N"]])   # costo 100, no 400
        self.assertEqual(app._jugador.sala, 4)
        self.assertEqual(len(relojes), 2)
        for avance in relojes:
            self.assertGreater(avance, 0)
        self.assertEqual(relojes, ordinarios)   # igual que un movimiento ordinario
        self.assertGreater(tiempo(app), inicio)
        self.assertTrue(cierre.cerrada)   # el evento del reloj corrió entre los pasos
        self.assertEqual(_mensajes_viaje(app), ["Viaje detenido: llegaste a la sala 4."])
        self.assertEqual(resultado.mensaje, "Viaje detenido: llegaste a la sala 4.")

    def test_viaje_paso_a_paso_y_cancelacion(self):
        """FR-019 y FR-034: cada avanzar_viaje da un paso y otra acción del jugador cancela el viaje."""
        app = self._recorrido()
        self.assertTrue(app.ir_a(4).activo)
        paso = app.avanzar_viaje()
        self.assertTrue(paso.ok and paso.activo)
        self.assertEqual(app._jugador.sala, 3)
        self.assertTrue(app.esperar().ok)             # otra acción: cancela
        self.assertEqual(_mensajes_viaje(app), ["Viaje cancelado."])
        self.assertFalse(app.avanzar_viaje().activo)
        self.assertEqual(app._jugador.sala, 3)
        self.assertTrue(app.ir_a(4).activo)
        self.assertFalse(app.cancelar_viaje().activo)
        self.assertEqual(_mensajes_viaje(app), ["Viaje cancelado.", "Viaje cancelado."])


# ---------------------------------------------------------------------------
# US4: detener el viaje ante peligro o falta de ruta
# ---------------------------------------------------------------------------

from types import SimpleNamespace

from cripta.modelo.Conocimiento import EXPLORADA
from cripta.modelo.Efectos import aplicar_veneno
from pruebas.apoyo_niebla import contenido

TEXTO_LLEGADA = "Viaje detenido: llegaste a la sala {}."
TEXTO_ENEMIGOS = "Viaje detenido: hay enemigos en la sala {}."
TEXTO_DANIO = "Viaje detenido: recibiste daño."
TEXTO_SIN_RUTA = "Viaje detenido: ya no existe una ruta conocida."
TEXTO_PARTIDA = "Viaje detenido: la partida terminó."
TEXTO_CANCELADO = "Viaje cancelado."


def _guardian(id_):
    """Contenido con un enemigo que no se mueve (guardián), para no depender del rastreo."""
    return {"sala": id_, "objetos": [], "trampas": [],
            "enemigos": [{"instancia": f"g{id_}", "tipo": "ent_guardian_oseo"}]}


def _conocer(app, ids):
    """Da al jugador el conocimiento de `ids` sin caminar: explora y observa cada sala."""
    conocimiento = app._exploracion.conocimiento
    for id_ in ids:
        conocimiento.explorar(id_, app._gestor.historial, 0)
    for id_ in ids:
        conocimiento.observar(id_, app._gestor.historial, 0)


def _cadena(contenidos=None):
    """1 a 2 a 3 a 4, todas conocidas, el jugador en 1."""
    app = armar_aplicacion(_lineal(), sala_inicial=1, sala_salida=4, contenidos=contenidos)
    _conocer(app, [1, 2, 3, 4])
    return app


def _trampa_de_danio(app, sala_id):
    """Convierte la trampa de la sala en una de daño directo (el catálogo local solo trae veneno)."""
    trampa = app._salas.obtener(sala_id).trampas[0]
    trampa.efecto = "dano"
    return trampa


def _escenario_llegada():
    app = _cadena()
    return app, app.ir_a_completo(3)


def _escenario_enemigos():
    app = _cadena([_guardian(3)])
    app._jugador.invulnerable = True
    return app, app.ir_a_completo(4)


def _escenario_danio():
    app = _cadena([contenido(2, trampas=1)])
    _trampa_de_danio(app, 2)
    return app, app.ir_a_completo(4)


def _escenario_sin_ruta():
    app = _cadena()
    app._salas.obtener(3).salidas.obtener("N").cerrada = True
    app.ir_a(4)
    app.avanzar_viaje()
    app.avanzar_viaje()
    return app, app.avanzar_viaje()


def _escenario_movimiento_rechazado():
    app = _cadena()
    app.ir_a(3)
    app._salas.obtener(1).salidas.obtener("N").cerrada = True   # la memoria dice abierta
    return app, app.avanzar_viaje()


def _escenario_partida_terminada():
    app = _cadena([contenido(2, trampas=1)])
    _trampa_de_danio(app, 2)
    app._jugador.vida = 1
    return app, app.ir_a_completo(4)


def _escenario_cancelado():
    app = _cadena()
    app.ir_a(3)
    return app, app.cancelar_viaje()


class PruebasIrAPeligro(unittest.TestCase):
    def test_us4_1_apendice_b_puerta_recordada_abierta_cerrada(self):
        """FR-026 (Apéndice B, caso 2): una puerta cambió sin que el jugador lo viera; al llegar
        a una sala desde la que se observa, el mapa se actualiza y la ruta se recalcula."""
        app = armar_aplicacion(_diamante(), sala_inicial=1, sala_salida=4)
        _conocer(app, [1, 2, 3, 4])
        conocimiento = app._exploracion.conocimiento
        puerta = app._salas.obtener(3).salidas.obtener("N")   # 3 a 4, la ruta de menor costo
        puerta.cerrada = True
        self.assertEqual(conocimiento.memoria_puerta(puerta.clave), 1)   # el mapa aún la recuerda abierta
        acciones = _grabar(app)
        resultado = app.ir_a_completo(4)
        self.assertTrue(resultado.ok, resultado.mensaje)
        self.assertEqual(resultado.motivo, "llegada")
        self.assertEqual(conocimiento.memoria_puerta(puerta.clave), 2)   # al llegar a 3 el mapa se actualizó
        self.assertEqual(acciones, [["mover", "E"], ["mover", "O"], ["mover", "N"], ["mover", "E"]])
        self.assertEqual(app._jugador.sala, 4)

    def test_us4_2_sin_ruta_alternativa_sin_tiempo(self):
        """FR-030: sin ruta alternativa el viaje se detiene con sin_ruta y el recálculo no gasta tiempo."""
        app = _cadena()
        app._salas.obtener(3).salidas.obtener("N").cerrada = True   # el mapa aún la recuerda abierta
        self.assertTrue(app.ir_a(4).activo)
        self.assertTrue(app.avanzar_viaje().ok)
        self.assertTrue(app.avanzar_viaje().ok)   # al llegar a 3 se observa la puerta cerrada
        self.assertEqual(app._jugador.sala, 3)
        antes = tiempo(app)
        acciones = _grabar(app)
        resultado = app.avanzar_viaje()
        self.assertFalse(resultado.ok)
        self.assertFalse(resultado.activo)
        self.assertEqual(resultado.motivo, "sin_ruta")
        self.assertEqual(tiempo(app), antes)
        self.assertEqual(acciones, [])
        self.assertEqual(app._jugador.sala, 3)

    def test_us4_3_apendice_b_enemigos_dormidos(self):
        """FR-028 (Apéndice B, caso 3): entrar a una sala con enemigos dormidos los activa según
        la Parte I y el viaje se detiene con enemigos."""
        app = _cadena([_guardian(3)])
        app._jugador.invulnerable = True
        enemigo = app._salas.obtener(3).enemigos[0]
        self.assertIsNone(enemigo._proximo_evento)   # dormido
        resultado = app.ir_a_completo(4)
        self.assertEqual(resultado.motivo, "enemigos")
        self.assertEqual(app._jugador.sala, 3)
        self.assertIsNotNone(enemigo._proximo_evento)   # activado por la Parte I
        self.assertEqual(resultado.mensaje, TEXTO_ENEMIGOS.format(3))

    def test_us4_4_enemigos_activos_detienen(self):
        """FR-028: entrar a una sala con enemigos ya activos detiene el viaje con enemigos."""
        app = _cadena([_guardian(3)])
        app._jugador.invulnerable = True
        enemigo = app._salas.obtener(3).enemigos[0]
        app._combate.activar_enemigo(enemigo, app._simulacion)
        self.assertIsNotNone(enemigo._proximo_evento)
        resultado = app.ir_a_completo(4)
        self.assertEqual(resultado.motivo, "enemigos")
        self.assertEqual(app._jugador.sala, 3)

    def test_us4_5_danio_ataque(self):
        """FR-029: el ataque de un enemigo durante el paso detiene el viaje con danio."""
        app = _cadena([contenido(2, enemigos=1)])
        vida = app._jugador.vida
        resultado = app.ir_a_completo(4)
        self.assertEqual(resultado.motivo, "danio")
        self.assertLess(app._jugador.vida, vida)

    def test_us4_5_danio_trampa(self):
        """FR-029: una trampa de daño directo detiene el viaje con danio."""
        app = _cadena([contenido(2, trampas=1)])
        _trampa_de_danio(app, 2)
        vida = app._jugador.vida
        resultado = app.ir_a_completo(4)
        self.assertEqual(resultado.motivo, "danio")
        self.assertEqual(app._jugador.sala, 2)
        self.assertLess(app._jugador.vida, vida)

    def test_us4_5_danio_veneno(self):
        """FR-029: el pulso de veneno entre dos pasos detiene el viaje con danio."""
        app = _cadena()
        aplicar_veneno(app._jugador, 1, tiempo(app), app._simulacion.agenda)
        vida = app._jugador.vida
        resultado = app.ir_a_completo(4)
        self.assertEqual(resultado.motivo, "danio")
        self.assertLess(app._jugador.vida, vida)
        self.assertNotEqual(app._jugador.sala, 4)

    def test_us4_5_danio_cero_no_detiene(self):
        """FR-029 (C4): un daño que no baja la vida no detiene el viaje."""
        app = _cadena([contenido(2, trampas=1)])
        _trampa_de_danio(app, 2)
        app._jugador.invulnerable = True
        vida = app._jugador.vida
        resultado = app.ir_a_completo(4)
        self.assertEqual(app._jugador.vida, vida)
        self.assertEqual(resultado.motivo, "llegada")
        self.assertEqual(app._jugador.sala, 4)

    def test_us4_6_toda_detencion_muestra_motivo(self):
        """FR-031 y SC-007: cada código deja exactamente un mensaje de categoría viaje con su texto."""
        casos = [
            ("llegada", _escenario_llegada, TEXTO_LLEGADA.format(3)),
            ("enemigos", _escenario_enemigos, TEXTO_ENEMIGOS.format(3)),
            ("danio", _escenario_danio, TEXTO_DANIO),
            ("sin_ruta", _escenario_sin_ruta, TEXTO_SIN_RUTA),
            ("movimiento_rechazado", _escenario_movimiento_rechazado, None),
            ("partida_terminada", _escenario_partida_terminada, TEXTO_PARTIDA),
            ("cancelado", _escenario_cancelado, TEXTO_CANCELADO),
        ]
        for codigo, escenario, texto in casos:
            with self.subTest(codigo=codigo):
                app, resultado = escenario()
                self.assertEqual(resultado.motivo, codigo)
                mensajes = _mensajes_viaje(app)
                self.assertEqual(len(mensajes), 1, mensajes)
                if texto is None:
                    self.assertTrue(mensajes[0].startswith("Viaje detenido: no se pudo avanzar ("), mensajes)
                    self.assertTrue(mensajes[0].endswith(")."), mensajes)
                else:
                    self.assertEqual(mensajes[0], texto)
                self.assertEqual(resultado.mensaje, mensajes[0])

    def test_motivo_llega_a_bitacora_sin_ventana(self):
        """FR-031, FR-018 y SC-007: sin abrir la vista, llegada, sin_ruta, el mapa y un rechazo
        dejan su resultado y su mensaje en la bitácora de Aplicacion."""
        con_arcade = "arcade" in sys.modules
        app, llegada = _escenario_llegada()
        self.assertEqual(_mensajes_viaje(app), [llegada.mensaje])
        self.assertEqual(llegada.motivo, "llegada")
        self.assertEqual(llegada.mensaje, TEXTO_LLEGADA.format(3))
        app, sin_ruta = _escenario_sin_ruta()
        self.assertEqual(_mensajes_viaje(app), [sin_ruta.mensaje])
        self.assertEqual(sin_ruta.motivo, "sin_ruta")
        self.assertEqual(sin_ruta.mensaje, TEXTO_SIN_RUTA)
        mapa = app.mapa_conocido()
        self.assertEqual([s.id for s in mapa.exploradas], [1, 2, 3, 4])
        self.assertEqual(len(_mensajes_viaje(app)), 1)   # el mapa no escribe en la bitácora de viaje
        rechazo = app.ir_a(99)
        self.assertEqual(_mensajes_viaje(app)[-1], rechazo.mensaje)
        self.assertEqual(rechazo.mensaje, NO_EXISTE)
        self.assertEqual("arcade" in sys.modules, con_arcade)   # nada abrió la vista

    def test_derrotados_no_detienen(self):
        """FR-028: una sala con solo enemigos derrotados no detiene el viaje."""
        app = _cadena([_guardian(2)])
        app._salas.obtener(2).enemigos[0].vida = 0
        resultado = app.ir_a_completo(4)
        self.assertEqual(resultado.motivo, "llegada")
        self.assertEqual(app._jugador.sala, 4)

    def test_prioridad_de_motivos(self):
        """FR-031a (C3): si coinciden motivos se muestra uno: partida_terminada, danio, enemigos, llegada."""
        # enemigos sobre llegada: el destino tiene un guardián
        app = _cadena([_guardian(2)])
        app._jugador.invulnerable = True
        resultado = app.ir_a_completo(2)
        self.assertEqual(resultado.motivo, "enemigos")
        self.assertEqual(_mensajes_viaje(app), [TEXTO_ENEMIGOS.format(2)])
        # danio sobre enemigos y llegada: la rata del destino ataca durante el paso
        app = _cadena([contenido(2, enemigos=1)])
        resultado = app.ir_a_completo(2)
        self.assertEqual(resultado.motivo, "danio")
        self.assertEqual(len(_mensajes_viaje(app)), 1)
        # partida_terminada sobre danio, enemigos y llegada
        app = _cadena([contenido(2, enemigos=1, trampas=1)])
        _trampa_de_danio(app, 2)
        app._jugador.vida = 1
        resultado = app.ir_a_completo(2)
        self.assertEqual(resultado.motivo, "partida_terminada")
        self.assertEqual(_mensajes_viaje(app), [TEXTO_PARTIDA])

    def test_movimiento_rechazado_y_partida_terminada(self):
        """FR-031a: un paso rechazado por mover y la derrota durante el viaje detienen con su motivo."""
        app, rechazado = _escenario_movimiento_rechazado()
        self.assertFalse(rechazado.ok)
        self.assertFalse(rechazado.activo)
        self.assertEqual(rechazado.motivo, "movimiento_rechazado")
        self.assertIn("La puerta está cerrada.", rechazado.mensaje)
        self.assertEqual(app._jugador.sala, 1)
        app, derrota = _escenario_partida_terminada()
        self.assertEqual(derrota.motivo, "partida_terminada")
        self.assertFalse(derrota.activo)
        self.assertFalse(app._partida_en_curso())
        self.assertFalse(app.avanzar_viaje().activo)   # con la partida terminada no hace nada

    def test_corte_por_cantidad_de_pasos(self):
        """FR-030: un viaje nunca da más pasos que salas exploradas y termina con sin_ruta (C1)."""
        app = armar_aplicacion(_lineal(), sala_inicial=1, sala_salida=4)
        _conocer(app, [1, 2, 3])
        self.assertTrue(app.ir_a(3).activo)
        direcciones = {1: "N", 2: "S"}
        app._viaje._buscar = lambda origen: SimpleNamespace(direccion=direcciones[origen])   # ruta que oscila
        conocimiento = app._exploracion.conocimiento
        exploradas = sum(1 for e in conocimiento.estado_sala if e == EXPLORADA)
        acciones = _grabar(app)
        resultado = app.avanzar_viaje()
        guardia = 0
        while resultado.activo:
            guardia += 1
            self.assertLess(guardia, 50)
            resultado = app.avanzar_viaje()
        self.assertEqual(resultado.motivo, "sin_ruta")
        self.assertEqual(len(acciones), exploradas)
        self.assertEqual(_mensajes_viaje(app), [TEXTO_SIN_RUTA])


# ---------------------------------------------------------------------------
# US6: iniciar o cargar una partida descarta el viaje activo (FR-034a)
# ---------------------------------------------------------------------------

import tempfile


class PruebasViajeYPartidaNueva(unittest.TestCase):
    def _viaje_activo(self, ruta=None):
        app = Aplicacion(FuenteNiebla(_lineal(), 1, 4), ruta_guardado=ruta)
        self.assertTrue(app.iniciar_partida("Jugador", "42", "cripta-01", registrar=False,
                                            verificar=False).ok)
        _conocer(app, [1, 2, 3, 4])
        return app

    def _comprobar_descartado(self, app):
        self.assertFalse(app.viaje_activo)
        self.assertEqual(app._viaje.motivo, "cancelado")
        antes = tiempo(app)
        sala_antes = app._jugador.sala
        paso = app.avanzar_viaje()
        self.assertFalse(paso.ok or paso.activo)
        self.assertEqual(app._jugador.sala, sala_antes)    # el viaje no continúa en la nueva partida
        self.assertEqual(tiempo(app), antes)

    def test_fr034a_iniciar_partida_descarta_el_viaje(self):
        """FR-034a: iniciar una partida descarta el viaje activo y no continúa en la nueva."""
        app = self._viaje_activo()
        self.assertTrue(app.ir_a(4).activo)
        self.assertTrue(app.avanzar_viaje().activo)
        self.assertEqual(app._jugador.sala, 2)
        self.assertTrue(app.iniciar_partida("Jugador", "42", "cripta-01", registrar=False,
                                            verificar=False).ok)
        self.assertEqual(app._jugador.sala, 1)
        self._comprobar_descartado(app)

    def test_fr034a_cargar_partida_descarta_el_viaje(self):
        """FR-034a: cargar una partida descarta el viaje activo y no continúa en la cargada."""
        with tempfile.TemporaryDirectory(prefix="cripta-viaje-carga-") as carpeta:
            ruta = Path(carpeta) / "guardado.bin"
            app = self._viaje_activo(ruta)
            self.assertTrue(app.guardar().ok)
            self.assertTrue(app.ir_a(4).activo)
            self.assertTrue(app.avanzar_viaje().activo)
            resultado = app.cargar()
            self.assertTrue(resultado.ok, resultado.motivo)
            self.assertEqual(app._jugador.sala, 1)
            self._comprobar_descartado(app)


if __name__ == "__main__":
    unittest.main()
