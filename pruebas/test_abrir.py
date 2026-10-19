from pathlib import Path

from cripta.adaptadores.AdaptadorOffline import AdaptadorOffline
from cripta.servicio.CriptaService import CriptaService
from cripta.controlador.Aplicacion import Aplicacion
from cripta.estructuras.Inventario import ItemInventario
from cripta.modelo.Jugador import Jugador
from cripta.modelo.Simulacion import Simulacion

DATOS = str(Path(__file__).resolve().parent.parent / "datos_offline")

servicio = CriptaService(AdaptadorOffline(DATOS))
esqueleto = servicio.cargar_esqueleto_salas("cripta-01", 6)

app = Aplicacion(AdaptadorOffline(DATOS))
app._crear_salas_desde_esqueleto(esqueleto)
app._gestor.estado.salas_conocidas = esqueleto
app._gestor.estado.sala_actual_id = 2
app._gestor.estado.sala_salida_id = 6
app._gestor.estado.activa = True
app._gestor.reiniciar_inventario(10)
app._simulacion = Simulacion(42)
app._jugador = Jugador("jugador", 30, 30, 5, 1, 100, 2, 0, 10)
app._jugador._proximo_evento = app._simulacion.agenda.insertar(0, app._jugador, "accion_actor")
app._gestor.refrescar_sala_actual()
app._salas.obtener(2).ultimo_tiempo_visita = 0

reloj = app._simulacion.reloj
puerta = app._salas.obtener(2).salidas.obtener("E")

# 1. Sin la llave: se rechaza y NO consume tiempo
r = app.abrir("E")
assert r.ok is False and "llave" in r.motivo.lower()
assert reloj.tiempo_actual == 0 and puerta.cerrada is True
assert app._jugador._proximo_evento.tiempo_siguiente == 0

# 2. Dirección sin salida / puerta ya abierta
assert app.abrir("O").ok is False
assert app.abrir("N").ok is False  # N está abierta

# 3. Con la llave: abre, cuesta 50, la llave NO se consume
app._gestor.inventario.agregar(ItemInventario("i-1", "itm_llave_bronce", "Llave de bronce", "desconocido", 1, 0))
r = app.abrir("E")
assert r.ok is True, r.motivo
assert puerta.cerrada is False
assert app._jugador._proximo_evento.tiempo_siguiente == 50
assert app._gestor.inventario.tamano == 1
assert puerta.evento_cierre is not None and puerta.evento_cierre.tiempo_siguiente == 0 + 500

# 4. La vecindad (Vista) lo refleja
vec = {v.direccion: v for v in app._gestor.estado.vecindad}
assert vec["E"].cerrada is False

# 5. Cierre automático: tras 500 unidades la puerta se cierra sola
for _ in range(6):
    app.esperar()
assert reloj.tiempo_actual >= 500
assert puerta.cerrada is True and puerta.evento_cierre is None
textos = [m.texto for m in app.bitacora().ultimos()]
assert any("se cierra" in t for t in textos), textos

# 6. Se puede volver a abrir (la llave sigue en el inventario)
assert app.abrir("E").ok is True and puerta.cerrada is False
print("OK: abrir con llave y cierre automatico")