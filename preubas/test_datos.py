# preubas/test_catalogo_dto.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "cripta"))

from adaptadores.Network_Adapter import NetworkAdapter
from dto.FactoryDto_Ficha import ficha_desde_dict


def main():
    adaptador = NetworkAdapter()
    ids = [
        "itm_antorcha", "itm_daga_oxidada", "ent_rata_gigante", "trp_dardos",
        "itm_llave_bronce", "itm_coraza_cuero", "ent_guardian_oseo",
        "itm_llave_negra", "itm_pocion_menor", "itm_pergamino_retroceso",
    ]
    respuesta = adaptador.catalog(ids)

    for entidad_dict in respuesta["entidades"]:
        ficha = ficha_desde_dict(entidad_dict)
        print(type(ficha).__name__, "->", ficha.id, ficha.nombre)


if __name__ == "__main__":
    main()