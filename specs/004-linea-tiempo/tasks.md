# Tareas: Línea de tiempo y puntos de control

**Entrada**: `specs/004-linea-tiempo/` (spec.md, plan.md, research.md, data-model.md, quickstart.md)

**Requisitos previos**: plan.md y spec.md. Las decisiones D1 a D12 de research.md son definitivas.

**Pruebas**: hay una prueba `unittest` en `pruebas/` por cada escenario del Apéndice B de línea de
tiempo (SC-001) y por los requisitos principales; cada prueba cita su FR en el docstring.

**Organización**: por historia de usuario (US1 a US7).

## Formato: `[ID] [P?] [Historia] Descripción con ruta`

- **[P]**: se puede hacer en paralelo (archivos distintos, sin dependencia de tareas incompletas).
- Cada tarea cita al menos un FR.

## Reglas transversales (constitución)

- Sin `dict`, `set`, `heapq`, `bisect`, `collections`, `sorted()` ni `list.sort()` en el código de
  esta capacidad (principio I).
- `Simulacion` y `Historial_Retroceso` solo ganan ganchos opcionales; no conocen la línea
  (principio III). `--bench` y `--replay --hasta` no instancian la vista (FR-033).
- Ningún dato de una cripta concreta en código ni en pruebas (principio IV).
- Docstring de cada prueba: `"""FR-0xx: ..."""`; las del Apéndice B dicen además `Apéndice B, caso n`.

---

## Fase 1: Preparación

- [ ] T001 Confirmar en Git `spec.md` y el checklist antes de cualquier código (hecho en `20557fc`), y en otro commit `plan.md`, `research.md`, `data-model.md`, `quickstart.md` y este `tasks.md`. Cita FR-001 a FR-034.
- [ ] T002 Con el código sin modificar, registrar en `specs/004-linea-tiempo/linea_base.txt` el commit, el comando de pruebas y las pruebas que ya fallan. Protege FR-006.

## Fase 2: Fundamentos (bloquea todo lo demás)

- [ ] T003 [P] Crear `src/cripta/estructuras/Linea_Tiempo.py` con `LineaTiempo`: ranuras (`nueva_ranura`), bitácora en listas paralelas (`registrar`), marcas (`marcar`, `acciones`), puntos de control cada K marcas con índice `a // K`, búsqueda binaria propia de marcas (`ubicar_tiempo`, `ubicar_accion`), reconstrucción `estado_en(pos, modo)` con modos `adelante`, `atras` y `cercano`, `recortar(m)`, `con_k(k)`, `memoria()`, `a_datos()` y `desde_datos()`. Cita FR-012, FR-013, FR-014, FR-015, FR-016 y FR-019 (no se re-simula, D1 y D7: el estado del azar no hace falta).
- [ ] T004 [P] `pruebas/test_linea_tiempo.py`: registrar solo cambios reales; ubicar instantes (igual a una marca, entre marcas, antes de la primera); los tres modos dan el mismo estado; ninguna reconstrucción aplica más de K acciones; puntos de control ≤ N/K + 1; recorte restaura el vector vivo y quita puntos de control; `con_k` describe la misma partida; ida y vuelta por `a_datos`. Cita FR-012 a FR-016.
- [ ] T005 Agregar a `Historial_Retroceso` el atributo `observador` (None por defecto) llamado desde `registrar`, y a `Simulacion` el atributo `al_terminar_evento` llamado tras cada evento en `avanzar_hasta_turno_jugador`. Cita FR-001, FR-006.
- [ ] T006 Crear `src/cripta/dto/Historia_dto.py` con `ResumenInstante` y `ResultadoHistoria`. Cita FR-005.
- [ ] T007 Crear `src/cripta/controlador/LineaTiempoControlador.py`: ranuras fijas y de conocimiento, tabla de enemigos, observador, `capturar()`, `antes_de_accion()`, `cancelar_accion()`, `tras_pergamino()`, `conectar(sim)`. Cita FR-001, FR-006, FR-008, FR-010, FR-011, FR-020.
- [ ] T008 Enlazar en `Aplicacion` (K, controlador, `historia()`), `InicioPartidaControlador` (crear la línea al iniciar), `CicloAccionesControlador.ejecutar` (marca, captura tras la acción y al cerrar, recorte si falla) y `usar_pergamino` (recorte y captura). Cita FR-001, FR-008, FR-010, FR-011.

## Fase 3: US1 y US2, consultar un instante (P1)

- [ ] T009 [US1] `historia(texto)` en el controlador: análisis de `<t>` y `#k`, rechazos (FR-004), resumen con sala, vida, estadísticas, inventario, efectos, enemigos de la sala y mapa conocido (FR-005, FR-020) y formato de texto compartido con el replay. Cita FR-002 a FR-005, FR-009.
- [ ] T010 [US1] `pruebas/apoyo_linea.py` y `pruebas/test_historia.py`: rechazo de t futuro (Apéndice B, caso 1; FR-004); eventos en el mismo instante (Apéndice B, caso 3; FR-001); consulta sin efectos sobre reloj, partida.log, historial y azar (Apéndice B, caso 4; FR-007); cada resumen anotado durante el juego coincide con `historia <t>` y `historia #k` (FR-006, SC-002); `historia 0` (US1-6); `#1`, `#N+1`, `#0`, `#N+2` (FR-003, FR-004); consulta tras terminar la partida (FR-009); mismo resultado con dos K (US6-3). Cita FR-001 a FR-009.

## Fase 4: US3, pergamino (P1)

- [ ] T011 [US3] `pruebas/test_historia_retroceso.py`: tras un pergamino, ningún instante muestra lo revertido (Apéndice B, caso 2; FR-010); `#k` renumera (US3-2); acción nueva tras el pergamino (US3-3); el pergamino aparece descontado (FR-011); acción rechazada no deja marca (FR-008). Cita FR-010, FR-011.

## Fase 5: US4, replay sin vista (P2)

- [ ] T012 [US4] `reproducir(..., hasta=None)` en `replay/reproductor.py` y `--hasta` en `bootstrap.py` con validación (FR-023). Cita FR-021 a FR-023, FR-033.
- [ ] T013 [US4] `pruebas/test_historia_replay.py`: `--hasta t` igual a `historia <t>` (FR-021); t posterior al final (Apéndice B, caso 5; FR-022); `--hasta` inválido y sin `--replay` (FR-023). Cita FR-021 a FR-023.

## Fase 6: US5, guardado (P2)

- [ ] T014 [US5] `guardado/Formato.py` (versión 3, `ID_LINEA`), `Escritura.py` (cuerpo de línea con valores etiquetados), `Lectura.py` (rechazo de versión 2 como Parte I), `Datos.py`, `GuardadoControlador.cargar` (restaurar conocimiento y línea, aviso de K, historial vacío). Cita FR-024 a FR-027, FR-034.
- [ ] T015 [US5] `pruebas/test_historia_guardado.py`: resúmenes iguales tras guardar y cargar (FR-024); mapa conocido idéntico (FR-025); archivo de la Parte I rechazado (Apéndice B, caso 6; FR-026); la línea continúa y el K guardado manda con aviso (FR-027); el pergamino no revierte lo anterior a la carga (FR-034). Cita FR-024 a FR-027, FR-034.

## Fase 7: US6, K y memoria (P2)

- [ ] T016 [US6] `--checkpoint-cada K` en `bootstrap.py` hacia `Aplicacion` (interactivo y replay), rechazo de K inválido antes de iniciar (FR-017), `K_POR_DEFECTO` (FR-018). Cita FR-013, FR-017, FR-018.
- [ ] T017 [US6] Pruebas en `pruebas/test_historia.py`: puntos de control ≤ N/K + 1 en una partida real (US6-1); K inválido termina con código 2 (US6-4). Cita FR-013, FR-015, FR-017.

## Fase 8: Interfaz (FR-028)

- [ ] T018 `vista/grafica/historia.py` (panel de entrada) y `ventana.py` (tecla H, entrada de menú, ayuda). Cita FR-028.

## Fase 9: US7, mediciones (P3)

- [ ] T019 [US7] `bench.py`: partida larga determinista, L1 a L5 y sección «Línea de tiempo» en `main`. Cita FR-029 a FR-033.
- [ ] T020 [US7] `pruebas/test_bench_linea.py`: L1 informa los K pedidos y la alternativa sin puntos de control y es determinista; ninguna reconstrucción supera K acciones. Cita FR-030, FR-031.
- [ ] T021 Ejecutar `--bench`, fijar `K_POR_DEFECTO` con L1 y guardar la salida en `specs/004-linea-tiempo/mediciones.txt`. Cita FR-018, FR-029.

## Fase 10: Cierre

- [ ] T022 `docs/decisiones.md`: sección 17 (§5.5, línea de tiempo) y 18 (§5.6, retroceso), con enlaces a spec y plan y si la decisión coincide con el plan. Cita FR-018, FR-030 a FR-032.
- [ ] T023 `README.md`: `--checkpoint-cada`, `--replay ... --hasta`, tecla H y pruebas de la spec 004. Cita FR-017, FR-021, FR-028.
- [ ] T024 Suite completa contra `linea_base.txt` y registro en `specs/004-linea-tiempo/regresion.txt`. Protege FR-006.
- [ ] T025 Entradas de `docs/PROMPTS_LLM.md` con los prompts reales de esta sesión. Constitución, flujo de trabajo.

## Dependencias

T003 → T004; T003, T005, T006 → T007 → T008 → T009 → T010; T008 → T011; T009 → T012 → T013;
T008 → T014 → T015; T008 → T016 → T017; T009 → T018; T009 → T019 → T020, T021 → T022.
