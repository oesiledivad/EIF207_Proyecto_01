# Contrato: ficha de enemigo cazador y salida con costo (datos de la cripta)

Lo que el programa acepta del servicio web o de `datos_offline`. Atiende FR-001, FR-002, FR-008 y FR-009.

## Ficha de enemigo

```json
{
  "id": "ejemplo-cazador",
  "nombre": "Acechador",
  "clase": "enemigo",
  "vida_max": 20,
  "ataque": 5,
  "defensa": 1,
  "velocidad": 120,
  "comportamiento": "cazador",
  "rango": 400,
  "suelta": null
}
```

| Campo | Regla |
|-------|-------|
| `comportamiento` | Se agrega `cazador` a `guardián`, `errante`, `rastreador` |
| `rango` | Obligatorio con `cazador`: entero ≥ 0 (no booleano). Ausente, negativo o no entero → `ValueError` con el id de la ficha |
| `rango` en otros comportamientos | Se acepta y se ignora |

Ningún id del ejemplo aparece en el código (principio IV); las pruebas arman sus fichas.

## Salida con costo (esqueleto, ya implementado en la spec 002)

| Campo | Regla |
|-------|-------|
| `costo` | Entero ≥ 1. Ausente → 100. Menor que 1 → 100 con aviso en la bitácora |

## Guardado

Tras los campos actuales del enemigo, solo si `comportamiento == "cazador"`: `entero(rango)`.
