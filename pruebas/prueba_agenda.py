# Prueba de AgendaEventos utilizando un Jugador como actor.
# Por ahora esta asi con lo basico despues se puede hacer mejor

from cripta.modelo.Jugador import Jugador
from cripta.estructuras.Agenda_Eventos import HeapAgendaEventos

agenda = HeapAgendaEventos()

jugador = Jugador(
    "jugador",
    100,       # vida
    100,       # vida máxima
    20,        # ataque
    10,        # defensa
    100,       # velocidad
    "sala1",   # sala
    0,         # tiempo siguiente
    5          # capacidad máxima del inventario
)


print("=== PRUEBA DE INSERCIÓN ===")

evento = agenda.insertar(
    100,
    jugador,
    "accion_actor"
)

# Guardamos en el jugador el evento que tiene programado.
jugador._proximo_evento = evento

print("Actor:", evento.actor.identificador)
print("Tipo:", evento.tipo)
print("Tiempo:", evento.tiempo_siguiente)
print("Válido:", evento.valido)


print("\n=== PRUEBA DE REPROGRAMACIÓN ===")

nuevo_evento = agenda.reprogramar(
    jugador,
    200,
    "accion_actor"
)

print("Tiempo anterior:", evento.tiempo_siguiente)
print("Evento anterior válido:", evento.valido)

print("Tiempo nuevo:", nuevo_evento.tiempo_siguiente)
print("Evento nuevo válido:", nuevo_evento.valido)

print(
    "¿El jugador apunta al evento nuevo?:",
    jugador._proximo_evento is nuevo_evento
)


print("\n=== PRUEBA DE EXTRACCIÓN ===")

evento_extraido = agenda.extraer_siguiente()

print("Actor:", evento_extraido.actor.identificador)
print("Tiempo:", evento_extraido.tiempo_siguiente)
print("Tipo:", evento_extraido.tipo)