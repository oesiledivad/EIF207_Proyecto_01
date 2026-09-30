# ensamblador/items.py

from src.cripta.modelo.Item import Item
from src.cripta.modelo.Item_Arma import ItemArma
from src.cripta.modelo.Item_Armadura import ItemArmadura
from src.cripta.modelo.Item_Pocion import ItemPocion
from src.cripta.modelo.Item_Antidoto import ItemAntidoto
from src.cripta.modelo.Item_Llave import ItemLlave
from src.cripta.modelo.Item_Antorcha import ItemAntorcha
from src.cripta.modelo.Item_Pergamino import ItemPergamino

from src.cripta.dto.ArmaDto import FichaArma
from src.cripta.dto.ArmaduraDto import FichaArmadura
from src.cripta.dto.PocionDto import FichaPocion
from src.cripta.dto.AntidotoDto import FichaAntidoto
from src.cripta.dto.LlaveDto import FichaLlave
from src.cripta.dto.AntorchatDto import FichaAntorcha
from src.cripta.dto.Pergamino_retorcesoDto import FichaPergaminoRetroceso

@staticmethod
def ensamblarItem(ficha) -> Item:
    if isinstance(ficha, FichaArma):
        return ItemArma(ficha.id, ficha.nombre, ficha.peso, ficha.valor, ficha.ataque_bonus)

    if isinstance(ficha, FichaArmadura):
        return ItemArmadura(ficha.id, ficha.nombre, ficha.peso, ficha.valor, ficha.defensa_bonus)

    if isinstance(ficha, FichaPocion):
        return ItemPocion(
            ficha.id, ficha.nombre, ficha.peso, ficha.valor,
            ficha.cura, ficha.modificador_velocidad, ficha.duracion,
        )

    if isinstance(ficha, FichaAntidoto):
        return ItemAntidoto(ficha.id, ficha.nombre, ficha.peso, ficha.valor)

    if isinstance(ficha, FichaLlave):
        return ItemLlave(ficha.id, ficha.nombre, ficha.peso, ficha.valor,
         ficha.abre)

    if isinstance(ficha, FichaAntorcha):
        return ItemAntorcha(ficha.id, ficha.nombre, ficha.peso, ficha.valor, ficha.duracion)

    if isinstance(ficha, FichaPergaminoRetroceso):
        return ItemPergamino(ficha.id, ficha.nombre, ficha.peso, ficha.valor)

    raise ValueError(f"No sé ensamblar item de tipo {type(ficha).__name__}")