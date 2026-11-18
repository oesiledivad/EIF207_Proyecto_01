# Guía de validación: Terreno con costo y enemigo cazador

**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

Comandos para CMD de Windows, desde la raíz del repositorio. No incluye código de implementación;
los detalles están en [data-model.md](data-model.md) y en [contracts/](contracts/).

## 0. Prerrequisitos y línea base

1. `spec.md` de esta capacidad confirmada en Git antes del primer commit de código (principio VII).
2. Antes de tocar código, correr la suite completa y guardar el resultado en
   `specs\003-terreno-cazador\linea_base.txt` (pruebas que ya fallan, si las hay).
3. Grabar con la versión actual una partida corta con errantes y rastreadores en una cripta de
   `datos_offline` (sin costos declarados) para la prueba de regresión de determinismo (D2).

## 1. Pruebas por historia

```bat
uv run python -m unittest discover -s pruebas -p "test_costo_movimiento.py"
uv run python -m unittest discover -s pruebas -p "test_cazador.py"
uv run python -m unittest discover -s pruebas -p "test_cazador_puertas.py"
uv run python -m unittest discover -s pruebas -p "test_ficha_cazador.py"
uv run python -m unittest discover -s pruebas -p "test_cazador_guardado.py"
uv run python -m unittest discover -s pruebas -p "test_bench_cazador.py"
uv run python -m unittest discover -s pruebas -p "test_rutas.py"
uv run python -m unittest discover -s pruebas -p "test_ir_a.py"
```

Esperado: todas pasan; las dos últimas son de la spec 002 y comprueban que el parámetro `limite`
no cambia «ir a». Cada prueba cita su FR.

Cobertura obligatoria del Apéndice B (SC-001):

| Caso | Escenario de la spec | Prueba |
|------|----------------------|--------|
| 1 Sin ruta abierta: espera con costo 100 | US2-1 | `test_cazador.py` |
| 2 Ruta más barata mayor que el rango: espera con costo 100 | US2-2 | `test_cazador.py` |
| 3 Menos salas y más costo frente a más salas y menos costo | US2-3 | `test_cazador.py` |
| 4 Dos vecinas empatadas: menor id | US2-4 | `test_cazador.py` |
| 5 Puerta que se cierra entre dos turnos: igual que desde cero | US2-5 | `test_cazador_puertas.py` |
| 6 Velocidad alta y costo 1: intervalo al menos 1 | US1-3 | `test_costo_movimiento.py` |
| 7 Cambio de velocidad con movimiento costoso pendiente | US1-4 | `test_costo_movimiento.py` |

## 2. Escenarios con la interfaz

Requieren una cripta de prueba local con costos declarados y un cazador (no se agrega a
`datos_offline`; se arma en la carpeta de pruebas).

1. Entrar a una sala con salidas de costo 1, sin costo y 250: cada puerta muestra su costo y la sin
   costo muestra 100 (US4-1).
2. Sala con un cazador y un errante: el cazador tiene marca propia y su texto emergente dice
   «cazador» y su rango (US4-2).
3. Matar al cazador: se ve como cualquier enemigo derrotado (US4-3).
4. Moverse por la salida de costo 250 con velocidad 100: el reloj avanza 250 (US1-2).
5. Dejar que el cazador persiga: entra a la sala del jugador y ataca en su turno siguiente.

## 3. Registro, guardado y retroceso

```bat
uv run python -m cripta --replay partidas\<registro con cazadores>
```

- El estado final coincide con el de la partida original (US5-1, FR-022).
- La partida grabada en el paso 0.3 se reproduce con el mismo estado final (D2).
- Guardar a mitad de una persecución, cargar y comprobar que el cazador conserva rango y siguiente
  turno y que decide igual (US5-2, FR-023).
- Usar el pergamino tras un movimiento costoso: reloj, posiciones y acciones de cazadores vuelven
  (US5-3, FR-024).

## 4. Rendimiento

```bat
uv run python -m cripta --bench --semilla 42
uv run python -m cripta --bench --semilla 42
```

Esperado ([contracts/bench-cazador.md](contracts/bench-cazador.md)):

- Aparecen H1 a H8 sin ventana (FR-027, SC-007).
- H5: máximo del ciclo entre dos decisiones del jugador con 50 cazadores en la cripta de
  referencia menor que 20 ms (FR-025, SC-004).
- H4: todas las decisiones coinciden con el cálculo desde cero (FR-017, SC-003).
- H2: con corte, de 2 000 a 20 000 salas el tiempo crece menos de 1,5 veces.
- H8: las dos corridas dan resultados idénticos; solo varían los tiempos (SC-005).
- Las alternativas de H1, H3, H6 y H7 se reportan con su razón frente a la elegida (principio VI).

Guardar la salida en `specs\003-terreno-cazador\mediciones.txt`.

## 5. Verificación final

```bat
uv run python -m unittest discover -s pruebas
```

- Sin fallas nuevas respecto de `linea_base.txt`; anotar en `specs\003-terreno-cazador\regresion.txt`.
- Ningún `heapq`, `bisect`, `collections`, `sorted(` ni `.sort(` en archivos nuevos o modificados, y
  ningún `dict` ni `set` como índice (principio I).
- Ningún id de sala, enemigo o cripta escrito en el código (principio IV).
- Cada tarea cita sus FR y cada prompt quedó en `docs/PROMPTS_LLM.md`.

## Resultado de la validación

Validado en un entorno de trabajo con Python 3.10 (sin interfaz) el 16/11/2026.

- Sección 0: spec confirmada en Git antes del código. La línea base está en `linea_base.txt` (T003, T004). La partida de regresión de determinismo (D2) no se grabó con la versión anterior: la cubre `test_decision_enemigo.py`, que comprueba que errante y rastreador eligen igual que antes y no tocan el azar.
- Sección 1: todas las pruebas por historia pasan; los siete casos del Apéndice B tienen su prueba con el FR en el docstring.
- Sección 2 (interfaz): las tres pruebas de `test_grafica.py` (US4) pasan con arcade simulado; **pendiente** abrir el juego una vez, con una cripta con costos y un cazador, y mirar las puertas y el contorno morado del cazador.
- Sección 3: replay, guardar y cargar a mitad de una persecución y pergamino tras un movimiento costoso pasan en `test_cazador_guardado.py`.
- Sección 4: la sección «Terreno y cazador» del bench se corrió dos veces con la semilla 42 y dio las mismas decisiones y conteos (`mediciones.txt`); H5 CUMPLE con 10, 50 y 100 cazadores. **Pendiente** correr `--bench` completo en el equipo de la entrega.

