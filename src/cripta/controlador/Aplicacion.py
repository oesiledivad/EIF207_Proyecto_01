"""Controlador de Aplicación (MVC).

Único controlador del proyecto. Traduce intenciones de la vista en
operaciones del modelo. No conoce Textual, requests ni open().

- Carga el esqueleto completo al iniciar partida.
- Carga el contenido de la sala inicial.
- Bitácora propia (estructuras/Bitacora).
- Consultas de solo lectura para la pantalla de juego.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from cripta.adaptadores.Crypt_Data_Source import CryptDataSource
from cripta.estructuras.Bitacora import Bitacora, Mensaje


@dataclass
class ResultadoInicio:
    ok: bool
    motivo: str | None = None
    semilla_efectiva: int | None = None


@dataclass
class SalidaVecina:
    direccion: str
    sala_id: int
    nombre: str
    cerrada: bool
    llave: str | None
    transitable: bool
    es_salida_final: bool
    tiene_enemigos: bool
    tiene_objetos: bool


@dataclass
class EstadoPartida:
    activa: bool = False
    terminada: bool = False
    victoria: bool = False
    derrota: bool = False

    nombre_jugador: str = ""
    cripta_id: str = ""
    version_cripta: str = ""
    semilla: int = 0
    modo: str = "red"
    presupuesto_solicitudes: int = 0
    inventario_max: int = 10

    reloj_virtual: int = 0
    sala_actual_id: int = 0
    sala_actual_nombre: str = ""
    sala_salida_id: int = 0
    llave_salida: str = ""

    jugador_vida: int = 0
    jugador_vida_max: int = 0
    jugador_ataque: int = 0
    jugador_defensa: int = 0
    jugador_velocidad: int = 0

    vecindad: list[SalidaVecina] = field(default_factory=list)
    enemigos: list[dict] = field(default_factory=list)
    objetos_suelo: list[dict] = field(default_factory=list)
    trampas: list[dict] = field(default_factory=list)
    inventario: list[dict] = field(default_factory=list)
    efectos: list[dict] = field(default_factory=list)

    salas_conocidas: dict = field(default_factory=dict)
    contenido_cargado: set = field(default_factory=set)
    contenido_pendiente: set = field(default_factory=set)


def _generar_semilla() -> int:
    return random.SystemRandom().randint(1, 2**31 - 1)


class Aplicacion:
    def __init__(self, data_source: CryptDataSource) -> None:
        self._data_source = data_source
        self._partida = EstadoPartida()
        self._bitacora = Bitacora(capacidad=20)

    # Selección

    def listar_criptas(self) -> list[dict]:
        try:
            respuesta = self._data_source.crypta_list()
        except Exception as e:
            raise RuntimeError(f"No se pudo listar criptas: {e}") from e
        return respuesta.get("criptas", [])

    def previsualizar_cripta(self, cripta_id: str) -> dict:
        """Datos generales para la previsualización en selección."""
        try:
            return self._data_source.crypta_details(cripta_id)
        except NotImplementedError:
            return {
                "id": cripta_id,
                "version": "offline",
                "salas_total": 0,
                "sala_inicial": 1,
                "sala_salida": 1,
                "llave_salida": "",
                "presupuesto_solicitudes": 0,
                "inventario_max": 10,
                "jugador": {
                    "vida_max": 30,
                    "ataque": 6,
                    "defensa": 2,
                    "velocidad": 100,
                },
            }

    def iniciar_partida(
        self,
        nombre_jugador: str,
        semilla: str,
        cripta_id: str,
    ) -> ResultadoInicio:
        nombre = nombre_jugador.strip()
        if not nombre:
            return ResultadoInicio(
                ok=False,
                motivo="El nombre del jugador no puede estar vacío.",
            )
        if not cripta_id:
            return ResultadoInicio(
                ok=False,
                motivo="Debes seleccionar una cripta.",
            )

        semilla_txt = semilla.strip()
        if semilla_txt:
            if not semilla_txt.isdigit():
                return ResultadoInicio(
                    ok=False,
                    motivo="La semilla debe ser un número entero o quedar vacía.",
                )
            semilla_efectiva = int(semilla_txt)
        else:
            semilla_efectiva = _generar_semilla()

        try:
            detalles = self._data_source.crypta_details(cripta_id)
        except NotImplementedError:
            detalles = self.previsualizar_cripta(cripta_id)

        jugador = detalles.get("jugador", {})

        self._partida = EstadoPartida(
            activa=True,
            nombre_jugador=nombre,
            cripta_id=detalles.get("id", cripta_id),
            version_cripta=detalles.get("version", ""),
            semilla=semilla_efectiva,
            modo="offline" if self._es_offline() else "red",
            presupuesto_solicitudes=detalles.get("presupuesto_solicitudes", 0),
            inventario_max=detalles.get("inventario_max", 10),
            reloj_virtual=0,
            sala_actual_id=detalles.get("sala_inicial", 1),
            sala_actual_nombre="(cargando...)",
            sala_salida_id=detalles.get("sala_salida", 1),
            llave_salida=detalles.get("llave_salida", ""),
            jugador_vida=jugador.get("vida_max", 0),
            jugador_vida_max=jugador.get("vida_max", 0),
            jugador_ataque=jugador.get("ataque", 0),
            jugador_defensa=jugador.get("defensa", 0),
            jugador_velocidad=jugador.get("velocidad", 0),
            salas_conocidas={},
            contenido_cargado=set(),
            contenido_pendiente=set(),
        )

        self._bitacora.limpiar()
        self._bitacora.append(Mensaje("sistema", f"Partida iniciada en {cripta_id}."))
        self._bitacora.append(Mensaje("sistema", f"Semilla: {semilla_efectiva}."))

        self._cargar_esqueleto(cripta_id)
        self._cargar_contenido_sala(self._partida.sala_actual_id)

        return ResultadoInicio(ok=True, semilla_efectiva=semilla_efectiva)

    # Consultas de juego

    def estado_partida(self) -> EstadoPartida:
        return self._partida

    def bitacora(self) -> Bitacora:
        return self._bitacora

    def solicitudes_usadas(self) -> int:
        return self._data_source.requests_made

    # Carga de datos

    def _es_offline(self) -> bool:
        return self._data_source.__class__.__name__ == "OfflineAdapter"

    def _cargar_esqueleto(self, cripta_id: str) -> None:
        pagina = 1
        while True:
            try:
                resp = self._data_source.list_rooms(cripta_id, pagina)
            except NotImplementedError:
                return
            for sala in resp.get("salas", []):
                self._partida.salas_conocidas[sala["id"]] = sala
            if pagina >= resp.get("total_paginas", 1):
                break
            pagina += 1
        self._refrescar_sala_actual()

    def _cargar_contenido_sala(self, sala_id: int) -> None:
        if sala_id in self._partida.contenido_cargado:
            return
        self._partida.contenido_pendiente.add(sala_id)
        try:
            resp = self._data_source.room_content(
                self._partida.cripta_id, [sala_id]
            )
        except NotImplementedError:
            self._partida.contenido_pendiente.discard(sala_id)
            return
        for entrada in resp.get("contenido", []):
            if entrada.get("sala") == sala_id:
                self._partida.enemigos = list(entrada.get("enemigos", []))
                self._partida.objetos_suelo = [
                    {"id": o, "nombre": o} for o in entrada.get("objetos", [])
                ]
                self._partida.trampas = list(entrada.get("trampas", []))
                break
        self._partida.contenido_cargado.add(sala_id)
        self._partida.contenido_pendiente.discard(sala_id)

    def _refrescar_sala_actual(self) -> None:
        sala = self._partida.salas_conocidas.get(self._partida.sala_actual_id)
        if sala is None:
            return
        self._partida.sala_actual_nombre = sala.get("nombre", "")

        vecindad: list[SalidaVecina] = []
        for direccion, salida in sala.get("salidas", {}).items():
            vecina_id = salida.get("sala")
            vecina = self._partida.salas_conocidas.get(vecina_id, {})
            cerrada = bool(salida.get("cerrada", False))
            llave = salida.get("llave")
            vecindad.append(
                SalidaVecina(
                    direccion=direccion,
                    sala_id=vecina_id,
                    nombre=vecina.get("nombre", f"Sala {vecina_id}"),
                    cerrada=cerrada,
                    llave=llave,
                    transitable=not cerrada,
                    es_salida_final=(vecina_id == self._partida.sala_salida_id),
                    tiene_enemigos=False,
                    tiene_objetos=False,
                )
            )
        orden = {"N": 0, "S": 1, "E": 2, "O": 3}
        vecindad.sort(key=lambda v: orden.get(v.direccion, 99))
        self._partida.vecindad = vecindad

    # Acciones (stubs hasta tener modelo real)

    def mover(self, direccion: str) -> dict:
        self._bitacora.append(
            Mensaje("sistema", f"Mover {direccion} aún no implementado.")
        )
        return {"ok": False, "motivo": "Movimiento aún no implementado."}

    def atacar(self, instancia_id: str) -> dict:
        self._bitacora.append(Mensaje("sistema", "Ataque aún no implementado."))
        return {"ok": False, "motivo": "Ataque aún no implementado."}

    def esperar(self) -> dict:
        self._bitacora.append(Mensaje("sistema", "Espera aún no implementada."))
        return {"ok": False, "motivo": "Espera aún no implementada."}

    def terminar(self) -> None:
        self._partida.activa = False
        self._partida.terminada = True