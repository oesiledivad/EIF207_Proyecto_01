from pathlib import Path

from cripta.adaptadores.AdaptadorOffline import AdaptadorOffline
from cripta.servicio.CriptaService import CriptaService
from cripta.controlador.Aplicacion import Aplicacion
from cripta.estructuras.Indice_Salas import IndiceSalas
from cripta.estructuras.Salidas import Salidas
from cripta.modelo.Jugador import Jugador
from cripta.modelo.Sala import SalaJuego
from cripta.modelo.Simulacion import Simulacion
from cripta.modelo.enemigos.Rastreador import Rastreador

DATOS = str(Path(__file__).resolve().parent.parent / "datos_prueba")


def mundo(rastro_11, rastro_12, cerrada_12=False):
    """Sala 10 con salidas N->11 y S->12. Devuelve (salas, rastreador en la sala 10)."""
    salas = IndiceSalas()
    s10 = Salidas()
    s10.agregar("N", 11, False)
    s10.agregar("S", 12, cerrada_12)
    for sid, salidas, rastro in ((10, s10, None), (11, Salidas(), rastro_11), (12, Salidas(), rastro_12)):
        sala = SalaJuego(sid, f"Sala {sid}", salidas, [], [], [])
        sala.ultimo_tiempo_visita = rastro
        salas.insertar(sid, sala)
    return salas, Rastreador("r-1", 10, 10, 3, 0, 100, 10, None)


# 1. Sigue el rastro más fresco (el de la sala 12, tiempo 300, frente al de la 11, tiempo 100)
salas, r = mundo(100, 300)
assert r._decidir_movimiento(salas, 350, None) == ("mover", 12)

# 2. Empate exacto: gana la sala de menor id
salas, r = mundo(300, 300)
assert r._decidir_movimiento(salas, 350, None) == ("mover", 11)

# 3. Caducidad: con 400 o más de antigüedad el rastro no sirve; con 399 sí
salas, r = mundo(0, None)
assert r._decidir_movimiento(salas, 399, None) == ("mover", 11)
assert r._decidir_movimiento(salas, 400, None) == ("esperar", None)

# 4. Sin rastro en ninguna vecina: espera
salas, r = mundo(None, None)
assert r._decidir_movimiento(salas, 100, None) == ("esperar", None)

# 5. Una puerta cerrada no se examina, aunque tenga el rastro más fresco
salas, r = mundo(100, 300, cerrada_12=True)
assert r._decidir_movimiento(salas, 350, None) == ("mover", 11)

# 6. El rastro de la sala actual se refresca en cada acción del jugador que consume tiempo
servicio = CriptaService(AdaptadorOffline(DATOS))
esqueleto = servicio.cargar_esqueleto_salas("cripta-01", 6)
app = Aplicacion(AdaptadorOffline(DATOS))
app._crear_salas_desde_esqueleto(esqueleto)
est = app._gestor.estado
est.salas_conocidas = esqueleto
est.sala_actual_id = 1
est.sala_salida_id = 6
est.activa = True
app._gestor.reiniciar_inventario(10)
app._simulacion = Simulacion(42)
app._jugador = Jugador("jugador", 30, 30, 5, 1, 100, 1, 0, 10)
app._jugador._proximo_evento = app._simulacion.agenda.insertar(0, app._jugador, "accion_actor")
app._gestor.refrescar_sala_actual()
app._salas.obtener(1).ultimo_tiempo_visita = 0       # la sala inicial recibe rastro en t=0
for sid in (1, 2, 3, 4, 5, 6):
    app._salas.obtener(sid).contenido_cargado = True  # sin red en la prueba

app.esperar()                                         # t=0 -> la acción corre en t=0, el reloj queda en 100
assert app._salas.obtener(1).ultimo_tiempo_visita == 0
app.esperar()                                         # esta acción corre en t=100
assert app._salas.obtener(1).ultimo_tiempo_visita == 100

# 7. Al completar un movimiento, la sala destino recibe el tiempo actual
assert app.mover("N").ok is True
assert app._salas.obtener(2).ultimo_tiempo_visita == 200
print("OK: rastro (fresco, empate, caducidad, puertas cerradas, refresco por accion y por movimiento)")