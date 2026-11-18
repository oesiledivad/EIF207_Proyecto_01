# Contrato: decisión de turno de un enemigo y costo del movimiento

Interfaz interna entre los comportamientos de enemigo (`modelo/enemigos/`) y `Simulacion`.
Atiende FR-003, FR-004, FR-005 y FR-010 a FR-019.

## Firma

```text
Enemigo.decidir_accion(sala_jugador, salas, tiempo_actual, azar, persecucion) -> [tipo, destino, costo]
```

- `persecucion` es la `Persecucion` de la simulación. Solo el cazador la usa; los demás la ignoran.
- `tipo` es `atacar`, `esperar` o `mover`.
- Para `mover`, `destino` es el id de sala y `costo` el de la salida usada (entero ≥ 1).
- Para `atacar` y `esperar`, `destino` y `costo` son nada.

## Uso en `Simulacion`

```text
costo_efectivo = costo si tipo == "mover" else costo_accion(tipo)
intervalo = max(1, costo_efectivo * 100 // enemigo.velocidad)
siguiente turno = tiempo_actual + intervalo
```

## Garantías por comportamiento

| Comportamiento | Garantía |
|----------------|----------|
| guardián | Igual que hoy |
| errante | Elige con `azar.choice` sobre las salidas abiertas en el mismo orden y cantidad que hoy; mismo consumo del azar |
| rastreador | Misma elección que hoy; el costo es el de la salida candidata elegida |
| cazador | Atacar si comparte sala; esperar si no hay ruta abierta o d > rango; si no, la salida que minimiza `costo + dist`, desempate por menor id de destino y luego N, S, E, O |

## Jugador

```text
ExploracionControlador.mover -> Aplicacion._accion_jugador("mover", ..., costo=salida.costo)
  -> CicloAccionesControlador.ejecutar(..., costo) -> consumir_tiempo("mover", costo)
```

Toda otra acción del jugador pasa `costo` nada y conserva `costo_accion(nombre)` (FR-005).

## Errores

- Un `decidir_accion` que devuelve `mover` sin costo es un error de programación (`ValueError`).
