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
