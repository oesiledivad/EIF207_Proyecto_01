"""Planificación y carga de las salas cercanas al jugador."""

from cripta.adaptadores.Crypt_Data_Source import PresupuestoAgotado

MAX_POR_LOTE = 10


class PrecargaService:
    """Selecciona salas por cercanía y distingue carga necesaria de opcional.

    Args:
        servicio: Servicio que obtiene el contenido por lotes.
    """

    def __init__(self, servicio) -> None:
        self._servicio = servicio

    #  Precarga por lotes (§4.2)

    @staticmethod
    def planificar_precarga(salas, max_id: int, origen_id: int) -> list[int]:
        """BFS desde `origen_id` por el esqueleto: las 10 salas sin contenido más cercanas.

        El origen va primero si falta. Cuesta O(salas visitadas) y se corta al
        juntar 10. Usa una lista de bool indexada por id (no set/dict).
        """
        visitado = [False] * (max_id + 1)
        cola = [origen_id]
        visitado[origen_id] = True
        i = 0
        elegidas: list[int] = []
        while i < len(cola) and len(elegidas) < MAX_POR_LOTE:
            sala = salas.obtener(cola[i])
            i += 1
            if sala is None:
                continue
            if not sala.contenido_cargado:
                elegidas.append(sala.id)
            for salida in sala.salidas:
                destino = salida.sala_destino
                if 0 <= destino <= max_id and not visitado[destino]:
                    visitado[destino] = True
                    cola.append(destino)
        return elegidas

    @staticmethod
    def necesita_precarga(salas, sala_id: int) -> bool:
        """True si la sala o alguna vecina directa todavía no tiene contenido. O(4)."""
        sala = salas.obtener(sala_id)
        if sala is None:
            return False
        if not sala.contenido_cargado:
            return True
        for salida in sala.salidas:
            vecina = salas.obtener(salida.sala_destino)
            if vecina is not None and not vecina.contenido_cargado:
                return True
        return False

    def cargar_lote(self, cripta_id: str, salas, max_id: int, origen_id: int, incorporar) -> None:
        """Pide el lote alrededor de `origen_id` y lo entrega a `incorporar(sala, contenido)`
        en el orden pedido (determinista). Esperar la red nunca mueve el reloj virtual.
        """
        ids = self.planificar_precarga(salas, max_id, origen_id)
        if not ids:
            return
        for sala_id, contenido in self._servicio.cargar_contenido_salas(cripta_id, ids):
            incorporar(salas.obtener(sala_id), contenido)

    def asegurar_sala_cargada(self, cripta_id: str, salas, max_id: int, sala_id: int,
                              incorporar) -> str | None:
        """Garantiza el contenido antes de confirmar un movimiento. Devuelve error o None."""
        sala = salas.obtener(sala_id)
        if sala is None:
            return f"La sala {sala_id} no existe en el esqueleto."
        if sala.contenido_cargado:
            return None
        try:
            self.cargar_lote(cripta_id, salas, max_id, sala_id, incorporar)  # sala_id va primero
        except (PresupuestoAgotado, RuntimeError) as e:
            return str(e)
        return None

    def precargar_alrededor(self, cripta_id: str, salas, max_id: int, sala_id: int,
                            incorporar) -> str | None:
        """Precarga opcional: si falta alguna vecina, pide un lote. Devuelve aviso o None."""
        if not self.necesita_precarga(salas, sala_id):
            return None
        try:
            self.cargar_lote(cripta_id, salas, max_id, sala_id, incorporar)
        except PresupuestoAgotado as e:
            return f"Precarga omitida: {e}"
        except RuntimeError as e:
            return f"Precarga fallida: {e}"
        return None
