# Tareas: Niebla de guerra y viaje automático «ir a»

**Entrada**: `specs/002-niebla-ir-a/` (spec.md, plan.md, research.md, data-model.md, contracts/, quickstart.md)

**Requisitos previos**: plan.md y spec.md. Las decisiones D1 a D15 de research.md y las «Decisiones tomadas» del plan son definitivas. Los puntos C1 a C12 del plan se resuelven dentro de las tareas que los citan.

**Pruebas**: solicitadas de forma explícita. Hay una prueba `unittest` en `pruebas/` por cada escenario de aceptación (incluidos los 6 del Apéndice B, listados en SC-001) y cada prueba cita su FR en el docstring. Las pruebas de cada historia se escriben antes de la implementación y DEBEN fallar primero. Excepción: T003 se escribe después de T002 porque T002 es, por pedido expreso, la primera tarea de implementación (decisión C8).

**Organización**: por historia de usuario (US1 a US8) para implementar y probar cada una por separado.

## Formato: `[ID] [P?] [Historia] Descripción con ruta`

- **[P]**: se puede hacer en paralelo (archivos distintos, sin dependencia de tareas incompletas).
- **[USn]**: historia de usuario de spec.md.
- Cada tarea cita al menos un FR. Las tareas de soporte citan los FR que protegen.
- Rutas desde la raíz del repositorio. Comandos para Windows con CMD y `uv run`.

## Reglas transversales (constitución)

- Sin `dict`, `set`, `heapq`, `bisect`, `collections`, `networkx`, `sorted()` ni `list.sort()` en el código de esta capacidad (principio I). `dict` solo donde ya existe (lectura del JSON).
- El modelo (`modelo/Conocimiento.py`, `modelo/Rutas.py`) NO conoce HTTP, archivos ni vista (principio III). `--bench` y `--replay` NO instancian la vista.
- Ningún dato de una cripta concreta en código ni en pruebas (FR-041, principio IV): cada prueba arma su esqueleto mínimo.
- Docstring de cada prueba: `"""FR-0xx: ..."""` con el escenario que cubre.
- Todo cambio del conocimiento pasa por `historial.asignar` y se anexa al registro con `historial.agregar`; nada del conocimiento se escribe desde `usar_pergamino` (fuera de intervalo).
- Texto en español y sin guiones largos, en código, docstrings y documentación.

---

## Fase 1: Preparación

**Propósito**: confirmar la línea base de la spec 001 antes de tocar código.

- [X] T001 Confirmar la línea base de pruebas registrada por la spec 001 en `specs/001-resolubilidad/linea_base.txt` (tarea T001 de esa spec). NO crear otra línea base ni un archivo `linea-base.txt` en esta carpeta. Comprobar que el archivo existe, está confirmado en Git y lista los comandos (a) selección del README y (b) suite completa, con las pruebas que ya fallan. Si no existe, ejecutar primero la T001 de `specs/001-resolubilidad/tasks.md` con el código sin modificar y confirmarla en Git. Anotar en el mensaje de la fase qué hash usa la línea base. Protege FR-014 y FR-016 (no alterar comportamiento existente).

**Punto de control**: `specs/001-resolubilidad/linea_base.txt` existe y está confirmado antes de T002.

---

## Fase 2: Fundamentos (bloquean todas las historias)

**Propósito**: historial invertible, montículo, costo y clave de salidas, entrantes y apoyo de pruebas.

**CRÍTICO**: ninguna historia empieza hasta terminar esta fase.

- [X] T002 Agregar el cambio `lista_asignada` al historial (decisión C8, D5), primera tarea de implementación. En `src/cripta/estructuras/Historial_Retroceso.py` crear `asignar(lista, posicion, valor)` que registra la etiqueta `lista_asignada` con `[lista, posicion, valor_anterior]` y asigna; si el valor no cambia NO registra nada. En `src/cripta/controlador/GestorPartida.py` ampliar `_aplicar_reversion` con el caso `lista_asignada` (restaura `lista[posicion] = valor_anterior`). Leer además el tratamiento de `lista_agregada` en `_aplicar_reversion`: DEBE invertirse con `pop()` del final (O(1)); si usa `remove` o `index`, corregirlo. No alterar los casos `atributo`, `lista_agregada` ni `lista_quitada`. Cita FR-016 y FR-037.
- [X] T003 Escribir `pruebas/test_historial_asignar.py`: `asignar` registra y revierte la posición, asignar el mismo valor no registra, varias asignaciones se revierten en orden inverso, `lista_agregada` se revierte quitando el último elemento sin recorrer la lista (verificar con una lista de 10 000 elementos y comprobando el resultado y que el orden de los demás no cambia), y los tres cambios existentes siguen funcionando. Docstrings citan FR-016 y FR-037. Debe pasar tras T002; ejecutar y, antes de seguir, correr la selección del README.
- [X] T004 [P] Escribir `pruebas/test_monticulo_minimo.py` para `MonticuloMinimo`: extrae por menor `(prioridad, desempate)`, empates por desempate entero, `esta_vacio`, `vaciar` deja listo para otra búsqueda sin reasignar, eliminación perezosa (el llamador reinserta con mejor prioridad y descarta obsoletas), 10 000 inserciones y extracciones en orden. Docstrings citan FR-024 y FR-038. DEBE fallar antes de T005.
- [X] T005 Crear `src/cripta/estructuras/Monticulo_Minimo.py` con `MonticuloMinimo`: tres listas paralelas (prioridad, desempate, elemento), `insertar`, `extraer_minimo`, `esta_vacio`, `vaciar`, comparación lexicográfica por `(prioridad, desempate)` con enteros, sin `heapq`. NO tocar `HeapAgendaEventos`. Cita FR-024 y FR-038.
- [X] T006 [P] Escribir `pruebas/test_costo_salida.py`: `parsear_sala` lee `costo` de cada salida; una salida sin `costo` vale 100; un costo declarado menor que 1 (0 o negativo) se trata como 100 y deja un aviso en la lista de avisos recibida; `Salidas.agregar` sin el parámetro nuevo sigue funcionando (las llamadas de `bench` no cambian). Docstrings citan FR-023 y el caso límite «costo menor que 1». DEBE fallar antes de T007.
- [X] T007 En `src/cripta/estructuras/Salidas.py` ampliar `SalidaSimple` con `costo: int = 100` y `clave: int = 0` y dar a `Salidas.agregar` el parámetro final opcional `costo`. En `src/cripta/dto/FactoryDto_Partida.py` hacer que `parsear_sala` lea `costo` de cada salida, normalice a 100 todo costo ausente o «menor que 1» (restricción verbatim de data-model.md: «`costo` menor que 1 o ausente se normaliza a 100 al parsear») y reciba un parámetro opcional `avisos` (lista, por defecto nada) donde anexa el texto del aviso en el caso menor que 1. Cita FR-023 y C1.
- [X] T008 En `src/cripta/dto/Partida_dto.py` ampliar `SalidaVecina` con `costo: int = 100`, `puerta_recordada: str = "sin_observar"` (valores `abierta`, `cerrada`, `sin_observar`) y `estado_vecina: str = "avistada"` (valores `explorada`, `avistada`), con valores por defecto para no romper usos actuales. En `src/cripta/controlador/InicioPartidaControlador.py` (leerlo entero primero, C10) pasar la lista `avisos` a `parsear_sala` y escribir cada aviso en la bitácora de arranque con la categoría que ya use el arranque. Cita FR-005, FR-018 y C1.
- [X] T009 [P] Escribir `pruebas/test_entrantes.py`: tras `ensamblar_salas` cada salida tiene `clave = origen * 4 + índice de dirección` (N 0, S 1, E 2, O 3), las claves son únicas, `clave // 4` es la sala de origen, `entrantes[v]` contiene exactamente las salidas con `sala_destino == v`, y una salida hacia una sala inexistente no rompe el ensamblado. Docstrings citan FR-007 y FR-022. DEBE fallar antes de T010.
- [X] T010 En `src/cripta/controlador/ExploracionControlador.py` (método `ensamblar_salas`, línea 67) fijar `clave` en cada `SalidaSimple` con una comparación explícita de dirección (sin `dict`) y construir una vez la lista `entrantes` indexada por id de sala (D3), expuesta como atributo del controlador. NO es estado del juego: no se guarda. Cita FR-007, FR-022 y FR-035.
- [X] T011 [P] Crear `pruebas/apoyo_niebla.py` con ayudas para las pruebas de esta capacidad: construir un esqueleto mínimo a partir de una descripción de salas, salidas, costos, puertas cerradas, enemigos y trampas armada en la propia prueba; armar una `Aplicacion` con una fuente falsa derivada de `FuentePrueba` (`pruebas/test_inventario.py`) y una partida iniciada; y un reloj controlable para forzar cierres automáticos. Sin ids ni datos de cripta reales. Cita FR-041.
- [X] T012 Ejecutar la selección del README (comando (a) de `specs/001-resolubilidad/linea_base.txt`) tras T010 y comprobar que pasa igual que en la línea base, más `uv run python -m unittest pruebas.test_historial_asignar pruebas.test_monticulo_minimo pruebas.test_costo_salida pruebas.test_entrantes`. Protege FR-016 y FR-023.

**Punto de control**: fundamentos listos; las historias pueden empezar.

---

## Fase 3: US1 - Ver solo lo que el jugador conoce (P1) 🎯 MVP

**Meta**: tres estados de sala para el jugador, mapa conocido sin salas desconocidas y vista derivada solo del conocimiento.

**Prueba independiente**: `uv run python -m unittest pruebas.test_conocimiento` con esqueletos armados en la prueba, sin vista.

### Pruebas de US1 (escribir primero; DEBEN fallar)

- [X] T013 [US1] En `pruebas/test_conocimiento.py`, `test_us1_1_instante_cero`: partida recién iniciada; la sala inicial figura explorada con salidas, costos y estado de puertas, sus destinos avistados y ninguna sala desconocida aparece en `Aplicacion.mapa_conocido()`. Docstring cita FR-002, FR-003 y FR-018.
- [X] T014 [US1] En `pruebas/test_conocimiento.py`, `test_us1_2_entrar_a_avistada`: al entrar a una sala avistada pasa a explorada y los destinos de sus salidas no explorados pasan a avistados. Docstring cita FR-002 y FR-003.
- [X] T015 [US1] En `pruebas/test_conocimiento.py`, `test_us1_3_nunca_desconocidas`: tras varias entradas, `mapa_conocido()` nunca incluye una sala desconocida y de las avistadas solo expone el id; `estado(id)` fuera de rango devuelve desconocida. Docstring cita FR-004, FR-006 y SC-002.
- [X] T016 [US1] En `pruebas/test_conocimiento.py`, `test_us1_4_costo_y_puerta_recordada`: cada salida de una sala explorada indica su costo y su puerta recordada (`abierta`, `cerrada`, `sin_observar`); una salida sin costo declarado muestra 100. Docstring cita FR-005 y FR-023.
- [X] T017 [US1] En `pruebas/test_conocimiento.py`, `test_us1_5_puertas_sin_observar`: una sala explorada con `Conocimiento.explorar` directo (sin entrar a ella ni observar sus puertas) muestra sus puertas «sin observar», ni abiertas ni cerradas. Docstring cita FR-005 y FR-009a.
- [X] T018 [US1] En `pruebas/test_conocimiento.py`, `test_vecindad_no_revela_contenido` y `test_conocimiento_no_inicializado_es_inocuo`: la vista de vecindad deja de copiar `tiene_enemigos` y `tiene_objetos` de las vecinas, y `es_salida_final` solo aparece para vecinas exploradas (C7); una `Aplicacion` armada sin `iniciar_partida` ejecuta una acción sin error (caso de `bench._bench_ciclo_completo`). Docstrings citan FR-011, FR-014 y FR-006.

### Implementación de US1

- [X] T019 [US1] Crear `src/cripta/modelo/Conocimiento.py` con las constantes de data-model.md (`DESCONOCIDA` 0, `AVISTADA` 1, `EXPLORADA` 2, `SIN_OBSERVAR` 0, `ABIERTA` 1, `CERRADA` 2, `COSTO_DEFECTO` 100) y `ConocimientoJugador`: listas `estado_sala` (tamaño `max_id + 1`) y `puerta` (tamaño `4 * (max_id + 1)`), `registro` y bandera `inicializado` en falso; `iniciar(salas, entrantes, sala_inicial)` que crea las listas en 0, explora la sala inicial, avista sus destinos y observa sus puertas sin historial A PROPÓSITO (es la base del instante 0 y no se revierte nunca; dejarlo escrito en el docstring de `iniciar`) (invariante 6); `estado(sala)` O(1), con un id fuera de rango devuelve 0; `memoria_puerta(clave)` O(1); y un método privado de asignación que usa `historial.asignar` y `historial.agregar(registro, [tiempo, tipo, indice, valor])`, sin registrar si el valor no cambia. Restricciones verbatim: «`estado_sala[id]` es exactamente 0, 1 o 2» y «Todos los valores caben en un byte sin signo». Sin `dict` ni `set`. Cita FR-001, FR-002, FR-005, FR-035.
- [X] T020 [US1] En `src/cripta/modelo/Conocimiento.py` agregar `explorar(sala, historial, tiempo)`: marca la sala explorada y avista los destinos aún desconocidos de sus salidas (no degrada una sala ya explorada), costo O(4), sin observar puertas, y `entrar(sala, antorcha, historial, tiempo)` que por ahora solo llama a `explorar` (la antorcha llega en T040). Inocuo si `inicializado` es falso. Cita FR-002, FR-003, FR-012 y FR-036.
- [X] T021 [US1] Crear `src/cripta/dto/Conocimiento_dto.py` con `MapaConocido` (`exploradas`, `avistadas`), `SalaConocida` (`id`, `nombre`, `salidas`), `SalidaConocida` (`direccion`, `destino`, `costo`, `puerta` en `abierta`, `cerrada` o `sin_observar`, `destino_estado` en `explorada` o `avistada`) y `ResultadoViaje` (`ok`, `activo`, `motivo`, `mensaje`). Cita FR-018 y FR-031.
- [X] T022 [US1] En `src/cripta/controlador/ExploracionControlador.py` hacer al controlador dueño de `ConocimientoJugador`; en `_ejecutar_movimiento` (línea 204) llamar a `conocimiento.entrar(...)` apenas el jugador cambia de sala, dentro del intervalo del historial; agregar `mapa_conocido()` que arma el `MapaConocido` recorriendo los ids en orden ascendente sin ordenar, sin salas desconocidas y con solo el id de las avistadas. En `src/cripta/controlador/InicioPartidaControlador.py` llamar a `iniciar` tras ensamblar y fijar la sala inicial. El esqueleto completo se conserva solo como infraestructura de precarga de contenido (FR-013): `mapa_conocido()` y la vista NO lo leen. Cita FR-002, FR-013, FR-014, FR-018 y SC-005.
- [X] T023 [US1] En `src/cripta/controlador/ExploracionControlador.py` (método `actualizar_vecindad`, línea 127) aplicar C7 y D15: dejar de copiar `tiene_enemigos` y `tiene_objetos` de las vecinas, mostrar `es_salida_final` solo si la vecina está explorada, y llenar `costo`, `puerta_recordada` y `estado_vecina` de cada `SalidaVecina` desde el conocimiento. Antes, buscar con Grep en `pruebas/` y `src/` cualquier uso de `tiene_enemigos` y `tiene_objetos` de vecinas, y ajustar las pruebas existentes que lo asuman, anotando cada ajuste en el mensaje de la tarea. Cita FR-011, FR-014 y FR-005.
- [X] T024 [US1] En `src/cripta/controlador/Aplicacion.py` agregar `mapa_conocido()` que delega en `ExploracionControlador` sin consumir tiempo ni escribir en `partida.log`. Cita FR-018.
- [X] T025 [US1] En `src/cripta/vista/grafica/escena.py` (método `minimapa`, línea 494; leer solo ese método) dibujar la cruz local desde el conocimiento: estado de la vecina (explorada o avistada), costo de la salida y puerta recordada; nunca salas desconocidas ni contenido. En `src/cripta/vista/grafica/ventana.py` (leerlo primero, C10) agregar el comando `mapa` que lista el mapa conocido completo (exploradas con nombre, salidas, costo y puerta; avistadas con su id). Cita FR-014 y FR-018.
- [X] T026 [US1] Ejecutar `uv run python -m unittest pruebas.test_conocimiento` y la selección del README; deben pasar T013 a T018. Cita FR-001 a FR-006, FR-018.

**Punto de control**: US1 completa y verificable sin vista.

---

## Fase 4: US2 - Recordar el estado de las puertas tal como se observó (P1)

**Meta**: memoria de puertas que se actualiza al observar desde cualquiera de las dos salas y conserva lo último visto.

**Prueba independiente**: `uv run python -m unittest pruebas.test_memoria_puertas`.

### Pruebas de US2 (escribir primero; DEBEN fallar)

- [X] T027 [US2] En `pruebas/test_memoria_puertas.py`, `test_us2_1_cierre_automatico_recordado_abierto`: puerta con cierre automático observada abierta; el jugador se aleja, la puerta cierra y el mapa la sigue mostrando abierta. Docstring cita FR-009.
- [X] T028 [US2] En `pruebas/test_memoria_puertas.py`, `test_us2_2_cambio_en_la_misma_sala`: una puerta de la sala actual cambia durante una acción y `memoria_puerta` refleja el cambio al terminar esa acción. Docstring cita FR-008.
- [X] T029 [US2] En `pruebas/test_memoria_puertas.py`, `test_us2_3_observa_desde_ambas_salas`: la puerta entre A y B se observa estando en A y estando en B, tanto la salida de ida como la entrante. Docstring cita FR-007.
- [X] T030 [US2] En `pruebas/test_memoria_puertas.py`, `test_us2_4_volver_actualiza`: puerta recordada con estado distinto del real; al volver a una de sus dos salas la memoria pasa al estado real. Docstring cita FR-009.
- [X] T031 [US2] En `pruebas/test_memoria_puertas.py`, `test_us2_5_sin_observar_pasa_a_real`: puerta «sin observar» (sala explorada con `explorar` directo) pasa a recordar su estado real al entrar a una de sus dos salas. Docstring cita FR-009a.
- [X] T032 [US2] En `pruebas/test_memoria_puertas.py`, `test_doble_cambio_conserva_el_ultimo` y `test_observar_sin_cambio_no_registra`: una puerta que cambia dos veces en la misma estancia deja el último estado; observar sin cambios no agrega entradas al registro. Docstrings citan FR-008 y FR-037.

### Implementación de US2

- [X] T033 [US2] En `src/cripta/modelo/Conocimiento.py` agregar `observar(sala, historial, tiempo)`: asigna el estado real (`ABIERTA` o `CERRADA`) a las 4 salidas de la sala y a sus entrantes (salidas de otras salas que llegan a ella), costo O(4 + entrantes), solo cambios reales al registro. NO debe llamarse al explorar por antorcha. Inocuo si `inicializado` es falso. Cita FR-007, FR-008, FR-009 y FR-009a.
- [X] T034 [US2] En `src/cripta/controlador/CicloAccionesControlador.py` (método `ejecutar`) llamar a la observación una vez por acción, al final de `consumir_tiempo` y antes de `finalizar`, dentro del intervalo del historial (D4). NO observar desde `usar_pergamino` ni desde `finalizar` fuera de intervalo. Cita FR-008 y FR-016.
- [X] T035 [US2] Ejecutar `uv run python -m unittest pruebas.test_memoria_puertas pruebas.test_conocimiento` y la selección del README; deben pasar. Si una prueba mostrara una diferencia observable con el estado real en el instante del cambio, aplicar el plan B de D4 (gancho por cambio de puerta) solo con acuerdo del equipo. Cita FR-007 a FR-009a.

**Punto de control**: US1 y US2 funcionan; el conocimiento y su memoria están completos.

---

## Fase 5: US3 - Viajar automáticamente con «ir a» (P1)

**Meta**: orden `ir a <sala>` que lleva al jugador por la ruta de menor costo con pasos ordinarios, solo con conocimiento del jugador.

**Prueba independiente**: `uv run python -m unittest pruebas.test_rutas pruebas.test_ir_a`.

### Pruebas de US3 (escribir primero; DEBEN fallar)

- [X] T036 [P] [US3] En `pruebas/test_rutas.py`, `test_us3_2_menor_costo_no_menos_saltos`: dos rutas conocidas, una con menos salas y mayor costo y otra con más salas y menor costo; `elegir_paso` sigue la de menor costo total. Docstring cita FR-023.
- [X] T037 [US3] En `pruebas/test_rutas.py`, `test_us3_3_empate_menor_id`: dos vecinas que inician rutas de igual costo mínimo; el primer paso va hacia la de menor id, y con dos salidas a la misma sala gana el menor costo y luego N, S, E, O. Docstring cita FR-024.
- [X] T038 [US3] En `pruebas/test_rutas.py`, `test_us3_5_costo_por_defecto_100` y `test_solo_exploradas_y_abiertas`: una salida sin costo cuenta 100; no se usan salas no exploradas ni salidas con puerta recordada cerrada o «sin observar»; sin ruta devuelve nada; la reutilización del buscador entre búsquedas no arrastra distancias previas (marca de generación). Docstrings citan FR-022 y FR-023.
- [X] T039 [US3] En `pruebas/test_ir_a.py`, `test_us3_1_apendice_b_sala_no_explorada` (Apéndice B, caso 1): `ir_a` hacia una sala avistada y hacia una desconocida se rechaza, el reloj no cambia, no se escribe en `partida.log` y el mensaje es el mismo en ambos casos. Docstring cita FR-020.
- [X] T040 [US3] En `pruebas/test_ir_a.py`, `test_us3_4_no_abre_puertas_con_llave`: puerta cerrada en la ruta y llave en el inventario; el viaje no la atraviesa ni la abre (y sin otra ruta se rechaza). Docstring cita FR-032.
- [X] T041 [US3] En `pruebas/test_ir_a.py`, `test_us3_6_sala_actual_rechazada` y `test_rechazos_sin_tiempo`: `ir_a` hacia la sala actual, id no entero o fuera de rango, partida no activa y destino explorado sin ruta (incluye puerta recordada cerrada y «sin observar») se rechazan sin consumir tiempo con los mensajes de contracts/comando-ir-a.md. Docstrings citan FR-021, FR-020 y FR-030.
- [X] T042 [US3] En `pruebas/test_ir_a.py`, `test_us3_7_llegada_detiene_viaje`: con `ir_a_completo` hacia una sala explorada lejana el jugador llega por la ruta de menor costo, el reloj avanza en cada paso lo mismo que avanza un movimiento ordinario equivalente (FR-025 enmendado; el costo de la salida como tiempo es de la spec 003) y corrieron los eventos del reloj entre pasos, y la bitácora muestra el motivo `llegada`. Docstring cita FR-025 y FR-027.

### Implementación de US3

- [X] T043 [US3] Crear `src/cripta/modelo/Rutas.py` con `BuscadorRutas` (data-model.md): listas `distancia` y `marca` de tamaño S, `generacion`, un `MonticuloMinimo` reutilizado; `distancias_hacia(destino, entrantes, usable, parar_en)` como Dijkstra inverso con eliminación perezosa y parada al fijar `parar_en`; `elegir_paso(origen, salidas, usable)` que minimiza `costo + distancia[destino]` y desempata por menor id de sala destino y luego índice de dirección (N, S, E, O). Sin `heapq`, `set`, `dict`. El predicado `usable` lo aporta el llamador (D9). Cita FR-022, FR-023 y FR-024.
- [X] T044 [US3] En `src/cripta/modelo/Conocimiento.py` agregar el predicado de uso para rutas: una salida es usable solo si su sala de origen está explorada, su destino está explorado y su memoria de puerta es `ABIERTA`; nunca consulta el estado real de las puertas. Cita FR-014 y FR-022.
- [X] T045 [US3] Crear `src/cripta/controlador/ViajeControlador.py` con `iniciar(destino)` que aplica los rechazos de contracts/comando-ir-a.md en su orden (partida no activa, id inválido, no explorada, sala actual, sin ruta), sin consumir tiempo, y deja el viaje activo si se acepta; y `avanzar()` que recalcula antes de cada paso (FR-026), elige la dirección, fija `en_paso = verdadero` en su propio estado antes de llamar a `Aplicacion.mover(direccion)` (sin agregar parámetros a `mover`), lo baja al volver, y detecta la llegada: si tras el paso el jugador está en el destino, detiene el viaje con motivo `llegada` y escribe su mensaje. Los demás motivos de detención los agrega US4 (T057 a T059). El estado del viaje (`destino`, `activo`, `pasos`, `en_paso`, `motivo`) NO es estado del juego. Escribir los mensajes de la bitácora con categoría `viaje`. Cita FR-019 a FR-021, FR-025 a FR-027 y FR-031.
- [X] T046 [US3] En `src/cripta/controlador/Aplicacion.py` agregar `ir_a(sala_id)`, `avanzar_viaje()`, `cancelar_viaje()` e `ir_a_completo(sala_id)` (repite `avanzar` hasta detenerse), y hacer que `_accion_jugador` (línea 115) consulte la bandera `en_paso` del `ViajeControlador` (fijada por el propio viaje en T045) y cancele el viaje con motivo `cancelado` cuando esa bandera es falsa. Cita FR-019, FR-025 y FR-034.
- [X] T047 [US3] En `src/cripta/vista/grafica/ventana.py` agregar el comando `ir a <sala>` que llama a `Aplicacion.ir_a` y, en cada ciclo de la vista, a `avanzar_viaje` mientras el viaje siga activo, mostrando el mensaje de la bitácora. Cambio mínimo; leer el archivo primero (C10). Cita FR-019 y FR-031.
- [X] T048 [US3] Ejecutar `uv run python -m unittest pruebas.test_rutas pruebas.test_ir_a` (pasan T036 a T042) y la selección del README. Cita FR-019 a FR-027 y FR-032.

**Punto de control**: US3 funciona sin motivos de detención adicionales.

---

## Fase 6: US4 - Detener el viaje ante peligro o falta de ruta (P1)

**Meta**: el viaje se detiene por enemigos vivos, daño, falta de ruta, paso rechazado o fin de la partida, y siempre muestra un motivo.

**Prueba independiente**: `uv run python -m unittest pruebas.test_ir_a`.

### Pruebas de US4 (escribir primero; DEBEN fallar)

- [X] T049 [US4] En `pruebas/test_ir_a.py`, `test_us4_1_apendice_b_puerta_recordada_abierta_cerrada` (Apéndice B, caso 2): el mapa recuerda abierta una puerta de la ruta que en realidad cerró; al llegar a una sala desde la que se observa, el mapa se actualiza y la ruta se recalcula por otra salida. Docstring cita FR-026.
- [X] T050 [US4] En `pruebas/test_ir_a.py`, `test_us4_2_sin_ruta_alternativa_sin_tiempo`: el caso anterior sin ruta alternativa; el viaje se detiene con `sin_ruta` y el reloj no avanza en ese recálculo. Docstring cita FR-030.
- [X] T051 [US4] En `pruebas/test_ir_a.py`, `test_us4_3_apendice_b_enemigos_dormidos` (Apéndice B, caso 3): la ruta entra a una sala con enemigos dormidos; se activan según la Parte I y el viaje se detiene con motivo `enemigos`. Docstring cita FR-028.
- [X] T052 [US4] En `pruebas/test_ir_a.py`, `test_us4_4_enemigos_activos_detienen`: la ruta entra a una sala con enemigos activos; el viaje se detiene con `enemigos`. Docstring cita FR-028.
- [X] T053 [US4] En `pruebas/test_ir_a.py`, `test_us4_5_danio_ataque`, `test_us4_5_danio_trampa` y `test_us4_5_danio_veneno`: un ataque, una trampa y el veneno entre dos pasos detienen el viaje con motivo `danio`; daño calculado 0 por defensa NO detiene (C4). Docstrings citan FR-029.
- [X] T054 [US4] En `pruebas/test_ir_a.py`, `test_us4_6_toda_detencion_muestra_motivo`: para cada código (`llegada`, `enemigos`, `danio`, `sin_ruta`, `movimiento_rechazado`, `partida_terminada`, `cancelado`) la bitácora recibe exactamente un mensaje de categoría `viaje` con el texto de contracts/comando-ir-a.md. Docstring cita FR-031 y SC-007.
- [X] T054a [US4] En `pruebas/test_ir_a.py`, `test_motivo_llega_a_bitacora_sin_ventana`: sin abrir la vista (comprobar que `arcade` no está en `sys.modules` ni se instancia la ventana), un viaje que se detiene por llegada y otro por `sin_ruta` dejan en la bitácora de `Aplicacion` un mensaje de categoría `viaje` con el motivo, y `ResultadoViaje.motivo` y `mensaje` coinciden con él;`mapa_conocido()` devuelve el mapa sin ventana y no agrega mensajes de viaje (FR-018 no le pide escribir en la bitácora), y la orden `ir_a` rechazada deja su mensaje sin ventana. Cubre lo que `ventana.py` solo pinta. Docstring cita FR-031, FR-018 y SC-007.
- [X] T055 [US4] En `pruebas/test_ir_a.py`, `test_derrotados_no_detienen`, `test_prioridad_de_motivos` y `test_movimiento_rechazado_y_partida_terminada`: una sala con solo enemigos derrotados no detiene el viaje; si coinciden motivos se muestra uno según `partida_terminada`, `danio`, `enemigos`, `llegada`; un paso rechazado por `mover` (por ejemplo falta de contenido sin presupuesto) y la victoria o derrota durante el viaje detienen con su motivo. Docstrings citan FR-028 y FR-031a.
- [X] T056 [US4] En `pruebas/test_ir_a.py`, `test_corte_por_cantidad_de_pasos`: un viaje nunca da más pasos que salas exploradas y termina con `sin_ruta` (defensa de C1). Docstring cita FR-030.

### Implementación de US4

- [X] T057 [US4] En `src/cripta/controlador/ExploracionControlador.py` (`_ejecutar_movimiento`, línea 204) fijar una bandera `entrada_con_enemigos` en el instante de la entrada, después de activar a los dormidos según la Parte I, que cuenta solo enemigos vivos (activos o dormidos) y no los derrotados (C5). Cita FR-028.
- [X] T058 [US4] Leer `aplicar_danio` en `src/cripta/modelo/Combate.py` (línea 23) y resolver C4: confirmar si el daño 0 por defensa deja la vida igual. En `src/cripta/controlador/ViajeControlador.py` guardar la vida antes del paso y detener con `danio` si es menor después. Anotar en el mensaje de la tarea si hizo falta otro mecanismo. Cita FR-029.
- [X] T059 [US4] En `src/cripta/controlador/ViajeControlador.py` implementar la decisión de detención tras cada paso con la prioridad `partida_terminada`, `danio`, `enemigos`, `llegada` (C3); `movimiento_rechazado` si `mover` devuelve fallo; `sin_ruta` al recalcular sin paso, sin consumir tiempo; corte a tantos pasos como salas exploradas (C1); y un solo mensaje de motivo en la bitácora con la categoría `viaje` y los textos de contracts/comando-ir-a.md. La detección de `llegada` ya existe desde T045: aquí solo se integra en la prioridad. Cita FR-026, FR-028 a FR-031a.
- [X] T060 [US4] Ejecutar `uv run python -m unittest pruebas.test_ir_a` y la selección del README; deben pasar T049 a T056 (incluida T054a). Cita FR-026 a FR-031a.

**Punto de control**: las cuatro historias P1 funcionan; el viaje es seguro.

---

## Fase 7: US5 - Explorar vecinas con la antorcha (P2)

**Meta**: con la antorcha encendida, entrar a una sala explora a sus vecinas sin activar nada.

**Prueba independiente**: `uv run python -m unittest pruebas.test_conocimiento_antorcha`.

### Pruebas de US5 (escribir primero; DEBEN fallar)

- [X] T061 [US5] En `pruebas/test_conocimiento_antorcha.py`, `test_us5_1_vecinas_exploradas_abiertas_y_cerradas`: antorcha encendida, entrar a una sala explora todas sus vecinas por salidas abiertas o cerradas. Docstring cita FR-010.
- [X] T062 [US5] En `pruebas/test_conocimiento_antorcha.py`, `test_us5_2_apendice_b_antorcha_no_activa_nada` (Apéndice B, caso 4): una vecina con enemigos y trampas queda explorada sin activar sus enemigos ni sus trampas (la agenda no gana eventos y la vida no baja). Docstring cita FR-011.
- [X] T063 [US5] En `pruebas/test_conocimiento_antorcha.py`, `test_us5_3_nombre_y_salidas_sin_contenido`: de la vecina explorada por antorcha el mapa conoce nombre y salidas, no su contenido, y sus puertas quedan «sin observar». Docstring cita FR-011 y FR-009a.
- [X] T064 [US5] En `pruebas/test_conocimiento_antorcha.py`, `test_us5_4_antorcha_apagada_solo_avista`: con la antorcha apagada las vecinas solo quedan avistadas. Docstring cita FR-012.
- [X] T065 [US5] En `pruebas/test_conocimiento_antorcha.py`, `test_us5_5_encender_dentro_no_explora` y `test_antorcha_con_vecinas_ya_exploradas`: encender la antorcha dentro de una sala no explora sus vecinas y sí las de la siguiente sala a la que se entra; con vecinas ya exploradas no se altera lo conocido. Docstrings citan FR-010.

### Implementación de US5

- [X] T066 [US5] En `src/cripta/modelo/Conocimiento.py` completar `entrar`: con la antorcha encendida al momento de entrar, además de `explorar(sala)`, llamar a `explorar` para el destino de cada salida de la sala, abiertas o cerradas (C6: no cuentan salas que solo tengan una salida hacia la actual). `explorar` NO observa puertas ni toca enemigos, trampas ni contenido. Costo O(16). Cita FR-010, FR-011, FR-012 y FR-036.
- [X] T067 [US5] En `src/cripta/controlador/ExploracionControlador.py` pasar a `entrar` el valor de `jugador.antorcha_encendida` tal como estaba antes de entrar (no se relee tras la acción), de modo que `Efectos.encender_antorcha` (`src/cripta/modelo/Efectos.py`, línea 116) no explore vecinas de la sala actual. Verificar que la carga de contenido de una vecina explorada por antorcha NO se dispare para activar enemigos o trampas. Cita FR-010 y FR-011.
- [X] T068 [US5] Ejecutar `uv run python -m unittest pruebas.test_conocimiento_antorcha pruebas.test_conocimiento` y la selección del README; deben pasar. Cita FR-010 a FR-012.

**Punto de control**: US5 completa.

---

## Fase 8: US6 - Conocimiento como parte del estado de la partida (P2)

**Meta**: el conocimiento se revierte, se guarda y se reconstruye.

**Prueba independiente**: `uv run python -m unittest pruebas.test_conocimiento_retroceso pruebas.test_conocimiento_serializable`.

### Pruebas de US6 (escribir primero; DEBEN fallar)

- [X] T069 [US6] En `pruebas/test_conocimiento_retroceso.py`, `test_us6_1_apendice_b_retroceso_entrada_con_antorcha` (Apéndice B, caso 5): entrada con antorcha encendida y pergamino; las salas exploradas por la antorcha, las avistadas y las puertas recordadas vuelven a su estado anterior y el registro se recorta. Docstring cita FR-016 y SC-006.
- [X] T070 [US6] En `pruebas/test_conocimiento_retroceso.py`, `test_us6_2_apendice_b_retroceso_durante_viaje` (Apéndice B, caso 6): con un viaje de varios pasos, el pergamino revierte solo el último paso, el conocimiento vuelve al anterior a ese paso y el viaje no continúa (motivo `cancelado`). Docstring cita FR-034.
- [X] T071 [US6] En `pruebas/test_conocimiento_serializable.py`, `test_us6_3_restaurar_identico`: guardar con `instantanea()` y restaurar en otra instancia produce un `MapaConocido` idéntico; la instantánea mide `5n + 2` y todos sus valores caben de 0 a 2; dos conocimientos iguales dan instantáneas idénticas. Docstring cita FR-015 y SC-005.
- [X] T072 [US6] En `pruebas/test_conocimiento_serializable.py`, `test_us6_4_reconstruir_instante_pasado`: partida con historia; `reconstruir(base, registro, n)` devuelve el mapa conocido exacto de ese instante, sin modificar el conocimiento vivo ni el historial; `reconstruir_hasta_tiempo` coincide en fronteras de acción. Docstring cita FR-017.
- [X] T073 [US6] En `pruebas/test_conocimiento_serializable.py`, `test_restaurar_invalida_y_n_fuera_de_rango`: `restaurar` falla con error de valor si la versión no es 1, `n` no coincide, el largo es incorrecto o un valor está fuera de 0 a 2; `reconstruir` con `n` fuera de `0..len(registro)` falla; `longitud_registro()` es correcta y un retroceso recorta el registro. Docstrings citan FR-015 y FR-017.

### Implementación de US6

- [X] T074 [US6] En `src/cripta/modelo/Conocimiento.py` agregar `instantanea()` (lista de enteros: versión 1, `n`, estados, memoria de salidas), `restaurar(instantanea)` (valida y reemplaza las dos listas completas, vacía el registro, no toca el historial A PROPÓSITO: ocurre al cargar con el historial limpio y no es un cambio de juego reversible; dejarlo escrito en el docstring de `restaurar`), `longitud_registro()`, `reconstruir(instantanea_base, registro, n)` en O(S + n) y `reconstruir_hasta_tiempo(instantanea_base, registro, t)`, según contracts/conocimiento-serializable.md. Cita FR-015 y FR-017.
- [X] T075 [US6] Verificar en `src/cripta/controlador/Aplicacion.py` (`usar_pergamino`, línea 224) y `src/cripta/controlador/GestorPartida.py` que el retroceso restaura estado, memoria y registro por `lista_asignada` y `lista_agregada`, que `usar_pergamino` no escribe conocimiento ni observa, y que cancela el viaje activo con motivo `cancelado`. Verificar también (FR-034a) que iniciar o cargar una partida descarta cualquier viaje activo con motivo `cancelado` y que el viaje no continúa en la nueva partida; si falla, corregirlo y agregar la prueba en `pruebas/test_ir_a.py` citando FR-034a. Corregir lo que T069 y T070 muestren fallando. Cita FR-016, FR-034 y FR-034a.
- [X] T076 [US6] Ejecutar `uv run python -m unittest pruebas.test_conocimiento_retroceso pruebas.test_conocimiento_serializable pruebas.test_retroceso` y la selección del README; deben pasar. Cita FR-015 a FR-017 y FR-034.
- [X] T076a [US6] Implementar y probar el valor por defecto de FR-015 al cargar un guardado sin conocimiento: en `src/cripta/controlador/GuardadoControlador.py` (`cargar`), tras `restaurar_partida`, rehacer el conocimiento con `iniciar_conocimiento(sala_actual_id)`; en `pruebas/test_conocimiento_serializable.py`, `test_fr015_carga_sin_conocimiento_parte_de_la_sala_actual`: tras guardar lejos de la sala inicial y cargar, la sala actual queda explorada con sus puertas observadas (incluida una cerrada), los destinos de sus salidas avistados, el resto desconocido y el registro vacío. No modifica el formato binario ni `src/cripta/controlador/guardado/`. Cita FR-015.

**Punto de control**: US6 completa; la spec 004 puede consumir la interfaz serializable.

---

## Fase 9: US7 - Registro de la partida y reproducción (P2)

**Meta**: cada paso queda como `mover` y la orden como comentario que el reproductor ignora.

**Prueba independiente**: `uv run python -m unittest pruebas.test_registro_ir_a`.

### Pruebas de US7 (escribir primero; DEBEN fallar)

- [X] T077 [US7] En `pruebas/test_registro_ir_a.py`, `test_us7_1_pasos_individuales_y_comentario`: un viaje de varios pasos deja `# ir_a <sala>` antes del primer paso y un `["mover", "<dirección>"]` por paso; una orden rechazada no escribe nada. Docstring cita FR-033.
- [X] T078 [US7] En `pruebas/test_registro_ir_a.py`, `test_us7_2_reproduccion_ignora_comentarios`: reproducir el registro llega al mismo mapa conocido y al mismo estado final que la partida original, con y sin los comentarios. Docstring cita FR-033 y SC-005.
- [X] T079 [US7] En `pruebas/test_registro_ir_a.py`, `test_comentar_y_lector`: `RegistroPartida.comentar` antepone `# ` y reemplaza saltos de línea por un espacio; `leer_partida` omite líneas que empiezan por `#` (con espacios iniciales) y el número de línea de los errores las cuenta; una línea vacía o inválida sigue siendo error; un comentario manual `# FR-028 escenario: ...` se ignora. Docstrings citan FR-033.

### Implementación de US7

- [X] T080 [US7] En `src/cripta/replay/reproductor.py` agregar `RegistroPartida.comentar(texto)` con las reglas de contracts/registro-partida.md (mismo error que `anexar` ante fallos) y hacer que `leer_partida` (línea 71) omita las líneas de comentario contando su número de línea. NO agregar la acción `ir_a` a `_validar_accion`. Cita FR-033.
- [X] T081 [US7] En `src/cripta/controlador/PartidaControlador.py` agregar `registrar_comentario(texto)` que delega en `RegistroPartida.comentar`, y en `src/cripta/controlador/ViajeControlador.py` escribir `# ir_a <sala>` una sola vez por orden aceptada, antes del primer paso y nunca en un rechazo. Cita FR-033.
- [X] T082 [US7] Ejecutar `uv run python -m unittest pruebas.test_registro_ir_a pruebas.test_replay` y la selección del README; deben pasar. Cita FR-033.

**Punto de control**: US7 completa; las partidas con viaje son reproducibles.

---

## Fase 10: US8 - Medir el rendimiento de las consultas y de «ir a» (P3)

**Meta**: sección de conocimiento en `--bench` con K1 a K9, determinista por semilla y sin abrir la vista.

**Prueba independiente**: `uv run python -m cripta --bench --semilla 42` dos veces.

### Pruebas de US8 (escribir primero; DEBEN fallar)

- [X] T083 [P] [US8] En `pruebas/test_bench_conocimiento.py`, `test_us8_1_mide_consultas_e_ir_a`: la función de medición devuelve y el texto impreso contiene tiempos de las consultas al mapa conocido y del cálculo de un paso de `ir_a`. Docstring cita FR-039.
- [X] T084 [US8] En `pruebas/test_bench_conocimiento.py`, `test_us8_2_paso_menor_5ms_cripta_referencia`: con el mapa conocido completo de la cripta de referencia (el mayor esqueleto de `datos_offline`, tamaño leído del paquete, sin copiar ids; si no hay paquete, una cripta sintética de 2 000 salas) el máximo de un paso de `ir_a` es menor que 5 ms (mejor de 3 corridas con `time.perf_counter`). Docstring cita FR-038 y SC-003.
- [X] T085 [US8] En `pruebas/test_bench_conocimiento.py`, `test_us8_3_consulta_no_crece_con_el_mapa`: con 200, 2 000 y 20 000 salas el costo por consulta de estado de sala y de puerta recordada con 10 veces el tamaño es a lo sumo 1,5 veces; el de explorar por sala revelada tiene una razón a lo sumo 1,5 (el mismo umbral de K1 y K2); el registro y la inversión crecen en proporción a los cambios. Se compara por conteo de operaciones donde sea posible para no depender de la máquina. Docstring cita FR-035, FR-036, FR-037 y SC-004.
- [X] T086 [US8] En `pruebas/test_bench_conocimiento.py`, `test_misma_semilla_mismos_resultados` y `test_bench_no_abre_vista`: dos generaciones con la misma semilla son idénticas y semillas distintas difieren; semilla vacía equivale a 42; `--bench` en un subproceso limpio (`sys.executable -I -m cripta --bench --semilla 42`) no importa `arcade` ni instancia la vista. Docstrings citan FR-039, FR-040 y SC-008.

### Implementación de US8

- [X] T087 [US8] Usar el `--semilla` de `src/cripta/bootstrap.py` y `bench.main` implementado por la spec 001 (C9): vacía equivale a 42, nunca aleatoria. La spec 001 se implementa antes en esta misma rama, así que NO se implementa aquí una versión mínima ni se duplica su generador; solo se comprueba que `--bench --semilla N` llega a las secciones de esta capacidad. Cita FR-039 y FR-040.
- [X] T088 [US8] En `src/cripta/bench.py` agregar el generador sintético determinista de criptas con conocimiento (`random.Random(semilla)`): cuadrículas con salidas dirigidas, puertas cerradas declaradas en un solo lado, costos variados y algunos sin declarar, ids secuenciales, tamaños 200, 2 000 y 20 000 salas, más la elección de la cripta de referencia como el mayor esqueleto del paquete con el mismo criterio de 001. Cita FR-039 y FR-041.
- [X] T089 [US8] En `src/cripta/bench.py`, medición K1: consulta de estado de sala y de puerta recordada con listas indexadas frente a búsqueda lineal en una lista de ids explorados, a 200, 2 000 y 20 000 salas; criterio: razón a lo sumo 1,5 con 10 veces el tamaño y la alternativa lineal crece. Cita FR-035 y SC-004.
- [X] T090 [US8] En `src/cripta/bench.py`, medición K2: explorar salas nuevas con y sin antorcha, costo por sala revelada a los tres tamaños; criterio: razón a lo sumo 1,5. Cita FR-036 y SC-004.
- [X] T091 [US8] En `src/cripta/bench.py`, medición K3: registrar e invertir con `lista_asignada` frente a copiar el conocimiento completo en cada acción, con 10 y 1 000 cambios; criterio: lineal en los cambios, la copia crece con el mapa. Cita FR-037.
- [X] T092 [US8] En `src/cripta/bench.py`, medición K4: un paso de `ir_a` con el mapa conocido completo de la cripta de referencia sobre pares origen y destino elegidos por semilla; imprimir el máximo y marcar si es menor que 5 ms. Cita FR-038 y SC-003.
- [X] T093 [US8] En `src/cripta/bench.py`, medición K5: un paso de `ir_a` a 2 000 y 20 000 salas exploradas, informativa, con crecimiento acorde a O((V + E) log V). Cita FR-038.
- [X] T094 [US8] En `src/cripta/bench.py`, medición K6: Dijkstra inverso con parada anticipada frente al completo, frente a Dijkstra desde el origen y frente a reutilizar distancias entre pasos; regla: se conserva el inverso con parada salvo que otra alternativa gane por más de 2 veces. Cita FR-024 y FR-038.
- [X] T095 [US8] En `src/cripta/bench.py`, medición K7: `MonticuloMinimo` con eliminación perezosa frente a decremento de clave con índice y frente a selección lineal del mínimo (O(V²)); regla: se conserva el perezoso salvo que el indexado gane por más de 2 veces. Cita FR-038.
- [X] T096 [US8] En `src/cripta/bench.py`, medición K8: búsqueda por costo con montículo frente a BFS con la cola de la spec 001 (`ColaLista`, válida solo con costos iguales); en la variante con costos variados BFS DEBE devolver rutas de mayor costo. Cita FR-023.
- [X] T097 [US8] En `src/cripta/bench.py`, medición K9: ejecutar K4 y K6 dos veces con la misma semilla y comprobar salida idéntica en los resultados (los tiempos pueden variar), sin abrir ventana. Cita FR-039, FR-040, SC-005 y SC-008.
- [X] T098 [US8] Ejecutar `uv run python -m unittest pruebas.test_bench_conocimiento` y `uv run python -m cripta --bench --semilla 42` dos veces; los resultados deterministas deben coincidir y los tiempos K1 a K9 deben imprimirse. Guardar la salida en `specs/002-niebla-ir-a/mediciones.txt` para la sección de decisiones. Cita FR-038, FR-039 y FR-040.

**Punto de control**: las ocho historias completas, con evidencia medida.

---

## Fase 11: Cierre y transversales

- [X] T099 Redactar en `docs/decisiones.md` la sección «13. Niebla de guerra e ir a (Parte II, §3.3, §3.4 y §5.3)» (el DECISIONES de este problema; usar el siguiente número libre tras la sección 12 de resolubilidad de la spec 001, y renumerar si 001 aún no la agregó), con el mismo estilo de las secciones 1 y 2: estados de sala y memoria de puertas en listas planas (D1, D2), entrantes (D3), observación al final de la acción frente al gancho por cambio (D4), tipo `lista_asignada` frente a copia completa (D5), costo y su normalización (D6), Dijkstra inverso con parada anticipada y alternativas descartadas (BFS, Dijkstra desde el origen, reutilizar distancias, Floyd-Warshall, A*) con su costo (D7), montículo propio frente a reutilizar la agenda (D8), qué se comparte con el cazador (D9, §5.3), viaje por pasos y registro como comentario (D10, D11), fugas de información corregidas (D15), complejidad de cada operación y la comparación medida con los números de `specs/002-niebla-ir-a/mediciones.txt` (K1 a K9). Cita FR-023, FR-035, FR-037, FR-038 y FR-039.
- [X] T100 [P] Actualizar `docs/estructuras.md` con `MonticuloMinimo`, `ConocimientoJugador` y `BuscadorRutas` (operaciones y costo según data-model.md) y el tipo `lista_asignada` del historial. Cita FR-035, FR-037 y FR-038.
- [X] T101 [P] Actualizar `README.md`: comandos `mapa` e `ir a <sala>`, el comentario `# ir_a` del registro y su reproducción, la opción `--semilla` para `--bench` de esta capacidad y el enlace a la nueva sección de `docs/decisiones.md`. Cita FR-018, FR-019 y FR-033.
- [X] T102 Revisar los archivos nuevos y modificados de esta capacidad contra el principio I y IV: ninguna búsqueda de `heapq`, `bisect`, `collections`, `sorted(` ni `.sort(`, ningún `dict` ni `set` como índice, ningún id de sala ni de cripta escrito en el código. Revisar además (FR-013) que el esqueleto completo de la cripta solo lo use la precarga de contenido: ni la vista (`escena.py`, `ventana.py`), ni `mapa_conocido()`, ni `ViajeControlador`, ni `BuscadorRutas` lo leen, y todo lo que muestran o usan deriva del conocimiento (FR-014). Corregir lo que aparezca. Cita FR-013, FR-014, FR-041 y FR-035.
- [X] T103 Ejecutar los 17 escenarios de punta a punta de `specs/002-niebla-ir-a/quickstart.md` en orden y anotar el resultado de cada uno al final de ese archivo bajo «Resultado de la validación»; incluir la sección 3 (registro y reproducción) y la sección 4 (rendimiento). Cita FR-001 a FR-041 y SC-001 a SC-008.
- [X] T104 Regresión contra la línea base de la spec 001: ejecutar de nuevo los comandos (a) selección del README y (b) suite completa registrados en `specs/001-resolubilidad/linea_base.txt` (NO crear otra línea base). La selección del README DEBE pasar y la suite completa de `pruebas/` NO DEBE tener fallas nuevas respecto de esa línea base; comparar nombre por nombre las pruebas que fallan y registrar el resultado en `specs/002-niebla-ir-a/regresion.txt`. Una falla de la línea base que persiste no cuenta como nueva. Si 001 agregó pruebas posteriores a la línea base, aparecen como pruebas nuevas, no como fallas. Protege FR-014, FR-016, FR-033 y FR-041.

---

## Dependencias y orden de ejecución

- **Fase 1 (T001)** antes de todo. Ningún cambio de código antes de confirmar la línea base de la spec 001.
- **Fase 2** depende de T001 y bloquea las historias. Dentro de ella: T002 antes de T003; T004 antes de T005; T006 antes de T007; T007 antes de T008 y T010; T009 antes de T010; T011 puede ir en cualquier momento antes de las pruebas de US1; T012 al final.
- **US1** (T013 a T026) depende de la Fase 2 completa. Es el MVP.
- **US2** depende de US1 (mismo `Conocimiento.py`, necesita `explorar` y `entrar`). **US3** depende de US2 (necesita memoria de puertas para el predicado). **US4** depende de US3 (mismo `ViajeControlador.py`).
- **US5** depende de US1 y es independiente de US3 y US4, pero toca `Conocimiento.py` (T066 después de T033) y `ExploracionControlador.py` (T067 después de T057). **US6** depende de US5 (T069 usa la antorcha) y de US3 (T070 usa el viaje). **US7** depende de US3 y de US4 (comentario antes del primer paso, reglas de rechazo). **US8** depende de US3 (mide `ir_a`) y de US5 (K2 con antorcha); T087 depende de la spec 001, que se implementa antes en esta misma rama (`--semilla` y criterio de cripta de referencia).
- **Fase 11** al final; T104 es la última tarea y T099 va después de T098 para citar las mediciones.

### Oportunidades de paralelismo

- Fase 2: T004, T006, T009 y T011 en paralelo (archivos distintos); luego T005, T007 y T010.
- US3: T036 es [P] con las pruebas de `test_ir_a.py` (T039 a T042 son secuenciales entre sí por ser el mismo archivo).
- US8: T083 es [P] con T084 a T086 solo en el sentido de escribir primero las pruebas; las mediciones K1 a K9 comparten `bench.py` y NO son paralelas.
- Archivos de prueba distintos entre historias (`test_conocimiento.py`, `test_memoria_puertas.py`, `test_rutas.py`, `test_ir_a.py`, `test_conocimiento_antorcha.py`, `test_conocimiento_retroceso.py`, `test_conocimiento_serializable.py`, `test_registro_ir_a.py`, `test_bench_conocimiento.py`) pueden escribirse a la vez.
- T100 y T101 en paralelo.
- Las tareas que editan el mismo archivo (`Conocimiento.py`, `ExploracionControlador.py`, `ViajeControlador.py`, `ventana.py`, `bench.py`, `Aplicacion.py`) NO son paralelas.

## Estrategia de implementación

1. **MVP**: Fases 1 y 2 y US1. Con eso el jugador ve solo lo que conoce y el mapa se puede probar sin vista.
2. **Incremento 2**: US2, US3 y US4 completan las historias P1: memoria de puertas, viaje automático y detenciones seguras.
3. **Incremento 3**: US5, US6 y US7 agregan antorcha, retroceso y guardado del conocimiento, y el registro con reproducción.
4. **Incremento 4**: US8 da la evidencia medida. Cerrar con T099 a T104. No marcar una historia como terminada sin que sus pruebas pasen y sin que la selección del README siga en verde.

## Cobertura de escenarios de aceptación

| Escenario | Prueba | FR |
|-----------|--------|----|
| US1.1 a US1.5 | T013 a T017 | FR-002, FR-003, FR-004, FR-005, FR-006, FR-009a, FR-018 |
| US2.1 a US2.5 | T027 a T031 | FR-007, FR-008, FR-009, FR-009a |
| US3.1 a US3.7 | T039, T036, T037, T040, T038, T041, T042 | FR-020, FR-023, FR-024, FR-032, FR-021, FR-027 |
| US4.1 a US4.6 | T049 a T054, T054a | FR-026, FR-030, FR-028, FR-029, FR-031 |
| FR-013 (esqueleto solo como infraestructura) | T022, T102 | FR-013, FR-014 |
| US5.1 a US5.5 | T061 a T065 | FR-010, FR-011, FR-012 |
| US6.1 a US6.4 | T069, T070, T071, T072 | FR-016, FR-034, FR-015, FR-017 |
| US7.1 y US7.2 | T077, T078 | FR-033 |
| US8.1 a US8.3 | T083, T084, T085 | FR-039, FR-038, FR-035 a FR-037 |
| Apéndice B 1 a 6 (SC-001) | T039, T049, T051, T062, T069, T070 | FR-020, FR-026, FR-028, FR-011, FR-016, FR-034 |

## Fase 12: US9 - Oscuridad de la sala y radio de la antorcha (aclaración del 2026-11-17)

La spec se enmendó antes del código (commits d51a621 y fefafff).

- [X] T105 [US9] `pruebas/test_oscuridad.py`: radio mínimo y al menos el triple con antorcha (FR-042, FR-043); área visible sin antorcha menor que 1/5 y con antorcha al menos 1/2, y niebla por debajo del 85 % de opacidad (SC-009); dibujar no cambia reloj, azar ni historial y al apagar la antorcha vuelve el radio mínimo (FR-044).
- [X] T106 [US9] `src/cripta/vista/grafica/escena.py`: capa `oscuridad` entre las entidades y los paneles, con máscara RGBA de anillos concéntricos centrada en el jugador y caché acotada de máscaras; el inventario, la bitácora, la barra inferior y el minimapa no se cubren (FR-042, FR-043, FR-045).
- [X] T107 [US9] Verificar en la ventana real, sin antorcha y con antorcha, en una sala con enemigos lejos del jugador, y anotar el resultado en `quickstart.md` (FR-042 a FR-045).
