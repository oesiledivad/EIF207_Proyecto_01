import uuid
import time
import requests
from .Crypt_Data_Source import CryptDataSource


class NetworkAdapter(CryptDataSource):
    def __init__(self, timeout: int = 10, max_reintentos_429: int = 5) -> None:
        self.BASE_URL = "https://cripta-api.kad06a0zhgs84.us-east-2.cs.amazonlightsail.com/v1"
        self.timeout = timeout
        self.max_reintentos_429 = max_reintentos_429
        self.client_id = str(uuid.uuid4())
        self.headers = {"X-Cripta-Client-Id": self.client_id}
        self._requests_made = 0
        
    @property
    def requests_made(self) -> int:
        return self._requests_made

    def _request(self, endpoint: str, params: dict = None) -> dict:
        url = f"{self.BASE_URL}{endpoint}"
        intentos = 0
        while True:
            respuesta = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            self._requests_made += 1

            if respuesta.status_code == 200:
                return respuesta.json()

            if respuesta.status_code == 429:
                intentos += 1
                if intentos > self.max_reintentos_429:
                    raise RuntimeError(f"Limite de reintentos 429 excedido en {endpoint}")
                time.sleep(respuesta.json().get("reintentar_en", 1))
                continue

            raise RuntimeError(f"Error {respuesta.status_code} en {endpoint}: {respuesta.text}")

    def crypta_list(self) -> dict:
        return self._request("/criptas")

    def crypta_details(self, crypta_id: str) -> dict:
        return self._request(f"/criptas/{crypta_id}")

    def list_rooms(self, crypta_id: str, pagina: int) -> dict:
        return self._request(f"/criptas/{crypta_id}/salas", params={"pagina": pagina})

    def room_content(self, crypta_id: str, room_ids: list) -> dict:
        ids = ",".join(str(r) for r in room_ids)
        return self._request(f"/criptas/{crypta_id}/contenido", params={"salas": ids})

    def catalog(self, ids: list) -> dict:
        return self._request("/catalogo", params={"ids": ",".join(ids)})

    def get_crypta_version(self, crypta_id: str) -> dict:
        return self._request(f"/criptas/{crypta_id}/version")

    def get_catalog_version(self) -> dict:
        return self._request("/catalogo/version")
    