"""Resolución de fichas y protección de referencias en uso."""

from cripta.adaptadores.Crypt_Data_Source import PresupuestoAgotado
from cripta.dto.FactoryDto_Ficha import parsear_ficha
from cripta.dto.FactoryDto_Partida import buscar_ficha
from cripta.estructuras.Catalogo_Lista import Catalogo_Lista

MAX_POR_LOTE = 10


def _sin_repetidos(ids: list) -> list:
    """Quita repetidos y vacíos conservando el orden de aparición (determinista)."""
    unicos: list = []
    for id_ in ids:
        if id_ and id_ not in unicos:
            unicos.append(id_)
    return unicos


class CatalogoService:
    """Resuelve fichas desde memoria, disco y red, y administra referencias.

    Args:
        servicio: Contexto de datos de la sesión; su caché cambia al reiniciar.
    """

    def __init__(self, servicio) -> None:
        self._servicio = servicio

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
            ficha = self._servicio._cache_fichas.obtener(id_)  # cuenta acierto/fallo
            if ficha is None:
                faltantes.append(id_)
            else:
                resueltas.agregar(ficha)
                if fijar:
                    self._fijar_apariciones(id_, ids)

        # 1) Disco: una ficha liberada de memoria cuesta una lectura, no una solicitud.
        para_red: list[str] = []
        for id_ in faltantes:
            bruto = self._servicio._almacen.leer_ficha(id_) if self._servicio._catalogo_en_disco else None
            if bruto is None:
                para_red.append(id_)
                continue
            self._servicio._lecturas_disco += 1
            self._incorporar_ficha(bruto, resueltas, ids, fijar)

        # 2) Red: solo lo que nunca se persistió (o cuya versión cambió), en lotes de 10.
        for i in range(0, len(para_red), MAX_POR_LOTE):
            lote = para_red[i:i + MAX_POR_LOTE]
            resp = self._servicio._data_source.catalog(lote)
            for bruto in resp.get("entidades", []):
                if self._servicio._catalogo_en_disco:
                    self._servicio._almacen.guardar_ficha(bruto)
                self._incorporar_ficha(bruto, resueltas, ids, fijar)
        return resueltas

    def _incorporar_ficha(self, bruto: dict, resueltas: Catalogo_Lista, ids: list[str], fijar: bool) -> None:
        ficha = parsear_ficha(bruto)
        self._servicio._cache_fichas.insertar(ficha.id, ficha)
        resueltas.agregar(ficha)
        if fijar:
            self._fijar_apariciones(ficha.id, ids)

    def _fijar_apariciones(self, id_: str, ids: list[str]) -> None:
        for otro in ids:
            if otro == id_:
                self._servicio._cache_fichas.marcar_en_uso(id_)

    def fijar_fichas(self, ids: list[str]) -> None:
        """Marca fichas como en uso (una referencia por aparición). Trae las que falten."""
        self.asegurar_fichas(ids, fijar=True)

    def liberar_fichas(self, ids: list[str]) -> None:
        """Quita una referencia por aparición; con 0 vuelven a ser desalojables."""
        for id_ in ids:
            if id_:
                self._servicio._cache_fichas.liberar(id_)

    def obtener_ficha_garantizada(self, id_: str):
        """Ficha desde caché; si fue desalojada, la vuelve a resolver."""
        ficha = self._servicio._cache_fichas.obtener(id_)
        if ficha is not None:
            return ficha
        return buscar_ficha(self.asegurar_fichas([id_]), id_)

    #  Protección de fichas en uso (§4.4)
    #  En uso = enemigo activo, objeto en inventario, objeto en el suelo o
    #  trampa de la sala actual. Cada aparición suma una referencia.

    def fijar_seguro(self, tipos: list[str]) -> str | None:
        """Protege fichas; si hubiera que traerlas y no se puede, devuelve el error."""
        try:
            self.fijar_fichas(tipos)
        except (PresupuestoAgotado, RuntimeError) as e:
            return f"No se pudo proteger fichas: {e}"
        return None

    @staticmethod
    def tipos_visibles(sala) -> list[str]:
        """Fichas que usa la sala actual: objetos del suelo y trampas."""
        tipos = [o.tipo_id or o.id for o in sala.objetos]
        for t in sala.trampas:
            tipos.append(t.tipo)
        return tipos

    def fijar_contenido_visible(self, sala) -> str | None:
        return self.fijar_seguro(self.tipos_visibles(sala))

    def liberar_contenido_visible(self, sala) -> None:
        self.liberar_fichas(self.tipos_visibles(sala))

    @classmethod
    def tipos_activos(cls, inventario, salas, sala_actual) -> list[str]:
        """Todas las referencias en uso; sirve para re-sincronizar tras un retroceso."""
        tipos = [item.tipo_id for item in inventario.items()]
        for sala in salas._datos:
            if sala is not None:
                tipos.extend(e.tipo for e in sala.enemigos
                             if e.vida > 0 and e._proximo_evento is not None)
        tipos.extend(cls.tipos_visibles(sala_actual))
        return tipos

    def reproteger(self, anteriores: list[str], actuales: list[str]) -> str | None:
        """Cambia las referencias de `anteriores` por las de `actuales` (retroceso)."""
        self.liberar_fichas(anteriores)
        return self.fijar_seguro(actuales)
