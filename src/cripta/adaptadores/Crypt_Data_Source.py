from abc import ABC, abstractmethod


class PresupuestoAgotado(RuntimeError):
    """Se lanzó una solicitud HTTP cuando ya no quedaba presupuesto (§5.1)."""


class CryptDataSource(ABC):
    @abstractmethod
    def crypta_list(self) -> dict:
        """GET /criptas"""

    @abstractmethod
    def crypta_details(self, crypta_id: str) -> dict:
        """GET /criptas/{id}"""

    @abstractmethod
    def list_rooms(self, crypta_id: str, pagina: int) -> dict:
        """GET /criptas/{id}/salas?pagina=n"""

    @abstractmethod
    def room_content(self, crypta_id: str, room_ids: list[int]) -> dict:
        """GET /criptas/{id}/contenido?salas=...  (máx. 10 por llamada)"""

    @abstractmethod
    def catalog(self, ids: list[str]) -> dict:
        """GET /catalogo?ids=...  (máx. 10 por llamada)"""

    @abstractmethod
    def get_crypta_version(self, crypta_id: str) -> dict:
        """GET /criptas/{id}/version"""

    @abstractmethod
    def get_catalog_version(self) -> dict:
        """GET /catalogo/version"""

    @property
    @abstractmethod
    def requests_made(self) -> int:
        """Cuenta solicitudes de red reales. Offline siempre devuelve 0."""

    def fijar_presupuesto(self, presupuesto: int) -> None:
        """Fija presupuesto_solicitudes de la cripta. Offline: no aplica."""

    def solicitudes_restantes(self) -> int | None:
        """None = sin límite (offline o presupuesto aún desconocido)."""
        return None
