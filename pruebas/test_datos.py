from cripta.dto.List_rooms import List_rooms
from cripta.dto.contenidoDto import ContenidoRespuesta
from cripta.dto.FactoryDto_Ficha import parsear_ficha

from cripta.adaptadores.Network_Adapter import NetworkAdapter
from cripta.dto.Crypta_All import Crypta_all
from cripta.dto.Crypta_Details import Crypta_Details

red = NetworkAdapter()

# 1. Lista de criptas
crudo = red.crypta_list()
criptas = [Crypta_all(**c) for c in crudo["criptas"]]
print(criptas)

# 2. Detalles de una cripta
detalles = Crypta_Details(**red.crypta_details(criptas[0].id))
print(detalles)
print("Jugador:", detalles.jugador.vida_max)

print("Solicitudes realizadas:", red.requests_made)

cid = criptas[0].id

# 3. Esqueleto (el mapa)
pagina = List_rooms(**red.list_rooms(cid, 1))
print("Salas:", len(pagina.salas))
print("Sala 1:", pagina.salas[0])

# 4. Contenido de las salas
ids_salas = [s.id for s in pagina.salas][:10]
contenido = ContenidoRespuesta(**red.room_content(cid, ids_salas))
print("Contenido sala 1:", contenido.contenido[0])

# 5. Fichas del catálogo, con los ids que aparecieron en el contenido
ids = []
for sala in contenido.contenido:
    for o in sala.objetos:
        if o not in ids:
            ids.append(o)
    for e in sala.enemigos:
        if e.tipo not in ids:
            ids.append(e.tipo)
    for t in sala.trampas:
        if t.tipo not in ids:
            ids.append(t.tipo)

crudo_cat = red.catalog(ids[:10])
fichas = [parsear_ficha(f) for f in crudo_cat["entidades"]]
for f in fichas:
    print(type(f).__name__, "->", f.id, f.nombre)