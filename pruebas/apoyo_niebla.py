"""Ayudas para las pruebas de la niebla de guerra y de «ir a» (no es una prueba).

Cada prueba arma su propio esqueleto mínimo: aquí no hay ids ni datos de ninguna
cripta concreta (FR-041). La fuente falsa deriva de `FuentePrueba` solo para
reutilizar el catálogo de fichas local; las salas, salidas, costos, puertas,
enemigos y trampas los describe la prueba.

Descripción de una sala: `sala(id, [[dir, destino, opciones], ...])`, donde
`opciones` es opcional y puede traer `costo`, `cerrada`, `llave` y
`cierre_automatico`.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pruebas.test_inventario import FuentePrueba
from cripta.controlador.Aplicacion import Aplicacion

# Tipos del catálogo local usados solo como relleno de contenido.
TIPO_ENEMIGO = "ent_rata_gigante"
TIPO_TRAMPA = "trp_dardos"


def sala(id_, salidas=None, nombre=None):
    """Una sala del esqueleto: `salidas` es una lista de `[direccion, destino, opciones]`."""
    resultado = {}
    for entrada in salidas or []:
        opciones = entrada[2] if len(entrada) > 2 else {}
        datos = {"sala": entrada[1], "cerrada": False}
        datos.update(opciones)
        resultado[entrada[0]] = datos
    return {"id": id_, "nombre": nombre or f"sala {id_}", "salidas": resultado}


def contenido(id_, enemigos=0, trampas=0):
    """Contenido de una sala: cantidad de enemigos y de trampas del tipo de relleno."""
    return {"sala": id_,
            "enemigos": [{"instancia": f"e{id_}-{i}", "tipo": TIPO_ENEMIGO} for i in range(enemigos)],
            "objetos": [],
            "trampas": [{"instancia": f"t{id_}-{i}", "tipo": TIPO_TRAMPA} for i in range(trampas)]}


class FuenteNiebla(FuentePrueba):
    """Fuente falsa con el esqueleto y el contenido que arma la prueba."""

    def __init__(self, salas, sala_inicial=1, sala_salida=None, contenidos=None):
        super().__init__()
        self._salas = salas
        self._inicial = sala_inicial
        self._salida = sala_salida if sala_salida is not None else salas[-1]["id"]
        self._contenidos = contenidos or []

    def crypta_details(self, cid):
        datos = super(FuentePrueba, self).crypta_details(cid)
        datos["salas_total"] = len(self._salas)
        datos["sala_inicial"] = self._inicial
        datos["sala_salida"] = self._salida
        datos["inventario_max"] = 20
        return datos

    def list_rooms(self, cid, pagina):
        return {"salas": self._salas, "total_paginas": 1}

    def room_content(self, cid, ids):
        filas = []
        for sid in ids:
            fila = next((c for c in self._contenidos if c["sala"] == sid), None)
            filas.append(fila or contenido(sid))
        return {"contenido": filas}


def armar_aplicacion(salas, sala_inicial=1, sala_salida=None, contenidos=None):
    """Una `Aplicacion` con la partida iniciada sobre el esqueleto de la prueba."""
    app = Aplicacion(FuenteNiebla(salas, sala_inicial, sala_salida, contenidos))
    resultado = app.iniciar_partida("Jugador", "42", "cripta-01", registrar=False, verificar=False)
    if not resultado.ok:
        raise AssertionError(resultado.motivo)
    return app


def avanzar_reloj(app, tiempo, limite=1000):
    """Reloj controlable: espera hasta que el reloj virtual alcance `tiempo`.

    Sirve para forzar cierres automáticos de puertas sin mover al jugador.
    """
    pasos = 0
    while app._simulacion.reloj.tiempo_actual < tiempo:
        pasos += 1
        if pasos > limite:
            raise AssertionError("El reloj no alcanzó el tiempo pedido.")
        if not app.esperar().ok:
            raise AssertionError("No se pudo esperar.")


def tiempo(app):
    """Reloj virtual actual."""
    return app._simulacion.reloj.tiempo_actual
