from cripta.util.reloj import Reloj


reloj = Reloj()

print("=== PRUEBA DEL RELOJ ===")

print("Tiempo inicial:", reloj.tiempo_actual)

reloj.avanzar_hasta(100)
print("Después de avanzar a 100:", reloj.tiempo_actual)

reloj.avanzar_hasta(250)
print("Después de avanzar a 250:", reloj.tiempo_actual)

try:
    reloj.avanzar_hasta(150)
except ValueError as error:
    print("Error esperado:", error)