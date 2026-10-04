


from .Crypt_Data_Source import CryptDataSource
from pathlib import Path
import json
MAX_POR_LOTE=10
class Adaptador_Offline(CryptDataSource):
    """Adaptador que no hace llamadas de red, sino que guarda las respuestas en archivos locales."""
    def __init__(self, carpeta):
        self.carpeta = Path(carpeta)
    @property
    def requests_made(self) -> int:
        return 0
    def _leer(self, nombre_archivo):
        ruta = self.carpeta / nombre_archivo
        if not ruta.exists():
            raise FileNotFoundError(f"No hay respuesta grabada: {ruta}")
        with ruta.open("r", encoding="utf-8") as f:
            return json.load(f)
    def crypta_list(self) -> dict:
        return self._leer("criptas.json")
    def crypta_details(self, crypta_id: str) -> dict:
        return self._leer(f"cripta_{crypta_id}.json")
    def list_rooms(self, crypta_id: str, pagina: int) -> dict:
        return self._leer(f"cripta_{crypta_id}_salas_{pagina}.json")
    def room_content(self, crypta_id: str, room_ids: list) -> dict:
        if len(room_ids) > MAX_POR_LOTE:
            raise ValueError(f"Máximo {MAX_POR_LOTE} salas por llamada")
        todo = self._leer(f"cripta_{crypta_id}_contenido.json")
        elegidas = []
        for entrada in todo["contenido"]:
            if entrada["sala"] in room_ids:
                elegidas.append(entrada)
        return {"contenido": elegidas}
    def catalog(self, ids: list) -> dict:
        if len(ids) > MAX_POR_LOTE:
            raise ValueError(f"Máximo {MAX_POR_LOTE} ids por llamada")
        todo = self._leer("catalogo.json")
        elegidas = []
        for id_pedido in ids:
            for ficha in todo["entidades"]:
                if ficha["id"] == id_pedido:
                    elegidas.append(ficha)
                    break
            else:
                raise RuntimeError(f"Ficha no grabada: {id_pedido}")
        return {"entidades": elegidas}
    def get_crypta_version(self, crypta_id: str) -> dict:
        return self._leer(f"cripta_{crypta_id}_version.json")

    def get_catalog_version(self) -> dict:
        return self._leer("catalogo_version.json")
    
