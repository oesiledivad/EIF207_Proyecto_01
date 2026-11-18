# Plan de implementación: Línea de tiempo y puntos de control

**Rama**: `eliseo` | **Fecha**: 2026-11-17 | **Spec**: [spec.md](spec.md)

**Entrada**: especificación `specs/004-linea-tiempo/spec.md` (FR-001 a FR-034, SC-001 a SC-008)

## Resumen

La línea de tiempo no guarda el estado completo del juego: guarda el **estado observable**, que es
lo que muestra `historia` (sala, vida y estadísticas del jugador, inventario, efectos, vida y sala
de cada enemigo y el conocimiento del jugador). Ese estado se representa como un vector de
**ranuras** (enteros, textos o tuplas pequeñas) y la partida se registra como una bitácora de
cambios `[tiempo, ranura, antes, después]`, anexada **por evento** del reloj. Cada acción del
jugador deja una **marca** (instante y posición en la bitácora) y cada K marcas se copia el vector
completo (**punto de control**). Una consulta ubica la marca con búsqueda binaria propia, toma el
punto de control anterior o el siguiente, el que quede más cerca, y aplica hacia adelante o
invierte hacia atrás los cambios necesarios (a lo sumo K acciones). El pergamino recorta la
bitácora desde la marca de la acción revertida, en tiempo proporcional a lo recortado.

La estructura (`LineaTiempo`) no conoce el juego. El controlador (`LineaTiempoControlador`) traduce
el juego a ranuras: lee al jugador, el inventario y los efectos al cerrar cada evento, toma los
enemigos que cambiaron mediante un observador del historial de retroceso y toma el conocimiento
del registro cronológico de la spec 002. Las decisiones de esta sección se detallan en
[research.md](research.md) (D1 a D12).

## Contexto técnico

**Lenguaje/Versión**: Python 3.13, gestionado con uv.

**Dependencias principales**: `arcade` (solo vista), `struct` (guardado), `tracemalloc` y `time`
(solo `--bench`). Ninguna dependencia nueva.

**Almacenamiento**: guardado binario existente; el cuerpo pasa a la versión 3 y se agrega un cuerpo
nuevo con el conocimiento y la línea de tiempo (D9).

**Pruebas**: `unittest` en `pruebas/`.

**Plataforma**: Windows con CMD (equipo); el código no depende de la plataforma.

**Tipo de proyecto**: aplicación de escritorio MVC con modos de consola (`--bench`, `--replay`,
`--verificar`).

**Metas de rendimiento**: FR-029, consulta `historia` ≤ 50 ms con ≥ 5 000 acciones y K por defecto.
El costo agregado a cada ciclo de eventos no debe comprometer los 20 ms de la spec 003.

**Restricciones**: sin `dict`, `set`, `heapq`, `bisect`, `collections`, `sorted()` ni `list.sort()`
(principio I). La búsqueda binaria de marcas es propia. El modelo no conoce la línea de tiempo: la
simulación solo expone un gancho opcional al terminar cada evento (principio III).

**Escala**: partidas de 5 000 a 20 000 acciones; criptas del paquete (hasta 50 salas) y sintéticas.

Sin puntos NEEDS CLARIFICATION: los cuatro de la sesión de clarificación están en la spec.

### Archivos leídos

`estructuras/Historial_Retroceso.py`, `controlador/GestorPartida.py`,
`controlador/CicloAccionesControlador.py`, `controlador/Aplicacion.py`,
`controlador/PartidaControlador.py` (retroceso y registro), `controlador/GuardadoControlador.py`,
`controlador/guardado/{Formato,Escritura,Lectura,Restauracion}.py`,
`estructuras/Guardado_Binario.py`, `modelo/Simulacion.py`, `modelo/Conocimiento.py`,
`controlador/ExploracionControlador.py` (mapa conocido), `controlador/EfectosControlador.py`
(describir), `estructuras/Inventario.py` (items), `replay/reproductor.py`, `bootstrap.py`,
`vista/grafica/{ventana,panel}.py`, `bench.py` (estructura), `specs/002-niebla-ir-a/contracts/
conocimiento-serializable.md`.

## Constitution Check

| Principio | Cumplimiento |
|-----------|--------------|
| I. Estructuras propias | Bitácora en listas paralelas, búsqueda binaria propia sobre las marcas, índice de enemigos por atributo del objeto (sin `dict`). Ningún módulo prohibido. |
| II. Determinismo | La línea solo lee el estado; no usa azar ni hora. El orden de la bitácora es el de los eventos (tiempo, secuencia). |
| III. MVC | `LineaTiempo` es una estructura sin dependencias del juego; `Simulacion` solo llama un gancho opcional; `--replay --hasta` y `--bench` no importan la vista. |
| IV. Sin datos de cripta | Las ranuras se derivan del esqueleto y de los enemigos de la partida. |
| V. Presupuesto de red | La consulta no hace solicitudes: usa solo el esqueleto y las salas ya ensambladas. |
| VI. Rendimiento con evidencia | Mediciones L1 a L5 en `--bench` (research.md). |
| VII. Spec antes que código | spec.md confirmada en `20557fc`; este plan y tasks.md se confirman antes del código. |

## Decisiones tomadas

1. Estado observable en ranuras y bitácora de cambios con antes y después (D1, D2).
2. Captura por evento: gancho al final de cada evento de la simulación (D3).
3. Enemigos por observador del historial de retroceso; jugador, inventario y efectos por lectura
   directa; conocimiento por su registro cronológico (D4).
4. Marcas por acción y búsqueda binaria propia (D5).
5. Puntos de control cada K marcas, índice directo `a // K` (D6).
6. Reconstrucción desde el punto de control más cercano, hacia adelante o hacia atrás (D7).
7. Recorte con el pergamino desde la marca (D8).
8. Guardado: cuerpo versión 3 y cuerpo nuevo de línea; versión 2 se rechaza como Parte I (D9).
9. `--replay --hasta`: reproducir el registro completo y consultar la línea (D10).
10. Interfaz: tecla H y entrada en el menú (D11).
11. K por defecto: se fija con L1; provisional 50 (D12).

## Estructura del proyecto

### Documentación (esta capacidad)

```text
specs/004-linea-tiempo/
├── spec.md
├── plan.md            # este archivo
├── research.md        # D1 a D12 y mediciones previstas
├── data-model.md
├── quickstart.md
├── tasks.md
└── checklists/requirements.md
```

### Código fuente (raíz del repositorio)

```text
src/cripta/
├── estructuras/
│   ├── Linea_Tiempo.py            # NUEVO: bitácora, marcas, puntos de control, consulta
│   └── Historial_Retroceso.py     # observador opcional de registrar
├── modelo/
│   └── Simulacion.py              # gancho opcional al terminar cada evento
├── controlador/
│   ├── LineaTiempoControlador.py  # NUEVO: ranuras, captura, historia, resumen
│   ├── Aplicacion.py              # historia(), K, enganche con pergamino y carga
│   ├── CicloAccionesControlador.py# marcas y captura alrededor de cada acción
│   ├── InicioPartidaControlador.py# crea la línea al iniciar
│   ├── GuardadoControlador.py     # restaura conocimiento y línea; aviso de K
│   └── guardado/{Formato,Escritura,Lectura,Datos}.py
├── dto/Historia_dto.py            # NUEVO: resumen de un instante
├── replay/reproductor.py          # --hasta
├── bootstrap.py                   # --checkpoint-cada, --hasta
├── vista/grafica/{ventana,historia}.py
└── bench.py                       # L1 a L5
pruebas/
├── apoyo_linea.py
├── test_linea_tiempo.py           # estructura
├── test_historia.py               # consultas y Apéndice B 1, 3, 4
├── test_historia_retroceso.py     # Apéndice B 2
├── test_historia_replay.py        # Apéndice B 5 y CLI
├── test_historia_guardado.py      # Apéndice B 6, FR-024 a FR-027, FR-034
└── test_bench_linea.py
```

## Complejidad agregada

| Operación | Costo |
|-----------|-------|
| Registrar un cambio | O(1) amortizado |
| Capturar un evento | O(1 + inventario + efectos + enemigos que cambiaron + cambios de conocimiento) |
| Marca de acción | O(1); con punto de control, O(ranuras) |
| Ubicar instante | O(log N) marcas + cambios de una acción |
| Ubicar punto de control | O(1) |
| Reconstruir | O(ranuras + cambios de a lo sumo K acciones) |
| Recorte por pergamino | O(cambios recortados) |
| Memoria | O(cambios + ranuras × N/K) |
