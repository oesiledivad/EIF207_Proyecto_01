# Guía de validación: Línea de tiempo y puntos de control

**Spec**: [spec.md](spec.md) | **Tareas**: [tasks.md](tasks.md)

Todos los comandos se ejecutan desde la raíz del repositorio en CMD.

## 0. Prerrequisitos

```bat
uv sync
uv run python -m unittest discover -s pruebas -t .
```

## 1. Pruebas por historia

```bat
uv run python -m unittest pruebas.test_linea_tiempo pruebas.test_historia pruebas.test_historia_retroceso pruebas.test_historia_replay pruebas.test_historia_guardado pruebas.test_bench_linea
```

| Apéndice B | Prueba |
|------------|--------|
| 1. t mayor que el reloj | `test_historia.TestConsulta.test_rechaza_t_futuro` (FR-004) |
| 2. historia tras pergamino | `test_historia_retroceso` (FR-010) |
| 3. varios eventos en t | `test_historia.TestConsulta.test_eventos_mismo_instante` (FR-001) |
| 4. sin efectos | `test_historia.TestConsulta.test_consulta_sin_efectos` (FR-007) |
| 5. replay más allá del final | `test_historia_replay.TestReplayHasta.test_mas_alla_del_final` (FR-022) |
| 6. archivo de la Parte I | `test_historia_guardado.TestGuardadoLinea.test_rechaza_parte_uno` (FR-026) |

## 2. Interfaz

1. `uv run python -m cripta --offline --cripta cripta-03 --semilla 7`.
2. Jugar unas acciones, pulsar H, escribir `0` y Enter: estado inicial.
3. Pulsar H, escribir `#3` y Enter: estado antes de la tercera acción.
4. Pulsar H con un instante mayor que el reloj: mensaje de rechazo.

## 3. Consola

```bat
uv run python -m cripta --offline --replay partidas\<archivo>.log --hasta 500
uv run python -m cripta --offline --replay partidas\<archivo>.log --hasta 999999
uv run python -m cripta --offline --checkpoint-cada 0
```

## 4. Rendimiento

```bat
uv run python -m cripta --bench --semilla 42
```

Revisar L1 (consulta ≤ 50 ms con K por defecto), L2 a L5.
