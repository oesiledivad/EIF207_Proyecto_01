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
        case "enemigo":             return _parsear_enemigo(d)
        case "trampa":              return FichaTrampa(**d)
        case c:
            raise ValueError(f"Clase desconocida en el catálogo: {c!r}")


def _parsear_enemigo(d: dict):
    """Ficha de enemigo; un cazador exige `rango` entero >= 0 (FR-008, FR-009)."""
    ficha = FichaEnemigo(**d)
    if ficha.comportamiento == "cazador":
        rango = ficha.rango
        if isinstance(rango, bool) or not isinstance(rango, int) or rango < 0:
            raise ValueError(
                f"Ficha {ficha.id!r}: un cazador necesita un campo rango entero mayor o igual que 0 "
                f"(recibido {rango!r}).")
    return ficha
