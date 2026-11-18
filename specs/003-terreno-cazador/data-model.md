# Modelo de datos: Terreno con costo y enemigo cazador

**Spec**: [spec.md](spec.md) | **Investigación**: [research.md](research.md)

## Constantes

| Nombre | Valor | Origen |
|--------|-------|--------|
| Costo por defecto de una salida | 100 | FR-001 (ya en `SalidaSimple.costo` y `FactoryDto_Partida`) |
| Costo de esperar del cazador | 100 (`COSTO_ESPERAR`) | FR-012 |
| Fórmula del intervalo | `max(1, costo * 100 // velocidad)` (`calcular_intervalo`) | FR-004 |
| Fórmula de reescalado | `max(1, restante * v_anterior // v_nueva)` (`reescalar_tiempo_siguiente`) | FR-006 |

## Entidades

### SalidaSimple (existente, sin cambios de campos)

| Campo | Tipo | Regla |
|-------|------|-------|
| `costo` | `int` | ≥ 1; 100 si no se declara o si se declara menor que 1 (FR-001, FR-002) |
| `cerrada` | `bool` | Estado real; el cazador solo usa salidas con `cerrada == False` (FR-011) |
| `clave` | `int` | `origen * 4 + dirección`; el origen es `clave // 4` |

Cada sentido de una conexión es una `SalidaSimple` distinta; ambas llevan el mismo costo porque el
esqueleto lo declara por conexión (FR-001).

### FichaEnemigo (existente, se amplía)

| Campo | Tipo | Regla |
|-------|------|-------|
| `comportamiento` | `str` | `guardián`, `errante`, `rastreador` o `cazador` (FR-008) |
| `rango` | `int \| None` | Obligatorio y entero ≥ 0 si `comportamiento == "cazador"`; si no, `ValueError` con el id (FR-009); ignorado en los demás |

### EnemigoPartida (DTO existente, se amplía)

| Campo | Tipo | Regla |
|-------|------|-------|
| `rango` | `int \| None` | Copia de la ficha; nada si no es cazador |
| `comportamiento` | `str` | Ya existe; la vista lo usa para distinguir al cazador (FR-021) |

### Cazador (nuevo, `modelo/enemigos/Cazador.py`, subclase de `Enemigo`)

| Campo | Tipo | Regla |
|-------|------|-------|
| `rango` | `int` | ≥ 0, en unidades de costo (FR-008) |
| heredados | | vida, ataque, defensa, velocidad, sala, siguiente turno (Parte I) |

Estados (Parte I §2.4, sin cambios): **dormido** (sin evento en la agenda) → **activo** al entrar el
jugador a su sala, con primera acción de costo 100 desde la activación (FR-019) → **muerto**.

Decisión por turno (activo): `atacar` si comparte sala; si no, `esperar` (costo 100) si no hay ruta
o d > rango; si no, `mover` a la salida de `elegir_paso`, con su costo (FR-010 a FR-014).

### Decisión de enemigo (contrato interno, se amplía)

`decidir_accion(...)` devuelve `[tipo, destino, costo]`:

| `tipo` | `destino` | `costo` |
|--------|-----------|---------|
| `atacar` | nada | nada (se usa `costo_accion("atacar")`) |
| `esperar` | nada | nada (se usa `costo_accion("esperar")`) |
| `mover` | id de sala | costo de la salida elegida (FR-003) |

Detalle en [contracts/decision-enemigo.md](contracts/decision-enemigo.md).

### Persecucion (nueva, `modelo/Persecucion.py`, propiedad de `Simulacion`; NO es estado del juego)

| Campo | Tipo | Significado |
|-------|------|-------------|
| `buscador` | `BuscadorRutas` | Reutilizado de la spec 002; se crea con el tamaño de `entrantes` |
| `entrantes` | `list[list[SalidaSimple]]` | Referencia a `ExploracionControlador.entrantes` |
| `rango_maximo` | `int` | Mayor rango registrado; solo crece (D7) |
| `valida` | `bool` | Hay distancias calculadas |
| `clave_sala` | `int` | Sala del jugador del último cálculo |
| `clave_puertas` | `int` | `agenda.cambios_puertas` del último cálculo |
| `clave_reversiones` | `int` | `historial.reversiones` del último cálculo (0 sin historial) |
| `limite_usado` | `int` | Límite con el que se cortó la búsqueda |

Operaciones: `configurar(entrantes)`, `registrar_rango(r)`, `distancias(sala_jugador, agenda,
historial, rango)` (recalcula si la clave no coincide o `limite_usado < rango`), `paso(sala,
salidas, rango)` (devuelve la salida o nada). Se crea vacía con cada `Simulacion`; por eso cargar
una partida la invalida.

### BuscadorRutas (existente, se amplía)

| Cambio | Regla |
|--------|-------|
| `distancias_hacia(..., limite: int \| None = None)` | Termina al extraer una entrada vigente con prioridad > `limite`; con nada, idéntico al actual («ir a» no cambia) |

### HeapAgendaEventos (existente, se amplía)

| Campo | Tipo | Regla |
|-------|------|-------|
| `cambios_puertas` | `int` | Monótono; lo suben `abrir_salida` y `procesar_cierre_puerta`; no pasa por el historial |

### Historial_Retroceso (existente, se amplía)

| Campo | Tipo | Regla |
|-------|------|-------|
| `reversiones` | `int` | Monótono; lo suben `revertir_abierto` y `deshacer` |

### Guardado del enemigo (existente, se amplía)

Tras `regeneracion_objetivo`, si `comportamiento == "cazador"`: `entero(rango)`. Los demás
enemigos no cambian, así que los guardados sin cazadores conservan su formato y `VERSION_CUERPO`.

## Relaciones

- `Simulacion` 1 → 1 `Persecucion` → 1 `BuscadorRutas` → 1 `MonticuloMinimo`.
- `Cazador` * → 1 `Persecucion` (la consulta desde `decidir_accion`).
- `Persecucion` → `entrantes` (esqueleto completo, FR-015), nunca el conocimiento del jugador.

## Reversibilidad

- Movimientos y turnos de enemigos: ya reversibles (agenda e historial).
- `cambios_puertas`, `reversiones`, `rango_maximo` y las distancias NO se revierten a propósito: son
  monótonos o derivados, y la clave de D8 detecta cualquier reversión.
