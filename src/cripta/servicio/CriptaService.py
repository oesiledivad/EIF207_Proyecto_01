from __future__ import annotations

from cripta.adaptadores.Crypt_Data_Source import CryptDataSource
from cripta.dto.Partida_dto import (
    CriptaResumen,
    DetallesCripta,
    SalaModelo,
    SalidaVecina,
    EnemigoPartida,
    ObjetoSuelo,
    TrampaPartida,
    ContenidoSala
)

class CriptaService:
    def __init__(self, data_source: CryptDataSource) -> None:
        self._data_source = data_source

    def listar_criptas(self) -> list[CriptaResumen]:
        try:
            respuesta = self._data_source.crypta_list()
            bruto = respuesta.get("criptas", [])
            resultado: list[CriptaResumen] = []
            for item in bruto:
                if isinstance(item, str):
                    resultado.append(CriptaResumen(id=item, nombre=item, salas=0, dificultad=1))
                elif isinstance(item, dict):
                    c_id = str(item.get("id", ""))
                    c_nombre = str(item.get("nombre", c_id))
                    c_salas = int(item.get("salas", 0))
                    c_dif = int(item.get("dificultad", 1))
                    if c_id:
                        resultado.append(CriptaResumen(id=c_id, nombre=c_nombre, salas=c_salas, dificultad=c_dif))
            return resultado
        except Exception as e:
            raise RuntimeError(f"No se pudo listar criptas: {e}") from e

    def obtener_detalles(self, cripta_id: str) -> DetallesCripta:
        try:
            detalles = self._data_source.crypta_details(cripta_id)
            if not isinstance(detalles, dict):
                detalles = {}

            jugador = detalles.get("jugador", {})
            if not isinstance(jugador, dict):
                jugador = {}

            return DetallesCripta(
                id=str(detalles.get("id", cripta_id)),
                version=str(detalles.get("version", "offline")),
                salas_total=int(detalles.get("salas_total", 0)),
                sala_inicial=int(detalles.get("sala_inicial", 1)),
                sala_salida=int(detalles.get("sala_salida", 1)),
                llave_salida=str(detalles.get("llave_salida", "—")),
                inventario_max=int(detalles.get("inventario_max", 10)),
                presupuesto_solicitudes=int(detalles.get("presupuesto_solicitudes", 0)),
                jugador_vida_max=int(jugador.get("vida_max", 0)),
                jugador_ataque=int(jugador.get("ataque", 0)),
                jugador_defensa=int(jugador.get("defensa", 0)),
                jugador_velocidad=int(jugador.get("velocidad", 0)),
            )
        except NotImplementedError:
            return DetallesCripta(
                id=cripta_id, version="offline", salas_total=0, sala_inicial=1, sala_salida=1,
                llave_salida="—", inventario_max=10, presupuesto_solicitudes=0,
                jugador_vida_max=30, jugador_ataque=6, jugador_defensa=2, jugador_velocidad=100
            )

    def cargar_esqueleto_salas(self, cripta_id: str, sala_salida_id: int) -> list[SalaModelo]:
        salas_conocidas: list[SalaModelo] = []
        pagina = 1
        while True:
            try:
                resp = self._data_source.list_rooms(cripta_id, pagina)
            except NotImplementedError:
                break

            salas_brutas = resp.get("salas", [])
            for item_sala in salas_brutas:
                s_id = int(item_sala.get("id", 0))
                s_nombre = str(item_sala.get("nombre", ""))
                s_desc = str(item_sala.get("descripcion", ""))

                lista_salidas: list[SalidaVecina] = []
                salidas_brutas = item_sala.get("salidas", {})

                if isinstance(salidas_brutas, dict):
                    for direccion, info_salida in salidas_brutas.items():
                        vecina_id = int(info_salida.get("sala", 0))
                        cerrada = bool(info_salida.get("cerrada", False))
                        llave = info_salida.get("llave")
                        llave_str = str(llave) if llave is not None else ""

                        lista_salidas.append(
                            SalidaVecina(
                                direccion=str(direccion),
                                sala_id=vecina_id,
                                nombre=f"Sala {vecina_id}",
                                cerrada=cerrada,
                                llave=llave_str,
                                transitable=not cerrada,
                                es_salida_final=(vecina_id == sala_salida_id),
                                tiene_enemigos=False,
                                tiene_objetos=False,
                            )
                        )

                nueva_sala = SalaModelo(id=s_id, nombre=s_nombre, descripcion=s_desc, salidas=lista_salidas)
                if not any(s.id == s_id for s in salas_conocidas):
                    salas_conocidas.append(nueva_sala)

            total_paginas = int(resp.get("total_paginas", 1))
            if pagina >= total_paginas:
                break
            pagina += 1

        return salas_conocidas

    def cargar_contenido_sala(self, cripta_id: str, sala_id: int) -> ContenidoSala:
        try:
            resp = self._data_source.room_content(cripta_id, [sala_id])
        except NotImplementedError:
            return ContenidoSala()

        contenido_bruto = resp.get("contenido", [])
        for entrada in contenido_bruto:
            if int(entrada.get("sala", 0)) == sala_id:
                enemigos = [
                    EnemigoPartida(
                        id=str(e.get("id", "")), nombre=str(e.get("nombre", "")),
                        vida=int(e.get("vida", 0)), ataque=int(e.get("ataque", 0)), defensa=int(e.get("defensa", 0))
                    ) for e in entrada.get("enemigos", [])
                ]
                objetos = [ObjetoSuelo(id=str(o), nombre=str(o)) for o in entrada.get("objetos", [])]
                trampas = [
                    TrampaPartida(id=str(t.get("id", "")), tipo=str(t.get("tipo", "")),
                                  activa=bool(t.get("activa", True)))
                    for t in entrada.get("trampas", [])
                ]
                return ContenidoSala(enemigos=enemigos, objetos=objetos, trampas=trampas)
        return ContenidoSala()

    @property
    def requests_made(self) -> int:
        return self._data_source.requests_made

    def es_offline(self) -> bool:
        return self._data_source.__class__.__name__ == "AdaptadorOffline"