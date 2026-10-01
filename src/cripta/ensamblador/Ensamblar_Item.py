from modelo.Item import Item
from modelo.Item_Arma import ItemArma
from modelo.Item_Armadura import ItemArmadura
from modelo.Item_Pocion import ItemPocion
from modelo.Item_Antidoto import ItemAntidoto
from modelo.Item_Llave import ItemLlave
from modelo.Item_Antorcha import ItemAntorcha
from modelo.Item_Pergamino import ItemPergamino

from dto.ArmaDto import FichaArma
from dto.ArmaduraDto import FichaArmadura
from dto.PocionDto import FichaPocion
from dto.AntidotoDto import FichaAntidoto
from dto.LlaveDto import FichaLlave
from dto.AntorchaDto import FichaAntorcha
from dto.Pergamino_RetrocesoDto import FichaPergaminoRetroceso


def ensamblar_item(ficha):
    if isinstance(ficha, FichaArma):
        return ItemArma(ficha.id, ficha.nombre, ficha.peso, ficha.valor, ficha.ataque_bonus)
    if isinstance(ficha, FichaArmadura):
        return ItemArmadura(ficha.id, ficha.nombre, ficha.peso, ficha.valor, ficha.defensa_bonus)
    if isinstance(ficha, FichaPocion):
        return ItemPocion(ficha.id, ficha.nombre, ficha.peso, ficha.valor, ficha.cura, ficha.modificador_velocidad, ficha.duracion)
    if isinstance(ficha, FichaAntidoto):
        return ItemAntidoto(ficha.id, ficha.nombre, ficha.peso, ficha.valor)
    if isinstance(ficha, FichaLlave):
        return ItemLlave(ficha.id, ficha.nombre, ficha.peso, ficha.valor, ficha.abre)
    if isinstance(ficha, FichaAntorcha):
        return ItemAntorcha(ficha.id, ficha.nombre, ficha.peso, ficha.valor, ficha.duracion)
    if isinstance(ficha, FichaPergaminoRetroceso):
        return ItemPergamino(ficha.id, ficha.nombre, ficha.peso, ficha.valor)
    raise ValueError("No se puede ensamblar item de tipo " + type(ficha).__name__)
