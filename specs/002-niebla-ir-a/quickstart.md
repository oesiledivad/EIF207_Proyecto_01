# Guía de validación: Niebla de guerra y viaje automático «ir a»

**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

Comandos para CMD de Windows, desde la raíz del repositorio. No incluye código de implementación;
los detalles están en [data-model.md](data-model.md) y en [contracts/](contracts/).

## 0. Prerrequisitos y línea base

1. Rama limpia (`git status` sin cambios) y dependencias instaladas con uv.
2. NO se crea una línea base nueva. Se usa la que registra la spec 001 en
   `specs\001-resolubilidad\linea_base.txt` (la spec 001 se implementa antes en esta misma rama).
   Comprobar que existe y está confirmada en Git.
3. Esa línea base lista las pruebas que ya fallan, si las hay. La regla de regresión es la misma de
   la spec 001: la selección del README pasa y la suite completa no tiene fallas nuevas respecto de
   esa línea base.

## 1. Pruebas por historia

```bat
uv run python -m unittest discover -s pruebas -p "test_monticulo_minimo.py"
uv run python -m unittest discover -s pruebas -p "test_conocimiento.py"
uv run python -m unittest discover -s pruebas -p "test_memoria_puertas.py"
uv run python -m unittest discover -s pruebas -p "test_rutas.py"
uv run python -m unittest discover -s pruebas -p "test_ir_a.py"
uv run python -m unittest discover -s pruebas -p "test_conocimiento_retroceso.py"
uv run python -m unittest discover -s pruebas -p "test_conocimiento_serializable.py"
uv run python -m unittest discover -s pruebas -p "test_registro_ir_a.py"
uv run python -m unittest discover -s pruebas -p "test_bench_conocimiento.py"
```

Resultado esperado: todas pasan. Cada prueba cita en su nombre o docstring el FR que cubre.

## 2. Escenarios de punta a punta (con la interfaz)

Se usa una cripta del paquete sin conexión. Consultar el id real con `--bench` o la pantalla de
selección; el código no contiene ids de cripta.

```bat
uv run python -m cripta --cripta <cripta> --offline
```

| # | Escenario | Qué observar | FR |
|---|-----------|--------------|----|
| 1 | Al iniciar, ejecutar `mapa` | Solo la sala inicial explorada, sus destinos avistados, ninguna sala desconocida | FR-001 a FR-006, FR-018 |
| 2 | Moverse a una vecina y volver a `mapa` | La vecina pasa a explorada; sus destinos nuevos, a avistados | FR-002, FR-003 |
| 3 | Encender la antorcha y entrar a una sala con vecinas con enemigos o trampas | Las vecinas figuran exploradas; no se activa nada de ellas; no se ve su contenido | FR-010, FR-011 |
| 4 | Encender la antorcha dentro de una sala y mirar `mapa` | Las vecinas de esa sala NO se exploran; sí las de la siguiente sala | FR-010 |
| 5 | Ver una puerta con cierre automático abierta, alejarse y esperar a que cierre | `mapa` la sigue mostrando abierta; al volver, cerrada | FR-009, spec 2 escenario 1 |
| 6 | Salas exploradas por antorcha: mirar las puertas que no se observaron | Figuran «sin observar» | FR-005, FR-009a |
| 7 | `ir a` hacia una sala avistada | Rechazada, sin consumir tiempo (el reloj no cambia) | FR-020 |
| 8 | `ir a` hacia la sala actual | Rechazada, sin consumir tiempo | FR-021 |
| 9 | `ir a` hacia una sala explorada lejana | Llega por la ruta de menor costo; cada paso consume tiempo; la bitácora muestra «llegaste» | FR-019, FR-023, FR-025, FR-027 |
| 10 | Dos rutas: una con menos salas y más costo, otra con más salas y menos costo | Toma la de menor costo total | FR-023 |
| 11 | Ruta con una puerta cerrada y la llave en el inventario | El viaje no la abre ni la cruza | FR-032 |
| 12 | Ruta por una puerta recordada abierta que en realidad cerró | Al llegar a una sala desde la que se observa, el mapa se actualiza; se recalcula; si no hay alternativa, se detiene por «ruta» sin consumir tiempo | FR-026, FR-030 |
| 13 | Ruta que pasa por una sala con enemigos dormidos | Se activan según la Parte I y el viaje se detiene mostrando enemigos | FR-028 |
| 14 | Ruta por una sala con solo enemigos derrotados | No se detiene por ese motivo | FR-028 |
| 15 | Recibir daño de trampa o veneno en un viaje | El viaje se detiene y muestra daño | FR-029 |
| 16 | Usar el pergamino durante un viaje | Se revierte solo el último paso; el viaje no continúa | FR-034 |
| 17 | Entrar con la antorcha encendida y usar el pergamino | Las salas exploradas por la antorcha vuelven a su estado anterior, con sus puertas recordadas y avistadas | FR-016 |

## 3. Registro y reproducción

1. Hacer un viaje de varios pasos con el registro activo (la opción de carpeta de registros que documente el
   README).
2. Abrir el `partida.log` generado: debe haber una línea `# ir_a <sala>` y, después, un
   `["mover", "<dirección>"]` por paso. Ver [contracts/registro-partida.md](contracts/registro-partida.md).
3. Reproducir el registro:

```bat
uv run python -m cripta --replay <ruta_al_partida.log>
```

Esperado: termina sin divergencias y con el mismo estado final; sin abrir la interfaz (FR-033, SC-005).

## 4. Rendimiento

```bat
uv run python -m cripta --bench --semilla 42
uv run python -m cripta --bench --semilla 42
```

Esperado:

- Aparecen las secciones K1 a K9 del plan; sin ventana (FR-040, SC-008).
- K4: máximo del paso de «ir a» con el mapa completo de la cripta de referencia menor que 5 ms
  (FR-038, SC-003).
- K1 y K2: con 10 veces el tamaño, el costo por consulta y por sala revelada no crece
  apreciablemente (razón a lo sumo 1,5; SC-004).
- Las dos corridas con la misma semilla producen los mismos resultados deterministas (K9, SC-005);
  los tiempos pueden variar, los resultados no.
- Las alternativas comparadas (búsqueda lineal, copia completa, BFS, selección lineal del mínimo,
  Dijkstra desde el origen) pierden en la dimensión que justifica cada decisión (principio VI).

## 5. Verificación final

```bat
uv run python -m unittest discover -s pruebas
```

Esperado: la selección del README pasa y la suite completa no tiene fallas nuevas respecto de
`specs\001-resolubilidad\linea_base.txt`; anotar la comparación en
`specs\002-niebla-ir-a\regresion.txt`. Revisar además:

- Ninguna búsqueda de `heapq`, `bisect`, `collections`, `sorted(` ni `.sort(` en los archivos
  nuevos o modificados (principio I).
- Ningún `dict` ni `set` como índice en el código de esta capacidad.
- Ningún id de sala ni de cripta escrito en el código (principio IV).
- Cada tarea de `tasks.md` cita los FR que atiende (principio VII).

## Resultado de la validación

Fecha: 2026-11-16. Sin ventana. «Automatizado» significa que la lógica del escenario se ejecutó y pasó con
`uv run python -m unittest <módulo>` (no se usó `discover`). La columna «GUI» dice qué falta mirar a mano en la
interfaz gráfica; ninguna casilla de GUI está marcada como hecha.

### Sección 1: pruebas por historia

Pasaron las 73 pruebas de `test_monticulo_minimo`, `test_conocimiento`, `test_memoria_puertas`, `test_rutas`,
`test_ir_a`, `test_conocimiento_antorcha`, `test_conocimiento_retroceso`, `test_conocimiento_serializable`,
`test_registro_ir_a` y `test_bench_conocimiento`.

### Sección 2: 17 escenarios

| # | Automatizado (prueba) | GUI pendiente |
|---|-----------------------|---------------|
| 1 | OK: `test_us1_1_instante_cero` | Pulsar C al iniciar: solo la sala inicial explorada, destinos avistados; minimapa sin salas desconocidas |
| 2 | OK: `test_us1_2_entrar_a_avistada` | Moverse y volver a C; ver el cambio en el panel y el minimapa |
| 3 | OK: `test_us5_1_...`, `test_us5_2_apendice_b_...`, `test_us5_3_...` | Encender la antorcha (U) y entrar; ver vecinas exploradas sin contenido en minimapa y panel |
| 4 | OK: `test_us5_5_encender_dentro_no_explora` | Encender dentro de una sala y mirar C |
| 5 | OK: `test_us2_1_cierre_automatico_recordado_abierto` | Ver el cierre automático en pantalla y comprobar C |
| 6 | OK: `test_us1_5_puertas_sin_observar`, `test_us5_3_...` | Mirar en C que las puertas dicen «sin observar» |
| 7 | OK: `test_us3_1_apendice_b_sala_no_explorada` | En el panel C las avistadas son solo ids y no tienen clic; comprobarlo |
| 8 | OK: `test_us3_6_sala_actual_rechazada` | En C la sala actual figura como «Estás en la sala…» sin clic |
| 9 | OK: `test_us3_7_llegada_detiene_viaje`, `test_viaje_paso_a_paso_y_cancelacion` | Clic en una sala explorada lejana: un paso por ciclo con pausa visual y mensaje «llegaste» |
| 10 | OK: `test_us3_2_menor_costo_no_menos_saltos` | No requiere GUI |
| 11 | OK: `test_us3_4_no_abre_puertas_con_llave` | No requiere GUI |
| 12 | OK: `test_us4_1_apendice_b_...`, `test_us4_2_sin_ruta_alternativa_sin_tiempo` | Ver el recálculo y el mensaje de «ruta» en pantalla |
| 13 | OK: `test_us4_3_apendice_b_enemigos_dormidos` | Ver el viaje detenido con enemigos en pantalla |
| 14 | OK: `test_derrotados_no_detienen` | No requiere GUI |
| 15 | OK: `test_us4_5_danio_ataque`, `_trampa`, `_veneno`, `_danio_cero_no_detiene` | Ver el viaje detenido por daño en pantalla |
| 16 | OK: `test_us6_2_apendice_b_retroceso_durante_viaje` | Pulsar P a mitad de un viaje: se revierte un paso y no sigue |
| 17 | OK: `test_us6_1_apendice_b_retroceso_entrada_con_antorcha` | Antorcha encendida, entrar y pulsar P; revisar el panel C |

### Sección 3: registro y reproducción

Sin ventana, con `Aplicacion` y el paquete `datos_offline` (cripta-02, semilla 42): 6 movimientos para explorar, luego
cuatro órdenes `ir_a 1` hasta llegar (el viaje se detuvo por daño tres veces y por llegada una). El `partida.log` trae una
línea `# ir_a 1` por orden aceptada, antes de sus pasos, y un `["mover", "S"]` por paso. `uv run python -m cripta --offline
--replay <partida.log>` terminó sin divergencias en `sala=1 vida=15 tiempo=1200`, igual que la partida original (sala 1,
vida 15, tiempo 1200), con 0 solicitudes de red. También pasaron `test_us7_1_pasos_individuales_y_comentario` y
`test_us7_2_reproduccion_ignora_comentarios`. Pendiente en GUI: jugar un viaje con la ventana y reproducir ese log.

### Sección 4: rendimiento

`uv run python -m cripta --bench --semilla 42` dos veces: aparecen K1 a K9, sin ventana, y las partes deterministas
coinciden (solo cambian los tiempos). K4: máximo 0,239 ms (menor que 5 ms). Salida en [mediciones.txt](mediciones.txt).

### Validación visual en la GUI (16/11/2026)

- Aviso «resolubilidad no verificada» (spec 001): verificado.
- Escenarios 1, 2, 7 y 8: verificados.
- Escenarios 3, 4 y 6: verificados.
- Escenario 17: verificado.
- Escenario 9: verificado.
- Escenario 16: verificado.
- Escenarios 5 y 12: verificados.
- Escenario 13: verificado.
- Escenario 15: verificado.
- Sección 3 (replay de un viaje): verificada.