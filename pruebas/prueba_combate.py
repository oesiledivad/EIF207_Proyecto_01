from cripta.modelo.jugador import Jugador
from cripta.modelo.enemigo import Enemigo
from cripta.controlador.combate import calcular_danio, aplicar_danio


jugador = Jugador(
    "jugador",
    100,
    100,
    20,
    10,
    100,
    "sala1",
    0,
    5
)

enemigo = Enemigo(
    "goblin1",
    50,
    50,
    15,
    5,
    80,
    "sala1",
    0,
    "guardian"
)


print("=== PRUEBA DE COMBATE ===")

dano = calcular_danio(jugador, enemigo)

print("Atacante:", jugador.identificador)
print("Defensor:", enemigo.identificador)
print("Daño calculado:", dano)

aplicar_danio(enemigo, dano)
print("Vida del defensor después del daño:", enemigo.vida)