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
        """FR-025 y FR-027: llega por la ruta de menor costo, cada paso gasta tiempo y corre el reloj."""
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


if __name__ == "__main__":
    unittest.main()
