
from .Crypt_Data_Source import CryptDataSource
from pathlib import Path
import json
class Guardar_Llamadas_API(CryptDataSource):
    def __init__(self, carpeta):
        self._carpeta= Path(carpeta)
        self._carpeta.mkdir(parents=True, exist_ok=True)

    def guardar_llamada(self,nombre_archivo, dict_json) :

        with(self._carpeta/nombre_archivo).open("w", encoding="utf-8") as f:
           json.dump(dict_json, f, ensure_ascii=False, indent=2)
    def _leer(self, nombre_archivo):
        ruta = self._carpeta / nombre_archivo
        if not ruta.exists():
            return None
        with ruta.open("r", encoding="utf-8") as f:
            return json.load(f)
    def _combinar(self, nombre_archivo, clave, campo_id, datos):
        """Suma lo nuevo a lo ya guardado. Si un elemento ya estaba, lo reemplaza."""
        previo = self._leer(nombre_archivo)
        elementos = previo[clave] if previo else []
        for nuevo in datos[clave]:
            for i in range(len(elementos)):
                if elementos[i][campo_id] == nuevo[campo_id]:
                    elementos[i] = nuevo
                    break
            else:
                elementos.append(nuevo)
        self.guardar_llamada(nombre_archivo, {clave: elementos})
#   metodos heredados
    def crypta_list(self, datos): 
        self.guardar_llamada("criptas.json", datos)
    def crypta_details(self, crypta_id: str, datos:dict):
        self.guardar_llamada(f"cripta_{crypta_id}.json", datos)
    def list_rooms(self, crypta_id: str, pagina: int, datos:dict):
        self.guardar_llamada(f"cripta_{crypta_id}_salas_{pagina}.json", datos)
    def room_content(self, crypta_id, room_ids, datos):
        self._combinar(f"cripta_{crypta_id}_contenido.json", "contenido", "sala", datos)
    def catalog(self, ids, datos):
        self._combinar("catalogo.json", "entidades", "id", datos)
    def get_crypta_version(self, crypta_id, datos):
        self.guardar_llamada(f"cripta_{crypta_id}_version.json", datos)
    def get_catalog_version(self, datos):
        self.guardar_llamada("catalogo_version.json", datos)
    @property
    def requests_made(self) -> int:
        """Cuenta solicitudes de red reales. Offline siempre devuelve 0."""