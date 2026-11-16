# Modelo de datos: Niebla de guerra y viaje automático «ir a»

**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Investigación**: [research.md](research.md)

Las clases y archivos se nombran como están en el plan. Los valores numéricos son constantes del
módulo `Conocimiento`, no datos de una cripta.

## Constantes

| Constante | Valor | Significado |
|-----------|-------|-------------|
| `DESCONOCIDA` | 0 | La sala no es explorada ni avistada |
| `AVISTADA` | 1 | No explorada, y destino de una salida de una sala explorada |
| `EXPLORADA` | 2 | El jugador entró al menos una vez, o la exploró la antorcha |
| `SIN_OBSERVAR` | 0 | La salida nunca se observó |
| `ABIERTA` | 1 | Última observación: puerta abierta |
| `CERRADA` | 2 | Última observación: puerta cerrada |
| `COSTO_DEFECTO` | 100 | Costo de una salida sin costo declarado |
| `DIRECCIONES` | N, S, E, O | Índices 0, 1, 2 y 3 |

## Entidades

### SalidaSimple (existente, se amplía)

Salida dirigida de una sala. Cada salida tiene su propio estado real y su propia memoria.

| Campo | Tipo | Notas |
|-------|------|-------|
| `direccion` | texto | N, S, E u O (existente) |
| `sala_destino` | entero | Id de la sala a la que llega (existente) |
| `cerrada` | booleano | Estado real (existente) |
| `llave` | texto o nada | Llave que la abre (existente) |
| `cierre_automatico` | entero o nada | Existente |
| `costo` | entero | NUEVO. Mayor o igual que 1; 100 si no se declara (D6, C1) |
| `clave` | entero | NUEVO. `origen * 4 + índice de dirección`; la fija `ensamblar_salas` |

Validaciones:

- `costo` menor que 1 o ausente se normaliza a 100 al parsear.
- `clave` es única por salida y `clave // 4` es la sala de origen.

### SalidaVecina (existente, DTO, se amplía)

Se agrega `costo` (entero, 100 por defecto) y `puerta_recordada` (texto: `abierta`, `cerrada` o
`sin_observar`) y `estado_vecina` (texto: `explorada` o `avistada`). `cerrada` y `transitable`
siguen reflejando el estado real de la sala actual, que el jugador observa. Se deja de copiar
`tiene_enemigos` y `tiene_objetos` de las vecinas (D15, C7).

### ConocimientoJugador (nuevo, `modelo/Conocimiento.py`)

Lo que el jugador sabe en un instante. Es parte del estado del juego (FR-015).

| Campo | Tipo | Notas |
|-------|------|-------|
| `estado_sala` | lista de enteros, tamaño `max_id + 1` | 0, 1 o 2 por id (D1) |
| `puerta` | lista de enteros, tamaño `4 * (max_id + 1)` | 0, 1 o 2 por `clave` (D2) |
| `entrantes` | lista de listas de `SalidaSimple`, tamaño `max_id + 1` | Construida una vez (D3). NO es estado del juego: se deriva del esqueleto y no se guarda |
| `registro` | lista de cambios | Anexada con cada cambio, en orden cronológico (D13) |
| `inicializado` | booleano | Falso hasta que `iniciar` construye el conocimiento (bench y pruebas parciales) |

Invariantes:

1. Para todo id, `estado_sala[id]` es exactamente 0, 1 o 2 (FR-001).
2. Toda sala con `estado_sala == 2` fue registrada con sus destinos avistados o explorados: ningún
   destino de una salida de una sala explorada queda en 0 (FR-003).
3. `puerta[clave]` distinta de 0 solo si la sala de origen de la salida o su destino fue visitada
   (entrada del jugador) en algún momento (FR-007, FR-009a). Explorar por antorcha NO la modifica.
4. Una sala nunca vuelve a un estado menor al revertir hacia adelante; solo un retroceso del
   historial puede devolverla al estado anterior (FR-016).
5. `len(registro)` crece solo con cambios reales; una asignación del mismo valor no registra nada.
6. En el instante 0 solo la sala inicial está explorada, sus destinos avistados y sus puertas
   observadas (spec, caso límite «conocimiento en el instante 0»).

Operaciones (contrato interno, sin código):

| Operación | Efecto | Costo |
|-----------|--------|-------|
| `iniciar(salas, entrantes, sala_inicial)` | Crea las listas en 0, explora la sala inicial y observa sus puertas, sin historial | O(S) una vez |
| `estado(sala)` | Devuelve 0, 1 o 2; un id fuera de rango devuelve 0 | O(1) |
| `memoria_puerta(clave)` | Devuelve 0, 1 o 2 | O(1) |
| `explorar(sala, historial, tiempo)` | Marca explorada y avista los destinos aún desconocidos de sus salidas | O(4) |
| `entrar(sala, antorcha, historial, tiempo)` | `explorar(sala)` y, si la antorcha estaba encendida, `explorar` de cada destino de sus salidas, abiertas o cerradas | O(4) o O(16) |
| `observar(sala, historial, tiempo)` | Asigna el estado real a las 4 salidas de la sala y a sus entrantes | O(4 + entrantes) |
| `instantanea()` / `restaurar(...)` | Ver contrato serializable | O(S) |
| `reconstruir(instantanea_base, registro, n)` | Estado tras los primeros `n` cambios | O(S + n) |

### CambioConocimiento (registro)

Elemento del registro: lista de cuatro enteros `[tiempo, tipo, indice, valor]`.

| Campo | Valores |
|-------|---------|
| `tiempo` | Reloj virtual al registrar |
| `tipo` | 0 estado de sala, 1 memoria de puerta |
| `indice` | Id de sala (tipo 0) o clave de salida (tipo 1) |
| `valor` | Valor nuevo (0, 1 o 2) |

### EstadoSalaVisible (derivado, no se almacena)

Lo que la vista puede leer de una sala según su estado:

| Estado | Visible |
|--------|---------|
| Desconocida | Nada |
| Avistada | Solo el id (existe) |
| Explorada | Nombre, salidas, costo de cada salida y puerta recordada |

### Entrante (relación)

Para cada sala `v`, las `SalidaSimple` con `sala_destino == v`. Se usa para observar (el jugador en
`v` observa las salidas que llegan) y para relajar aristas en el Dijkstra inverso.

### MonticuloMinimo (nuevo, `estructuras/Monticulo_Minimo.py`)

Cola de prioridad genérica. Tres listas paralelas: prioridad, desempate y elemento.

| Regla | Detalle |
|-------|---------|
| Orden | Menor `(prioridad, desempate)` primero; ambos enteros |
| Eliminación | Perezosa: el llamador descarta entradas obsoletas al extraer |
| Vacío | `extraer_minimo` sobre un montículo vacío es un error del llamador; se consulta `esta_vacio` |
| Reutilización | `vaciar` deja las listas listas para otra búsqueda sin reasignar memoria |

### BuscadorRutas (nuevo, `modelo/Rutas.py`)

Reutilizable por «ir a» y, en la spec 003, por el cazador.

| Campo | Tipo | Notas |
|-------|------|-------|
| `distancia` | lista de enteros, tamaño S | Válida solo donde `marca == generacion` |
| `marca` | lista de enteros, tamaño S | Generación que escribió la distancia |
| `generacion` | entero | Se incrementa por búsqueda; evita reinicializar S posiciones |
| `monticulo` | `MonticuloMinimo` | Reutilizado entre búsquedas |

| Operación | Resultado |
|-----------|-----------|
| `distancias_hacia(destino, entrantes, usable, parar_en)` | Llena `distancia` desde el destino; se detiene al fijar `parar_en` (puede ser nada) |
| `elegir_paso(origen, salidas, usable)` | La `SalidaSimple` de menor `costo + distancia[destino]`; empate por menor id de sala destino y luego índice de dirección; nada si no hay camino |

### Viaje (nuevo, `controlador/ViajeControlador.py`, NO es estado del juego)

| Campo | Tipo | Notas |
|-------|------|-------|
| `destino` | entero | Sala explorada indicada por el jugador |
| `activo` | booleano | Verdadero entre `iniciar` y la detención |
| `pasos` | entero | Pasos dados; también corta el viaje al llegar a tantos como salas exploradas (C1) |
| `en_paso` | booleano | Verdadero mientras `avanzar` llama a `mover`; evita que `_accion_jugador` lo cancele |
| `motivo` | texto o nada | Último motivo de detención |

Transiciones:

```text
inactivo --iniciar (orden aceptada)--> activo
activo --avanzar sin detención--> activo
activo --avanzar con motivo--> inactivo (motivo mostrado)
activo --otra acción del jugador o pergamino--> inactivo (motivo cancelado)
inactivo --iniciar con orden rechazada--> inactivo (sin tiempo, sin comentario)
```

### MotivoDetencion

| Código | Cuándo | Consume tiempo adicional |
|--------|--------|--------------------------|
| `llegada` | El jugador está en el destino | No |
| `enemigos` | Entró a una sala con al menos un enemigo vivo, activo o dormido | No |
| `danio` | La vida bajó durante el paso (ataque, trampa o veneno) | No |
| `sin_ruta` | Tras recalcular no hay ruta conocida | No |
| `movimiento_rechazado` | `mover` devolvió fallo (por ejemplo capacidad de fichas) | No |
| `partida_terminada` | Victoria o derrota durante el paso | No |
| `cancelado` | Otra acción del jugador o el pergamino interrumpió el viaje | No |

Prioridad cuando coinciden en un paso: `partida_terminada`, `danio`, `enemigos`, `llegada` (C3).

### MapaConocido (DTO nuevo, `dto/Conocimiento_dto.py`)

Resultado del comando `mapa`. Se arma recorriendo los ids en orden ascendente (sin ordenar).

| Campo | Tipo |
|-------|------|
| `exploradas` | lista de `SalaConocida` |
| `avistadas` | lista de ids |

`SalaConocida`: `id`, `nombre`, `salidas` (lista de `SalidaConocida`).

`SalidaConocida`: `direccion`, `destino` (id), `costo`, `puerta` (`abierta`, `cerrada` o
`sin_observar`), `destino_estado` (`explorada` o `avistada`).

Validaciones: ninguna sala desconocida aparece; de una avistada solo se conoce el id.

### ResultadoViaje (DTO nuevo)

| Campo | Tipo |
|-------|------|
| `ok` | booleano: orden aceptada o paso dado |
| `activo` | booleano: el viaje continúa |
| `motivo` | texto (código) o vacío |
| `mensaje` | texto para la bitácora |

## Relaciones

```text
Cripta (esqueleto) 1 --- * SalaJuego 1 --- 0..4 SalidaSimple
SalidaSimple * --- 1 SalaJuego (destino)   -> forma `entrantes` por sala
ConocimientoJugador 1 --- 1 Partida (estado del juego, reversible)
ConocimientoJugador 1 --- * CambioConocimiento (registro cronológico)
ViajeControlador 0..1 --- 1 Partida (efímero, no guardado)
```

## Reversibilidad

Todo cambio de `estado_sala` y `puerta` pasa por `historial.asignar`, y cada cambio se anexa al
`registro` con `historial.agregar`. Por tanto, dentro de un intervalo, el pergamino revierte
estado, memoria y registro en orden inverso (FR-016). Lo hecho en `iniciar` ocurre sin intervalo
abierto y no se revierte nunca (es la base en el instante 0).
