# Contrato: comandos `ir a` y `mapa`, y motivos de detención

**Spec**: [../spec.md](../spec.md) | **Modelo**: [../data-model.md](../data-model.md)

Este contrato fija lo que la interfaz y las pruebas pueden esperar. NO fija el diseño visual.

## Comando `ir a <sala>`

Entrada: un id de sala entero.

La interfaz expone `Aplicacion.ir_a(sala_id)`. Si la orden se acepta, el viaje queda activo y
cada llamada a `Aplicacion.avanzar_viaje()` da exactamente un paso. `Aplicacion.cancelar_viaje()`
lo interrumpe. `Aplicacion.ir_a_completo(sala_id)` repite los pasos hasta detenerse y es la forma
para pruebas y consola.

### Rechazos (sin consumir tiempo y sin escribir en `partida.log`)

| Condición | Mensaje en la bitácora | FR |
|-----------|------------------------|----|
| Partida no activa | La partida no está activa. | FR-019 |
| Id no entero o fuera del rango de salas | La sala indicada no existe. | FR-020 |
| Sala avistada o desconocida | Solo puedes ir a una sala que ya exploraste. | FR-020 |
| Sala actual | Ya estás en esa sala. | FR-021 |
| Sin ruta conocida (incluye puerta recordada cerrada o sin observar) | No hay ruta conocida hacia esa sala. | FR-022, FR-030 |

No se distingue en el mensaje entre «desconocida» y «avistada», para no revelar que una sala
desconocida existe.

### Aceptación

Si la orden se acepta: se escribe el comentario de [registro-partida.md](registro-partida.md) y el
viaje queda activo. La orden en sí NO consume tiempo; cada paso sí.

### Un paso

Antes de cada paso se recalcula la ruta con el conocimiento vigente (FR-026). El paso es una llamada
a `mover(direccion)`:

- Consume el tiempo de la acción y corre los eventos del reloj (FR-025).
- Queda en `partida.log` como `["mover", "<dirección>"]` (FR-033).
- Lo revierte el pergamino como cualquier movimiento (FR-034).
- Nunca abre una puerta, aunque el jugador tenga la llave (FR-032).

### Reglas de la ruta

- Solo salas exploradas y solo salidas con puerta recordada abierta (FR-022).
- Minimiza la suma de costos; una salida sin costo declarado vale 100 (FR-023).
- Empate: primer paso hacia la sala vecina de menor id; si hay dos salidas hacia la misma sala,
  la de menor costo y luego el orden N, S, E, O (FR-024).

## Motivos de detención

Cada detención escribe en la bitácora un mensaje de categoría `viaje` con el motivo (FR-031).

| Código | Texto en la bitácora | FR |
|--------|----------------------|----|
| `llegada` | Viaje detenido: llegaste a la sala {id}. | FR-027 |
| `enemigos` | Viaje detenido: hay enemigos en la sala {id}. | FR-028 |
| `danio` | Viaje detenido: recibiste daño. | FR-029 |
| `sin_ruta` | Viaje detenido: ya no existe una ruta conocida. | FR-030 |
| `movimiento_rechazado` | Viaje detenido: no se pudo avanzar ({motivo}). | FR-031a |
| `partida_terminada` | Viaje detenido: la partida terminó. | FR-031a |
| `cancelado` | Viaje cancelado. | FR-034 |

Reglas:

- `sin_ruta` NO consume tiempo adicional: se detecta al recalcular, antes de mover (FR-030).
- `enemigos` cuenta enemigos vivos, activos o dormidos; los derrotados no cuentan (FR-028). La
  comprobación se hace en el instante de la entrada, después de activar a los dormidos según la
  Parte I (C5).
- `danio` se detecta si la vida del jugador es menor al final del paso que al inicio, lo que cubre
  ataque, trampa y veneno (C4).
- Si coinciden varios en un paso, se muestra uno solo por esta prioridad: `partida_terminada`,
  `danio`, `enemigos`, `llegada` (FR-031a, C3).
- Todo viaje detenido muestra exactamente un motivo (SC-007).

Los códigos `movimiento_rechazado` y `partida_terminada` los exige FR-031a (C2 resuelto). El código
`cancelado` es una adición del plan: lo produce el pergamino u otra acción del jugador (FR-034).

## Comando `mapa`

La interfaz expone `Aplicacion.mapa_conocido()`, que devuelve un `MapaConocido` (ver
[../data-model.md](../data-model.md)). No consume tiempo ni escribe en `partida.log` (FR-018).

Contenido:

- Para cada sala explorada: id, nombre y, por cada salida, dirección, id de destino, costo y puerta
  recordada (`abierta`, `cerrada` o `sin_observar`).
- Para cada sala avistada: solo su id.
- Ninguna sala desconocida (FR-006, SC-002).

Las salas se listan por id ascendente, de modo que la salida es determinista (SC-005).

## Minimapa

El minimapa muestra la sala actual y sus vecinas. Para cada vecina indica si está explorada o
avistada; para cada salida, el costo y la puerta recordada. No dibuja salas desconocidas, no muestra
contenido de las vecinas y solo marca la sala de salida si está explorada (C7).
