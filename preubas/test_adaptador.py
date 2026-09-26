
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "cripta"))


from adaptadores.Crypt_Data_Source import CryptDataSource
from adaptadores.Network_Adapter import NetworkAdapter

def main() -> None:
    adaptador: CryptDataSource =NetworkAdapter()

    print("Mostrando cryptas")
    print(adaptador.crypta_list())

    print("\nMostrando detalles de la primera crypta")
    print(adaptador.crypta_details("cripta-01"))

    print("\nMostrando salas de la primera crypta")
    print(adaptador.list_rooms("cripta-01", 1))

    print("\nMostrando contenido de salas 1,2,3")
    print(adaptador.room_content("cripta-01", [1, 2, 3]))

    print("\nMostrando catálogo")
    print(adaptador.catalog(["itm_antorcha", "ent_rata_gigante"]))

    print("\nVersión de la cripta")
    print(adaptador.get_crypta_version("cripta-01"))

    print("\nVersión del catálogo")
    print(adaptador.get_catalog_version())

    print("\nTotal de solicitudes realizadas:", adaptador.requests_made)


if __name__ == "__main__":
    main()