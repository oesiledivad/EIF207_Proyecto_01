from .CatalogoDto import FichaCatalogo
from .EnemigoDto import FichaEnemigo
from .ArmaDto import FichaArma
from .ArmaduraDto import FichaArmadura
from .LlaveDto import FichaLlave
from .PocionDto import FichaPocion
from .AntidotoDto import FichaAntidoto
from .AntorchatDto import FichaAntorcha
from .Pergamino_retorcesoDto import FichaPergaminoRetroceso  
from .TrampaDto import FichaTrampa

def ficha_desde_dict(d: dict) -> FichaCatalogo:
    mapeo = {
        "enemigo": FichaEnemigo,
        "arma": FichaArma,
        "armadura": FichaArmadura,
        "pocion": FichaPocion,
        "antidoto": FichaAntidoto,
        "llave": FichaLlave,
        "antorcha": FichaAntorcha,
        "pergamino_retroceso": FichaPergaminoRetroceso,
        "trampa": FichaTrampa,
    }
    clase_dto = mapeo.get(d["clase"])
    if clase_dto is None:
        raise ValueError(f"Clase de catálogo desconocida: {d['clase']}")
    return clase_dto.desde_dict(d)