# Modelo de datos: Verificación de resolubilidad

**Spec**: [spec.md](spec.md) | **Investigación**: [research.md](research.md)

Los DTO viven en `dto/Verificacion_dto.py` (dataclasses, como los de `Partida_dto.py`). Las
estructuras de trabajo del algoritmo viven dentro del modelo y NO se exponen. Nada de esto contiene
datos de una cripta concreta (principio IV).

## Entradas

### UbicacionLlave (DTO)

Una ubicación publicada por `GET /criptas/<id>/llaves`.

| Campo | Tipo | Regla |
|-------|------|-------|
| `llave` | `str` | Id de la llave, no vacío. Los ids de llave se comparan como cadenas, carácter por carácter (orden lexicográfico: `itm_llave_10` va antes que `itm_llave_2`); los ids de sala se comparan como enteros (spec, supuestos) |
| `sala` | `int` | Id de sala; si no existe en el esqueleto, la ubicación se descarta con advertencia |
| `enemigo` | `str` o `None` | Id de la instancia que suelta la llave; `None` si está en el suelo |

Una llave puede aparecer en varias ubicaciones (aclaración 3). Se ignora el orden de llegada: las
ubicaciones de una llave se guardan ordenadas por id de sala (empate por id de enemigo).

### Esqueleto (reutiliza `SalaModelo` y `SalidaVecina`)

El modelo lee `SalaModelo.id` y, de cada `SalidaVecina`: `direccion`, `sala_id`, `cerrada` y
`llave`. NO usa `cierre_automatico` (FR-005) ni `transitable`.

Reglas de validación:

- Salida con `cerrada = True` y `llave` vacía: dato inválido, el resultado es "no verificable"
  con motivo de datos.
- Salida cuyo `sala_id` no existe en el esqueleto: se ignora y se registra una advertencia.
- Sala duplicada en el esqueleto: la primera gana (igual que `cargar_esqueleto_salas`).
- Cada salida se trata como un arco dirigido con su propia llave (el lado contrario no se infiere).

### Parámetros de la cripta

`sala_inicial`, `sala_salida` y `llave_salida`, tomados de `DetallesCripta`. Si `sala_inicial` no
existe en el esqueleto, el resultado es "no verificable" con motivo de datos.

## Estructuras internas del modelo

Todas son `list` indexadas por entero (principio I).

| Estructura | Índice | Contenido |
|------------|--------|-----------|
| `IndiceLlaves` (`estructuras/Indice_Llaves.py`) | posición = rango por id | Arreglo de ids de llave distintos, ordenado con `ordenar` por comparación de cadenas (lexicográfica); búsqueda binaria propia con la misma comparación, que devuelve el rango o -1 |
| `ColaLista` (`estructuras/Cola_Lista.py`) | posición de la cola | `list` más índice de cabeza; `encolar`, `sacar`, `vacia`; sin `pop(0)` |
| Estado por sala | id de sala | `ronda` (-1 = no alcanzada), `etiqueta` (rango de llave o -1), `puerta_testigo` (índice de salida o -1) |
| Salidas planas | índice de salida | `origen`, `destino`, `llave` (rango o -1), `direccion`; agrupadas por sala con `inicio[sala]` y `fin[sala]`, ordenadas por (destino, dirección) |
| Estado por llave | rango de llave | `obtenida`, `espera` (lista de índices de salida), `ubicaciones` (lista de `UbicacionLlave`), `sala_obtencion` (-1 si no) |
| Orden de obtención | posición | Rangos de llave en el orden en que se obtuvieron |

Invariantes:

1. Una sala se encola como máximo una vez; una salida entra a una espera como máximo una vez; una
   llave se obtiene como máximo una vez.
2. Si `obtenida[k]` entonces `espera[k]` está vacía (se liberó al obtenerla).
3. La ronda de una sala es 1 más que la mínima ronda en la que se obtuvo la llave de la puerta que
   la alcanzó, o la ronda de la sala que la alcanzó por una salida abierta; la sala inicial tiene
   ronda 0.
4. Toda llave del orden aparece después de todas las llaves necesarias para alcanzar su sala.

## Salidas (DTO)

### ResultadoVerificacion

| Campo | Tipo | Regla |
|-------|------|-------|
| `estado` | `"resoluble"`, `"no_resoluble"` o `"no_verificable"` | `no_verificable` no emite veredicto (FR-022) |
| `orden_llaves` | `list[LlaveEnOrden]` | Solo con `resoluble`: todas las obtenibles (FR-007); vacía en los otros casos |
| `reporte` | `ReporteBloqueo` o `None` | Solo con `no_resoluble` |
| `motivo_no_verificable` | `str` | Solo con `no_verificable`: ubicación no disponible o datos inválidos |
| `advertencias` | `list[str]` | Ubicaciones descartadas, salidas a salas inexistentes |
| `cripta_id`, `version` | `str` | Para mostrar y para validar reutilización |
| `estadisticas` | `EstadisticasVerificacion` o `None` | Opcional, por defecto `None`. Lo llena el modelo al explorar; `None` en `no_verificable` (no hubo exploración). No altera el veredicto, el orden ni el reporte |

### EstadisticasVerificacion

Contadores de la exploración, para pruebas de complejidad sin depender del tiempo (FR-024, FR-025).

| Campo | Tipo | Regla |
|-------|------|-------|
| `salas_encoladas` | `int` | Salas encoladas en toda la exploración (fase 1 más fase 2); cada sala cuenta una vez |
| `salidas_examinadas` | `int` | Salidas examinadas; cada salida cuenta una vez |
| `llaves_obtenidas` | `int` | Llaves obtenidas en la fase 1 (las del orden) |

### LlaveEnOrden

`llave` (id), `sala` (donde se obtuvo), `enemigo` (id o `None`), `ronda`.

### ReporteBloqueo

| Campo | Tipo | Regla |
|-------|------|-------|
| `motivo` | `"llave_salida_inobtenible"` o `"puerta_sin_destino"` | La segunda: `llave_salida` obtenida pero ninguna puerta con ella llega a `sala_salida` |
| `llaves_inobtenibles` | `list[LlaveBloqueada]` | Todas las de U, por id (FR-009) |
| `frontera` | `list[PuertaBloqueada]` | Puertas cerradas desde la región alcanzada, por (llave, orden de inserción) (FR-010) |
| `ciclos` | `list[Ciclo]` | Todos los del grafo de testigos, cada uno desde su llave de menor id, ordenados por ese id (FR-012, FR-013) |

### LlaveBloqueada

`llave`, `ubicaciones` (lista de `UbicacionLlave`; TODAS las publicadas, FR-011) y `causa`:
`en_ciclo`, `depende_de` (con la llave de la que depende), `sin_ubicacion` (dato faltante),
`sala_desconectada` o `ubicacion_invalida`.

### PuertaBloqueada

`sala_origen`, `direccion`, `sala_destino`, `llave` requerida.

### Ciclo

Lista de `PasoCiclo`; cada paso: `llave`, `sala` (ubicación usada), `enemigo` (o `None`),
`puerta` (`PuertaBloqueada` testigo que exige la llave siguiente). El paso final apunta a la llave
inicial. Un ciclo de longitud 1 es una llave detrás de la única puerta que ella misma abre.

## Estados y transiciones

Resultado de una verificación:

```text
construir -> explorar fase 1 -> [llave_salida obtenida y puerta a sala_salida recorrida] -> resoluble
                             -> [en otro caso]  -> fase 2 especulativa -> ciclos -> no_resoluble
datos o ubicaciones faltantes (antes de construir) ---------------------------> no_verificable
```

Estado de una partida respecto de la verificación (lo guarda el inicio, no el modelo):

| Estado | Condición | Partida |
|--------|-----------|---------|
| `resoluble` | veredicto positivo | inicia |
| `bloqueada` | `no_resoluble` sin `--forzar` | NO inicia |
| `forzada` | `no_resoluble` con `--forzar` | inicia, reporte disponible |
| `no_verificada` | `no_verificable` | inicia con el aviso, sin veredicto |

## Persistencia

`AlmacenDisco`: `criptas/<id>/llaves.json` con la respuesta cruda `{"llaves": [...]}`. La carpeta
`criptas/<id>/` se reinicia en `validar_cripta` cuando cambia la versión de la cripta, así que la
información de otra versión no se reutiliza (FR-021). El resultado de la verificación NO se
persiste: se recalcula (es de bajo costo) y así nunca queda un veredicto viejo.

## Campos añadidos a DTO existentes

- `ResultadoInicio`: `verificacion: ResultadoVerificacion | None = None`, `aviso: str = ""`. Con
  el valor por defecto, los usos actuales no cambian.
