import sys
from pathlib import Path
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src" / "cripta"))
from  cripta.adaptadores.Network_Adapter import NetworkAdapter
from cripta.adaptadores.Guardar_Llamadas_API import Guardar_Llamadas_API
red = NetworkAdapter()
guardador = Guardar_Llamadas_API(RAIZ / "datos_prueba")
datos = red.crypta_list()
guardador.crypta_list(datos)
cid = datos["criptas"][0]["id"]
datos = red.crypta_details(cid)
guardador.crypta_details(cid, datos)
datos = red.list_rooms(cid, 1)
guardador.list_rooms(cid, 1, datos)
salas = [s["id"] for s in datos["salas"]][:10]
datos = red.room_content(cid, salas)
guardador.room_content(cid, salas, datos)
fichas = [o for s in datos["contenido"] for o in (s.get("objetos") or [])][:10]
datos = red.catalog(fichas)
guardador.catalog(fichas, datos)
print("Solicitudes:", red.requests_made)