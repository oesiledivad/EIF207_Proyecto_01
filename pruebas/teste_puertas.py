from cripta.adaptadores.AdaptadorOffline import AdaptadorOffline
from cripta.servicio.CriptaService import CriptaService
from cripta.controlador.Aplicacion import Aplicacion

servicio = CriptaService(AdaptadorOffline("datos_prueba"))
esqueleto = servicio.cargar_esqueleto_salas("cripta-01", 6)

app = Aplicacion(AdaptadorOffline("datos_prueba"))
app._crear_salas_desde_esqueleto(esqueleto)

puerta = app._salas.obtener(2).salidas.obtener("E")
assert puerta.cerrada is True
assert puerta.llave == "itm_llave_bronce"
assert puerta.cierre_automatico == 500
assert app._salas.obtener(2).salidas.obtener("N").llave is None
print("OK: las puertas conservan llave y cierre automatico")