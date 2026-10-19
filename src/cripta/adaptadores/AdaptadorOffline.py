"""Modo --offline: responde desde disco con el mismo contrato que el cliente de red.

Orden de lectura:
    1. La caché persistente (--cache-dir): lo que se fue descargando al jugar
       en línea (lista de criptas, datos generales, esqueleto, contenido y fichas).
    2. El paquete de respuestas del curso (--offline-dir, p. ej. datos_prueba),
       solo para lo que la caché no tenga.

Una cripta que está en la caché se juega SOLO con lo de la caché (nunca se
mezclan versiones). Si falta una sala que nunca se descargó, esa sala no se
devuelve y el juego no deja entrar en ella. Leer disco no cuenta como
solicitud de red (5.1).
El catálogo sigue el origen de la cripta seleccionada: caché o paquete local.
"""
from .Crypt_Data_Source import CryptDataSource
from pathlib import Path
import json
from hashlib import sha256

MAX_POR_LOTE = 10


class AdaptadorOffline(CryptDataSource):
    """Lee respuestas guardadas: primero la caché descargada, después el paquete del curso."""

    def __init__(self, carpeta="datos_prueba", almacen=None):
        self.carpeta = Path(carpeta)
        self.almacen = almacen   # AlmacenDisco de --cache-dir (None = solo el paquete)
        self._catalogo_del_paquete = False

    @property
    def requests_made(self) -> int:
        return 0

    #  Paquete del curso

    def _hay(self, nombre_archivo) -> bool:
        return (self.carpeta / nombre_archivo).exists()

    def _leer(self, nombre_archivo):
        ruta = self.carpeta / nombre_archivo
        if not ruta.exists():
            raise FileNotFoundError(f"No hay respuesta grabada: {ruta}")
        with ruta.open("r", encoding="utf-8") as f:
            return json.load(f)

    #  Caché descargada

    def _en_cache(self, crypta_id: str) -> bool:
        """La cripta se descargó al jugar en línea (hay datos generales guardados)."""
        return self.almacen is not None and self.almacen.leer_detalles(crypta_id) is not None

    #  Contrato

    def crypta_list(self) -> dict:
        criptas = []
        ids = []
        guardada = self.almacen.leer_lista_criptas() if self.almacen is not None else None
        for item in (guardada or {}).get("criptas", []):
            c_id = item if isinstance(item, str) else str(item.get("id", ""))
            if c_id and c_id not in ids and self._en_cache(c_id):
                criptas.append(item)
                ids.append(c_id)
        if self._hay("criptas.json"):
            for item in self._leer("criptas.json").get("criptas", []):
                c_id = item if isinstance(item, str) else str(item.get("id", ""))
                if c_id and c_id not in ids:
                    criptas.append(item)
                    ids.append(c_id)
        if not criptas:
            raise FileNotFoundError("No hay criptas descargadas. Juega primero en línea "
                                    "o indica el paquete con --offline-dir.")
        return {"criptas": criptas}

    def crypta_details(self, crypta_id: str) -> dict:
        en_cache = self._en_cache(crypta_id)
        datos = (self.almacen.leer_detalles(crypta_id) if en_cache
                 else self._leer(f"cripta_{crypta_id}.json"))
        # El catálogo debe pertenecer al mismo origen que la cripta seleccionada.
        self._catalogo_del_paquete = not en_cache
        return datos

    def list_rooms(self, crypta_id: str, pagina: int) -> dict:
        if self._en_cache(crypta_id):
            datos = self.almacen.leer_pagina_salas(crypta_id, pagina)
            if datos is None:
                raise FileNotFoundError(f"La página {pagina} del mapa de {crypta_id} no se descargó.")
            return datos
        return self._leer(f"cripta_{crypta_id}_salas_{pagina}.json")

    def room_content(self, crypta_id: str, room_ids: list) -> dict:
        if len(room_ids) > MAX_POR_LOTE:
            raise ValueError(f"Máximo {MAX_POR_LOTE} salas por llamada")
        elegidas = []
        if self._en_cache(crypta_id):
            for sala_id in room_ids:
                entrada = self.almacen.leer_contenido(crypta_id, sala_id)
                if entrada is not None:      # sala nunca descargada: no se inventa
                    elegidas.append(entrada)
            return {"contenido": elegidas}
        todo = self._leer(f"cripta_{crypta_id}_contenido.json")
        for entrada in todo["contenido"]:
            if entrada["sala"] in room_ids:
                elegidas.append(entrada)
        return {"contenido": elegidas}

    def catalog(self, ids: list) -> dict:
        if len(ids) > MAX_POR_LOTE:
            raise ValueError(f"Máximo {MAX_POR_LOTE} ids por llamada")
        paquete = None
        elegidas = []
        version_cache = (self.almacen.leer_version_catalogo()
                         if self.almacen is not None and not self._catalogo_del_paquete else None)
        for id_pedido in ids:
            ficha = self.almacen.leer_ficha(id_pedido) if version_cache else None
            if ficha is None and self._hay("catalogo.json"):
                if paquete is None:
                    if version_cache and self._version_catalogo_paquete().get("version") != version_cache:
                        raise RuntimeError(f"Ficha no descargada: {id_pedido}; el catálogo del paquete "
                                           "tiene otra versión.")
                    paquete = self._leer("catalogo.json")["entidades"]
                for candidata in paquete:
                    if candidata["id"] == id_pedido:
                        ficha = candidata
                        break
            if ficha is None:
                raise RuntimeError(f"Ficha no descargada: {id_pedido}")
            elegidas.append(ficha)
        return {"entidades": elegidas}

    def get_crypta_version(self, crypta_id: str) -> dict:
        if self._en_cache(crypta_id):
            return {"version": self.almacen.leer_detalles(crypta_id).get("version")}
        return self._leer(f"cripta_{crypta_id}_version.json")

    def get_catalog_version(self) -> dict:
        version = (self.almacen.leer_version_catalogo()
                   if self.almacen is not None and not self._catalogo_del_paquete else None)
        if version:
            return {"version": version}
        return self._version_catalogo_paquete()

    def _version_catalogo_paquete(self) -> dict:
        """Obtiene la versión del paquete sin sustituirla por la de la caché."""
        try:
            return self._leer("catalogo_version.json")
        except FileNotFoundError:
            # Sin version declarada, solo este archivo local exacto es compatible.
            return {"version": "offline-sha256:" + sha256(
                (self.carpeta / "catalogo.json").read_bytes()).hexdigest()}
