# Plan de implementación: Niebla de guerra y viaje automático «ir a»

**Rama**: `kyara` | **Fecha**: 2026-11-15 | **Spec**: [spec.md](spec.md)

**Entrada**: especificación `specs/002-niebla-ir-a/spec.md` (FR-001 a FR-041, SC-001 a SC-008)

## Resumen

El jugador deja de ver el mapa completo. El modelo guarda su conocimiento: el estado de cada sala
(desconocida, avistada, explorada) y la memoria de cada puerta (sin observar, abierta, cerrada).
Todo vive en listas planas indexadas por id de sala, de modo que cada consulta cuesta O(1) y
explorar cuesta lo que se revela. Cada cambio del conocimiento se registra en el historial de
retroceso como un cambio invertible, y además se anexa a un registro cronológico que la spec 004
usa para reconstruir cualquier instante y para guardar.

El comando «ir a» calcula, antes de cada paso, las distancias hacia el destino con un Dijkstra
inverso sobre el subgrafo conocido (salas exploradas y salidas recordadas abiertas), con un
montículo mínimo propio y genérico. El paso elige la vecina de menor «costo de salida más
distancia» y desempata por menor id. Cada paso se ejecuta con el mismo flujo de acción que un
movimiento normal, por lo que consume tiempo, ejecuta eventos, queda en `partida.log` como un
`mover` individual y se revierte con el pergamino. La orden queda como una línea de comentario
que el reproductor ignora. Detalle y alternativas en [research.md](research.md), decisiones D1 a D12.

## Contexto técnico

**Lenguaje/Versión**: Python 3.13, gestionado con uv.

**Dependencias principales**: `arcade` (solo vista), `json` y `struct`. Ninguna dependencia nueva.

**Almacenamiento**: ninguno propio. El conocimiento se expone como estructura serializable
([contracts/conocimiento-serializable.md](contracts/conocimiento-serializable.md)); el formato
binario del guardado es de la spec 004.

**Pruebas**: `unittest` en `pruebas/`.

**Plataforma**: Windows con CMD (equipo); el código no depende de la plataforma.

**Tipo de proyecto**: aplicación de escritorio MVC con modos de consola.

**Metas de rendimiento**: FR-035 a FR-038. Consultas de estado de sala y de puerta sin crecer con
el tamaño del mapa; un paso de «ir a» en menos de 5 ms con el mapa conocido completo de la
cripta de referencia; explorar proporcional a lo revelado; registrar e invertir proporcional a los
cambios.

**Restricciones**: sin `dict`, `set`, `heapq`, `bisect`, `collections`, `networkx`, `sorted()` ni
`list.sort()` (principio I). El modelo NO DEBE conocer HTTP, archivos ni vista (principio III).
Ids de sala enteros pequeños y secuenciales; máximo 4 salidas por sala (N, S, E, O).

**Escala**: la cripta de referencia es la publicada más grande del paquete `datos_offline`; las
criptas sintéticas de `--bench` llegan a 20 000 salas (10 veces la de referencia o más).

### Alcance de datos y archivos leídos

Se leyeron los archivos pedidos: `ExploracionControlador`, `Aplicacion`, `CicloAccionesControlador`,
`PartidaControlador`, `Historial_Retroceso`, `Salidas`, `Indice_Salas`, `Agenda_Eventos`, `Sala`,
`Puertas`, `Efectos`, `Jugador`, `FactoryDto_Partida`, `Partida_dto`, `reproductor`, `bench` y,
de `escena.py`, solo el método `minimapa`. Además `spec.md`, la constitución y
`specs/001-resolubilidad/plan.md`.

Hechos del código existente que condicionan el diseño:

- `Historial_Retroceso` solo conoce tres cambios invertibles: `atributo` (`cambiar`),
  `lista_agregada` y `lista_quitada`. NO existe asignar una posición de una lista, y
  `cambiar` solo sirve para atributos de un objeto. Hace falta un tipo nuevo (D5).
- `ejecutar` (`CicloAccionesControlador`) abre el intervalo, corre la acción, llama a
  `consumir_tiempo` y a `finalizar`, y solo después cierra el intervalo. Todo cambio hecho dentro
  de esa ventana es reversible; un cambio fuera de ella NO se registra (`registrar_si_abierto`).
- `usar_pergamino` llama a `finalizar` fuera de un intervalo: nada del conocimiento DEBE
  escribirse desde ahí.
- `SalidaSimple` no tiene costo ni identifica su sala de origen; `parsear_sala` no lee `costo`.
- `abrir_salida` y `procesar_cierre_puerta` cambian `cerrada` con `agenda.cambiar`, sin saber el
  origen de la salida ni quién la observa.
- `actualizar_vecindad` copia a la vista datos de las vecinas (`tiene_enemigos`, `tiene_objetos`)
  y `es_salida_final`: con niebla es una fuga de información (punto a confirmar C7).
- `leer_partida` exige que cada línea sea `[accion, argumento]`; una línea de comentario hoy la
  invalida. `_validar_accion` no admite una acción `ir_a`, por diseño: la orden va como comentario.
- `bench._bench_ciclo_completo` arma una `Aplicacion` sin `iniciar_partida` y le asigna `_salas`
  directamente: el nuevo paso de observación DEBE ser inocuo si el conocimiento no se inicializó.
- `Jugador` ya tiene `antorcha_encendida`; `Efectos.encender_antorcha` la activa con
  `agenda.cambiar`.

## Constitution Check

*Compuerta previa a la investigación; reevaluada tras el diseño. Resultado: aprobada, sin
violaciones.*

| Principio | Evaluación | Cumple |
|-----------|------------|--------|
| I. Estructuras propias | Estados y memoria de puertas en `list` indexadas por entero; entrantes como `list` de `list`; montículo mínimo propio con listas paralelas (sin `heapq`); marcas por generación en lugar de `set`; sin `dict`/`set`, sin `sorted()` ni `list.sort()`. El único orden necesario (ids ascendentes) sale de recorrer el índice. `dict` solo existe donde ya existe (lectura del JSON). | Sí |
| II. Determinismo | Sin aleatoriedad en el modelo. Empates por regla explícita: menor id de sala destino, luego índice de dirección (N, S, E, O). `--bench` usa `random.Random(semilla)`; nunca `hash()`, hora ni orden de red. | Sí |
| III. MVC | El conocimiento y la búsqueda de rutas viven en `modelo/`, sin E/S. El viaje y los comandos viven en `controlador/`. La vista solo lee DTO. `--bench` y `--replay` NO instancian la vista (import diferido ya usado). | Sí |
| IV. Sin datos de cripta | Ningún id ni tamaño de cripta en el código. La cripta de referencia de `--bench` es la mayor del paquete, descubierta al leer; las pruebas arman esqueletos mínimos en el propio test. | Sí |
| V. Presupuesto de red | La capacidad NO agrega solicitudes: el conocimiento se deriva del esqueleto ya descargado. «Ir a» mueve con `mover`, que ya asegura el contenido de la sala destino con el flujo existente. | Sí |
| VI. Rendimiento con evidencia | `--bench` compara cada decisión con una alternativa medida (tabla de mediciones). Deterministas por semilla. | Sí |
| VII. Spec primero | La spec está confirmada en Git (`bf0edfc`). Cada tarea futura DEBE citar FR. `spec.md` no nombra estructuras; este plan sí, como corresponde. | Sí |

**Reevaluación tras el diseño**: sin cambios. El único punto de atención es el tipo nuevo del
historial (D5), que se limita a agregar un caso invertible y no altera los existentes.

## Decisiones tomadas y puntos a confirmar

### Decisiones tomadas

El detalle, las razones y las alternativas están en [research.md](research.md).

1. **D1 Estado de sala**: `list[int]` por id, valores 0 desconocida, 1 avistada, 2 explorada.
2. **D2 Memoria de puertas**: `list[int]` plana, posición `sala * 4 + dirección` (N=0, S=1, E=2,
   O=3), valores 0 sin observar, 1 abierta, 2 cerrada.
3. **D3 Entrantes**: una `list` por sala con las `SalidaSimple` que llegan a ella, construida una
   sola vez al ensamblar las salas.
4. **D4 Observación**: se refresca al final de cada acción, dentro del intervalo, para la sala
   actual y sus entrantes. Es equivalente a observar «en el momento» porque el jugador no se mueve
   durante el avance del tiempo de una acción.
5. **D5 Historial**: tipo nuevo `lista_asignada` (`asignar(lista, posición, valor)`), O(1) por
   cambio. Además, cada cambio se anexa al registro cronológico con `lista_agregada` (ya existe).
6. **D6 Costo de salida**: campo `costo` en `SalidaSimple` y `SalidaVecina`, 100 si no se declara.
7. **D7 «Ir a»**: Dijkstra inverso desde el destino sobre el subgrafo conocido, con parada
   anticipada al fijar la sala actual, recalculado antes de cada paso.
8. **D8 Montículo**: `MonticuloMinimo` genérico en `estructuras/`, con eliminación perezosa; NO
   reemplaza al heap de la agenda.
9. **D9 Compartir con el cazador (§5.3)**: se comparte el montículo, la regla de desempate y el
   módulo `modelo/Rutas.py` parametrizado por un predicado de arista; las salas permitidas son
   decisión de cada llamador.
10. **D10 Viaje**: `ViajeControlador` con estado propio (no es estado del juego), un paso por
    llamada a `avanzar`, cada paso por `Aplicacion.mover`.
11. **D11 Registro**: comentario `# ir_a <sala>` solo si la orden se acepta; el lector ignora toda
    línea que empiece por `#`.
12. **D12 Vista**: el minimapa dibuja la cruz local desde el conocimiento (estado de la vecina,
    costo y puerta recordada); un comando `mapa` lista el mapa conocido completo.

### Puntos a confirmar

| # | Punto | Propuesta por defecto | Dónde se decide |
|---|-------|-----------------------|-----------------|
| C1 | Costo cero o negativo. El algoritmo supone costo mayor que cero | Un costo declarado menor que 1 se trata como 100 al parsear y se avisa en la bitácora de arranque; el viaje además se corta a tantos pasos como salas exploradas | Equipo, antes de tareas |
| C2 | Motivos de detención adicionales a los cuatro de la spec | Agregar `movimiento_rechazado`, `partida_terminada` y `cancelado`. RESUELTO por FR-031a (paso rechazado y partida terminada); `cancelado` es solo del plan | Resuelto en la spec (FR-031a) |
| C3 | Prioridad cuando coinciden varios motivos en un mismo paso | `partida_terminada`, luego `daño`, luego `enemigos`, luego `llegada`. RESUELTO por FR-031a | Resuelto en la spec (FR-031a) |
| C4 | «Daño» cuando el daño calculado es 0 por defensa | No cuenta: se compara la vida antes y después del paso; `aplicar_danio` (`Combate.py`) no se leyó | Se verifica en tareas |
| C5 | Enemigos al entrar: comprobar en el instante de la entrada o al final del paso | En el instante de la entrada (bandera que fija `_ejecutar_movimiento`), porque un enemigo errante puede salir de la sala durante el avance del tiempo | Equipo |
| C6 | «Vecina» a efectos de la antorcha | Destino de una salida de la sala (abierta o cerrada); no cuentan las salas que solo tienen una salida hacia la actual | Equipo |
| C7 | `actualizar_vecindad` revela contenido de vecinas y la sala de salida | Dejar de copiar `tiene_enemigos` y `tiene_objetos` de las vecinas y mostrar `es_salida_final` solo si la vecina está explorada. Cambia comportamiento de la Parte I: se buscan en tareas las pruebas que lo asuman | Equipo y tareas |
| C8 | `GestorPartida._aplicar_reversion` y el tratamiento de `lista_agregada` no se leyeron | DEBE agregarse el caso `lista_asignada` y DEBE confirmarse que `lista_agregada` se invierte con `pop()` del final (O(1)); si usa `remove` o `index`, corregir para cumplir FR-037 | Primera tarea de implementación |
| C9 | Dependencia de la spec 001 | `--semilla` en `--bench` y el criterio de «cripta de referencia» (mayor esqueleto del paquete) se reutilizan de 001; 001 se implementa antes en esta misma rama y aquí NO se implementa una versión mínima | Orden de ramas |
| C10 | Archivos fuera de la lectura pedida (`InicioPartidaControlador`, `GestorPartida`, `ventana.py`, entrada de teclado) | Se leen al inicio de las tareas que los tocan; el plan solo fija el contrato | Tareas |
| C11 | Compartir `Rutas.py` con el cazador | Se propone en D9; la spec 003 DEBE confirmarlo al planificar | Spec 003 |
| C12 | Guardado de FR-015 | Aquí se entrega la interfaz serializable y su ida y vuelta en pruebas; el guardado de punta a punta es de la spec 004 | Spec 004 |

## Estructura del proyecto

### Documentación de esta capacidad

```text
specs/002-niebla-ir-a/
├── plan.md              # Este archivo
├── research.md          # Decisiones, razones y alternativas
├── data-model.md        # Entidades, validaciones y transiciones
├── quickstart.md        # Guía de validación de punta a punta
├── contracts/
│   ├── comando-ir-a.md                # Comandos, rechazos y motivos de detención
│   ├── registro-partida.md            # Línea de comentario de partida.log
│   └── conocimiento-serializable.md   # Interfaz para el guardado y la línea de tiempo (spec 004)
└── tasks.md             # Lo genera /speckit-tasks (NO existe todavía)
```

### Código fuente (raíz del repositorio)

```text
src/cripta/
├── bench.py                                 # MODIFICA: secciones de conocimiento y de «ir a»
├── estructuras/
│   ├── Monticulo_Minimo.py                  # NUEVO: montículo mínimo genérico, listas paralelas
│   ├── Salidas.py                           # MODIFICA: SalidaSimple con costo y clave; agregar(costo)
│   └── Historial_Retroceso.py               # MODIFICA: asignar() y etiqueta lista_asignada
├── modelo/
│   ├── Conocimiento.py                      # NUEVO: estados, memoria de puertas, entrantes, registro
│   └── Rutas.py                             # NUEVO: distancias inversas y elección del paso
├── dto/
│   ├── Partida_dto.py                       # MODIFICA: costo y estado recordado en SalidaVecina
│   ├── FactoryDto_Partida.py                # MODIFICA: parsear costo
│   └── Conocimiento_dto.py                  # NUEVO: MapaConocido, SalaConocida, SalidaConocida, ResultadoViaje
├── controlador/
│   ├── ExploracionControlador.py            # MODIFICA: dueño del conocimiento, entrada, observación
│   ├── CicloAccionesControlador.py          # MODIFICA: una llamada de observación en ejecutar
│   ├── ViajeControlador.py                  # NUEVO: orden ir a, pasos y motivos de detención
│   ├── PartidaControlador.py                # MODIFICA: registrar_comentario
│   ├── Aplicacion.py                        # MODIFICA: ir_a, avanzar_viaje, cancelar_viaje, mapa_conocido
│   ├── InicioPartidaControlador.py          # MODIFICA: iniciar el conocimiento (leer en tareas)
│   └── GestorPartida.py                     # MODIFICA: invertir lista_asignada (leer en tareas)
├── replay/reproductor.py                    # MODIFICA: comentar() y omitir líneas de comentario
└── vista/grafica/
    ├── escena.py                            # MODIFICA: método minimapa
    └── ventana.py                           # MODIFICA mínimo: comandos mapa e ir a (leer en tareas)

pruebas/
├── apoyo_niebla.py                          # ayudas comunes (esqueleto mínimo, Aplicacion, reloj); no es prueba
├── test_historial_asignar.py                # lista_asignada y lista_agregada (C8; FR-016, FR-037)
├── test_costo_salida.py                     # costo por defecto y menor que 1 (FR-023)
├── test_entrantes.py                        # clave de salida y entrantes (FR-007, FR-022)
├── test_conocimiento_antorcha.py            # exploración por antorcha (FR-010 a FR-012)
├── test_monticulo_minimo.py                 # orden, desempate, vacío, reutilización
├── test_conocimiento.py                     # tres estados, antorcha, instante 0 (FR-001 a FR-012)
├── test_memoria_puertas.py                  # observación desde ambos lados, cierre automático (FR-007 a FR-009a)
├── test_rutas.py                            # costo frente a saltos, empate por id, sin ruta (FR-022 a FR-024)
├── test_ir_a.py                             # rechazos, viaje, motivos de detención (FR-019 a FR-032)
├── test_conocimiento_retroceso.py           # retroceso de entrada con antorcha y de un paso (FR-016, FR-034)
├── test_conocimiento_serializable.py        # ida y vuelta y reconstrucción por registro (FR-015, FR-017)
├── test_registro_ir_a.py                    # comentario, pasos individuales, reproducción (FR-033)
└── test_bench_conocimiento.py               # determinismo por semilla, límite de 5 ms, sin vista (FR-038 a FR-040)
```

**Decisión de estructura**: se conserva la separación existente. `ExploracionControlador` ya es
dueño del índice de salas y de «mover», por eso también lo es del conocimiento; `Aplicacion`
conserva la plantilla `_accion_jugador` y solo delega. `ViajeControlador` es nuevo porque el viaje
tiene estado propio (destino, motivo) que no es estado del juego y no se guarda ni se revierte.

**Fuentes falsas de pruebas**: esta capacidad NO agrega métodos abstractos a `CryptDataSource`, por
lo que las fuentes falsas existentes no cambian. Sí hay dos riesgos de pruebas existentes: las que
arman una `Aplicacion` sin `iniciar_partida` (por ejemplo `bench._bench_ciclo_completo`) y las
que asuman `tiene_enemigos` o `tiene_objetos` en la vecindad (C7).

## Línea base de pruebas

Esta capacidad NO crea una línea base propia: usa la que registra la spec 001 en
`specs/001-resolubilidad/linea_base.txt` (selección de pruebas del README y suite completa de
`pruebas/`, con las pruebas que ya fallan). Al terminar, la selección del README DEBE pasar y la
suite completa NO DEBE tener fallas nuevas respecto de esa línea base; el resultado de la
comparación se anota en `specs/002-niebla-ir-a/regresion.txt`. La spec 001 se implementa antes en
esta misma rama.

## Mediciones previstas (`--bench --semilla N`)

Todas deterministas por semilla (`random.Random(semilla)`; semilla vacía equivale a 42, como en
001). Las criptas sintéticas son cuadrículas con salidas dirigidas, puertas cerradas declaradas en
un solo lado, costos variados y algunos sin declarar (100), con ids secuenciales. Tamaños: 200,
2 000 y 20 000 salas. La cripta de referencia es el mayor esqueleto del paquete `datos_offline`,
con el mismo criterio de 001.

| # | Medición | Qué prueba | Criterio |
|---|----------|------------|----------|
| K1 | Consulta de estado de sala y de puerta recordada: listas indexadas frente a búsqueda lineal en una lista de ids explorados, a 200, 2 000 y 20 000 salas | FR-035, SC-004, principio VI | Costo por consulta con 10 veces el tamaño, a lo sumo 1,5 veces; la alternativa lineal crece |
| K2 | Explorar salas nuevas (con y sin antorcha), costo por sala revelada a los tres tamaños | FR-036, SC-004 | Costo por sala revelada estable (razón a lo sumo 1,5) |
| K3 | Registrar e invertir cambios: `lista_asignada` frente a copiar el conocimiento completo en cada acción, 10 y 1 000 cambios | FR-037, principio VI | Lineal en los cambios; la copia crece con el mapa |
| K4 | Un paso de «ir a» con el mapa conocido completo de la cripta de referencia, sobre pares origen y destino elegidos por semilla | FR-038, SC-003 | Máximo menor que 5 ms |
| K5 | Un paso de «ir a» a 2 000 y 20 000 salas exploradas | FR-038 | Crecimiento acorde a O((V + E) log V); informativo |
| K6 | Dijkstra inverso con parada anticipada, frente al completo, frente a Dijkstra desde el origen y frente a reutilizar distancias entre pasos | D7, principio VI | Se conserva el inverso con parada salvo que otra alternativa gane por más de 2 veces |
| K7 | `MonticuloMinimo` con eliminación perezosa frente a decremento de clave con índice, y frente a selección lineal del mínimo (O(V²)) | D8, principio VI | Se conserva el montículo perezoso salvo que el indexado gane por más de 2 veces |
| K8 | Búsqueda por costo con montículo frente a BFS con la cola de 001 (solo válida con costos iguales), para mostrar que BFS no basta | D7, FR-023 | BFS devuelve rutas de mayor costo en la variante con costos variados |
| K9 | Determinismo: la misma semilla produce los mismos resultados de K4 y K6 en dos corridas | SC-005, FR-039 | Salida idéntica; sin ventana (SC-008) |

Los tiempos se imprimen en consola y NO se abre la vista (FR-040).

## Seguimiento de complejidad

Sin violaciones de la constitución; no se requiere justificación.
