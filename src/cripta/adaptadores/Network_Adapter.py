import uuid
import time
import requests
from .Crypt_Data_Source import CryptDataSource, PresupuestoAgotado
from .Diagnostico_Red import registro_red

_CLIENT_ID = str(uuid.uuid4())


class NetworkAdapter(CryptDataSource):
    def __init__(self, timeout: int = 10, max_reintentos_429: int = 5) -> None:
        self.BASE_URL = "https://cripta-api.kad06a0zhgs84.us-east-2.cs.amazonlightsail.com/v1"
        self.timeout = timeout
        self.max_reintentos_429 = max_reintentos_429
        self.client_id = _CLIENT_ID  # compartido por todas las partidas de esta ejecución
        self.headers = {"X-Cripta-Client-Id": self.client_id}
        self._requests_made = 0
        self._presupuesto: int | None = None  # se conoce al leer los datos generales

    @property
    def requests_made(self) -> int:
        return self._requests_made

    def reiniciar_partida(self) -> None:
        self._requests_made = 0
        self._presupuesto = None

    def fijar_presupuesto(self, presupuesto: int) -> None:
        self._presupuesto = presupuesto
        registro_red.info("presupuesto conocido solicitudes=%s/%s", self._requests_made, presupuesto)

    def solicitudes_restantes(self) -> int | None:
        if self._presupuesto is None:
            return None
        return max(0, self._presupuesto - self._requests_made)

    def _request(self, endpoint: str, params: dict = None) -> dict:
        url = f"{self.BASE_URL}{endpoint}"
        intentos = 0
        while True:
            # Control estricto: se revisa ANTES de cada intento, reintentos incluidos (5.1).
            if self._presupuesto is not None and self._requests_made >= self._presupuesto:
                registro_red.warning("rechazo recurso=%s solicitudes=%s/%s motivo=presupuesto",
                                     endpoint, self._requests_made, self._presupuesto)
                raise PresupuestoAgotado(
                    f"Presupuesto de red agotado ({self._requests_made}/{self._presupuesto}) "
                    f"al solicitar {endpoint}"
                )
            inicio = time.perf_counter()
            try:
                respuesta = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            except requests.RequestException as e:
                self._requests_made += 1  # la solicitud salió, cuenta
                registro_red.error("intento recurso=%s numero=%s resultado=transporte error=%s "
                                   "duracion_ms=%.3f solicitudes=%s/%s", endpoint, intentos + 1,
                                   type(e).__name__, (time.perf_counter() - inicio) * 1000,
                                   self._requests_made, self._presupuesto)
                raise RuntimeError(f"Error de red en {endpoint}: {e}") from e
            self._requests_made += 1
            registro_red.info("intento recurso=%s parametros=%s numero=%s estado=%s duracion_ms=%.3f "
                              "solicitudes=%s/%s", endpoint, params, intentos + 1, respuesta.status_code,
                              (time.perf_counter() - inicio) * 1000, self._requests_made, self._presupuesto)

            if respuesta.status_code == 200:
                return respuesta.json()

            if respuesta.status_code == 429:
                intentos += 1
                if intentos > self.max_reintentos_429:
                    registro_red.error("rechazo recurso=%s motivo=limite_reintentos_429", endpoint)
                    raise RuntimeError(f"Limite de reintentos 429 excedido en {endpoint}")
                try:
                    espera = respuesta.json().get("reintentar_en", 1)
                except ValueError:
                    espera = 1
                registro_red.info("espera recurso=%s motivo=429 segundos=%s", endpoint, espera)
                time.sleep(espera)  # tiempo real: nunca toca el reloj virtual
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

    def key_locations(self, crypta_id: str) -> dict:
        return self._request(f"/criptas/{crypta_id}/llaves")
