# dto/FactoryDto_Ficha.py
from .ArmaDto import FichaArma
from .ArmaduraDto import FichaArmadura
from .PocionDto import FichaPocion
from .AntidotoDto import FichaAntidoto
from .AntorchaDto import FichaAntorcha
from .LlaveDto import FichaLlave
from .Pergamino_RetrocesoDto import FichaPergaminoRetroceso
from .EnemigoDto import FichaEnemigo
from .TrampaDto import FichaTrampa


def parsear_ficha(d: dict):
    match d.get("clase"):
        case "arma":                return FichaArma(**d)
        case "armadura":            return FichaArmadura(**d)
        case "pocion":              return FichaPocion(**d)
        case "antidoto":            return FichaAntidoto(**d)
        case "antorcha":            return FichaAntorcha(**d)
        case "llave":               return FichaLlave(**d)
        case "pergamino_retroceso": return FichaPergaminoRetroceso(**d)
        case "enemigo":             return FichaEnemigo(**d)
        case "trampa":              return FichaTrampa(**d)
        case c:
            raise ValueError(f"Clase desconocida en el catálogo: {c!r}")