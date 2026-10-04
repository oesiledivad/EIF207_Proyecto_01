import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src" / "cripta"))

from dto.FactoryDto_Ficha import parsear_ficha
from dto.Crypta_Details import Crypta_Details
from dto.contenidoDto import EnemigoContenido
from estructuras.Catalogo_Lista import Catalogo_Lista
from ensamblador.Ensamblar_Item import ensamblar_item
from ensamblador.ensamblador_enemigo import ensamblar_enemigo
from ensamblador.ensamblar_jugador import ensamblar_jugador
from ensamblador.ensamblador_cripta import ensamblar_cripta
# datos de prueba: fichas crudas (dict) que simulan la respuesta de la API
crudos = [
    {"id": "itm_daga", "nombre": "Daga oxidada", "clase": "arma",
     "peso": 2, "valor": 5, "ataque_bonus": 3},
    {"id": "itm_pocion", "nombre": "Poción menor", "clase": "pocion",
     "peso": 1, "valor": 8, "cura": 10},
    {"id": "ent_rata", "nombre": "Rata gigante", "clase": "enemigo",
     "vida_max": 12, "ataque": 3, "defensa": 0, "velocidad": 120,
     "comportamiento": "rastreador"},
]

# 1. parsear fichas (dict -> dataclass)
fichas = [parsear_ficha(c) for c in crudos]
print("1. parsear_ficha OK:", [type(f).__name__ for f in fichas])

# 2. catálogo (lista)
catalogo = Catalogo_Lista(fichas)
assert catalogo.obtener("itm_pocion").nombre == "Poción menor"
print("2. CatalogoLista OK")

# 3. item
item = ensamblar_item(catalogo.obtener("itm_daga"))
print("3. ensamblar_item OK:", type(item).__name__)

# 4. enemigo, sin vida en la colocación: debe nacer con la vida máxima
colocacion = EnemigoContenido(instancia="rata#1", tipo="ent_rata")
enemigo = ensamblar_enemigo(colocacion, catalogo.obtener(colocacion.tipo), sala_id=1)
assert enemigo.vida == 12
print("4. ensamblar_enemigo OK:", type(enemigo).__name__, "vida", enemigo.vida)

# 5. jugador, con el objeto anidado que arma __post_init__
detalles = Crypta_Details(
    id="cripta-01", version="x", salas_total=6, paginas=1, salas_por_pagina=50,
    sala_inicial=1, sala_salida=6, llave_salida="itm_llave_negra",
    presupuesto_solicitudes=9, inventario_max=10,
    jugador={"vida_max": 30, "ataque": 6, "defensa": 2, "velocidad": 100},
)
jugador = ensamblar_jugador(detalles)
assert jugador.vida == 30
print("5. ensamblar_jugador OK: vida", jugador.vida, "sala", jugador.sala)
print("\nTodo bien.")

#Ensamblar cripta y ensamblar sala sin el adapatador de red, solo con los datos que ya tenemos, que son identicos a las respuestas de la API


crudo_esqueleto = {
    "pagina": 1, "total_paginas": 1,
    "salas": [
        {"id": 1, "nombre": "Entrada", "salidas": {"N": {"sala": 2}}},
        {"id": 2, "nombre": "Pasillo", "salidas": {"S": {"sala": 1}, "E": {"sala": 3}}},
        {"id": 3, "nombre": "Cripta final", "salidas": {"O": {"sala": 2}}},
    ],
}

# contenido: lo que devolvería room_content (qué hay dentro)
crudo_contenido = {
    "contenido": [
        {"sala": 1, "objetos": ["itm_daga"]},                      # sin enemigos ni trampas
        {"sala": 2, "enemigos": [{"instancia": "rata#1", "tipo": "ent_rata"}],
                     "objetos": ["itm_pocion"]},
    ]
}
from dto.List_rooms import List_rooms
from dto.contenidoDto import ContenidoRespuesta
from ensamblador.ensamblar_sala import ensamblar_sala, poblar_sala
from ensamblador.ensamblador_cripta import ensamblar_cripta

# 6. sala: primero solo el mapa
pagina = List_rooms(**crudo_esqueleto)
sala1 = ensamblar_sala(pagina.salas[0])
assert sala1.nombre == "Entrada"
assert sala1.objetos == [] and sala1.enemigos == []        # todavía sin contenido
print("6. ensamblar_sala OK (sin contenido)")

# 7. poblar: llega el contenido y se crean los objetos reales
contenido = ContenidoRespuesta(**crudo_contenido)
poblar_sala(sala1, contenido.contenido[0], catalogo)
assert len(sala1.objetos) == 1
print("7. poblar_sala OK:", type(sala1.objetos[0]).__name__)

# 8. sala con enemigo y objeto
sala2 = ensamblar_sala(pagina.salas[1])
poblar_sala(sala2, contenido.contenido[1], catalogo)
assert len(sala2.enemigos) == 1 and sala2.enemigos[0].vida == 12
print("8. sala con enemigo OK:", type(sala2.enemigos[0]).__name__)

# 9. cripta completa
detalles.salas_total = 3                   
cripta = ensamblar_cripta(detalles, [pagina])
assert len(cripta.salas) == 3
assert cripta.obtener_sala(3).nombre == "Cripta final"
print("9. ensamblar_cripta OK:", cripta.resumen())

#TAREA, HACERLO CON EL ADAPTADOR DE RED

