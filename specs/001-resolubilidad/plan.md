# Plan de implementación: Verificación de resolubilidad de la cripta

**Rama**: `kyara` | **Fecha**: 2026-11-15 | **Spec**: [spec.md](spec.md)

**Entrada**: especificación `specs/001-resolubilidad/spec.md` (FR-001 a FR-029, SC-001 a SC-007)

## Resumen

Antes de iniciar una partida, el programa DEBE decidir si la cripta se puede ganar usando solo el
esqueleto (salas, salidas dirigidas, puertas cerradas con su llave) y la ubicación de las llaves
publicada por el servicio. El algoritmo vive en el modelo, es una sola exploración en anchura por
rondas con listas de espera por llave, y la misma exploración, continuada de forma especulativa
más allá de la frontera bloqueada, produce el reporte de bloqueo y los ciclos. El costo de la
exploración es O(S + E + K); el índice de llaves añade un factor logarítmico en K, medido en
`--bench` (ver [research.md](research.md), decisiones D1 a D8).

La capacidad se expone por tres vías: la partida normal (bloquea salvo `--forzar`), la consola
(`--verificar CRIPTA`, sin vista, con códigos de salida 0, 1 y 2) y `--bench` (compara contra la
alternativa ingenua O(K · (S + E))). La ubicación de llaves llega por una consulta nueva del
adaptador, `GET /criptas/<id>/llaves`, que cuenta en el presupuesto y se persiste con la versión
de la cripta.

## Contexto técnico

**Lenguaje/Versión**: Python 3.13, gestionado con uv.

**Dependencias principales**: `arcade` (solo vista), `requests` (solo `NetworkAdapter`), `json` y
`struct`. Ninguna dependencia nueva.

**Almacenamiento**: `AlmacenDisco` (`--cache-dir`): se añade `criptas/<id>/llaves.json`, dentro de
la carpeta que `validar_cripta` ya borra cuando cambia la versión de la cripta. Paquete
`datos_offline`: archivo opcional `cripta_<id>_llaves.json` (hoy ausente, ver Alcance de datos).

**Pruebas**: `unittest` en `pruebas/`.

**Plataforma**: Windows con CMD (equipo); el código no depende de la plataforma.

**Tipo de proyecto**: aplicación de escritorio MVC con modos de consola (`--replay`, `--bench`, y
ahora `--verificar`).

**Metas de rendimiento**: FR-023 y SC-003, verificación de la cripta publicada más grande en
menos de 200 ms sin contar red. SC-004, 10 veces el tamaño en menos de 15 veces el tiempo.

**Restricciones**: sin `dict`, `set`, `heapq`, `bisect`, `collections`, `networkx`, `sorted()` ni
`list.sort()` en el algoritmo (principio I). El modelo NO DEBE conocer HTTP, archivos ni vista
(principio III). Presupuesto de red respetado (principio V).

**Escala**: ids de sala enteros pequeños y secuenciales; el esqueleto más grande del paquete es
`cripta-stormlight` (2 páginas). Las criptas sintéticas de `--bench` llegan a 20 000 salas.

### Alcance de datos y archivos leídos

El contexto salió de `bootstrap.py`, los tres adaptadores, `Crypt_Data_Source.py`,
`CriptaService.py`, `FactoryDto_Partida.py`, `Partida_dto.py`, `InicioPartidaControlador.py`,
`Indice_Salas.py`, `Ordenamientos.py` y `bench.py`. De `vista/` solo se ubicó el punto donde se
muestra el resultado del inicio: `vista/grafica/ventana.py`, método `iniciar_partida`, cuyo
callback `terminado` ya muestra `resultado.motivo` cuando `resultado.ok` es falso. Para ubicar
dónde se inyecta la verificación se leyó además la firma de `Aplicacion.iniciar_partida`.

Hechos relevantes del código existente:

- `CryptDataSource` es una `ABC` con métodos abstractos; `NetworkAdapter`, `AdaptadorOffline` y
  `Guardar_Llamadas_API` son sus tres implementaciones. `Guardar_Llamadas_API` recibe un
  parámetro `datos` adicional en cada método (es el grabador de respuestas).
- `CriptaService` ya persiste el esqueleto con `_cripta_en_disco` y `validar_cripta`; la consulta
  de llaves DEBE seguir el mismo patrón que `cargar_esqueleto_salas`.
- `_FuenteSincronizada` envuelve la fuente con `__getattr__`, así que la consulta nueva queda
  sincronizada sin cambios.
- `InicioPartidaControlador.iniciar` carga el esqueleto antes del contenido y ya devuelve
  `ResultadoInicio(ok=False, motivo=...)` ante fallas; ese es el punto natural de bloqueo.
- `bench.py` usa `random.Random(semilla)` y funciones `_bench_*`; `bootstrap` llama
  `medir()` sin semilla.
- El paquete `datos_offline` no trae archivos de llaves: con él, el resultado es "no
  verificable" (código 2 con `--verificar`).

## Constitution Check

*Compuerta previa a la investigación; reevaluada tras el diseño. Resultado: aprobada, sin
violaciones.*

| Principio | Evaluación | Cumple |
|-----------|------------|--------|
| I. Estructuras propias | Cola con `list` y un índice de cabeza (sin `deque`). Índice de llaves como arreglo ordenado con `ordenar` y búsqueda binaria propia (sin `bisect`). Listas de espera, banderas y ubicaciones en `list` indexadas por entero. Sin `dict`/`set` como índice; `dict` solo al leer el JSON de la respuesta. Sin `sorted()` ni `list.sort()`. | Sí |
| II. Determinismo | Orden de salas por ronda y por id, de salidas por (id destino, dirección), de llaves por id. Empates: menor id. Sin aleatoriedad en el algoritmo; el generador de `--bench` usa `random.Random(semilla)`. Sin `hash()` de Python (varía por proceso) en la alternativa de hash medida. | Sí |
| III. MVC | Algoritmo en `modelo/`, sin HTTP ni archivos. Red y disco en adaptadores y servicio. `--verificar` y `--bench` NO instancian la vista (import diferido ya usado en `bootstrap`). | Sí |
| IV. Sin datos de cripta | El algoritmo y las pruebas sintéticas no contienen ids de cripta reales; las pruebas arman esqueletos mínimos en el propio test. La referencia de `--bench` lee del paquete si existe. | Sí |
| V. Presupuesto | La consulta de llaves cuenta como cualquier solicitud (pasa por `_request`), se reutiliza validando versión y su agotamiento NO aborta la partida: produce "no verificada". | Sí |
| VI. Rendimiento con evidencia | `--bench` mide la alternativa ingenua y la comparación índice ordenado frente a tabla hash propia, con semilla. | Sí |
| VII. Spec primero | La spec está confirmada en Git (`8bec8a2`). Cada tarea futura DEBE citar FR. `spec.md` no nombra estructuras. | Sí |

**Reevaluación tras el diseño**: sin cambios. Las decisiones tomadas de la sección siguiente no
afectan la constitución.

## Decisiones tomadas

1. **Ciclos (FR-012)**. Se aceptan los ciclos del grafo de testigos. FR-012 define ciclo como una
   cadena de llaves encontrada por la exploración en la que cada llave está detrás de una puerta
   que requiere la siguiente, y no exige enumerar las combinaciones de rutas alternativas. El
   diseño reporta todos los ciclos de ese grafo (una dependencia por llave, ciclos disjuntos,
   listados sin omisiones). Ver research D6, alineada con esa definición.
2. **Complejidad**. Se acepta O(S + E + K) para la exploración más el factor log K del índice de
   llaves, es decir O((Ec + L) log K) para construirlo. Ver research D3.
3. **Regla de empate "menor id de sala"** (aclaración 3). Se cumple procesando cada ronda
   ordenada por id; ver D2.
4. **Replay y cargas**: `--replay` y continuar una partida guardada NO verifican, como dice la
   sección de supuestos de la spec (esas partidas ya iniciaron). Se pasa `verificar=False`.
5. **Presupuesto**: la consulta de llaves suma al presupuesto de la partida. Si el presupuesto no
   alcanza, el resultado es "no verificada" y la partida inicia sin veredicto (FR-022).

## Estructura del proyecto

### Documentación de esta capacidad

```text
specs/001-resolubilidad/
├── plan.md              # Este archivo
├── research.md          # Decisiones, razones y alternativas
├── data-model.md        # Entidades, validaciones y estados
├── quickstart.md        # Guía de validación de punta a punta
├── contracts/
│   ├── verificar-cli.md       # Salida y códigos de --verificar, --forzar, --bench
│   └── adaptador-llaves.md    # Consulta nueva de CryptDataSource y del servicio
└── tasks.md             # Lo genera /speckit-tasks (NO existe todavía)
```

### Código fuente (raíz del repositorio)

```text
src/cripta/
├── bootstrap.py                         # MODIFICA: --verificar, --forzar, --semilla en --bench
├── bench.py                             # MODIFICA: sección de resolubilidad
├── adaptadores/
│   ├── Crypt_Data_Source.py             # MODIFICA: key_locations abstracto
│   ├── Network_Adapter.py               # MODIFICA: key_locations (GET /criptas/{id}/llaves)
│   ├── AdaptadorOffline.py              # MODIFICA: key_locations (caché, luego paquete)
│   ├── Guardar_Llamadas_API.py          # MODIFICA: key_locations (graba cripta_<id>_llaves.json)
│   └── Almacen_Disco.py                 # MODIFICA: leer_llaves / guardar_llaves
├── servicio/
│   └── CriptaService.py                 # MODIFICA: obtener_ubicaciones_llaves y validación mínima
├── dto/
│   ├── Partida_dto.py                   # MODIFICA: ResultadoInicio con verificación y aviso
│   ├── FactoryDto_Partida.py            # MODIFICA: parsear_llaves
│   └── Verificacion_dto.py              # NUEVO: UbicacionLlave, ResultadoVerificacion y reporte
├── estructuras/
│   ├── Indice_Llaves.py                 # NUEVO: arreglo ordenado + búsqueda binaria propia
│   └── Cola_Lista.py                    # NUEVO: cola con list e índice de cabeza
├── modelo/
│   └── Resolubilidad.py                 # NUEVO: exploración, reporte y ciclos (sin E/S)
├── controlador/
│   ├── VerificacionControlador.py       # NUEVO: orquesta servicio + modelo, formatea texto
│   ├── InicioPartidaControlador.py      # MODIFICA: verifica tras cargar el esqueleto
│   └── Aplicacion.py                    # MODIFICA: parámetro forzar, verificar=False en cargas
└── vista/grafica/ventana.py             # MODIFICA mínimo: mostrar reporte en el aviso de inicio

pruebas/
├── test_resolubilidad.py                # modelo: escenarios del Apéndice B, determinismo
├── test_cola_lista.py                   # ColaLista: FIFO, vacía, sin pop(0)
├── test_indice_llaves.py                # índice ordenado y su búsqueda
├── test_llaves_adaptadores.py           # tres adaptadores, persistencia y versión
├── test_verificar_cli.py                # salida y códigos 0, 1 y 2, sin vista
├── test_inicio_verificacion.py          # bloqueo, --forzar, "no verificada"
└── test_bench_resolubilidad.py          # criptas sintéticas por semilla; límite de 200 ms (M7); --bench sin arcade
```

**Decisión de estructura**: se conserva la separación existente (adaptadores, servicio, dto,
estructuras, modelo, controlador). El modelo recibe esqueleto y ubicaciones ya parseados como DTO
y devuelve un DTO de resultado; nunca toca red ni disco. `Aplicacion.py` y `ventana.py` se
tocan con cambios de una o dos líneas; su lectura detallada ocurre en la fase de tareas.

**Fuentes falsas de pruebas**. En `pruebas/` hay fuentes de datos falsas en `test_partida.py`,
`test_inventario.py`, `test_combate_efectos.py` y `test_guardados.py`. Como la consulta nueva es
abstracta, DEBEN recibirla devolviendo "sin datos" (resultado "no verificada"), y la selección
de pruebas del README DEBE seguir pasando y la suite completa de pruebas/ NO DEBE tener fallas
nuevas respecto de una línea base registrada antes de implementar. Nota de lectura del código: hoy
esas fuentes no heredan de `CryptDataSource` directamente, sino a través de `FuentePrueba`
(`test_inventario.py`, subclase de `AdaptadorOffline`), `FuenteReplay` y `FuenteRetroceso`; el
punto de edición mínimo es la base común, más la clase `AdaptadorOffline` local de
`test_guardados.py`. La verificación de que no queda ninguna fuente sin la consulta queda como
tarea explícita.

## Mediciones previstas (`--bench --semilla N`)

Todas deterministas por semilla (`random.Random(semilla)`; semilla vacía equivale a 42, nunca
aleatoria). Criptas sintéticas: región base aleatoria más una cadena de llaves, ids de sala
permutados por la semilla, en variante resoluble y en variante con ciclo final.

| # | Medición | Qué prueba | Criterio |
|---|----------|------------|----------|
| M1 | Verificación O(S + E + K) frente a repetir la exploración por cada llave O(K · (S + E)), tamaños 200, 2 000 y 20 000 salas (la ingenua hasta 2 000) | FR-024, FR-026, SC-004 | La ingenua pierde y la brecha crece con K |
| M2 | Escalado de la verificación al multiplicar por 10 el tamaño | SC-004 | Menos de 15 veces |
| M3 | Cripta de referencia del paquete con llaves, si existe; si no, mensaje "sin llaves en el paquete". Sigue midiendo la cripta real cuando haya llaves | FR-023, SC-003 | Menos de 200 ms sin red |
| M7 | Cripta sintética generada por semilla de al menos 10 veces el tamaño (salas) del esqueleto más grande de `datos_offline`, medida sin red; no depende de que el paquete traiga llaves | FR-023, SC-003 | Menos de 200 ms sin red; hay prueba automatizada del mismo límite |
| M4 | Índice de llaves: arreglo ordenado con búsqueda binaria frente a tabla hash propia con hash polinomial determinista | Principio VI | Se conserva el arreglo salvo que el hash gane por más de 2 veces en la verificación completa al mayor tamaño |
| M5 | Costo del reporte (fase especulativa y ciclos) sobre la verificación pura, variante con ciclo | FR-025 | Lineal, sin repetir exploraciones |
| M6 | Orden por ronda con `ordenar` frente a orden de cola sin ordenar | Aclaración 3 | Sobrecosto aceptable dentro de SC-004 |

## Seguimiento de complejidad

Sin violaciones de la constitución; no se requiere justificación.

## Cierre de entrega (17/11/2026)

FR-030: logger de Python en el adaptador HTTP; archivo rotativo en --log-dir/red.log configurado al arrancar, independiente del registro de acciones. Se registran intentos, tiempos monotónicos, estado y presupuesto; no se registran cuerpos ni cabeceras. Pruebas con respuestas HTTP simuladas y reloj controlado.

FR-031: herramienta manual con --destino; descarga en una carpeta temporal vecina y publica el paquete únicamente tras validar versiones. Reutiliza NetworkAdapter y Guardar_Llamadas_API, recorre todas las páginas y lotes de hasta diez y resuelve referencias de enemigos, objetos, trampas y botín. El paquete datos_entrega se versiona separado de datos_offline.
