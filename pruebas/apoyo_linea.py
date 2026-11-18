"""Ayudas para las pruebas de la línea de tiempo (spec 004; no es una prueba).

La verdad de cada prueba es el estado vivo de la partida, anotado mientras se juega: antes de cada
decisión del jugador y después de cada evento del reloj. `historia` debe reproducir esas notas sin
haberlas visto. Ningún dato de una cripta concreta: el esqueleto y el contenido los arma la prueba.
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pruebas.apoyo_niebla import FuenteNiebla, TIPO_ENEMIGO, sala
from cripta.controlador.Aplicacion import Aplicacion
from cripta.controlador.EfectosControlador import EfectosControlador
from cripta.estructuras.Ordenamientos import ordenar

TIPO_PERGAMINO = "itm_pergamino_retroceso"


class FuenteLinea(FuenteNiebla):
    """Fuente de prueba con versión de catálogo, para poder reproducir el registro."""

    def get_catalog_version(self):
        return {"version": "catalogo-linea-1"}


def esqueleto():
    """Seis salas en anillo con costos distintos y una puerta cerrada con llave."""
    return [
        sala(1, [["N", 2], ["E", 4, {"costo": 150}]]),
        sala(2, [["S", 1], ["N", 3, {"costo": 50}]]),
        sala(3, [["S", 2], ["E", 6]]),
        sala(4, [["O", 1, {"costo": 150}], ["N", 5]]),
        sala(5, [["S", 4], ["N", 6, {"cerrada": True, "llave": "itm_llave_x"}]]),
        sala(6, [["O", 3], ["S", 5, {"cerrada": True, "llave": "itm_llave_x"}]]),
    ]


def contenidos(pergaminos=6):
    """Ratas juntas en las salas 2, 3 y 5 (actúan en los mismos instantes), una en la 4 y pergaminos en la 1."""
    def enemigos(id_, cantidad):
        return [{"instancia": f"e{id_}-{i}", "tipo": TIPO_ENEMIGO} for i in range(cantidad)]
    return [
        {"sala": 1, "enemigos": [], "objetos": [TIPO_PERGAMINO] * pergaminos, "trampas": []},
        {"sala": 2, "enemigos": enemigos(2, 2), "objetos": [], "trampas": []},
        {"sala": 3, "enemigos": enemigos(3, 3), "objetos": [], "trampas": []},
        {"sala": 4, "enemigos": enemigos(4, 1), "objetos": [], "trampas": []},
        {"sala": 5, "enemigos": enemigos(5, 2), "objetos": [], "trampas": []},
    ]


def armar(k=None, carpeta_logs=None, registrar=False):
    """Partida iniciada sobre el esqueleto de prueba; el jugador no muere (vida alta)."""
    fuente = FuenteLinea(esqueleto(), 1, 6, contenidos())
    app = Aplicacion(fuente, carpeta_logs=carpeta_logs, checkpoint_cada=k)
    resultado = app.iniciar_partida("Jugador", "42", "cripta-01", registrar=registrar, verificar=False)
    if not resultado.ok:
        raise AssertionError(resultado.motivo)
    return app


def foto(app):
    """Estado observable vivo, con el mismo contenido que exige el resumen (FR-005)."""
    j = app._jugador
    e = app.estado_partida()
    sala_actual = app._salas.obtener(j.sala)
    enemigos = ordenar([[x.identificador, x.vida] for x in sala_actual.enemigos if x.vida > 0],
                       key=lambda par: par[0])
    return [j.sala, j.vida, j.vida_max, j.ataque, j.defensa, j.velocidad,
            "victoria" if e.victoria else "derrota" if e.derrota else "en curso",
            [f"{i.nombre} (equipado)" if i.equipado else i.nombre for i in app.inventario().items()],
            EfectosControlador.describir(j), enemigos, repr(app.mapa_conocido())]


def foto_resumen(r):
    """El mismo formato que `foto`, a partir de un resumen de `historia`."""
    return [r.sala_id, r.vida, r.vida_max, r.ataque, r.defensa, r.velocidad, r.resultado,
            list(r.inventario), list(r.efectos), [[x.id, x.vida] for x in r.enemigos], repr(r.mapa)]


class Anotador:
    """Anota la foto viva antes de cada decisión y después de cada evento del reloj."""

    def __init__(self, app):
        self.app = app
        self.decisiones: list = []    # [instante, foto] antes de cada acción
        self.eventos: list = []       # [instante, foto] después de cada evento
        self._enganchar()

    def _enganchar(self):
        sim = self.app._simulacion
        original = sim.al_terminar_evento

        def gancho(t):
            original(t)
            self.eventos.append([t, foto(self.app)])
        sim.al_terminar_evento = gancho

    def antes_de_decidir(self):
        self.decisiones.append([self.app._simulacion.reloj.tiempo_actual, foto(self.app)])


def jugar(app, acciones, semilla=7, anotador=None, inmortal=True):
    """Política determinista: recoge, ataca si hay enemigos, si no se mueve o espera.

    Con `inmortal` la vida del jugador se repone fuera de las acciones (no queda en partida.log, así
    que una partida que se va a reproducir usa `inmortal=False`).
    """
    azar = random.Random(semilla)
    hechas = 0
    while hechas < acciones:
        e = app.estado_partida()
        if e.terminada:
            break
        if inmortal and app._jugador.vida < 1000:
            app._jugador.vida = app._jugador.vida_max = 10 ** 6   # fuera de las acciones: t actual
        if anotador is not None:
            app._linea.capturar()
            anotador.antes_de_decidir()
        if e.objetos_suelo and azar.random() < 0.5:
            resultado = app.recoger(e.objetos_suelo[0].id)
        elif e.enemigos and azar.random() < 0.2:
            resultado = app.atacar(e.enemigos[0].id)
        else:
            abiertas = [s for s in e.vecindad if not s.cerrada]
            if abiertas and azar.random() < 0.8:
                resultado = app.mover(abiertas[azar.randrange(len(abiertas))].direccion)
            else:
                resultado = app.esperar()
        if not resultado.ok:
            if anotador is not None:
                anotador.decisiones.pop()
            continue
        hechas += 1
    return app
