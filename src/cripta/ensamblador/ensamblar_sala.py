
from modelo.Sala import SalaJuego
from ensamblador.ensamblador_enemigo import ensamblar_enemigo
from ensamblador.Ensamblar_Item import ensamblar_item
def ensamblar_sala(esqueleto) -> SalaJuego:
    """Crea la sala solo con el mapa. El contenido llega después."""
    return SalaJuego(
        id=esqueleto.id,
        nombre=esqueleto.nombre,
        salidas=esqueleto.salidas,     
        enemigos=[],
        objetos=[],
        trampas=[],
    )
def poblar_sala(sala, contenido, catalogo):
    """Cuando llega el contenido de la sala, crea sus enemigos y objetos reales."""
    for colocacion in contenido.enemigos:
        ficha = catalogo.obtener(colocacion.tipo)
        sala.enemigos.append(ensamblar_enemigo(colocacion, ficha, sala.id))

    for id_objeto in contenido.objetos:
        ficha = catalogo.obtener(id_objeto)
        sala.objetos.append(ensamblar_item(ficha))

    sala.trampas = list(contenido.trampas)   # TODO: ensamblar_trampa