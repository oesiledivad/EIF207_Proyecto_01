# Contrato: salida de `--bench` para terreno y cazador

Atiende FR-025 a FR-027, SC-004 y SC-007. `--bench` no abre la vista ni usa red o disco, salvo para
leer el esqueleto mayor de `datos_offline`.

## Encabezado

```text
=== Terreno y cazador (spec 003), semilla <n> ===
```

## Líneas por medición

Cada medición imprime una línea por caso con este orden de campos:

```text
H<n> <caso>: <campo>=<valor> ... [CUMPLE|EXCEDE|INFORMATIVA]
```

| Id | Campos mínimos |
|----|----------------|
| H1 | `cazadores`, `rango`, `compartida_ms`, `individual_ms`, `razon` |
| H2 | `salas`, `con_corte_fijadas`, `con_corte_ms`, `sin_corte_fijadas`, `sin_corte_ms` |
| H3 | `puertas` (estables o inestables), `clave_ms`, `por_turno_ms`, `por_ciclo_ms`, `recalculos` |
| H4 | `turnos`, `coinciden` (debe ser igual a `turnos`) |
| H5 | `cazadores`, `media_ms`, `maximo_ms`, `limite=20ms` y CUMPLE o EXCEDE según el máximo |
| H6 | `eventos`, `heap_ms`, `lista_ms` |
| H7 | `predicado_ms`, `banderas_ms` |
| H8 | `identico=si` o `identico=no` |

## Determinismo

Dos ejecuciones con la misma semilla imprimen las mismas decisiones, conteos y estados de CUMPLE;
solo cambian los tiempos.
