# ensamblador/ensamblar_sala.py

from src.cripta.modelo.Room import SalaJuego
from src.cripta.ensamblador.ensamblador_enemigo import ensamblar_enemigo
from src.cripta.ensamblador.Ensamblar_Item import ensamblar_item


def ensamblar_sala(esqueleto, contenido, fichas: dict) -> SalaJuego:
    """
    esqueleto: objeto Sala (DTO, de EsqueletoSala.salas)
    contenido: objeto ContenidoSala (DTO, de room_content)
    fichas: dict {id_tipo: FichaCatalogo} ya resuelto
    """
    enemigos = []
    for dto_enemigo in contenido.enemigos:
        ficha = fichas[dto_enemigo.tipo]
        enemigo = ensamblar_enemigo(dto_enemigo, ficha, esqueleto.id)
        enemigos.append(enemigo)

    objetos = []
    for id_objeto in contenido.objetos:
        ficha = fichas[id_objeto]
        item = ensamblar_item(ficha)
        objetos.append(item)

    return SalaJuego(
        id=esqueleto.id,
        nombre=esqueleto.nombre,
        salidas=esqueleto.salidas,
        enemigos=enemigos,
        objetos=objetos,
        trampas=contenido.trampas,
    )