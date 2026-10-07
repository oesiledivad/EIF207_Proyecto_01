from __future__ import annotations

from cripta.adaptadores.Crypt_Data_Source import CryptDataSource, PresupuestoAgotado
from cripta.adaptadores.Almacen_Disco import AlmacenDisco
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
from cripta.estructuras.Cache_Fichas import Cache_Fichas
from cripta.estructuras.Catalogo_Lista import Catalogo_Lista
from cripta.dto.FactoryDto_Ficha import parsear_ficha

MAX_POR_LOTE = 10  # §3.4: contenido y catálogo aceptan hasta 10 por solicitud


def _sin_repetidos(ids: list) -> list:
    """Quita repetidos y vacíos conservando el orden de aparición (determinista)."""
    unicos: list = []
    for id_ in ids:
        if id_ and id_ not in unicos:
            unicos.append(id_)
    return unicos


def _buscar_ficha(catalogo: Catalogo_Lista, id_tipo):
    try:
        return catalogo.obtener(id_tipo)
    except KeyError:
        return None


class CriptaService:
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
            version_cat = str(self._data_source.get_catalog_version().get("version", ""))
        except (PresupuestoAgotado, RuntimeError, OSError) as e:
            return f"No se pudo validar el catálogo en disco ({e}); se usará solo la red."
        if not version_cat:
            return "El servicio no informó versión de catálogo; se usará solo la red."
        cat_vigente = self._almacen.validar_catalogo(version_cat)
        self._catalogo_en_disco = True
        return (f"Caché en disco: cripta {'vigente' if cripta_vigente else 'nueva/actualizada'}, "
                f"catálogo {'vigente' if cat_vigente else 'nuevo/actualizado'}.")

    @property
    def lecturas_disco(self) -> int:
        return self._lecturas_disco

    #  Catálogo (§4.3, §4.4)

    def asegurar_fichas(self, ids: list[str], fijar: bool = False) -> Catalogo_Lista:
        """Resuelve los ids a fichas pidiendo a la red solo lo que falta, en lotes de 10.

        Devuelve las fichas resueltas en una lista propia, así quien llama
        puede leerlas aunque la caché desaloje alguna al insertar otras.

        Si `fijar` es True, suma una referencia por cada aparición del id en
        `ids` (dos ratas = 2 referencias) en el mismo momento en que la ficha
        está en memoria, para que un lote posterior no la desaloje.
        """
        resueltas = Catalogo_Lista()
        faltantes: list[str] = []
        for id_ in _sin_repetidos(ids):
            ficha = self._cache_fichas.obtener(id_)  # cuenta acierto/fallo
            if ficha is None:
                faltantes.append(id_)
            else:
                resueltas.agregar(ficha)
                if fijar:
                    self._fijar_apariciones(id_, ids)

        # 1) Disco: una ficha liberada de memoria cuesta una lectura, no una solicitud.
        para_red: list[str] = []
        for id_ in faltantes:
            bruto = self._almacen.leer_ficha(id_) if self._catalogo_en_disco else None
            if bruto is None:
                para_red.append(id_)
                continue
            self._lecturas_disco += 1
            self._incorporar_ficha(bruto, resueltas, ids, fijar)

        # 2) Red: solo lo que nunca se persistió (o cuya versión cambió), en lotes de 10.
        for i in range(0, len(para_red), MAX_POR_LOTE):
            lote = para_red[i:i + MAX_POR_LOTE]
            resp = self._data_source.catalog(lote)
            for bruto in resp.get("entidades", []):
                if self._catalogo_en_disco:
                    self._almacen.guardar_ficha(bruto)
                self._incorporar_ficha(bruto, resueltas, ids, fijar)
        return resueltas

    def _incorporar_ficha(self, bruto: dict, resueltas: Catalogo_Lista, ids: list[str], fijar: bool) -> None:
        ficha = parsear_ficha(bruto)
        self._cache_fichas.insertar(ficha.id, ficha)
        resueltas.agregar(ficha)
        if fijar:
            self._fijar_apariciones(ficha.id, ids)

    def _fijar_apariciones(self, id_: str, ids: list[str]) -> None:
        for otro in ids:
            if otro == id_:
                self._cache_fichas.marcar_en_uso(id_)

    def fijar_fichas(self, ids: list[str]) -> None:
        """Marca fichas como en uso (una referencia por aparición). Trae las que falten."""
        self.asegurar_fichas(ids, fijar=True)

    def liberar_fichas(self, ids: list[str]) -> None:
        """Quita una referencia por aparición; con 0 vuelven a ser desalojables."""
        for id_ in ids:
            if id_:
                self._cache_fichas.liberar(id_)

    def obtener_ficha_garantizada(self, id_: str):
        """Ficha desde caché; si fue desalojada, la vuelve a resolver."""
        ficha = self._cache_fichas.obtener(id_)
        if ficha is not None:
            return ficha
        return _buscar_ficha(self.asegurar_fichas([id_]), id_)

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
        if self._detalles is not None and self._detalles.id == cripta_id:
            return self._detalles  # ya pedidos (p.ej. al previsualizar): no gastar otra solicitud
        try:
            detalles = self._data_source.crypta_details(cripta_id)
            if not isinstance(detalles, dict):
                detalles = {}

            jugador = detalles.get("jugador", {})
            if not isinstance(jugador, dict):
                jugador = {}

            self._detalles = DetallesCripta(
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

    def cargar_contenido_salas(self, cripta_id: str, sala_ids: list[int]) -> list[tuple[int, ContenidoSala]]:
        """Pide el contenido de varias salas en lotes de hasta 10 (§4.2).

        Por cada lote: 1 solicitud de contenido + las de catálogo que falten
        (también en lotes de 10). El resultado sigue el orden de `sala_ids`,
        no el de la respuesta, para que la incorporación sea determinista.
        """
        resultado: list[tuple[int, ContenidoSala]] = []
        for i in range(0, len(sala_ids), MAX_POR_LOTE):
            lote = sala_ids[i:i + MAX_POR_LOTE]

            # Primero disco; a la red solo van las salas que no estaban guardadas.
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

            tipos: list[str] = []
            for entrada in entradas:
                for e in entrada.get("enemigos", []):
                    tipos.append(e.get("tipo"))
                for o in entrada.get("objetos", []):
                    tipos.append(str(o))
                for t in entrada.get("trampas", []):
                    tipos.append(t.get("tipo"))
            catalogo = self.asegurar_fichas(tipos)

            for sala_id in lote:
                entrada = None
                for candidata in entradas:
                    if int(candidata.get("sala", 0)) == sala_id:
                        entrada = candidata
                        break
                if entrada is None:
                    resultado.append((sala_id, ContenidoSala()))
                else:
                    resultado.append((sala_id, self._parsear_contenido(entrada, catalogo)))
        return resultado

    def cargar_contenido_sala(self, cripta_id: str, sala_id: int) -> ContenidoSala:
        """Compatibilidad: una sola sala (gasta un lote entero, preferir la versión por lotes)."""
        return self.cargar_contenido_salas(cripta_id, [sala_id])[0][1]

    @staticmethod
    def _parsear_contenido(entrada: dict, catalogo: Catalogo_Lista) -> ContenidoSala:
        enemigos: list[EnemigoPartida] = []
        for e in entrada.get("enemigos", []):
            tipo = str(e.get("tipo", ""))
            ficha = _buscar_ficha(catalogo, tipo)
            vida_max = ficha.vida_max if ficha else 0
            vida = e.get("vida")  # puede venir null: entonces empieza con vida_max
            enemigos.append(EnemigoPartida(
                id=str(e.get("instancia", "")),
                nombre=ficha.nombre if ficha else tipo,
                vida=int(vida) if vida is not None else vida_max,
                ataque=ficha.ataque if ficha else 0,
                defensa=ficha.defensa if ficha else 0,
                vida_max=vida_max,
                velocidad=ficha.velocidad if ficha else 100,
                comportamiento=ficha.comportamiento if ficha else "errante",
                regeneracion=getattr(ficha, "regeneracion", None),
                tipo=tipo,
                suelta=list(ficha.suelta or []) if ficha else [],
            ))

        objetos: list[ObjetoSuelo] = []
        for o in entrada.get("objetos", []):
            ficha = _buscar_ficha(catalogo, str(o))
            objetos.append(ObjetoSuelo(id=str(o), nombre=ficha.nombre if ficha else str(o)))

        trampas: list[TrampaPartida] = []
        for t in entrada.get("trampas", []):
            tipo = str(t.get("tipo", ""))
            ficha = _buscar_ficha(catalogo, tipo)
            trampas.append(TrampaPartida(
                id=str(t.get("instancia", "")),
                tipo=tipo,
                activa=True,
                dano=ficha.daño if ficha else 0,
                rearme=ficha.rearme if ficha else None,
                efecto=getattr(ficha, "efecto", "daño"),
            ))
        return ContenidoSala(enemigos=enemigos, objetos=objetos, trampas=trampas)

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
        return self._data_source.__class__.__name__ == "AdaptadorOffline"

    def obtener_ficha(self, id_: str):
        return self._cache_fichas.obtener(id_)