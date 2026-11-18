# Plan de implementación: Terreno con costo y enemigo cazador

**Rama**: `fiore` | **Fecha**: 2026-11-16 | **Spec**: [spec.md](spec.md)

**Entrada**: especificación `specs/003-terreno-cazador/spec.md` (FR-001 a FR-028, SC-001 a SC-007)

## Resumen

Moverse por una salida pasa a costar el costo de esa salida, para el jugador y para todos los
enemigos. El costo se fija antes de mover: el jugador lo pasa desde `ExploracionControlador.mover`
hasta `consumir_tiempo`, y cada enemigo lo devuelve en su decisión `[tipo, destino, costo]`. El
reescalado por cambio de velocidad ya existe y no se toca.

El cazador es una subclase de `Enemigo`. Todos los cazadores comparten una sola búsqueda: un
Dijkstra inverso desde la sala del jugador con el `BuscadorRutas` y el `MonticuloMinimo` de la spec
002 (se confirma C11 y D9), sobre las salidas abiertas en ese instante y cortado al superar el
mayor rango registrado. Cada cazador lee su distancia y elige su paso con el mismo desempate que
«ir a». Las distancias se reutilizan mientras no cambien la sala del jugador, las puertas ni el
historial, y eso se detecta con dos contadores monótonos. Las decisiones de esta sección se
detallan en [research.md](research.md) (D1 a D12, mediciones H1 a H8).

## Contexto técnico

**Lenguaje/Versión**: Python 3.13, gestionado con uv.

**Dependencias principales**: `arcade` (solo vista), `json` y `struct`. Ninguna dependencia nueva.

**Almacenamiento**: guardado binario existente; se agrega el rango del cazador de forma compatible
(D10).

**Pruebas**: `unittest` en `pruebas/`.

**Plataforma**: Windows con CMD (equipo); el código no depende de la plataforma.

**Tipo de proyecto**: aplicación de escritorio MVC con modos de consola (`--bench`, `--replay`,
`--verificar`).

**Metas de rendimiento**: FR-025. Ciclo de eventos entre dos decisiones del jugador con al menos 50
cazadores activos en la cripta de referencia menor que 20 ms; recálculo de distancias proporcional
a la región del rango, no al tamaño de la cripta.

**Restricciones**: sin `dict`, `set`, `heapq`, `bisect`, `collections`, `networkx`, `sorted()` ni
`list.sort()` (principio I). Ninguna cola de prioridad nueva: se reutiliza `MonticuloMinimo`. El
modelo NO DEBE conocer HTTP, archivos ni vista (principio III).

**Escala**: cripta de referencia = esqueleto mayor de `datos_offline`; criptas sintéticas de 200 a
20 000 salas; de 1 a 100 cazadores.

Sin puntos NEEDS CLARIFICATION: los seis de la sesión de clarificación están en la spec.

### Archivos leídos

`modelo/Rutas.py`, `estructuras/Monticulo_Minimo.py`, `modelo/Simulacion.py`, `modelo/Actor.py`,
`modelo/Enemigo.py`, `modelo/enemigos/*.py`, `modelo/Puertas.py`, `util/Costo_Acciones.py`,
`estructuras/Salidas.py`, `estructuras/Indice_Salas.py`, `estructuras/Agenda_Eventos.py` (firmas),
`estructuras/Historial_Retroceso.py` (firmas), `controlador/CicloAccionesControlador.py`,
`controlador/CombateControlador.py`, `controlador/ExploracionControlador.py`,
`controlador/ViajeControlador.py`, `controlador/Aplicacion.py` (partes),
`controlador/PartidaControlador.py` (partes), `controlador/guardado/{Escritura,Lectura,Datos}.py`
(partes), `dto/EnemigoDto.py`, `dto/FactoryDto_Partida.py`, `dto/Partida_dto.py`,
`vista/grafica/escena.py` (enemigos y minimapa), `bench.py` (estructura), `docs/api.md` (enemigo),
y de la spec 002 `research.md` D9 y `plan.md`. Los hechos que condicionan el diseño están al inicio
de [research.md](research.md).

## Constitution Check

*Compuerta previa a la investigación; reevaluada tras el diseño. Resultado: aprobada, con un
requisito pendiente del principio VII antes de implementar.*

| Principio | Evaluación | Cumple |
|-----------|------------|--------|
| I. Estructuras propias | Se reutilizan `MonticuloMinimo` y `BuscadorRutas` (listas paralelas, marcas por generación). La clave de validez son tres enteros; los contadores son enteros. Ningún `dict` ni `set`; el comportamiento se despacha con `match`, como hoy. | Sí |
| II. Determinismo | Sin azar nuevo en el modelo. Desempate explícito: menor id de destino, luego N, S, E, O. Errante y rastreador conservan el consumo de `azar` (D2). `--bench` usa `random.Random(semilla)`. | Sí |
| III. MVC | `Cazador` y `Persecucion` en `modelo/`, sin E/S. La vista solo lee `EstadoPartida`. `--bench` y `--replay` no instancian la vista. | Sí |
| IV. Sin datos de cripta | Ni ids ni rangos en el código; la cripta de referencia se descubre al leer `datos_offline`; las pruebas arman sus fichas y esqueletos. | Sí |
| V. Presupuesto de red | Ninguna solicitud nueva: el rango viaja en la ficha que ya se pide; restaurar no pide la ficha (D10). | Sí |
| VI. Rendimiento con evidencia | H1 a H8 comparan cada decisión con una alternativa medida, deterministas por semilla. | Sí |
| VII. Spec primero | `spec.md` aún NO está confirmada en Git. DEBE confirmarse antes del primer commit de código. Cada tarea DEBE citar FR. | Pendiente |

**Reevaluación tras el diseño**: sin violaciones. El plan no agrega reglas de juego: los únicos
puntos donde el código debe elegir algo que la spec no dice están en la tabla de puntos a confirmar.

## Decisiones tomadas y puntos a confirmar

### Decisiones tomadas

1. **D1 Costo del jugador**: `salida.costo` se lee en `ExploracionControlador.mover` y llega a
   `consumir_tiempo(nombre, costo)` por `_accion_jugador` y `ejecutar`; nada usa el costo base.
2. **D2 Costo de enemigos**: `decidir_accion` devuelve `[tipo, destino, costo]`; `Simulacion` usa
   el costo de la salida para `mover`. Errante y rastreador eligen entre salidas sin cambiar el azar.
3. **D3 Reescalado**: sin cambios; `Actor.actualizar_velocidad` ya cumple FR-006. Solo pruebas.
4. **D4 Cazador**: `modelo/enemigos/Cazador.py` con `rango`; atacar, esperar o mover según FR-010 a
   FR-014; predicado `not salida.cerrada`; nunca abre puertas.
5. **D5 Búsqueda compartida**: una búsqueda inversa desde la sala del jugador sirve a todos los
   cazadores; objeto `Persecucion` propiedad de `Simulacion`.
6. **D6 Corte**: parámetro opcional `limite` en `distancias_hacia`, compatible con «ir a»; el
   invariante del corte garantiza la misma decisión que desde cero (FR-017).
7. **D7 Límite**: mayor rango registrado al activar cazadores; solo crece.
8. **D8 Invalidación**: clave `(sala_jugador, agenda.cambios_puertas, historial.reversiones)` más
   `limite_usado ≥ rango`; contadores monótonos.
9. **D9 Ficha**: `FichaEnemigo.rango`; validación en `parsear_ficha`.
10. **D10 Guardado**: rango escrito solo para cazadores, sin subir `VERSION_CUERPO`; restaurar
    registra los rangos en la persecución nueva.
11. **D11 Vista**: costo junto a cada puerta; marca propia y texto «cazador · rango r» para
    cazadores vivos.
12. **D12 Bench**: `generar_cripta_cazadores` sobre la cuadrícula de la spec 002 y la cripta de
    referencia; mediciones H1 a H8.

### Puntos a confirmar

| # | Punto | Propuesta por defecto | Dónde se decide |
|---|-------|-----------------------|-----------------|
| C1 | FR-009 dice «la carga de la cripta se rechaza», pero las fichas llegan por lotes durante la partida | El rechazo ocurre al incorporar la ficha; si es en plena partida, falla el movimiento que necesitaba ese contenido. Corregir la redacción de FR-009 en la spec (commit aparte) | Equipo, en `/speckit-analyze` |
| C2 | FR-018: la muerte de otros actores no cambia la decisión | Se implementa así; pendiente de confirmar con el profesor (ya en la spec) | Profesor |
| C3 | Errante o rastreador con dos salidas hacia la misma sala: costo de cuál | La salida candidata que hoy ya resulta elegida (orden de las salidas en la sala), sin regla nueva | Equipo |
| C4 | Mensaje en la bitácora cuando un cazador entra a la sala del jugador | No se agrega: la spec no lo pide | Equipo |
| C5 | Spec sin confirmar en Git | Confirmarla antes de `/speckit-implement` | Equipo |

## Estructura del proyecto

### Documentación (esta capacidad)

```text
specs/003-terreno-cazador/
├── plan.md              # este archivo
├── research.md          # D1 a D12, mediciones H1 a H8
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── decision-enemigo.md
│   ├── ficha-cazador.md
│   └── bench-cazador.md
├── checklists/requirements.md
└── tasks.md             # lo crea /speckit-tasks
```

### Código fuente (raíz del repositorio)

```text
src/cripta/
├── modelo/
│   ├── Rutas.py                     # + parámetro opcional `limite` (D6)
│   ├── Persecucion.py               # NUEVO: búsqueda compartida y clave de validez (D5, D7, D8)
│   ├── Simulacion.py                # posee Persecucion; costo de la decisión (D2)
│   ├── Enemigo.py                   # decidir_accion devuelve [tipo, destino, costo]
│   ├── Puertas.py                   # sube agenda.cambios_puertas
│   └── enemigos/
│       ├── Cazador.py               # NUEVO (D4)
│       ├── Errante.py               # elige salida, mismo azar (D2)
│       ├── Rastreador.py            # devuelve el costo de la salida (D2)
│       └── Guardian.py              # nuevo formato de decisión
├── estructuras/
│   ├── Agenda_Eventos.py            # + cambios_puertas
│   └── Historial_Retroceso.py       # + reversiones
├── controlador/
│   ├── ExploracionControlador.py    # pasa salida.costo (D1)
│   ├── Aplicacion.py                # _accion_jugador(..., costo); configura la persecución
│   ├── CicloAccionesControlador.py  # consumir_tiempo(nombre, costo)
│   ├── CombateControlador.py        # caso cazador; registrar_rango al activar
│   └── guardado/{Escritura,Lectura,Datos,Restauracion}.py   # rango del cazador (D10)
├── dto/
│   ├── EnemigoDto.py                # FichaEnemigo.rango
│   ├── FactoryDto_Ficha.py          # validación del rango (D9)
│   ├── FactoryDto_Partida.py        # copia el rango
│   └── Partida_dto.py               # EnemigoPartida.rango
├── vista/grafica/escena.py          # costos de puertas y marca de cazador (D11)
└── bench.py                         # H1 a H8 (D12)

pruebas/
├── test_costo_movimiento.py         # US1, Apéndice B casos 6 y 7
├── test_cazador.py                  # US2, casos 1 a 4
├── test_cazador_puertas.py          # US3 y caso 5
├── test_persecucion.py              # corte, clave de validez, propiedad desde cero
├── test_ficha_cazador.py            # FR-008, FR-009
├── test_cazador_guardado.py         # US5
└── test_bench_cazador.py            # US6, formato y determinismo

docs/
├── api.md                           # comportamiento cazador y campo rango
├── decisiones.md                    # sección 14
└── estructuras.md                   # Persecucion y contadores
```

**Decisión de estructura**: proyecto único existente; solo dos módulos nuevos (`Persecucion.py` y
`Cazador.py`), el resto son ampliaciones.

## Complejidad agregada

| Elemento | Por qué hace falta | Alternativa más simple rechazada |
|----------|--------------------|----------------------------------|
| Clave de validez con dos contadores | Reutilizar distancias entre turnos sin perder FR-017 | Recalcular por turno: C búsquedas por ciclo; se mide en H3 y se conserva la clave salvo que la alternativa gane por más de 2 veces |
| Parámetro `limite` | Costo según la región del rango (FR-025) | Búsqueda completa: O(S log S) por recálculo; se mide en H2 |
