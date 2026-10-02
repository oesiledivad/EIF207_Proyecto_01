# pruebas basico de unicamente el modelo

from cripta.modelo.Enemigo import Enemigo


enemigo = Enemigo(
    "goblin1",
    50,          # vida
    50,          # vida máxima
    15,          # ataque
    5,           # defensa
    80,          # velocidad
    "sala2",     # sala
    0,           # tiempo siguiente
    "guardian"   # comportamiento
)

print("=== PRUEBA DE ENEMIGO ===")

print("Identificador:", enemigo.identificador)
print("Vida:", enemigo.vida)
print("Vida máxima:", enemigo.vida_max)
print("Ataque:", enemigo.ataque)
print("Defensa:", enemigo.defensa)
print("Velocidad:", enemigo.velocidad)
print("Sala:", enemigo.sala)
print("Tiempo siguiente:", enemigo.tiempo_siguiente)
print("Comportamiento:", enemigo.comportamiento)