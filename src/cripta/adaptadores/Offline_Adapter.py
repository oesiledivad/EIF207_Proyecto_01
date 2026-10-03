"""Adaptador offline.

Permite montar la vista y probar el flujo sin depender de HTTP.
Los métodos que aún no se usan lanzan NotImplementedError para que
no fallen en silencio si alguien los invoca antes de implementarlos.

Cuando el paquete offline real esté disponible, estos métodos leerán
de los archivos descargados sin cambiar el contrato.
"""

from __future__ import annotations

from .Crypt_Data_Source import CryptDataSource


_CRIPTAS_EJEMPLO: list[dict] = [
    {"id": "cripta-01", "nombre": "Osario menor", "salas": 20, "dificultad": 1},
    {"id": "cripta-02", "nombre": "Bóvedas negras", "salas": 60, "dificultad": 2},
    {"id": "cripta-03", "nombre": "Cripta del rey", "salas": 120, "dificultad": 3},
]


class OfflineAdapter(CryptDataSource):
    """Implementa CryptDataSource leyendo de datos locales."""

    def __init__(self) -> None:
        self._requests_made = 0

    @property
    def requests_made(self) -> int:
        # Offline nunca hace solicitudes de red.
        return 0

    # ---------- Implementados ----------

    def crypta_list(self) -> dict:
        return {"criptas": list(_CRIPTAS_EJEMPLO)}

    # ---------- Pendientes (se implementarán cuando hagan falta) ----------

    def crypta_details(self, crypta_id: str) -> dict:
        raise NotImplementedError(
            "OfflineAdapter.crypta_details aún no implementado."
        )

    def list_rooms(self, crypta_id: str, pagina: int) -> dict:
        raise NotImplementedError(
            "OfflineAdapter.list_rooms aún no implementado."
        )

    def room_content(self, crypta_id: str, room_ids: list[int]) -> dict:
        raise NotImplementedError(
            "OfflineAdapter.room_content aún no implementado."
        )

    def catalog(self, ids: list[str]) -> dict:
        raise NotImplementedError(
            "OfflineAdapter.catalog aún no implementado."
        )

    def get_crypta_version(self, crypta_id: str) -> dict:
        raise NotImplementedError(
            "OfflineAdapter.get_crypta_version aún no implementado."
        )

    def get_catalog_version(self) -> dict:
        raise NotImplementedError(
            "OfflineAdapter.get_catalog_version aún no implementado."
        )