from __future__ import annotations

import threading

from cripta.adaptadores.Crypt_Data_Source import CryptDataSource, PresupuestoAgotado
from cripta.adaptadores.Almacen_Disco import AlmacenDisco
from cripta.dto.Partida_dto import (
    CriptaResumen,
    DetallesCripta,
    SalaModelo,
    ContenidoSala
)
from cripta.estructuras.Cache_Fichas import Cache_Fichas
from cripta.estructuras.Catalogo_Lista import Catalogo_Lista
from cripta.servicio.CatalogoService import CatalogoService
from cripta.servicio.PrecargaService import PrecargaService
from cripta.dto.FactoryDto_Partida import (
    parsear_detalles, parsear_sala, parsear_contenido,
)

MAX_POR_LOTE = 10  # §3.4: contenido y catálogo aceptan hasta 10 por solicitud


class _FuenteSincronizada:
    """Envuelve el adaptador para que la precarga en segundo plano y el hilo del
    juego nunca hagan solicitudes al mismo tiempo (el contador de presupuesto
    y el cliente HTTP no son seguros entre hilos)."""

    def __init__(self, fuente: CryptDataSource) -> None:
        self.fuente = fuente
        self._candado = threading.Lock()

    def __getattr__(self, nombre):
        valor = getattr(self.fuente, nombre)
        if not callable(valor):
            return valor
        def sincronizado(*args, **kwargs):
            with self._candado:
                return valor(*args, **kwargs)
        return sincronizado


class CriptaService:
    """Coordina solicitudes, caché y precarga sin avanzar el reloj del juego."""

    def __init__(self, data_source: CryptDataSource, cache_fichas: Cache_Fichas | None = None,
                 almacen: AlmacenDisco | None = None) -> None:
        self._data_source = data_source
        self._cache_fichas = cache_fichas if cache_fichas is not None else Cache_Fichas()
        self._detalles: DetallesCripta | None = None  # evita pedir 2 veces los datos generales
        # Persistencia (§4.4). Solo se usa lo del disco si su versión fue validada.
        self._almacen = almacen
        self._catalogo_en_disco = False
        self._cripta_en_disco = False
        self._lecturas_disco = 0
        self._version_catalogo = None
        self._catalogo = CatalogoService(self)
        self._precarga = PrecargaService(self)

    #  Precarga en segundo plano (§4.2)

    def activar_precarga_en_segundo_plano(self) -> None:
        """La vista interactiva la activa: la red ya no congela la ventana al cruzar
        puertas. Replay, bench y pruebas siguen sincrónicos."""
        if not isinstance(self._data_source, _FuenteSincronizada):
            self._data_source = _FuenteSincronizada(self._data_source)
        self._precarga.activar_segundo_plano()

    @property
    def precarga_en_segundo_plano(self) -> bool:
        return self._precarga.en_segundo_plano

    def completar_precarga(self) -> str | None:
        """Incorpora lo que la precarga trajo (se llama al inicio de cada acción)."""
        return self._precarga.completar_pendiente()

    def esperar_precarga(self) -> None:
        """Espera y descarta la precarga pendiente (fin o reinicio de partida)."""
        self._precarga.descartar_pendiente()

    def reiniciar_partida(self) -> None:
        self._precarga.descartar_pendiente()
        self._data_source.reiniciar_partida()
        self._detalles = None
        self._version_catalogo = None
        self._lecturas_disco = 0
        self._cache_fichas = Cache_Fichas(capacidad=self._cache_fichas.capacidad)

    def obtener_version_catalogo(self, actualizar: bool = False) -> str:
        if actualizar:
            self._version_catalogo = None
        if self._version_catalogo is None:
            respuesta = self._data_source.get_catalog_version()
            if not isinstance(respuesta, dict):
                raise ValueError("Respuesta de version de catalogo invalida.")
            version = respuesta.get("version")
            if not isinstance(version, str) or not version.strip():
                raise ValueError("El servicio no informo una version de catalogo valida.")
            self._version_catalogo = version
        return self._version_catalogo

    #  Persistencia (§4.4)

    def preparar_persistencia(self, detalles: DetallesCripta) -> str:
        """Valida lo guardado en disco contra las versiones actuales.

        - Cripta: la versión viene en los datos generales (ya pedidos), así
          que validar esqueleto y contenido no cuesta solicitudes extra.
        - Catálogo: cuesta 1 solicitud liviana (GET /catalogo/version).
        Si algo falla, se juega sin disco para ese dato: nunca con datos viejos.

        Returns:
            Mensaje para la bitácora.
        """
        self._catalogo_en_disco = False
        self._cripta_en_disco = False
        if self._almacen is None:
            return "Caché persistente desactivada."

        cripta_vigente = self._almacen.validar_cripta(detalles.id, detalles.version)
        self._cripta_en_disco = True
        try:
            version_cat = self.obtener_version_catalogo()
        except (PresupuestoAgotado, RuntimeError, OSError, ValueError) as e:
            return f"No se pudo validar el catálogo en disco ({e}); se usará solo la red."
        cat_vigente = self._almacen.validar_catalogo(version_cat)
        self._catalogo_en_disco = True
        return (f"Caché en disco: cripta {'vigente' if cripta_vigente else 'nueva/actualizada'}, "
                f"catálogo {'vigente' if cat_vigente else 'nuevo/actualizado'}.")

    @property
    def lecturas_disco(self) -> int:
        return self._lecturas_disco

    #  Catálogo (delegado)

    def asegurar_fichas(self, ids: list[str], fijar: bool = False) -> Catalogo_Lista:
        return self._catalogo.asegurar_fichas(ids, fijar)

    def fijar_fichas(self, ids: list[str]) -> None:
        self._catalogo.fijar_fichas(ids)

    def validar_capacidad(self, tipos: list[str]) -> None:
        self._catalogo.validar_capacidad(tipos)

    def liberar_fichas(self, ids: list[str]) -> None:
        self._catalogo.liberar_fichas(ids)

    def obtener_ficha_garantizada(self, id_: str):
        return self._catalogo.obtener_ficha_garantizada(id_)

    def fijar_seguro(self, tipos: list[str]) -> str | None:
        return self._catalogo.fijar_seguro(tipos)

    @staticmethod
    def tipos_visibles(sala) -> list[str]:
        return CatalogoService.tipos_visibles(sala)

    def fijar_contenido_visible(self, sala) -> str | None:
        return self._catalogo.fijar_contenido_visible(sala)

    def liberar_contenido_visible(self, sala) -> None:
        self._catalogo.liberar_contenido_visible(sala)

    @classmethod
    def tipos_activos(cls, inventario, salas, sala_actual) -> list[str]:
        return CatalogoService.tipos_activos(inventario, salas, sala_actual)

    def reproteger(self, anteriores: list[str], actuales: list[str]) -> str | None:
        return self._catalogo.reproteger(anteriores, actuales)

    #  Precarga (delegada)

    @staticmethod
    def planificar_precarga(salas, max_id: int, origen_id: int) -> list[int]:
        return PrecargaService.planificar_precarga(salas, max_id, origen_id)

    @staticmethod
    def necesita_precarga(salas, sala_id: int) -> bool:
        return PrecargaService.necesita_precarga(salas, sala_id)

    def cargar_lote(self, cripta_id: str, salas, max_id: int, origen_id: int, incorporar) -> None:
        self._precarga.cargar_lote(cripta_id, salas, max_id, origen_id, incorporar)

    def asegurar_sala_cargada(self, cripta_id: str, salas, max_id: int, sala_id: int,
                              incorporar) -> str | None:
        return self._precarga.asegurar_sala_cargada(cripta_id, salas, max_id, sala_id, incorporar)

    def precargar_alrededor(self, cripta_id: str, salas, max_id: int, sala_id: int,
                            incorporar) -> str | None:
        return self._precarga.precargar_alrededor(cripta_id, salas, max_id, sala_id, incorporar)

    def listar_criptas(self) -> list[CriptaResumen]:
        try:
            respuesta = self._data_source.crypta_list()
            if self._almacen is not None:
                self._almacen.guardar_lista_criptas(respuesta)   # para --offline
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
        if self._detalles is not None and self._detalles.id == cripta_id:
            return self._detalles  # ya pedidos (p.ej. al previsualizar): no gastar otra solicitud
        try:
            detalles = self._data_source.crypta_details(cripta_id)
            self._detalles = parsear_detalles(detalles, cripta_id)
            if self._almacen is not None:
                self._almacen.guardar_detalles(cripta_id, detalles)   # para --offline
            return self._detalles
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
            resp = self._almacen.leer_pagina_salas(cripta_id, pagina) if self._cripta_en_disco else None
            if resp is None:
                try:
                    resp = self._data_source.list_rooms(cripta_id, pagina)
                except NotImplementedError:
                    break
                if self._cripta_en_disco:
                    self._almacen.guardar_pagina_salas(cripta_id, pagina, resp)

            salas_brutas = resp.get("salas", [])
            for item_sala in salas_brutas:
                nueva_sala = parsear_sala(item_sala, sala_salida_id)
                if not any(s.id == nueva_sala.id for s in salas_conocidas):
                    salas_conocidas.append(nueva_sala)

            total_paginas = int(resp.get("total_paginas", 1))
            if pagina >= total_paginas:
                break
            pagina += 1

        return salas_conocidas

    def cargar_contenido_salas(self, cripta_id: str, sala_ids: list[int]) -> list[list]:
        """Pide el contenido de varias salas en lotes de hasta 10 (§4.2).

        Por cada lote: 1 solicitud de contenido + las de catálogo que falten
        (también en lotes de 10). El resultado sigue el orden de `sala_ids`,
        no el de la respuesta, para que la incorporación sea determinista.
        """
        resultado: list[list] = []
        for i in range(0, len(sala_ids), MAX_POR_LOTE):
            lote = sala_ids[i:i + MAX_POR_LOTE]
            resultado.extend(self.armar_contenido(lote, self._leer_entradas(cripta_id, lote)))
        return resultado

    def _leer_entradas(self, cripta_id: str, lote: list[int]) -> list[dict]:
        """Solo E/S: primero disco; a la red solo van las salas que no estaban guardadas."""
        entradas: list[dict] = []
        para_red: list[int] = []
        for sala_id in lote:
            entrada = self._almacen.leer_contenido(cripta_id, sala_id) if self._cripta_en_disco else None
            if entrada is None:
                para_red.append(sala_id)
            else:
                self._lecturas_disco += 1
                entradas.append(entrada)
        if para_red:
            try:
                resp = self._data_source.room_content(cripta_id, para_red)
            except NotImplementedError:
                resp = {}
            for entrada in resp.get("contenido", []):
                if self._cripta_en_disco:
                    self._almacen.guardar_contenido(cripta_id, entrada)
                entradas.append(entrada)
        return entradas

    @staticmethod
    def _tipos_de(entradas: list[dict]) -> list[str]:
        tipos: list[str] = []
        for entrada in entradas:
            for e in entrada.get("enemigos", []):
                tipos.append(e.get("tipo"))
            for o in entrada.get("objetos", []):
                tipos.append(str(o))
            for t in entrada.get("trampas", []):
                tipos.append(t.get("tipo"))
        return tipos

    def armar_contenido(self, lote: list[int], entradas: list[dict],
                        fichas_descargadas: list[dict] | None = None) -> list[list]:
        """Resuelve fichas y arma el contenido en el orden de `lote` (determinista).

        Toca la caché de fichas, así que siempre corre en el hilo del juego.
        """
        catalogo = self._catalogo.asegurar_fichas(self._tipos_de(entradas),
                                                  descargadas=fichas_descargadas)
        resultado: list[list] = []
        for sala_id in lote:
            entrada = None
            for candidata in entradas:
                if int(candidata.get("sala", 0)) == sala_id:
                    entrada = candidata
                    break
            if entrada is not None:
                resultado.append([sala_id, parsear_contenido(entrada, catalogo)])
            # Sin respuesta (p. ej. --offline sin esa sala descargada) la sala queda
            # sin cargar: nunca se entra a una sala cuyo contenido no se conoce (§4.2).
        return resultado

    def descargar_contenido(self, cripta_id: str, lote: list[int]) -> list[list]:
        """Trabajo del hilo de precarga: SOLO E/S (disco y red), sin tocar el modelo.

        Trae el contenido del lote y las fichas que no estén ni en memoria ni en
        disco. Devuelve [entradas, fichas_crudas]; el armado se hace después en
        el hilo del juego, en un punto fijo (determinista).
        """
        entradas = self._leer_entradas(cripta_id, lote)
        faltantes: list[str] = []
        for id_ in self._tipos_de(entradas):
            if not id_ or id_ in faltantes or self._cache_fichas.contiene(id_):
                continue
            if self._catalogo_en_disco and self._almacen.leer_ficha(id_) is not None:
                continue
            faltantes.append(id_)
        fichas: list[dict] = []
        for i in range(0, len(faltantes), MAX_POR_LOTE):
            resp = self._data_source.catalog(faltantes[i:i + MAX_POR_LOTE])
            for bruto in resp.get("entidades", []):
                if self._catalogo_en_disco:
                    self._almacen.guardar_ficha(bruto)
                fichas.append(bruto)
        return [entradas, fichas]

    #  Presupuesto y estadísticas (§5.1)

    def fijar_presupuesto(self, presupuesto: int) -> None:
        self._data_source.fijar_presupuesto(presupuesto)

    def solicitudes_restantes(self) -> int | None:
        return self._data_source.solicitudes_restantes()

    @property
    def aciertos_cache(self) -> int:
        return self._cache_fichas.aciertos

    @property
    def fallos_cache(self) -> int:
        return self._cache_fichas.fallos

    @property
    def requests_made(self) -> int:
        return self._data_source.requests_made

    def es_offline(self) -> bool:
        fuente = getattr(self._data_source, "fuente", self._data_source)
        return fuente.__class__.__name__ == "AdaptadorOffline"

    def obtener_ficha(self, id_: str):
        return self._cache_fichas.obtener(id_)
