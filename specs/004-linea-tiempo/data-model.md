# Modelo de datos: Línea de tiempo y puntos de control

**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

## Constantes

| Nombre | Valor | Uso |
|--------|-------|-----|
| `K_POR_DEFECTO` | fijado con L1 | `--checkpoint-cada` ausente (FR-018) |
| `VERSION_CUERPO` | 3 | guardado de la Parte II (FR-026) |
| `ID_LINEA` | `0xFFFFFFFE` | cuerpo con conocimiento y línea |
| Ranuras fijas | 0 sala, 1 vida, 2 vida máxima, 3 ataque, 4 defensa, 5 velocidad, 6 resultado, 7 inventario, 8 efectos | |
| Conocimiento | desde 9: n estados de sala y 4n memorias de salida | spec 002 |

## Entidades

### LineaTiempo (nueva, `estructuras/Linea_Tiempo.py`)

| Campo | Tipo | Significado |
|-------|------|-------------|
| `k` | int ≥ 1 | acciones entre puntos de control |
| `_vivo` | list | vector de ranuras vigente |
| `_base` | list | valor de cada ranura antes de su primer cambio |
| `_t`, `_ranura`, `_antes`, `_despues` | list | bitácora de cambios |
| `_marca_t`, `_marca_pos`, `_marca_extra` | list | marcas por acción (instante, posición, dato del llamador) |
| `_cp_pos`, `_cp_estado` | list | puntos de control |

Operaciones: `nueva_ranura(valor)`, `registrar(t, ranura, valor)`, `marcar(t, extra)`,
`recortar(m)`, `acciones()`, `ubicar_tiempo(t)`, `ubicar_accion(k)`, `estado_en(pos, modo)`,
`con_k(k)`, `memoria()`, `a_datos()` / `desde_datos()`.

Invariantes: `_t` no decrece; `_marca_t` crece estrictamente; `_marca_pos` no decrece; el punto de
control i (i ≥ 1) está en la marca i·K; aplicar `_despues[0:n]` sobre el punto de control 0 da el
estado en n.

### LineaTiempoControlador (nuevo, `controlador/LineaTiempoControlador.py`)

Traduce la partida a ranuras: `iniciar()`, `conectar(sim)`, `antes_de_accion()`, `capturar()`,
`cancelar_accion()`, `tras_pergamino()`, `historia(texto)`, `resumen_en_tiempo(t)`,
`a_datos()` / `restaurar(datos)`. Tabla de enemigos: listas paralelas `_enemigos`, `_ids`,
`_nombres`; el índice del enemigo se guarda en el atributo `_linea_indice` del objeto.

### ResumenInstante (DTO nuevo, `dto/Historia_dto.py`)

`reloj`, `accion` (número de la próxima acción), `sala_id`, `sala_nombre`, `vida`, `vida_max`,
`ataque`, `defensa`, `velocidad`, `resultado`, `inventario`, `efectos`, `enemigos`
(`[id, nombre, vida, vida_max]`), `mapa` (`MapaConocido`), `aviso`.

### ResultadoHistoria (DTO nuevo)

`ok`, `motivo`, `resumen`.

## Relaciones

- `Aplicacion` posee un `LineaTiempoControlador`; este posee la `LineaTiempo`.
- `Historial_Retroceso.observador` y `Simulacion.al_terminar_evento` apuntan al controlador.
- El guardado escribe `a_datos()` del controlador y la instantánea del conocimiento.

## Reversibilidad

La línea no se registra en el historial de retroceso: el pergamino la recorta explícitamente (D8).
Las consultas solo leen.
