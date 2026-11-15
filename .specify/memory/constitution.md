# Constitución de Cripta

Proyecto del curso EIF207 Estructuras de Datos, II Ciclo 2026, Parte II.

## Principios Fundamentales

### I. Estructuras de datos propias (NO NEGOCIABLE)

Las estructuras de datos de los problemas evaluados DEBEN implementarse a mano.

- Está prohibido usar `dict` o `set` como índice, caché o tabla de búsqueda.
- Están prohibidos `heapq`, `bisect`, `collections` (`deque`, `OrderedDict`,
  `defaultdict`, `Counter`), `networkx` y cualquier biblioteca de grafos o de búsqueda de rutas.
- Tampoco se permite ninguna implementación equivalente de una biblioteca (por ejemplo
  `queue.PriorityQueue`), ni `sorted()` o `list.sort()` para resolver los problemas evaluados;
  se usan los ordenamientos propios del proyecto.
- Está permitido `list` como almacenamiento contiguo, `dict` solo para leer el JSON de las
  respuestas, y los módulos `struct`, `json`, `requests` y `arcade`.
- Un plan que proponga una dependencia prohibida DEBE corregirse antes de generar tareas.

### II. Determinismo

La misma versión de cripta, la misma semilla y las mismas acciones DEBEN producir la misma partida.

- Toda aleatoriedad DEBE usar la instancia propia `random.Random(semilla)` del modelo.
- Nunca se usa el generador global, la hora del sistema ni el orden de llegada de respuestas HTTP.
- Todo empate DEBE resolverse con una regla explícita (número de secuencia, menor id).

### III. Separación MVC

El modelo NO DEBE conocer HTTP, archivos ni la interfaz. La red y el disco se acceden mediante
adaptadores. Los modos `--replay`, `--bench` y `--verificar` NO DEBEN instanciar la vista.

### IV. Ningún dato de una cripta en el código

El código NO DEBE contener ids de salas o entidades, cantidades de páginas, presupuestos ni
estadísticas de una cripta concreta. Todo dato proviene del servicio web o de los datos offline.

### V. Presupuesto de red

Se DEBE respetar `presupuesto_solicitudes` de cada cripta.

- Toda solicitud HTTP cuenta, incluidos los reintentos y la consulta de llaves.
- Lo persistido DEBE reutilizarse validando su versión.

### VI. Rendimiento con evidencia

Toda afirmación de rendimiento DEBE respaldarse con mediciones de `--bench`, deterministas por
semilla. Cada decisión de estructura de datos DEBE comparar al menos una alternativa medida.

### VII. La especificación precede a la implementación (NO NEGOCIABLE)

Cada capacidad DEBE tener su `spec.md` confirmada en Git antes que el código que la implementa.

- Si la spec resulta incorrecta, se corrige primero la spec y luego el código, en commits
  separados.
- Cada requisito funcional DEBE tener un id estable (FR-001).
- Cada caso del Apéndice B del enunciado DEBE aparecer como escenario de aceptación en alguna spec.
- Cada escenario de aceptación DEBE tener una prueba automatizada o un `partida.log` que cita
  su FR.
- Cada tarea DEBE citar los FR que atiende.
- `spec.md` NO DEBE nombrar estructuras de datos, clases ni módulos.

## Restricciones técnicas

- Lenguaje: Python 3.13 o superior, gestionado con uv.
- Vista: Arcade.
- Pruebas: `unittest`, en la carpeta `pruebas/`.
- Agente: Claude Code con spec-kit v1.3.3 y scripts sh.
- Entorno del equipo: Windows con CMD.

## Flujo de trabajo

- Por capacidad se ejecuta constitution (una sola vez), specify, clarify, plan, tasks, analyze
  e implement. Clarify y analyze son obligatorios.
- Cada integrante trabaja en su propia rama y se integra a `master` mediante pull request con
  merge commit, nunca squash.
- Cada prompt a un LLM, incluidos los comandos de spec-kit con texto propio, DEBE registrarse en
  la bitácora `PROMPTS_LLM.md` con fecha, integrante, herramienta, prompt textual y uso.

## Gobernanza

Esta constitución prevalece sobre cualquier plan o tarea. Se enmienda por pull request con
versión semántica (MAJOR por eliminar o redefinir principios de forma incompatible, MINOR por
agregar principios o ampliar guía de forma material, PATCH por aclaraciones). El comando
`/speckit-analyze` verifica su cumplimiento.

**Versión**: 1.0.0 | **Ratificada**: 2026-11-15 | **Última enmienda**: 2026-11-15
