# Tareas: Terreno con costo y enemigo cazador

**Entrada**: `specs/003-terreno-cazador/` (spec.md, plan.md, research.md, data-model.md, contracts/, quickstart.md)

**Requisitos previos**: plan.md y spec.md. Las decisiones D1 a D12 de research.md y las «Decisiones tomadas» del plan son definitivas. Los puntos C1 a C5 del plan se resuelven dentro de las tareas que los citan.

**Pruebas**: solicitadas de forma explícita. Hay una prueba `unittest` en `pruebas/` por cada escenario de aceptación, incluidos los 7 del Apéndice B (SC-001), y cada prueba cita su FR en el docstring. Las pruebas de cada historia se escriben antes de la implementación y DEBEN fallar primero.

**Organización**: por historia de usuario (US1 a US6) para implementar y probar cada una por separado.

## Formato: `[ID] [P?] [Historia] Descripción con ruta`

- **[P]**: se puede hacer en paralelo (archivos distintos, sin dependencia de tareas incompletas).
- **[USn]**: historia de usuario de spec.md.
- Cada tarea cita al menos un FR. Las tareas de soporte citan los FR que protegen.
- Rutas desde la raíz del repositorio. Comandos para Windows con CMD y `uv run`.

## Reglas transversales (constitución)

- Sin `dict`, `set`, `heapq`, `bisect`, `collections`, `networkx`, `sorted()` ni `list.sort()` en el código de esta capacidad (principio I). `dict` solo donde ya existe (lectura del JSON y `FichaEnemigo(**d)`).
- Ninguna cola de prioridad nueva: toda búsqueda usa `MonticuloMinimo` y `BuscadorRutas` (D5).
- El modelo (`modelo/Persecucion.py`, `modelo/enemigos/Cazador.py`, `modelo/Rutas.py`) NO conoce HTTP, archivos, vista ni el conocimiento del jugador (principio III, FR-015). `--bench` y `--replay` NO instancian la vista.
- Ningún dato de una cripta concreta en código ni en pruebas (FR-028, principio IV): cada prueba arma su esqueleto y sus fichas.
- Docstring de cada prueba: `"""FR-0xx: ..."""` con el escenario que cubre; las del Apéndice B dicen además `Apéndice B, caso n`.
- Texto en español y sin guiones largos, en código, docstrings y documentación.

---

## Fase 1: Preparación

**Propósito**: spec confirmada, línea base y partida de regresión antes de tocar código.

- [x] T001 Confirmar en Git `specs/003-terreno-cazador/spec.md` y `specs/003-terreno-cazador/checklists/requirements.md` en un commit propio (por ejemplo `docs(003): spec de terreno y cazador`), antes de cualquier commit de código (principio VII, punto C5). Confirmar en otro commit `plan.md`, `research.md`, `data-model.md`, `quickstart.md`, `contracts/` y este `tasks.md`. Cita FR-001 a FR-028.
- [x] T002 Resolver C1 con el equipo. Si se acepta, corregir en `specs/003-terreno-cazador/spec.md` FR-009 y el caso límite del rango para que digan que la ficha se rechaza al incorporarse y que, si ocurre durante la partida, falla el movimiento que necesitaba ese contenido; confirmar la corrección en un commit separado antes de T048. Si no se acepta, anotar en el plan cómo se cumple la redacción actual. Cita FR-009.
- [x] T003 Con el código sin modificar, ejecutar (a) la selección de pruebas del README y (b) `uv run python -m unittest discover -s pruebas`, y registrar en `specs/003-terreno-cazador/linea_base.txt` los dos comandos, el hash del commit y los nombres de las pruebas que ya fallan. Confirmarlo en Git. Protege FR-005 y FR-022.
- [x] T004 Con el código sin modificar, jugar una partida corta y determinista (semilla fija, una cripta de `datos_offline`, que no declara costos) en la que actúen errantes y rastreadores, copiar su registro a `specs/003-terreno-cazador/regresion_partida.log` y anotar en `specs/003-terreno-cazador/regresion_estado.txt` el estado final tras `--replay` (reloj, sala y vida del jugador, sala y vida de cada enemigo). Sirve para comprobar que D2 no cambia el consumo del azar. Cita FR-005 y FR-022.

**Punto de control**: spec confirmada, línea base y partida de regresión guardadas antes de T005.

---

## Fase 2: Fundamentos (bloquean todas las historias)

**Propósito**: corte por costo en la búsqueda existente, contadores de invalidación y apoyo de pruebas.

**CRÍTICO**: ninguna historia empieza hasta terminar esta fase.

- [x] T005 [P] Crear `pruebas/apoyo_cazador.py` (puede importar de `pruebas/apoyo_niebla.py`): (1) armar un modelo puro sin `Aplicacion` a partir de una descripción de salas, salidas con costo y puertas cerradas: `IndiceSalas`, `entrantes` (misma construcción que `ExploracionControlador.ensamblar_salas`, con `clave = origen * 4 + dirección`), `Simulacion` con semilla y un `Jugador`; (2) crear enemigos de cualquier comportamiento con velocidad y rango dados y activarlos; (3) armar una `Aplicacion` con una fuente falsa cuyo contenido incluya fichas de enemigo con `comportamiento` y `rango`; (4) `decision_desde_cero(salas, entrantes, sala_cazador, sala_jugador, rango)` que calcula la decisión con un `BuscadorRutas` nuevo, sin `limite` y sin caché, para comparar (FR-017). Sin ids ni datos de cripta reales. Cita FR-017 y FR-028.
- [x] T006 [P] En `pruebas/test_rutas.py` agregar: `test_limite_nada_igual_que_antes` (con `limite` omitido las distancias son las mismas que hoy), `test_limite_corta_busqueda` (con límite L ninguna sala con distancia real mayor que L queda fijada) y `test_limite_invariante` (500 cuadrículas generadas con `random.Random(semilla)` y límites al azar: toda sala con distancia completa ≤ L tiene la misma `distancia_de`, y toda otra sala da nada o un valor mayor que L). Docstrings citan FR-017 y FR-025. DEBEN fallar antes de T007.
- [x] T007 En `src/cripta/modelo/Rutas.py` agregar a `BuscadorRutas.distancias_hacia` el parámetro final opcional `limite: int | None = None` con la regla verbatim de data-model.md: «Termina al extraer una entrada vigente con prioridad > `limite`; con nada, idéntico al actual («ir a» no cambia)». Actualizar el docstring del módulo con la complejidad O((V_R + A_R) log V_R) con corte. NO tocar `elegir_paso` ni `MonticuloMinimo`. Cita FR-017 y FR-025.
- [x] T008 [P] Escribir `pruebas/test_contadores.py`: `agenda.cambios_puertas` empieza en 0 y sube en 1 con `Puertas.abrir_salida` y con `Puertas.procesar_cierre_puerta`; NO baja al revertir el intervalo con el historial; `historial.reversiones` empieza en 0 y sube en 1 con `revertir_abierto` y con `deshacer`; una agenda sin historial sigue cambiando atributos. Docstrings citan FR-017 y FR-024. DEBEN fallar antes de T009 a T011.
- [x] T009 En `src/cripta/estructuras/Agenda_Eventos.py` agregar a `HeapAgendaEventos.__init__` el entero `self.cambios_puertas = 0`, con la regla de data-model.md: «Monótono; lo suben `abrir_salida` y `procesar_cierre_puerta`; no pasa por el historial». Cita FR-017.
- [x] T010 En `src/cripta/modelo/Puertas.py` sumar 1 a `agenda.cambios_puertas` en `abrir_salida` y en `procesar_cierre_puerta`, con asignación directa (no con `agenda.cambiar`). Depende de T009. Cita FR-011 y FR-017.
- [x] T011 En `src/cripta/estructuras/Historial_Retroceso.py` agregar el entero monótono `reversiones` (0 al crear; `limpiar` NO lo reinicia) y sumarle 1 en `revertir_abierto` y en `deshacer` cuando revierten al menos un intervalo. Cita FR-017 y FR-024.
- [x] T012 Ejecutar `uv run python -m unittest pruebas.test_rutas pruebas.test_ir_a pruebas.test_contadores pruebas.test_retroceso` y la selección del README; comparar con `specs/003-terreno-cazador/linea_base.txt`. Protege FR-007 y FR-017.

**Punto de control**: `limite` y contadores listos; «ir a» sin cambios.

---

## Fase 3: US1 - El movimiento consume el costo de la salida (P1) 🎯 MVP

**Meta**: jugador y enemigos pagan el costo de la salida al moverse; el resto de las acciones conserva su costo.

**Prueba independiente**: `uv run python -m unittest pruebas.test_costo_movimiento pruebas.test_decision_enemigo`.

### Pruebas de US1 (escribir primero; DEBEN fallar)

- [x] T013 [US1] En `pruebas/test_costo_movimiento.py`, `test_us1_1_sin_costo_vale_100`: salida sin costo declarado y jugador de velocidad 100; tras `mover`, el siguiente turno del jugador es 100 después. Docstring cita FR-001, FR-003 y FR-004.
- [x] T014 [US1] En `pruebas/test_costo_movimiento.py`, `test_us1_2_costo_250`: salida de costo 250 y velocidad 100; el siguiente turno es 250 después. Docstring cita FR-003 y FR-004.
- [x] T015 [US1] En `pruebas/test_costo_movimiento.py`, `test_apendice_b_6_velocidad_alta_costo_1`: jugador de velocidad 1000 por una salida de costo 1; el intervalo es exactamente 1, nunca 0; repetir con un enemigo errante de velocidad 1000. Docstring: «FR-004: Apéndice B, caso 6».
- [x] T016 [US1] En `pruebas/test_costo_movimiento.py`, `test_apendice_b_7_cambio_velocidad_con_movimiento_costoso`: el jugador atraviesa una salida de costo 300 con velocidad 100 (turno pendiente en t + 300); a mitad del intervalo cambia su velocidad a 200 con `actualizar_velocidad` y el turno pasa a `t_cambio + max(1, restante * 100 // 200)`; repetir con un cambio a velocidad 1 y con un enemigo que acaba de moverse por una salida costosa. Docstring: «FR-006: Apéndice B, caso 7».
- [x] T017 [US1] En `pruebas/test_costo_movimiento.py`, `test_us1_5_otras_acciones_no_cambian`: en una sala cuyas salidas cuestan 1 y 250, esperar cuesta 100, atacar 100, usar un objeto 50 y abrir una puerta 50, igual que en la Parte I. Docstring cita FR-005.
- [x] T018 [US1] En `pruebas/test_costo_movimiento.py`, `test_us1_6_mismo_costo_en_ambos_sentidos`: una conexión de costo 70 cuesta 70 de A a B y de B a A. Docstring cita FR-001.
- [x] T019 [US1] En `pruebas/test_costo_movimiento.py`, `test_us1_7_enemigos_pagan_el_costo`: un errante (con una sola salida abierta) y un rastreador que se mueven por una salida de costo 180 con velocidad 120 reprograman su turno a `t + max(1, 180 * 100 // 120)`. Docstring cita FR-003 y FR-004.
- [x] T020 [US1] En `pruebas/test_costo_movimiento.py`, `test_ir_a_consume_costo_de_cada_paso`: un viaje de «ir a» por salidas de costo 40 y 160 avanza el reloj 40 y luego 160 con velocidad 100. Docstring cita FR-007.
- [x] T021 [P] [US1] Escribir `pruebas/test_decision_enemigo.py` según `contracts/decision-enemigo.md`: guardián, errante y rastreador devuelven `[tipo, destino, costo]`; con `mover` el costo es el de la salida elegida (entero ≥ 1) y con `atacar` o `esperar` destino y costo son nada; con la misma semilla el errante elige el mismo destino que el algoritmo actual (copiado en la prueba: `azar.choice` sobre los destinos abiertos) y deja `azar.getstate()` igual. Docstrings citan FR-003 y FR-022.

### Implementación de US1

- [x] T022 [US1] En `src/cripta/controlador/CicloAccionesControlador.py` agregar el parámetro final opcional `costo=None` a `ejecutar` y a `consumir_tiempo`; en `consumir_tiempo` el intervalo es `calcular_intervalo(costo if costo is not None else costo_accion(nombre_costo), velocidad)`. Cita FR-003, FR-004 y FR-005.
- [x] T023 [US1] En `src/cripta/controlador/Aplicacion.py` agregar `costo=None` a `_accion_jugador` y pasarlo a `self._ciclo.ejecutar`. Depende de T022. Cita FR-003.
- [x] T024 [US1] En `src/cripta/controlador/ExploracionControlador.py`, método `mover`, pasar `costo=salida.costo` a `app._accion_jugador` con la salida obtenida antes de mover (D1). Depende de T023. Cita FR-003 y FR-007.
- [x] T025 [US1] En `src/cripta/modelo/Enemigo.py` hacer que `decidir_accion` devuelva `["atacar", None, None]` al compartir sala y documentar en el docstring el formato `[tipo, destino, costo]` de `contracts/decision-enemigo.md`. Cita FR-003 y FR-010.
- [x] T026 [P] [US1] En `src/cripta/modelo/enemigos/Guardian.py` devolver `["esperar", None, None]`. Depende de T025. Cita FR-005.
- [x] T027 [P] [US1] En `src/cripta/modelo/enemigos/Errante.py` armar la lista de salidas abiertas (mismo orden y cantidad que la lista actual de destinos), elegir con `azar.choice` sobre esa lista y devolver `["mover", salida.sala_destino, salida.costo]`, o `["esperar", None, None]`. Depende de T025. Cita FR-003 y FR-022.
- [x] T028 [P] [US1] En `src/cripta/modelo/enemigos/Rastreador.py` guardar la salida en cada candidato y devolver el costo de la salida del candidato elegido, sin cambiar qué candidato se elige (punto C3: misma salida que hoy, orden de las salidas en la sala). Depende de T025. Cita FR-003 y FR-022.
- [x] T029 [US1] En `src/cripta/modelo/Simulacion.py`, `_ejecutar_turno_enemigo`, desempacar `[tipo, destino, costo]`; si `tipo == "mover"` usar `costo` en `calcular_intervalo` y lanzar `ValueError` si es nada; si no, `costo_accion(tipo)`. Depende de T025 a T028. Cita FR-003, FR-004 y FR-005.
- [x] T030 [US1] Buscar con Grep los demás usos de `decidir_accion` (por ejemplo `src/cripta/bench.py` en `_bench_decidir_accion` y `pruebas/prueba_enemigo.py`) y adaptarlos al formato de tres elementos. Cita FR-022.
- [x] T031 [US1] Reproducir `specs/003-terreno-cazador/regresion_partida.log` con `--replay` y comprobar que el estado final coincide con `specs/003-terreno-cazador/regresion_estado.txt`; ejecutar `pruebas.test_costo_movimiento`, `pruebas.test_decision_enemigo`, `pruebas.test_ir_a` y la selección del README. Protege FR-005 y FR-022.

**Punto de control**: US1 completa; el reloj refleja el terreno para todos los actores.

---

## Fase 4: US2 - El cazador persigue al jugador por la ruta más barata (P1)

**Meta**: comportamiento cazador con rango, búsqueda compartida cortada por rango y reutilizada mientras nada relevante cambie.

**Prueba independiente**: `uv run python -m unittest pruebas.test_cazador pruebas.test_persecucion pruebas.test_ficha_cazador`.

### Pruebas de US2 (escribir primero; DEBEN fallar)

- [x] T032 [US2] En `pruebas/test_cazador.py`, `test_apendice_b_1_sin_ruta_abierta_espera`: toda ruta de la sala del cazador a la del jugador pasa por una puerta cerrada; en su turno espera y su siguiente turno es `t + max(1, 100 * 100 // velocidad)`. Docstring: «FR-011, FR-012: Apéndice B, caso 1».
- [x] T033 [US2] En `pruebas/test_cazador.py`, `test_apendice_b_2_ruta_mayor_que_rango_espera`: la ruta abierta más barata cuesta 301 y el rango es 300; espera con costo 100 y no cambia de sala. Docstring: «FR-012: Apéndice B, caso 2».
- [x] T034 [US2] En `pruebas/test_cazador.py`, `test_apendice_b_3_menor_costo_no_menos_salas`: una ruta de 1 salida de costo 500 frente a otra de 3 salidas de costo 50 cada una; el cazador da el paso por la de costo total 150. Docstring: «FR-011, FR-013: Apéndice B, caso 3».
- [x] T035 [US2] En `pruebas/test_cazador.py`, `test_apendice_b_4_empate_menor_id`: dos vecinas con id 7 y 4 inician rutas del mismo costo mínimo (la de id 7 en la dirección N); el cazador va a la sala 4. Docstring: «FR-014: Apéndice B, caso 4».
- [x] T036 [US2] Escribir `pruebas/test_cazador_puertas.py`, `test_apendice_b_5_puerta_se_cierra_entre_turnos`: el cazador da un paso por una ruta; antes de su turno siguiente una puerta de esa ruta se cierra con `procesar_cierre_puerta`; su decisión es igual a `decision_desde_cero` con el estado de ese instante (otra ruta o espera); repetir reabriendo la puerta con `abrir_salida`. Docstring: «FR-017, FR-011: Apéndice B, caso 5».
- [x] T037 [US2] En `pruebas/test_cazador.py`, `test_us2_6_misma_sala_ataca`: el cazador comparte sala con el jugador y ataca con costo 100. Docstring cita FR-010.
- [x] T038 [US2] En `pruebas/test_cazador.py`, `test_us2_7_d_igual_al_rango_se_mueve`: la ruta cuesta exactamente el rango; el cazador da el paso. Docstring cita FR-012.
- [x] T039 [US2] En `pruebas/test_cazador.py`, `test_us2_8_intervalo_del_paso`: el paso por una salida de costo 60 con velocidad 150 reprograma su turno a `t + max(1, 60 * 100 // 150)`. Docstring cita FR-013 y FR-004.
- [x] T040 [US2] En `pruebas/test_cazador.py`, `test_us2_9_dos_salidas_a_la_misma_vecina`: dos salidas abiertas hacia la vecina elegida, de costo 80 (E) y 40 (S), usa la de costo 40; con el mismo costo en S y E usa S (orden N, S, E, O). Docstring cita FR-014.
- [x] T041 [US2] En `pruebas/test_cazador.py`, `test_us2_10_dormido_hasta_que_entra_el_jugador`: con una `Aplicacion` de `apoyo_cazador`, un cazador dormido no actúa mientras el jugador está fuera; cuando el jugador entra a su sala, su primera acción ocurre en `t_activacion + max(1, 100 * 100 // velocidad)`. Docstring cita FR-019.
- [x] T042 [US2] En `pruebas/test_cazador.py`, `test_us2_11_muerte_de_otro_enemigo_no_cambia`: entre dos turnos del cazador muere otro enemigo de una sala de su ruta, sin que el jugador se mueva ni cambien puertas; la decisión es la misma y la persecución no recalcula. Docstring cita FR-018.
- [x] T043 [P] [US2] Escribir `pruebas/test_persecucion.py`: (a) sin cambios, dos cazadores en el mismo ciclo usan un solo recálculo (contador `recalculos` de `Persecucion`); (b) recalcula si cambia la sala del jugador, si sube `agenda.cambios_puertas`, si sube `historial.reversiones` y si pide un rango mayor que `limite_usado`; (c) prueba de propiedad: 2 000 estados aleatorios de cuadrículas con `random.Random(semilla)` (puertas, sala del jugador, salas y rangos de cazadores) donde la decisión de `Persecucion` coincide con `decision_desde_cero`; (d) sin `configurar`, el cazador espera. Docstrings citan FR-017, FR-018 y FR-025.
- [x] T044 [P] [US2] Escribir `pruebas/test_ficha_cazador.py` según `contracts/ficha-cazador.md`: una ficha `cazador` con `rango` 0 o 400 se acepta; sin `rango`, con `rango` -1, `"400"`, `4.5` o `True` lanza `ValueError` cuyo texto incluye el id de la ficha; una ficha `errante` con o sin `rango` se acepta. Docstrings citan FR-008 y FR-009.

### Implementación de US2

- [x] T045 [P] [US2] En `src/cripta/dto/EnemigoDto.py` agregar a `FichaEnemigo` el campo `rango: int | None = None` y `cazador` al comentario de comportamientos. Cita FR-008.
- [x] T046 [P] [US2] En `src/cripta/dto/Partida_dto.py` agregar a `EnemigoPartida` el campo `rango: int | None = None`. Cita FR-008 y FR-021.
- [x] T047 [US2] En `src/cripta/dto/FactoryDto_Partida.py` copiar `rango` de la ficha a cada `EnemigoPartida` (nada si no hay ficha). Depende de T045 y T046. Cita FR-008.
- [x] T048 [US2] En `src/cripta/dto/FactoryDto_Ficha.py`, caso `enemigo` de `parsear_ficha`, validar con la regla verbatim de data-model.md: «Obligatorio y entero ≥ 0 si `comportamiento == "cazador"`; si no, `ValueError` con el id (FR-009); ignorado en los demás», rechazando también los booleanos. Depende de T002 y T045. Cita FR-008 y FR-009.
- [x] T049 [US2] Crear `src/cripta/modelo/Persecucion.py` con la clase `Persecucion` de data-model.md: campos `buscador`, `entrantes`, `rango_maximo`, `valida`, `clave_sala`, `clave_puertas`, `clave_reversiones`, `limite_usado` y el contador de diagnóstico `recalculos`; operaciones `configurar(entrantes)` (crea el `BuscadorRutas` del tamaño de `entrantes`), `registrar_rango(r)` (solo crece), `distancias(sala_jugador, agenda, historial, rango)` (recalcula con `distancias_hacia(sala_jugador, entrantes, usable, None, limite=rango_maximo)` si la clave no coincide o `limite_usado < rango`) y `paso(sala, salidas, rango)` (devuelve la salida de `elegir_paso` o nada si no hay distancia o d > rango). Predicado `usable(salida) = not salida.cerrada`. Sin `dict` ni `set`; sin cola nueva. Depende de T007, T009 y T011. Cita FR-011, FR-012, FR-013, FR-014, FR-015, FR-017, FR-018 y FR-025.
- [x] T050 [US2] Crear `src/cripta/modelo/enemigos/Cazador.py` con `Cazador(Enemigo)` y el atributo `rango`; `_decidir_movimiento` pide `persecucion.paso(self.sala, sala_actual.salidas, self.rango)` y devuelve `["mover", salida.sala_destino, salida.costo]` o `["esperar", None, None]`. Nunca llama a `abrir_salida`. Depende de T049. Cita FR-010 a FR-016.
- [x] T051 [US2] Agregar el parámetro `persecucion` a `decidir_accion` y `_decidir_movimiento` en `src/cripta/modelo/Enemigo.py`, `src/cripta/modelo/enemigos/Guardian.py`, `src/cripta/modelo/enemigos/Errante.py` y `src/cripta/modelo/enemigos/Rastreador.py` (los tres últimos lo ignoran), y ajustar los usos de T030. Depende de T050. Cita FR-011 y FR-015.
- [x] T052 [US2] En `src/cripta/modelo/Simulacion.py` crear `self.persecucion = Persecucion()` en `__init__` y pasarla a `decidir_accion` en `_ejecutar_turno_enemigo`. Depende de T051. Cita FR-011 y FR-017.
- [x] T053 [US2] En `src/cripta/controlador/CombateControlador.py`, `crear_enemigo`, agregar el caso `cazador` que crea un `Cazador` con `rango = dto.rango`; en `activar_enemigo`, si el enemigo es cazador, llamar a `simulacion.persecucion.registrar_rango(enemigo.rango)`. Depende de T047 y T052. Cita FR-008 y FR-019.
- [x] T054 [US2] Leer `src/cripta/controlador/InicioPartidaControlador.py` y `src/cripta/controlador/PartidaControlador.py` y, en el punto donde ya existen la simulación nueva y `ExploracionControlador.entrantes` (tras `ensamblar_salas`), llamar a `simulacion.persecucion.configurar(exploracion.entrantes)` en el archivo que corresponda. Depende de T052. Cita FR-015.
- [x] T055 [US2] Ejecutar `pruebas.test_cazador`, `pruebas.test_cazador_puertas` (solo T036), `pruebas.test_persecucion`, `pruebas.test_ficha_cazador`, `pruebas.test_ir_a` y la selección del README. Protege FR-010 a FR-019.

**Punto de control**: US2 completa; los 5 casos del Apéndice B del cazador pasan.

---

## Fase 5: US3 - El cazador no ve niebla ni abre puertas (P1)

**Meta**: el cazador usa el esqueleto completo y el estado real de las puertas, nunca el conocimiento del jugador, y no abre puertas.

**Prueba independiente**: `uv run python -m unittest pruebas.test_cazador_puertas`.

### Pruebas de US3 (escribir primero; DEBEN fallar si algo lee el conocimiento o abre puertas)

- [x] T056 [US3] En `pruebas/test_cazador_puertas.py`, `test_us3_1_salas_no_exploradas`: con una `Aplicacion`, un cazador activado en una zona que el jugador no exploró ni avistó decide igual que `decision_desde_cero`. Docstring cita FR-015.
- [x] T057 [US3] En `pruebas/test_cazador_puertas.py`, `test_us3_2_memoria_abierta_real_cerrada`: el mapa del jugador recuerda abierta una puerta que en realidad está cerrada; el cazador no la atraviesa. Docstring cita FR-011 y FR-015.
- [x] T058 [US3] En `pruebas/test_cazador_puertas.py`, `test_us3_3_no_abre_puertas`: con una puerta con llave cerrada en la ruta más corta del esqueleto, tras varios turnos del cazador la puerta sigue cerrada y `agenda.cambios_puertas` no cambió por sus turnos. Docstring cita FR-016.
- [x] T059 [US3] En `pruebas/test_cazador_puertas.py`, `test_us3_modulos_sin_conocimiento`: el código de `src/cripta/modelo/Persecucion.py` y `src/cripta/modelo/enemigos/Cazador.py` no importa `Conocimiento` ni llama a `abrir_salida` (lectura del texto del módulo). Docstring cita FR-015 y FR-016.

### Implementación de US3

- [x] T060 [US3] Si T056 a T059 fallan, corregir `src/cripta/modelo/Persecucion.py` o `src/cripta/modelo/enemigos/Cazador.py` para que solo lean `entrantes`, `SalidaSimple.cerrada` y `SalidaSimple.costo`; ejecutar `pruebas.test_cazador_puertas` completo. Cita FR-015 y FR-016.

**Punto de control**: historias P1 completas.

---

## Fase 6: US4 - Ver costos de las salidas y reconocer a los cazadores (P2)

**Meta**: la vista muestra el costo de cada salida de la sala actual y distingue a los cazadores vivos.

**Prueba independiente**: `uv run python -m unittest pruebas.test_grafica`.

### Pruebas de US4 (escribir primero; DEBEN fallar)

- [x] T061 [US4] En `pruebas/test_grafica.py`, siguiendo el patrón de lienzo falso que ya usa ese archivo, `test_us4_1_costos_de_las_salidas`: con vecinas de costo 1, 100 (sin declarar) y 250, `escena.puertas` dibuja el texto de cada costo junto a su puerta. Docstring cita FR-020.
- [x] T062 [US4] En `pruebas/test_grafica.py`, `test_us4_2_cazador_distinguible`: con un cazador y un errante en `EstadoPartida.enemigos`, `escena.enemigos` dibuja la marca propia solo para el cazador y su texto emergente incluye «cazador» y su rango. Docstring cita FR-021.
- [x] T063 [US4] En `pruebas/test_grafica.py`, `test_us4_3_cazador_derrotado_como_los_demas`: un cazador en `vista.enemigos_muertos` se dibuja sin marca de cazador. Docstring cita FR-021.

### Implementación de US4

- [x] T064 [US4] En `src/cripta/controlador/CicloAccionesControlador.py`, `sincronizar`, pasar `rango=getattr(e, "rango", None)` al crear cada `EnemigoPartida`. Depende de T046. Cita FR-021.
- [x] T065 [US4] En `src/cripta/vista/grafica/escena.py`, método `puertas`, dibujar junto a cada puerta el costo de `vecindad[i].costo` con la fuente de píxeles existente. Cita FR-020.
- [x] T066 [US4] En `src/cripta/vista/grafica/escena.py`, método `enemigos`, dibujar para cada cazador vivo (`comportamiento == "cazador"`) un contorno bajo los pies de color distinto al de selección y agregar al texto de la zona «cazador · rango r». Depende de T064. Cita FR-021.
- [x] T067 [US4] Ejecutar `pruebas.test_grafica`; la verificación visual queda para T101. Cita FR-020 y FR-021.

---

## Fase 7: US5 - Coherencia con guardado, retroceso y reproducción (P2)

**Meta**: partidas con cazadores reproducibles, guardables y reversibles.

**Prueba independiente**: `uv run python -m unittest pruebas.test_cazador_guardado`.

### Pruebas de US5 (escribir primero; DEBEN fallar)

- [x] T068 [US5] En `pruebas/test_cazador_guardado.py`, `test_us5_1_replay_con_cazadores`: siguiendo el patrón de `pruebas/test_replay.py`, grabar una partida con cazadores y salidas de costos distintos y reproducirla; cada instante del reloj y la sala y vida de cada cazador coinciden. Docstring cita FR-022.
- [x] T069 [US5] En `pruebas/test_cazador_guardado.py`, `test_us5_2_guardar_y_cargar_en_persecucion`: guardar con un cazador activo a mitad de una persecución, cargar, y comprobar comportamiento, rango y siguiente turno, y que su siguiente decisión es la misma que sin guardar. Docstring cita FR-023.
- [x] T070 [US5] En `pruebas/test_cazador_guardado.py`, `test_us5_3_retroceso_tras_movimiento_costoso`: tras un movimiento de costo 300 durante el cual actúan cazadores, el pergamino devuelve reloj, sala del jugador y salas de los cazadores al estado previo, y el siguiente turno del cazador decide igual que `decision_desde_cero`. Docstring cita FR-024 y FR-017.
- [x] T071 [US5] En `pruebas/test_cazador_guardado.py`, `test_guardado_sin_cazadores_no_cambia`: un guardado sin cazadores se escribe y se lee igual que antes y `VERSION_CUERPO` no cambió. Docstring cita FR-023.

### Implementación de US5

- [x] T072 [P] [US5] En `src/cripta/controlador/guardado/Datos.py` agregar a `EnemigoG` el campo final `rango: int | None = None`. Cita FR-023.
- [x] T073 [US5] En `src/cripta/controlador/guardado/Escritura.py`, `_escribir_enemigo`, escribir `w.entero(e.rango)` después de `regeneracion_objetivo` solo si `e.comportamiento == "cazador"`. Cita FR-023.
- [x] T074 [US5] En `src/cripta/controlador/guardado/Lectura.py`, `_leer_enemigo`, leer `r.entero()` como rango con la misma condición y pasarlo a `EnemigoG`. Depende de T072. Cita FR-023.
- [x] T075 [US5] En `src/cripta/controlador/guardado/Restauracion.py` pasar `rango` al `EnemigoPartida` que crea cada enemigo; tras crear la `Simulacion` nueva, llamar a `sim.persecucion.configurar(app._exploracion.entrantes)` y a `registrar_rango` por cada cazador activo. Depende de T053 y T074. Cita FR-015 y FR-023.
- [x] T076 [US5] Ejecutar `pruebas.test_cazador_guardado`, `pruebas.test_guardado`, `pruebas.test_replay` y `pruebas.test_retroceso`; si T070 falla, corregir la clave en `src/cripta/modelo/Persecucion.py` o el contador de T011, sin revertir los contadores con el historial. Cita FR-022, FR-023 y FR-024.

---

## Fase 8: US6 - Medir el ciclo de eventos con muchos cazadores (P3)

**Meta**: evidencia medida de D5 a D8 y del límite de 20 ms (principio VI).

**Prueba independiente**: `uv run python -m unittest pruebas.test_bench_cazador`.

### Pruebas de US6 (escribir primero; DEBEN fallar)

- [x] T077 [US6] En `pruebas/test_bench_cazador.py`, `test_us6_1_formato_y_sin_vista`: H5 a escala reducida imprime una línea con los campos de `contracts/bench-cazador.md` (`cazadores`, `media_ms`, `maximo_ms`, `limite=20ms` y CUMPLE o EXCEDE) y, tras correrla, ningún módulo de `cripta.vista` ni `arcade` quedó importado por ella. Docstring cita FR-026 y FR-027.
- [x] T078 [US6] En `pruebas/test_bench_cazador.py`, `test_us6_2_determinista_por_semilla`: `generar_cripta_cazadores` con la misma semilla da la misma cripta (salidas, costos, puertas, salas de cazadores y del jugador) y H4 y H8 a escala reducida dan los mismos conteos dos veces. Docstring cita FR-026.
- [x] T079 [US6] En `pruebas/test_bench_cazador.py`, `test_generador`: ids secuenciales, costos en 1 a 300 o 100, ningún cazador en la sala del jugador, y con `puertas_inestables` hay salidas con cierre automático. Docstring cita FR-026 y FR-028.

### Implementación de US6 (todas en `src/cripta/bench.py`, secuenciales)

- [x] T080 [US6] En `src/cripta/bench.py` crear `generar_cripta_cazadores(semilla, salas, cazadores, rango, puertas_inestables=False)` sobre la cuadrícula de `generar_cripta_conocimiento` (costos de 1 a 300, 20 % sin costo, puertas cerradas de un lado), con `random.Random(semilla)` para colocar jugador y cazadores y, si `puertas_inestables`, cierre automático corto en parte de las salidas abiertas. Cita FR-026 y FR-028.
- [x] T081 [US6] En `src/cripta/bench.py` agregar la colocación de cazadores sobre el esqueleto mayor de `datos_offline` (misma búsqueda que usa K4 con `tamano_cripta_referencia`), sin escribir ids ni tamaños en el código. Cita FR-025 y FR-028.
- [x] T082 [US6] En `src/cripta/bench.py` medir H1: decisión de C cazadores por ciclo con C = 1, 10, 50 y 100, rango 300 y rango sin límite efectivo, búsqueda compartida frente a una búsqueda por cazador; imprimir `razon` según el contrato. Cita FR-025.
- [x] T083 [US6] En `src/cripta/bench.py` medir H2: un recálculo con 200, 2 000 y 20 000 salas, mismo rango, con corte frente a sin corte, con salas fijadas y tiempo; criterio de D6 (con corte crece menos de 1,5 veces de 2 000 a 20 000). Cita FR-025.
- [x] T084 [US6] En `src/cripta/bench.py` medir H3: 200 decisiones del jugador con cazadores, puertas estables e inestables, reutilizar con la clave frente a recalcular en cada turno y frente a recalcular una vez por ciclo, con tiempo y `recalculos`. Cita FR-017 y FR-025.
- [x] T085 [US6] En `src/cripta/bench.py` medir H4: 10 000 turnos aleatorios donde la decisión de `Persecucion` coincide con la búsqueda completa desde cero; `coinciden` debe ser igual a `turnos`. Cita FR-017.
- [x] T086 [US6] En `src/cripta/bench.py` medir H5: ciclo de eventos entre dos decisiones del jugador (acción del jugador más `avanzar_hasta_turno_jugador`) en la cripta de referencia con 10, 50 y 100 cazadores activos; media y máximo, y CUMPLE si el máximo es menor que 20 ms con 50 cazadores. Cita FR-025.
- [x] T087 [US6] En `src/cripta/bench.py` medir H6 (§5.6): repetir la comparación de la agenda de `_bench_simulacion` (heap propio frente a lista ordenada) con la carga nueva: eventos de acción con intervalos de costos de 1 a 300 y velocidades variadas, más cierres de puertas. Cita FR-025.
- [x] T088 [US6] En `src/cripta/bench.py` medir H7: costo del predicado por arista relajada frente a un arreglo de banderas por clave de salida (alternativa de D9 de la spec 002), con el resto igual. Cita FR-025.
- [x] T089 [US6] En `src/cripta/bench.py` medir H8: H1, H4 y H5 dos veces con la misma semilla; imprimir `identico=si` si decisiones y conteos coinciden. Cita FR-022 y FR-026.
- [x] T090 [US6] En `src/cripta/bench.py` agregar `_bench_cazador(semilla)` con el encabezado del contrato y llamarla desde `main`, de modo que `uv run python -m cripta --bench --semilla 42` la ejecute sin abrir la vista. Cita FR-026 y FR-027.
- [x] T091 [US6] Ejecutar `uv run python -m cripta --bench --semilla 42` dos veces y guardar la salida en `specs/003-terreno-cazador/mediciones.txt`. Aplicar las reglas de decisión de D5 y D8 (cambiar solo si una alternativa correcta gana por más de 2 veces) y la de D6; si alguna regla pide cambiar de estrategia, detenerse y reportarlo antes de tocar código. Si H5 EXCEDE, reportarlo con los números. Cita FR-025 y FR-026.

---

## Fase 9: Cierre y transversales

- [x] T092 Redactar en `docs/decisiones.md` la sección «14. Costo del movimiento por terreno (Parte II, §5.1)», tras la sección 13 de la spec 002 y con el mismo estilo: dónde se fija el costo del jugador y de los enemigos (D1, D2), preservación del azar, reescalado existente (D3), complejidad y la medición H6. Comprobar el título contra el enunciado antes de confirmarla. Cita FR-001 a FR-007.
- [x] T093 Redactar en `docs/decisiones.md` la sección «15. Enemigo cazador y búsqueda compartida (Parte II, §5.2)»: búsqueda compartida frente a individual (D5), corte por rango y su invariante (D6), límite (D7), clave de invalidación con contadores monótonos y tabla de eventos (D8), ficha y guardado (D9, D10), con los números de H1 a H5, H7 y H8 de `specs/003-terreno-cazador/mediciones.txt`. Depende de T091. Cita FR-011 a FR-018 y FR-025.
- [x] T094 Redactar en `docs/decisiones.md` la sección «16. Agenda de eventos con cazadores (Parte II, §5.6)»: repetir el análisis de la sección 1 con la carga nueva (H6) y el ciclo de H5, y concluir si el heap propio sigue siendo la elección. Depende de T091. Cita FR-025.
- [x] T095 [P] Actualizar `docs/estructuras.md` con `Persecucion`, el parámetro `limite` de `BuscadorRutas` y los contadores `cambios_puertas` y `reversiones` (operaciones y costo según data-model.md). Cita FR-017 y FR-025.
- [x] T096 [P] Actualizar `docs/api.md`: `cazador` en la lista de comportamientos de `Enemy` y el campo `rango` (`integer`, ≥ 0, obligatorio con `cazador`). Cita FR-008 y FR-009.
- [x] T097 [P] Actualizar `README.md`: costo de las salidas en el tiempo, el cazador y cómo se ve en la interfaz, y las mediciones H1 a H8 de `--bench`, con enlace a las secciones 14 a 16. Cita FR-003, FR-020, FR-021 y FR-026.
- [x] T098 Registrar en `docs/PROMPTS_LLM.md`, con el formato de las entradas existentes (fecha, integrante, herramienta, objetivo, prompt textual y uso de la respuesta), las entradas de `/speckit-specify`, `/speckit-clarify`, `/speckit-plan` y `/speckit-tasks` de esta spec, a continuación de la última entrada. Protege la trazabilidad de FR-001 a FR-028 (flujo de trabajo de la constitución).
- [x] T099 Registrar en `docs/PROMPTS_LLM.md` cada prompt de `/speckit-analyze` y de `/speckit-implement` de esta spec en el momento en que se use, con el mismo formato. Protege la trazabilidad de FR-001 a FR-028.
- [x] T100 Revisar los archivos nuevos y modificados contra los principios I y IV: ninguna búsqueda de `heapq`, `bisect`, `collections`, `sorted(` ni `.sort(`, ningún `dict` ni `set` como índice, ninguna cola de prioridad nueva, ningún id de sala, enemigo o cripta en el código. Corregir lo que aparezca. Cita FR-015 y FR-028.
- [X] T101 Ejecutar `specs/003-terreno-cazador/quickstart.md` completo (secciones 1 a 4, incluida la verificación con la interfaz) y anotar el resultado de cada punto al final de ese archivo bajo «Resultado de la validación». Cita FR-001 a FR-028 y SC-001 a SC-007.
- [x] T102 Regresión: repetir los comandos de `specs/003-terreno-cazador/linea_base.txt`; la selección del README DEBE pasar y la suite completa NO DEBE tener fallas nuevas, comparando nombre por nombre; registrar el resultado en `specs/003-terreno-cazador/regresion.txt`. Última tarea. Protege FR-005, FR-022 y FR-028.

---

## Dependencias y orden de ejecución

- **Fase 1**: T001 antes de todo; T002 antes de T048; T003 y T004 con el código sin modificar, antes de T005.
- **Fase 2** depende de la Fase 1 y bloquea las historias: T006 antes de T007; T008 antes de T009 a T011; T009 antes de T010; T012 al final.
- **US1** (T013 a T031) depende de la Fase 2. Es el MVP. T022 → T023 → T024; T025 antes de T026 a T028; T029 después de T028; T030 y T031 al final.
- **US2** depende de US1 (formato de decisión de tres elementos, T025 a T029). T045 y T046 antes de T047; T049 depende de T007, T009 y T011; T050 → T051 → T052 → T053 y T054.
- **US3** depende de US2 (mismos módulos).
- **US4** depende de T046 (rango en `EnemigoPartida`) y de US1 para los costos; es independiente de US3 y US5.
- **US5** depende de US2 (T053) y de T011.
- **US6** depende de US2 (mide `Persecucion`) y de US1 (H6 usa intervalos con costo).
- **Fase 9**: T093 y T094 después de T091; T099 continúa durante analyze e implement; T102 es la última.

### Oportunidades de paralelismo

- Fase 2: T005, T006 y T008 en paralelo; luego T007, T009 y T011 en paralelo entre sí (archivos distintos), y T010 tras T009.
- US1: T013 a T020 son secuenciales (mismo archivo), pero T021 es [P] con ellas; T026, T027 y T028 en paralelo tras T025.
- US2: T043 y T044 en paralelo con T032 a T042; T045 y T046 en paralelo.
- US4 puede avanzar en paralelo con US3 y US5 (archivos distintos: `escena.py`, `test_grafica.py`), salvo T064, que toca `CicloAccionesControlador.py`.
- US5: T072 en paralelo con T068 a T071.
- Fase 9: T095, T096 y T097 en paralelo.
- NO son paralelas las tareas que editan el mismo archivo: `bench.py` (T080 a T090), `Simulacion.py` (T029, T052), `Enemigo.py` (T025, T051), `CicloAccionesControlador.py` (T022, T064), `docs/decisiones.md` (T092 a T094).

## Estrategia de implementación

1. **MVP**: Fases 1 y 2 y US1. El tiempo refleja el terreno para todos los actores, con los casos 6 y 7 del Apéndice B.
2. **Incremento 2**: US2 y US3 completan las historias P1: el cazador con los casos 1 a 5 del Apéndice B.
3. **Incremento 3**: US4 y US5 agregan la vista y la coherencia con guardado, retroceso y reproducción.
4. **Incremento 4**: US6 da la evidencia medida; cerrar con T092 a T102. No marcar una historia como terminada sin que sus pruebas pasen y sin que la selección del README siga en verde.

## Cobertura de escenarios de aceptación

| Escenario | Prueba | FR |
|-----------|--------|----|
| US1.1 a US1.7 | T013, T014, T015, T016, T017, T018, T019 | FR-001, FR-003, FR-004, FR-005, FR-006 |
| «Ir a» con costo | T020 | FR-007 |
| Contrato de decisión | T021 | FR-003, FR-022 |
| US2.1 a US2.11 | T032, T033, T034, T035, T036, T037, T038, T039, T040, T041, T042 | FR-010 a FR-019 |
| Persecución y FR-017 | T006, T043 | FR-017, FR-018, FR-025 |
| Ficha del cazador | T044 | FR-008, FR-009 |
| US3.1 a US3.3 | T056, T057, T058, T059 | FR-011, FR-015, FR-016 |
| US4.1 a US4.3 | T061, T062, T063 | FR-020, FR-021 |
| US5.1 a US5.3 | T068, T069, T070, T071 | FR-022, FR-023, FR-024 |
| US6.1 y US6.2 | T077, T078, T079, T086, T089 | FR-025, FR-026, FR-027 |
| Apéndice B 1 a 7 (SC-001) | T032, T033, T034, T035, T036, T015, T016 | FR-011, FR-012, FR-013, FR-014, FR-017, FR-004, FR-006 |

## Referencia publicada (17/11/2026)

- [ ] T104 Medir y probar el esqueleto publicado mayor sin E/S cronometrada; guardar evidencia y actualizar decisiones y README (FR-025, FR-026, FR-029; spec 001 FR-023; spec 002 FR-038).
