from cripta.adaptadores.Network_Adapter import NetworkAdapter
from cripta.dto.Crypta_All import Crypta_all
from cripta.dto.Crypta_Details import Crypta_Details

red = NetworkAdapter()

# 1. Lista de criptas
crudo = red.crypta_list()
criptas = [Crypta_all(**c) for c in crudo["criptas"]]
print(criptas)

# 2. Detalles de una cripta
detalles = Crypta_Details(**red.crypta_details(criptas[0].id))
print(detalles)
print("Jugador:", detalles.jugador.vida_max)

print("Solicitudes realizadas:", red.requests_made)