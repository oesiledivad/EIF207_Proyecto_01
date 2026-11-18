# Tareas: Verificación de resolubilidad de la cripta

**Entrada**: `specs/001-resolubilidad/` (spec.md, plan.md, research.md, data-model.md, contracts/, quickstart.md)

**Requisitos previos**: plan.md y spec.md. Las decisiones D1 a D8 de research.md y las "Decisiones tomadas" del plan son definitivas.

**Pruebas**: solicitadas de forma explícita. Hay una prueba `unittest` por cada escenario de aceptación (incluidos los 4 del Apéndice B) y cada prueba cita su FR en el docstring. Las pruebas de cada historia se escriben antes de la implementación y DEBEN fallar primero.

**Organización**: por historia de usuario (US1 a US6) para implementar y probar cada una por separado.

## Formato: `[ID] [P?] [Historia] Descripción con ruta`

- **[P]**: se puede hacer en paralelo (archivos distintos, sin dependencia de tareas incompletas).
- **[USn]**: historia de usuario de spec.md.
- Cada tarea cita al menos un FR. Las tareas de soporte citan los FR que protegen.
- Rutas desde la raíz del repositorio. Comandos para Windows con CMD y `uv run`.

## Reglas transversales (constitución)

- Sin `dict`, `set`, `heapq`, `bisect`, `collections`, `networkx`, `sorted()` ni `list.sort()` en el algoritmo (principio I). `dict` solo al leer el JSON de la respuesta.
- El modelo (`modelo/Resolubilidad.py`) NO conoce HTTP, archivos ni vista (principio III).
- Ningún dato de una cripta concreta en código ni en pruebas (FR-029, principio IV): cada prueba arma su esqueleto mínimo.
- Docstring de cada prueba: `"""FR-0xx: ..."""` con el escenario que cubre.

---

## Fase 1: Preparación

**Propósito**: fijar la línea base antes de tocar código.

- [X] T001 Registrar la línea base de la suite existente en `specs/001-resolubilidad/linea_base.txt`. Con el código sin modificar, ejecutar (a) `uv run python -m unittest pruebas.test_partida pruebas.test_inventario pruebas.test_retroceso pruebas.test_guardado pruebas.test_replay pruebas.test_bench pruebas.test_grafica` (la selección del README) y (b) `uv run python -m unittest discover -s pruebas -p "test*.py"` (la suite completa). Anotar fecha, hash de `git rev-parse --short HEAD`, comando, cantidad de pruebas y la lista exacta de pruebas que fallan o dan error (nombre completo `modulo.Clase.metodo`), sin corregir ninguna. Protege FR-027 y FR-029 (no modificar estado ni datos).

**Punto de control**: `linea_base.txt` existe y está confirmado en Git antes de la tarea T002.

---

## Fase 2: Fundamentos (bloquean todas las historias)

**Propósito**: DTO, estructuras propias, consulta de llaves en las tres fuentes y fuentes falsas de pruebas.

**CRÍTICO**: ninguna historia empieza hasta terminar esta fase.

- [X] T002 [P] Crear `src/cripta/dto/Verificacion_dto.py` con dataclasses `UbicacionLlave`, `LlaveEnOrden`, `LlaveBloqueada`, `PuertaBloqueada`, `PasoCiclo`, `Ciclo`, `ReporteBloqueo` y `ResultadoVerificacion` según data-model.md. Restricciones verbatim: `UbicacionLlave.llave` es `str` "Id de la llave, no vacío"; `sala` es `int` "Id de sala; si no existe en el esqueleto, la ubicación se descarta con advertencia"; `enemigo` es `str` o `None`; `EstadisticasVerificacion` con `salas_encoladas`, `salidas_examinadas` y `llaves_obtenidas` (enteros) y el campo opcional `ResultadoVerificacion.estadisticas` (`EstadisticasVerificacion` o `None`, por defecto `None`); `ResultadoVerificacion.estado` es `"resoluble"`, `"no_resoluble"` o `"no_verificable"`; `orden_llaves` "Solo con `resoluble`... vacía en los otros casos"; `reporte` "Solo con `no_resoluble`"; `motivo_no_verificable` "Solo con `no_verificable`"; `ReporteBloqueo.motivo` es `"llave_salida_inobtenible"` o `"puerta_sin_destino"`; `LlaveBloqueada.causa` es `en_ciclo`, `depende_de`, `sin_ubicacion`, `sala_desconectada` o `ubicacion_invalida`. Cita FR-002, FR-007, FR-009 a FR-012.
- [X] T003 [P] Escribir `pruebas/test_cola_lista.py` con pruebas de `ColaLista`: orden FIFO, `vacia`, y que tras 10 000 `encolar` y `sacar` no se usa `pop(0)` (índice de cabeza avanza). Docstring cita FR-024. DEBE fallar antes de T004.
- [X] T004 Crear `src/cripta/estructuras/Cola_Lista.py`: `ColaLista` con `list` e índice de cabeza, métodos `encolar`, `sacar`, `vacia`, sin `deque` ni `pop(0)`. Cita FR-024.
- [X] T005 [P] Escribir `pruebas/test_indice_llaves.py`: rango por posición ordenada, búsqueda binaria devuelve -1 si no existe, ids duplicados se deduplican, el mismo resultado para dos permutaciones de la entrada, y los ids de llave se ordenan como cadenas (el rango de un id como `<prefijo>10` es menor que el de `<prefijo>2`, con ids armados en la prueba). Docstrings citan FR-008 y FR-024. DEBE fallar antes de T006.
- [X] T006 Crear `src/cripta/estructuras/Indice_Llaves.py`: `IndiceLlaves` con arreglo de ids distintos ordenado con `ordenar` de `Ordenamientos.py` y búsqueda binaria propia (sin `bisect`). El rango es la posición, de modo que "menor id" equivale a menor rango. Cita FR-008, FR-024.
- [X] T007 [P] Añadir `parsear_llaves(respuesta) -> list[UbicacionLlave]` en `src/cripta/dto/FactoryDto_Partida.py` según contracts/adaptador-llaves.md: `sala` con `int`, `enemigo` a `str` o `None`, descartar entradas sin `id`, `ValueError` si falta `llaves` o la estructura general es inválida; una lista `llaves` vacía y válida es un dato legítimo. Cita FR-002, FR-022.
- [X] T008 Añadir el método abstracto `key_locations(self, crypta_id)` (`GET /criptas/{id}/llaves`) en `src/cripta/adaptadores/Crypt_Data_Source.py`. Cita FR-001, FR-002.
- [X] T009 [P] Implementar `key_locations` en `src/cripta/adaptadores/Network_Adapter.py` con `_request(f"/criptas/{id}/llaves")`, de modo que cuente en `requests_made`, respete `presupuesto_solicitudes` y los reintentos 429. Cita FR-019.
- [X] T010 [P] Añadir `leer_llaves(cripta_id)` y `guardar_llaves(cripta_id, datos)` en `src/cripta/adaptadores/Almacen_Disco.py`: ruta `criptas/<id>/llaves.json`, escritura atómica con `_escribir_json`, archivo ausente o dañado equivale a `None`. La ruta queda dentro de la carpeta que `validar_cripta` reinicia. Cita FR-020, FR-021.
- [X] T011 Implementar `key_locations` en `src/cripta/adaptadores/AdaptadorOffline.py` (depende de T010): primero `AlmacenDisco.leer_llaves` si la cripta está en caché, luego `cripta_<id>_llaves.json` del paquete, si no hay ninguno `FileNotFoundError`; no cuenta solicitudes. Cita FR-018, FR-022.
- [X] T012 [P] Implementar `key_locations(crypta_id, datos)` en `src/cripta/adaptadores/Guardar_Llamadas_API.py`: graba `cripta_<id>_llaves.json` con `guardar_llamada`, igual que las demás consultas del grabador. Cita FR-020.
- [X] T013 Hacer que las fuentes falsas de `pruebas/` reciban la consulta nueva devolviendo "sin datos": en `pruebas/test_inventario.py` (clase base `FuentePrueba`, de la que heredan las de `test_partida.py` y `test_combate_efectos.py` vía `FuenteRetroceso` y `FuenteReplay`) y en la clase local `AdaptadorOffline` de `pruebas/test_guardados.py`, señalar "sin datos" con `FileNotFoundError` en `key_locations`. Buscar con Grep cualquier otra subclase de `CryptDataSource` o `AdaptadorOffline` en `pruebas/` y cubrirla. Cita FR-022.
- [X] T014 Ejecutar la selección del README (comando (a) de T001) tras T013 y comprobar que pasa igual que en `linea_base.txt`. Protege FR-022.
- [X] T015 Añadir en `src/cripta/servicio/CriptaService.py`: `UbicacionLlavesNoDisponible`, `obtener_ubicaciones_llaves(cripta_id)` (disco si `_cripta_en_disco`, si no la fuente; guarda en disco tras una respuesta válida; convierte `PresupuestoAgotado`, `RuntimeError`, `OSError`, `ValueError`, `FileNotFoundError` y `NotImplementedError` en `UbicacionLlavesNoDisponible`; una respuesta malformada es "no disponible", no "sin llaves") y `validar_cripta_en_disco(detalles)` sin consultar el catálogo. Cita FR-019, FR-020, FR-021, FR-022.

**Punto de control**: fundamentos listos; las historias pueden empezar.

---

## Fase 3: US1 - Saber si una cripta se puede ganar y el orden de llaves (P1)

**Meta**: veredicto "resoluble" con el orden de todas las llaves obtenibles, determinista.

**Prueba independiente**: `uv run python -m unittest pruebas.test_resolubilidad` con esqueletos armados en la prueba, sin vista.

### Pruebas de US1 (escribir primero; DEBEN fallar)

- [X] T016 [US1] En `pruebas/test_resolubilidad.py`, `test_us1_1_unica_llave_salida`: esqueleto mínimo con `llave_salida` en una sala alcanzable desde la inicial y una puerta a `sala_salida`; resoluble y el orden contiene únicamente `llave_salida`. Docstring cita FR-006 y FR-007.
- [X] T017 [US1] En `pruebas/test_resolubilidad.py`, `test_us1_2_llaves_encadenadas`: tres llaves donde cada una está tras la puerta de la anterior; el orden incluye todas, cada una después de las necesarias para alcanzarla, e incluye `llave_salida`. Docstring cita FR-007.
- [X] T018 [US1] En `pruebas/test_resolubilidad.py`, `test_us1_3_llave_innecesaria_incluida`: una llave obtenible no necesaria para ganar aparece en el orden. Docstring cita FR-007.
- [X] T019 [US1] En `pruebas/test_resolubilidad.py`, `test_us1_4_apendice_b_orden_determinista` (Apéndice B, caso 3): cripta con varios órdenes válidos, dos ejecuciones y además con las listas de entrada en otro orden producen exactamente el mismo orden. Docstring cita FR-008.
- [X] T020 [US1] En `pruebas/test_resolubilidad.py`, `test_us1_5_apendice_b_llave_de_enemigo_errante` (Apéndice B, caso 2): la llave publicada con `enemigo` se ubica en la sala publicada (donde el enemigo inicia) y es obtenible allí; el orden la reporta con su `enemigo`. Nota: el servicio publica como `sala` de la llave la sala donde inicia el enemigo (contrato del §4.2), así que el modelo usa esa sala tal cual, sin buscar al enemigo. Docstring cita FR-002 y FR-004.
- [X] T021 [US1] En `pruebas/test_resolubilidad.py`, pruebas de bordes de resolubilidad: `llave_salida` en la sala inicial (ronda 0, orden la incluye con las demás), llave obtenible que no abre ninguna puerta hacia `sala_salida` (no resoluble, motivo `puerta_sin_destino`), varias puertas con la misma llave (todas se abren), llave de región solo alcanzable con otra llave, llave no obtenible no aparece en el orden de una cripta resoluble. Un método por borde; docstrings citan FR-006, FR-007 y FR-003.
- [X] T022 [US1] En `pruebas/test_resolubilidad.py`, `test_trampas_y_cierres_no_bloquean` y `test_salidas_dirigidas`: una salida con `cierre_automatico` no cambia el veredicto, y una puerta declarada cerrada en un solo lado no se infiere en el lado contrario. Docstrings citan FR-005 y FR-003.
- [X] T023 [US1] En `pruebas/test_resolubilidad.py`, `test_llave_con_varias_ubicaciones`: la llave se obtiene en la alcanzable primero y, con empate de ronda, en la de menor id de sala. Docstring cita FR-002 y FR-008.
- [X] T024 [US1] En `pruebas/test_resolubilidad.py`, `test_no_modifica_entradas_ni_contiene_datos_de_cripta`: tras `verificar` las listas `salas` y `ubicaciones` son iguales a una copia previa, y el texto de `src/cripta/modelo/Resolubilidad.py` no contiene las cadenas `cripta-` ni `itm_llave`. Docstring cita FR-027 y FR-029.

### Implementación de US1

- [X] T025 [US1] Crear `src/cripta/modelo/Resolubilidad.py` con la construcción de estructuras (D4): validar el esqueleto (salida cerrada sin llave y `sala_inicial` inexistente dan `no_verificable` con motivo de datos; salida a sala inexistente se ignora con advertencia; sala duplicada, la primera gana), construir `IndiceLlaves` con las llaves de las salidas cerradas y de las ubicaciones, salidas planas ordenadas por (destino, dirección) y ubicaciones por llave ordenadas por (id de sala, id de enemigo). Listas indexadas por entero, sin `dict` ni `set`. Declarar el contador `EstadisticasVerificacion` (en cero) que las tareas T026 y T027 incrementan. Cita FR-001, FR-008, FR-029 y data-model.md.
- [X] T026 [US1] En `src/cripta/modelo/Resolubilidad.py`, implementar la fase 1 de D1 y D2: exploración en anchura por rondas con `ColaLista`, ordenar cada ronda por id con `ordenar`, obtener las llaves de la sala en orden de id, listas de espera por llave, liberar esperas al obtener, no detenerse al ganar. Cada sala se encola una vez, cada salida se examina una vez; contar en `estadisticas` las salas encoladas y las salidas examinadas. Cita FR-003, FR-004, FR-007, FR-008, FR-024.
- [X] T027 [US1] En `src/cripta/modelo/Resolubilidad.py`, implementar la condición de D5 y el `ResultadoVerificacion` resoluble: `llave_salida` obtenida y una salida cerrada con esa llave cuyo destino es `sala_salida`, recorrida desde una sala alcanzada; `orden_llaves` con `LlaveEnOrden` (llave, sala, enemigo, ronda) incluyendo todas las obtenibles y ninguna inobtenible; entregar `estadisticas` con `llaves_obtenidas` y los demás contadores (`None` solo en `no_verificable`). Cita FR-005, FR-006, FR-007, FR-024.
- [X] T028 [US1] Crear `src/cripta/controlador/VerificacionControlador.py` con `verificar_cripta(cripta_id)`: obtiene detalles y esqueleto con `CriptaService`, `validar_cripta_en_disco`, `obtener_ubicaciones_llaves`, llama a `Resolubilidad.verificar` y devuelve el resultado; si `UbicacionLlavesNoDisponible`, devuelve `no_verificable` sin invocar el modelo. Incluir `formatear(resultado)` para el caso resoluble según contracts/verificar-cli.md (primera línea `Cripta <id> (version <v>): RESOLUBLE`, lista numerada, `Solicitudes de red: <usadas>/<presupuesto>`). Cita FR-001, FR-007, FR-022.
- [X] T029 [US1] Ejecutar `uv run python -m unittest pruebas.test_resolubilidad` y comprobar que T016 a T024 pasan; revisar que la exploración no repite recorridos por llave. Cita FR-024.

**Punto de control**: US1 completa y verificable sin vista.

---

## Fase 4: US2 - Entender por qué no se puede ganar (P1)

**Meta**: reporte de bloqueo con llaves inobtenibles, frontera, ubicaciones y todos los ciclos.

**Prueba independiente**: cripta con `llave_salida` tras la única puerta que ella abre; el reporte lista llave, puerta, ubicación y ciclo.

### Pruebas de US2 (escribir primero; DEBEN fallar)

- [X] T030 [US2] En `pruebas/test_resolubilidad.py`, `test_us2_1_apendice_b_ciclo_de_llave_salida` (Apéndice B, caso 1): `llave_salida` tras la única puerta que ella abre; no resoluble y el reporte trae un ciclo de longitud 1. Docstring cita FR-012.
- [X] T031 [US2] En `pruebas/test_resolubilidad.py`, `test_us2_2_ciclo_de_dos_llaves`: A tras una puerta que exige B y B tras una puerta que exige A; el ciclo tiene dos pasos con sus puertas testigo y salas. Docstring cita FR-012.
- [X] T032 [US2] En `pruebas/test_resolubilidad.py`, `test_us2_3_reporte_completo`: el reporte incluye todas las llaves inobtenibles, las puertas de la frontera con su llave y, por llave, su sala y el `enemigo` si lo suelta. Docstring cita FR-009, FR-010 y FR-011.
- [X] T033 [US2] En `pruebas/test_resolubilidad.py`, `test_us2_4_ciclo_determinista`: dos verificaciones (y una con las listas de entrada permutadas) dan el mismo ciclo, mismo punto de partida y mismo sentido. Docstring cita FR-013.
- [X] T034 [US2] En `pruebas/test_resolubilidad.py`, `test_us2_5_varios_ciclos_ordenados`: dos o más ciclos disjuntos; el reporte los incluye todos, cada uno inicia en su llave de menor id y la lista se ordena por ese id. Docstring cita FR-012 y FR-013.
- [X] T035 [US2] En `pruebas/test_resolubilidad.py`, pruebas de bordes del reporte: llave sin ubicación publicada (causa `sin_ubicacion`), llave con varias ubicaciones sin ninguna alcanzable (se listan todas), llave en sala desconectada (`sala_desconectada`), y el ejemplo de research D6 con A tras puertas de B y C, donde se reporta el ciclo A, B y no se lista A, C aparte. Docstrings citan FR-011 y FR-012.
- [X] T036 [US2] En `pruebas/test_resolubilidad.py`, `test_reporte_misma_exploracion`: contar los recorridos de salidas de una cripta con K llaves encadenadas bloqueada al final y comprobar con `estadisticas.salidas_examinadas` que el conteo es menor que `K * E` (sin exploración por llave). Docstring cita FR-025 y FR-024.

### Implementación de US2

- [X] T037 [US2] En `src/cripta/modelo/Resolubilidad.py`, implementar la fase 2 especulativa de D6 sobre la misma cola: frontera bloqueada (esperas pendientes con llave en U) listada por (rango de llave, orden de inserción), etiquetado de salas con la llave que las libera y registro de la puerta testigo. Cada sala y salida una sola vez. Cita FR-010, FR-025.
- [X] T038 [US2] En `src/cripta/modelo/Resolubilidad.py`, construir el grafo de dependencias de testigos (una arista por llave de U, ubicación alcanzada primero en fase 2) y asignar la causa de cada llave bloqueada (`en_ciclo`, `depende_de`, `sin_ubicacion`, `sala_desconectada`, `ubicacion_invalida`); incluir todas las ubicaciones publicadas de cada llave inobtenible. Cita FR-009, FR-011, FR-012.
- [X] T039 [US2] En `src/cripta/modelo/Resolubilidad.py`, enumerar ciclos con la pasada de colores de D6: cada ciclo emitido desde su llave de menor rango, mismo sentido, lista ordenada por ese rango sin ordenamiento adicional, ciclo de longitud 1 incluido, `PasoCiclo` con la puerta testigo. Cita FR-012, FR-013.
- [X] T040 [US2] En `src/cripta/modelo/Resolubilidad.py`, armar `ReporteBloqueo` con `motivo` (`llave_salida_inobtenible` o `puerta_sin_destino`), llaves por id, frontera y ciclos, y devolver `no_resoluble`. Cita FR-009, FR-010, FR-013.
- [X] T041 [US2] En `src/cripta/controlador/VerificacionControlador.py`, ampliar `formatear` con el caso no resoluble de contracts/verificar-cli.md: línea `NO RESOLUBLE`, `Motivo`, secciones de llaves, puertas y ciclos con `Ciclo n: A -> B -> A`, ordenadas por id, `(0)` si no hay ciclos, y el caso sin veredicto (`Cripta <id>: resolubilidad no verificada` más `Motivo`). Cita FR-009 a FR-013, FR-022.
- [X] T042 [US2] Ejecutar `uv run python -m unittest pruebas.test_resolubilidad` y comprobar que T030 a T036 pasan. Cita FR-012, FR-013.

**Punto de control**: US1 y US2 funcionan; el modelo está completo.

---

## Fase 5: US3 - Impedir iniciar partidas imposibles, con opción de forzar (P2)

**Meta**: la partida muestra el resultado, se bloquea sin `--forzar` y inicia con aviso si no hay datos.

**Prueba independiente**: iniciar con una cripta no resoluble sin y con `--forzar`.

### Pruebas de US3 (escribir primero; DEBEN fallar)

- [X] T043 [P] [US3] En `pruebas/test_inicio_verificacion.py`, `test_us3_1_apendice_b_bloqueada_sin_forzar` (Apéndice B, caso 4): fuente falsa con cripta no resoluble; `ok` es falso, `estado.activa` es falso, no se crea registro de partida y `motivo` contiene el reporte con al menos una puerta bloqueada y la llave que exige. Docstring cita FR-015 y SC-007.
- [X] T044 [US3] En `pruebas/test_inicio_verificacion.py`, `test_us3_2_forzada_inicia`: con `forzar=True` la partida inicia, `aviso` trae el veredicto negativo y el reporte queda en la bitácora. Docstring cita FR-016.
- [X] T045 [US3] En `pruebas/test_inicio_verificacion.py`, `test_us3_3_resoluble_muestra_resultado`: la partida inicia sin intervención y `aviso` trae el veredicto y el orden de llaves. Docstring cita FR-014.
- [X] T046 [US3] En `pruebas/test_inicio_verificacion.py`, `test_us3_4_sin_ubicacion_no_verificada`: fuente que no tiene llaves; la partida inicia con `aviso` igual a "resolubilidad no verificada", sin las palabras "resoluble" ni "no resoluble", con y sin `forzar`. Docstring cita FR-022.
- [X] T047 [US3] En `pruebas/test_inicio_verificacion.py`, `test_presupuesto_agotado_da_no_verificada`: fuente con presupuesto que se agota justo en la consulta de llaves; la partida inicia con el aviso "resolubilidad no verificada" y sin veredicto. Docstring cita FR-019 y FR-022.
- [X] T048 [US3] En `pruebas/test_inicio_verificacion.py`, `test_replay_y_carga_no_verifican`: iniciar con `verificar=False` (replay y partida guardada) no llama a `key_locations` (la fuente cuenta llamadas) y no bloquea una cripta no resoluble. Docstring cita FR-016 y los supuestos de la spec.

### Implementación de US3

- [X] T049 [US3] Ampliar `ResultadoInicio` en `src/cripta/dto/Partida_dto.py` con `verificacion: ResultadoVerificacion | None = None` y `aviso: str = ""`, con valores por defecto para no cambiar los usos actuales. Cita FR-014, FR-022.
- [X] T050 [US3] Modificar `src/cripta/controlador/InicioPartidaControlador.py`: tras cargar el esqueleto y antes de cargar el contenido de salas, verificar con `VerificacionControlador`; no resoluble sin `forzar` devuelve `ResultadoInicio(ok=False, motivo=<reporte>)` sin crear registro; con `forzar` inicia y deja el reporte en la bitácora; `no_verificable` inicia con el aviso "resolubilidad no verificada". Cita FR-014, FR-015, FR-016, FR-022.
- [X] T051 [US3] Modificar `src/cripta/controlador/Aplicacion.py`: parámetros `forzar` y `verificar=True` en `iniciar_partida`; el replay y la carga de partidas guardadas pasan `verificar=False`. Cita FR-016 y los supuestos de la spec.
- [X] T052 [US3] Modificar `src/cripta/bootstrap.py`: bandera `--forzar` que llega a `Aplicacion` y no a la vista; se ignora con `--verificar`, `--bench` y `--replay`. Cita FR-016.
- [X] T053 [US3] Modificar `src/cripta/vista/grafica/ventana.py` (método `iniciar_partida`, cambio mínimo): mostrar `resultado.aviso` además de `resultado.motivo` cuando exista. Cita FR-014, FR-015.
- [X] T054 [US3] Ejecutar `uv run python -m unittest pruebas.test_inicio_verificacion` y la selección del README; deben pasar. Cita FR-014 a FR-016, FR-022.

**Punto de control**: US3 funciona de punta a punta sin romper la Parte I.

---

## Fase 6: US4 - Verificar desde consola sin interfaz (P2)

**Meta**: `--verificar CRIPTA` imprime el resultado, con códigos 0, 1 y 2, sin vista.

**Prueba independiente**: ejecutar `--verificar` y revisar salida y código.

### Pruebas de US4 (escribir primero; DEBEN fallar)

- [X] T055 [P] [US4] En `pruebas/test_verificar_cli.py`, `test_us4_1_imprime_y_no_abre_vista`: `main(["--verificar", ...])` con fuente falsa imprime el resultado y `arcade` no está en `sys.modules` ni se instancia la vista. Docstring cita FR-017, FR-028.
- [X] T056 [US4] En `pruebas/test_verificar_cli.py`, `test_us4_2_offline_sin_red`: con `--offline` y una caché con llaves, la salida lleva `Solicitudes de red: 0/<presupuesto>` y la fuente de red nunca se invoca. Docstring cita FR-018, SC-006.
- [X] T057 [US4] En `pruebas/test_verificar_cli.py`, `test_us4_3_codigos_de_salida`: 0 si resoluble, 1 si no resoluble, 2 si la ubicación de llaves no está disponible, y 2 por error de uso (`--verificar` sin cripta, o junto con `--replay`); nunca 0 sin veredicto positivo. Docstring cita FR-018a.
- [X] T058 [US4] En `pruebas/test_verificar_cli.py`, `test_salida_determinista_y_primera_linea`: dos ejecuciones dan salida idéntica y la primera línea es el veredicto. Docstring cita FR-013, SC-002.

### Implementación de US4

- [X] T059 [US4] Modificar `src/cripta/bootstrap.py`: bandera `--verificar CRIPTA` en el grupo mutuamente excluyente con `--replay`, `--bench` y `--grafica`; construir fuente, `AlmacenDisco`, `CriptaService` y `VerificacionControlador` con import diferido, sin importar `arcade` ni la vista. Cita FR-017, FR-018, FR-028.
- [X] T060 [US4] En `src/cripta/bootstrap.py`, imprimir `VerificacionControlador.formatear(...)` en la salida estándar, las advertencias en la salida de errores con el prefijo `Aviso:`, y devolver el código 0, 1 o 2 según contracts/verificar-cli.md; cripta inexistente y presupuesto agotado dan 2. Cita FR-018a, FR-022.
- [X] T061 [US4] Ejecutar `uv run python -m unittest pruebas.test_verificar_cli` y una verificación manual `uv run python -m cripta --verificar <cripta> --offline` con el paquete actual (debe dar código 2 y "resolubilidad no verificada"). Cita FR-017, FR-018a, FR-022.

**Punto de control**: US4 funciona y se puede automatizar.

---

## Fase 7: US5 - Reutilizar la ubicación de llaves sin repetir solicitudes (P3)

**Meta**: la consulta cuenta en el presupuesto, se guarda por versión y se reutiliza.

**Prueba independiente**: verificar dos veces la misma versión y comprobar 0 solicitudes de llaves en la segunda.

### Pruebas de US5 (escribir primero; DEBEN fallar)

- [X] T062 [P] [US5] En `pruebas/test_llaves_adaptadores.py`, `test_us5_1_reutiliza_misma_version`: dos llamadas a `obtener_ubicaciones_llaves` con la misma versión; la fuente recibe una sola consulta (la segunda lee `llaves.json`). Docstring cita FR-020, SC-005.
- [X] T063 [US5] En `pruebas/test_llaves_adaptadores.py`, `test_us5_2_version_distinta_no_reutiliza`: cambiar la versión de la cripta hace que `validar_cripta` borre `llaves.json` y se consulte de nuevo. Docstring cita FR-021.
- [X] T064 [US5] En `pruebas/test_llaves_adaptadores.py`, `test_us5_3_cuenta_en_presupuesto`: con `NetworkAdapter` y `unittest.mock.patch` sobre `requests.get` (el adaptador no tiene sesión inyectable y llama a `requests.get` directamente; NO modificar el adaptador para la prueba), `requests_made` aumenta en 1 por la consulta y con presupuesto agotado se lanza `PresupuestoAgotado`, que el servicio convierte en `UbicacionLlavesNoDisponible`. Docstring cita FR-019.
- [X] T065 [US5] En `pruebas/test_llaves_adaptadores.py`, pruebas de adaptadores: `AdaptadorOffline` lee de la caché y luego del paquete, da `FileNotFoundError` sin ninguno y no cuenta solicitudes; `Guardar_Llamadas_API` graba `cripta_<id>_llaves.json`; un `llaves.json` dañado equivale a `None`; una respuesta sin `llaves` es "no disponible" mientras una lista vacía válida es legítima. Docstrings citan FR-018, FR-020 y FR-022.

### Implementación de US5

- [X] T066 [US5] Corregir en `src/cripta/servicio/CriptaService.py` y en los adaptadores lo que T062 a T065 muestren fallando (guardar solo tras una respuesta válida y solo si `_cripta_en_disco`; no reutilizar datos de otra versión). Cita FR-019, FR-020, FR-021.
- [X] T067 [US5] Ejecutar `uv run python -m unittest pruebas.test_llaves_adaptadores`; deben pasar. Cita FR-019 a FR-021, SC-005.

**Punto de control**: US5 completa; el presupuesto de red queda protegido.

---

## Fase 8: US6 - Medir el rendimiento frente a la alternativa ingenua (P3)

**Meta**: sección "Resolubilidad" en `--bench` con M1 a M7, determinista por semilla.

**Prueba independiente**: `uv run python -m cripta --bench --semilla 42` dos veces.

### Pruebas de US6 (escribir primero; DEBEN fallar)

- [X] T068 [P] [US6] En `pruebas/test_bench_resolubilidad.py`, `test_us6_1_mide_ambas_alternativas`: la función de medición devuelve y el texto impreso contiene tiempos de la verificación y de la ingenua para criptas sintéticas con llaves encadenadas. Docstring cita FR-026.
- [X] T069 [US6] En `pruebas/test_bench_resolubilidad.py`, `test_us6_2_misma_semilla_misma_cripta`: dos generaciones con la misma semilla son idénticas (S, E, K y contenido de salas y ubicaciones) y semillas distintas difieren; semilla vacía equivale a 42. Docstring cita FR-026.
- [X] T070 [US6] En `pruebas/test_bench_resolubilidad.py`, `test_us6_3_escala_casi_lineal`: sobre tamaños pequeños (200 y 2 000 salas) el conteo de operaciones (recorridos de salidas y llaves obtenidas) crece de forma lineal con S, E y K y es menor que el de la ingenua. Se mide por conteo de operaciones, no por tiempo, para que no dependa de la máquina. Docstring cita FR-024.
- [X] T071 [US6] En `pruebas/test_bench_resolubilidad.py`, `test_generador_resoluble_y_con_ciclo`: la variante resoluble da `resoluble` y la variante con ciclo final da `no_resoluble` con al menos un ciclo. Docstring cita FR-026 y FR-012.
- [X] T071a [US6] En `pruebas/test_bench_resolubilidad.py`, `test_limite_200ms_cripta_sintetica_grande`: generar con semilla fija una cripta sintética de al menos 10 veces las salas del esqueleto más grande de `datos_offline` (el tamaño se lee del paquete en la prueba, sin copiar ids ni datos; si el paquete no está, usar 10 veces 2 000 salas), verificar sin red (fuente falsa, 0 solicitudes) y comprobar que tarda menos de 200 ms (mejor de 3 corridas, con `time.perf_counter`). Docstring cita FR-023 y SC-003.
- [X] T071b [US6] En `pruebas/test_bench_resolubilidad.py`, `test_bench_no_importa_arcade`: ejecutar `--bench` en un subproceso limpio (`sys.executable -I -m cripta --bench --semilla 42`, o `bench.main` en un proceso con `arcade` ausente de `sys.modules`) y comprobar que `arcade` no se importa y no se instancia la vista. Docstring cita FR-028.

### Implementación de US6

- [X] T072 [US6] En `src/cripta/bench.py`, generador sintético determinista con `random.Random(semilla)` según D8: región base conectada por árbol aleatorio con salidas abiertas, cadena de K llaves (la puerta j exige la llave j-1 y la llave j está en la sala que esa puerta abre), ramas decorativas y ubicaciones repetidas, ids de sala permutados por la semilla, variante con ciclo final. Cita FR-026.
- [X] T073 [US6] En `src/cripta/bench.py`, implementar la alternativa ingenua O(K · (S + E)) (repite la exploración completa cada vez que se obtiene una llave), marcada como descartada, solo para medición. Cita FR-024, FR-026.
- [X] T074 [US6] En `src/cripta/bench.py`, medición M1: verificación frente a la ingenua en 200, 2 000 y 20 000 salas (la ingenua hasta 2 000); la ingenua debe perder y la brecha crecer con K. Cita FR-024, FR-026, SC-004.
- [X] T075 [US6] En `src/cripta/bench.py`, medición M2: escalado de la verificación al multiplicar por 10 el tamaño; imprimir el cociente y marcar si es menor que 15. Cita FR-024, SC-004.
- [X] T076 [US6] En `src/cripta/bench.py`, medición M3: verificar la cripta de referencia del paquete si trae `cripta_<id>_llaves.json` (imprimir el tiempo sin red y marcar si es menor que 200 ms); si no, imprimir "sin llaves en el paquete". Sigue midiendo la cripta real cuando haya llaves. Cita FR-023, SC-003.
- [X] T076a [US6] En `src/cripta/bench.py`, medición M7: cripta sintética por semilla de al menos 10 veces las salas del esqueleto más grande de `datos_offline` (tamaño leído del paquete), verificada sin red; imprimir S, E, K, el tiempo y si es menor que 200 ms. Se ejecuta aunque el paquete no traiga llaves. Cita FR-023, SC-003.
- [X] T077 [US6] En `src/cripta/bench.py`, medición M4: índice de llaves con arreglo ordenado y búsqueda binaria frente a tabla hash propia con hash polinomial determinista (sin `hash()` de Python), a 20 000 salas; regla de decisión: se conserva el arreglo salvo que el hash gane por más de 2 veces. Cita FR-024, FR-008.
- [X] T078 [US6] En `src/cripta/bench.py`, medición M5: costo del reporte (fase especulativa y ciclos) sobre la verificación pura, variante con ciclo; debe ser lineal y sin repetir exploraciones. Cita FR-025.
- [X] T079 [US6] En `src/cripta/bench.py`, medición M6: orden por ronda con `ordenar` frente a orden de cola sin ordenar; documentar el sobrecosto frente a SC-004. Cita FR-008, FR-024.
- [X] T080 [US6] Modificar `src/cripta/bootstrap.py` y `bench.main`: bandera `--semilla N` para `--bench` (vacía equivale a 42, nunca aleatoria), sin efecto en `--verificar`, y sin abrir la vista. Cita FR-026, FR-028.
- [X] T081 [US6] Ejecutar `uv run python -m unittest pruebas.test_bench_resolubilidad` y `uv run python -m cripta --bench --semilla 42` dos veces; los conteos deben coincidir y los tiempos de M1 a M7 deben imprimirse. Guardar la salida en `specs/001-resolubilidad/mediciones.txt` para la sección de decisiones. Cita FR-023, FR-024, FR-026.

**Punto de control**: las seis historias completas, con evidencia medida.

---

## Fase 9: Cierre y transversales

- [X] T082 Redactar la sección "12. Resolubilidad de la cripta (Parte II, §3.5 y §5.4)" en `docs/decisiones.md` (el documento DECISIONES de este problema), con el mismo estilo de las secciones 1 y 2: algoritmo (exploración en anchura por rondas con listas de espera por llave, D1 y D2), alternativas descartadas (repetir la exploración por llave, punto fijo, recursión, conjuntos disjuntos, cola de prioridad) con su costo, estructuras propias y por qué (D3 y D4), complejidad O(S + E + K) más el factor log K del índice y su justificación, definición de ciclo del grafo de testigos y sus tres lemas (D6), consulta de llaves, presupuesto y persistencia (D7), replay y cargas sin verificar (D8), y la comparación medida con los números de `mediciones.txt` (M1 a M7), incluida la decisión del arreglo frente a la tabla hash. Cita FR-001, FR-008, FR-012, FR-024 y FR-026.
- [X] T083 [P] Actualizar `README.md`: banderas `--verificar`, `--forzar` y `--semilla` con un ejemplo cada una, códigos de salida 0, 1 y 2, y el enlace a la nueva sección de `docs/decisiones.md`. Cita FR-016, FR-017, FR-018a.
- [X] T084 [P] Actualizar `docs/estructuras.md` con `ColaLista` e `IndiceLlaves` (operaciones y costo). Cita FR-024.
- [X] T085 Ejecutar los siete escenarios de `specs/001-resolubilidad/quickstart.md` en orden y anotar el resultado de cada uno al final de ese archivo bajo "Resultado de la validación". Cita FR-006, FR-007, FR-009 a FR-013, FR-014 a FR-018, FR-018a, FR-019 a FR-024, FR-026, FR-028 y SC-001 a SC-007.
- [X] T086 Regresión contra la línea base: ejecutar de nuevo los comandos (a) y (b) de T001. La selección de pruebas del README DEBE seguir pasando y la suite completa de `pruebas/` NO DEBE tener fallas nuevas respecto de `specs/001-resolubilidad/linea_base.txt`; comparar nombre por nombre las pruebas que fallan y registrar el resultado en `specs/001-resolubilidad/regresion.txt`. Una falla de la línea base que persiste no cuenta como nueva. Protege FR-022, FR-027 y FR-029.

---

## Dependencias y orden de ejecución

- **Fase 1 (T001)** antes de todo. Ningún cambio de código antes de que la línea base esté confirmada.
- **Fase 2** depende de T001 y bloquea las historias. Dentro de ella: T003 antes de T004; T005 antes de T006; T008 antes de T009 a T013; T010 antes de T011; T013 antes de T014; T007, T010 y T008 antes de T015.
- **US1** (T016 a T029) depende de la Fase 2 (T002, T004, T006). **US2** depende de US1 (misma exploración y mismo archivo). **US3** depende de US2 (necesita reporte y controlador). **US4** depende de US2 (formato del reporte) y es independiente de US3 salvo por `bootstrap.py` (T052 antes de T059 para evitar conflictos en el mismo archivo). **US5** depende solo de la Fase 2 (T015) y puede ir en paralelo con US1 y US2. **US6** depende de US2 (modelo completo) y de T080 después de T052 y T059 por `bootstrap.py`. T071a y T071b se escriben con las demás pruebas de US6 (antes de T072) y T076a va después de T076 en `bench.py`.
- **Fase 9** al final; T086 es la última tarea.

### Oportunidades de paralelismo

- Fase 2: T002, T003, T005 y T007 en paralelo; luego T009, T010 y T012.
- US5 (T062 a T067) en paralelo con US1 y US2 por vivir en archivos distintos.
- Archivos de prueba distintos entre historias (`test_inicio_verificacion.py`, `test_verificar_cli.py`, `test_llaves_adaptadores.py`, `test_bench_resolubilidad.py`) pueden escribirse a la vez.
- T083 y T084 en paralelo.
- Las tareas que editan el mismo archivo (`Resolubilidad.py`, `bootstrap.py`, `bench.py`, `VerificacionControlador.py`, `test_resolubilidad.py`) NO son paralelas.

## Estrategia de implementación

1. **MVP**: Fases 1 y 2, US1 y US2. Con eso el modelo decide y explica, y se puede probar sin vista.
2. **Incremento 2**: US3 y US4 conectan la capacidad con la partida y la consola.
3. **Incremento 3**: US5 y US6 protegen el presupuesto y dan la evidencia medida.
4. Cerrar con T082 a T086. No marcar una historia como terminada sin que sus pruebas pasen y sin que la selección del README siga en verde.

## Cobertura de escenarios de aceptación

| Escenario | Prueba | FR |
|-----------|--------|----|
| US1.1 a US1.5 | T016 a T020 | FR-006, FR-007, FR-008, FR-002, FR-004 |
| US2.1 a US2.5 | T030 a T034 | FR-009 a FR-013 |
| US3.1 a US3.4 | T043 a T046 | FR-014, FR-015, FR-016, FR-022 |
| US4.1 a US4.3 | T055 a T057 | FR-017, FR-018, FR-018a, FR-028 |
| US5.1 a US5.3 | T062 a T064 | FR-019, FR-020, FR-021 |
| US6.1 a US6.3 | T068 a T070 | FR-024, FR-026 |
| Límite de 200 ms (sintética) y `--bench` sin vista | T071a, T071b | FR-023, FR-028 |
| Apéndice B 1 a 4 | T030, T020, T019, T043 | FR-012, FR-004, FR-008, FR-015 |

## Cierre de entrega (17/11/2026)

- [x] T090 Registrar y probar intentos HTTP, 429, transporte, presupuesto y rotación; documentar red.log (FR-030).
- [x] T091 Completar la herramienta de descarga, capturar datos actuales en datos_entrega y probar verificación offline sin red conservando el replay histórico (FR-018, FR-020, FR-031).
