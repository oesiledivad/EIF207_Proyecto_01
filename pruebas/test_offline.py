import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src" / "cripta"))

from cripta.adaptadores.AdaptadorOffline import AdaptadorOffline

fuente = AdaptadorOffline(RAIZ / "datos_prueba")

datos = fuente.crypta_list()
cid = datos["criptas"][0]["id"]
fuente.crypta_details(cid)
datos = fuente.list_rooms(cid, 1)
salas = [s["id"] for s in datos["salas"]][:10]

datos = fuente.room_content(cid, salas)
fichas = [o for s in datos["contenido"] for o in (s.get("objetos") or [])][:10]

datos = fuente.catalog(fichas)
print("Fichas leídas:", len(datos["entidades"]))
print("Solicitudes de red:", fuente.requests_made)