# Investigación y decisiones: Terreno con costo y enemigo cazador

**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Fecha**: 2026-11-16

Cada decisión indica qué se eligió, por qué, qué alternativas se evaluaron, su complejidad y qué
medición de `--bench` la respalda (principio VI). Las mediciones H1 a H8 se describen al final.
Notación: S salas de la cripta, E salidas, C cazadores activos, R mayor rango registrado,
V_R salas a costo menor o igual que R desde la sala del jugador, A_R salidas que entran a ellas.

Hechos del código que condicionan el diseño (leídos en la rama):

- `BuscadorRutas.distancias_hacia(destino, entrantes, usable, parar_en)` ya hace un Dijkstra
  inverso desde el destino con `MonticuloMinimo` y eliminación perezosa. Sus listas `distancia` y
  `marca` (con `generacion`) se reutilizan entre búsquedas. `elegir_paso` ya desempata por menor id
  de destino y luego N, S, E, O, que es exactamente FR-013 y FR-014.
- Cada dirección de una sala es un `SalidaSimple` propio con su `cerrada` y su `costo`; la clave
  es `origen * 4 + dirección`. `ExploracionControlador.entrantes` ya existe y no es estado del juego.
- Las puertas solo cambian con `agenda.cambiar(salida, "cerrada", ...)` en `Puertas.abrir_salida`
  y `Puertas.procesar_cierre_puerta`, más la reversión del historial (`setattr` directo) y la
  restauración de un guardado (`Restauracion`, sobre una simulación nueva).
- `CicloAccionesControlador.consumir_tiempo` calcula el intervalo con `costo_accion(nombre)`, sin
  saber qué salida se usó. `Simulacion._ejecutar_turno_enemigo` hace lo mismo con la acción que
  devuelve `decidir_accion`, que hoy es `[tipo, destino]`.
- `Actor.actualizar_velocidad` ya reescala cualquier evento pendiente con
  `reescalar_tiempo_siguiente` (P1 §2.3, mínimo 1), sea cual sea su costo.
- `FactoryDto_Partida` ya normaliza a 100 un costo ausente o menor que 1 y avisa (FR-002).
- `FichaEnemigo(**d)` rechaza campos no declarados: una ficha con `rango` hoy falla.
- Ninguna cripta de `datos_offline` declara `costo` ni un enemigo `cazador`: las partidas y
  registros existentes no cambian de tiempos con esta capacidad.
- El minimapa ya muestra el costo, pero solo en el texto emergente de cada vecina.

---

## D1. Dónde se calcula el costo del movimiento del jugador

**Decisión**: `ExploracionControlador.mover` ya obtiene la `SalidaSimple` antes de mover; pasa
`salida.costo` a `Aplicacion._accion_jugador(..., costo=salida.costo)`, que lo entrega a
`CicloAccionesControlador.ejecutar(..., costo)` y este a `consumir_tiempo(nombre_costo, costo)`.
Si `costo` es nada, se usa `costo_accion(nombre_costo)` como hoy (FR-005). El intervalo es
`calcular_intervalo(costo, velocidad)` (FR-004).

**Razón**: el costo se fija antes de mover, cuando la sala de origen y la dirección son ciertas.
Cada paso de «ir a» llama a `Aplicacion.mover`, así que FR-007 se cumple sin tocar el viaje.

**Alternativas**:
- Buscar la salida dentro de `consumir_tiempo` con la sala de origen y el argumento: depende de
  guardar la sala de origen y duplica la búsqueda de la salida.
- Un `costo_accion("mover", salida)` global: mezcla la tabla de costos base con el terreno.

**Complejidad**: O(1) adicional por movimiento. Sin medición propia: no hay alternativa de costo
distinto; la corrección se prueba con FR-004 (SC-002).

## D2. Costo del movimiento de los enemigos

**Decisión**: `decidir_accion` devuelve `[tipo, destino, costo]`. Para `mover`, `costo` es el de la
salida elegida; para el resto es nada y `Simulacion` usa `costo_accion(tipo)`. Errante y rastreador
pasan a elegir entre las salidas (no entre los destinos), en el mismo orden y con la misma cantidad
de candidatos que hoy, de modo que `azar.choice` consume el azar igual y la elección no cambia.

**Razón**: la salida es conocida en el instante de decidir; después de mover, el origen ya cambió.
Mantener el mismo consumo del azar preserva el determinismo de las partidas grabadas (principio II).

**Alternativas**:
- Que `Simulacion` busque la salida de origen a destino después de decidir: ambigua si dos salidas
  llevan a la misma sala, y obliga a recordar el origen.
- Guardar el costo en el enemigo como atributo: estado extra que el historial tendría que revertir.

**Complejidad**: O(1) adicional por decisión. Se verifica con la prueba de regresión de partidas
grabadas (mismo estado final antes y después del cambio) y con H8.

## D3. Reescalado por cambio de velocidad

**Decisión**: no se cambia código. `Actor.actualizar_velocidad` ya reescala el evento pendiente con
`max(1, restante * v_anterior // v_nueva)` (FR-006). Se agregan pruebas con un movimiento de costo
alto pendiente (Apéndice B, caso 7) y con costo 1 y velocidad alta (caso 6, FR-004).

## D4. El cazador como comportamiento nuevo

**Decisión**: clase `Cazador(Enemigo)` en `modelo/enemigos/Cazador.py`, con atributo `rango`.
`_decidir_movimiento` pide a la persecución compartida (D5) el paso hacia el jugador:

1. Si comparte sala con el jugador, `Enemigo.decidir_accion` ya devuelve `atacar` (FR-010).
2. Pide las distancias vigentes (D8). Sea d la distancia de su sala. Si no hay distancia o
   d > rango, devuelve `esperar` (FR-012).
3. En otro caso, `elegir_paso(sala, salidas, usable)` devuelve la salida; devuelve
   `["mover", salida.sala_destino, salida.costo]` (FR-013, FR-014).

El predicado es `usable(salida) = not salida.cerrada` (estado real, FR-015). El cazador nunca llama
a `abrir_salida` (FR-016). La activación y el sueño no cambian: `CombateControlador.activar_enemigo`
ya agenda la primera acción con costo 100 desde la activación (FR-019).

**Alternativas**: un campo `comportamiento` interpretado dentro de `Enemigo` con un `match`: rompe
el patrón de una subclase por comportamiento que ya usan guardián, errante y rastreador.

## D5. Búsqueda compartida por todos los cazadores (confirma C11 y D9 de la spec 002)

**Decisión**: se confirma D9. Se reutilizan `MonticuloMinimo` y `BuscadorRutas` sin crear otra cola
de prioridad. Una sola búsqueda inversa desde la sala del jugador, con `usable = not cerrada`,
deja en `distancia` el costo mínimo de cada sala hasta el jugador; cada cazador lee su d y elige su
paso con `elegir_paso` sobre esas mismas distancias. Un objeto `Persecucion` (modelo, propiedad de
`Simulacion`) guarda el buscador, la referencia a `entrantes` y la clave de validez (D8).

**Razón**: como las distancias son hacia un único destino (la sala del jugador), una búsqueda sirve
a C cazadores. La regla de desempate es la misma que la de «ir a» por construcción.

**Alternativas**:
- **Una búsqueda por cazador y por turno**, inversa desde el jugador con `parar_en` en la sala del
  cazador, o directa desde el cazador: C búsquedas por ciclo. Es lo más simple y no necesita
  invalidación, pero cuesta C veces más con cazadores agrupados.
- **Búsqueda directa desde el cazador con heurística (A*)**: no hay heurística admisible útil sin
  coordenadas; con heurística nula es lo mismo que la anterior.
- **Distancias de todos contra todos precalculadas**: O(S²) de memoria y se invalidan con cada
  puerta.

**Complejidad**: compartida, O((V_R + A_R) log V_R) por recálculo más O(4) por decisión; individual,
C veces lo anterior por ciclo. **Medición H1** (compartida frente a individual, con 1, 10, 50 y 100
cazadores, rango pequeño y grande). Regla: se conserva la compartida salvo que la individual gane
por más de 2 veces en el caso de 50 cazadores.

## D6. Corte de la búsqueda por rango

**Decisión**: `distancias_hacia` recibe un parámetro opcional nuevo `limite: int | None = None`.
Al extraer una entrada vigente con prioridad mayor que `limite`, la búsqueda termina. Con
`limite = None` el comportamiento es idéntico al actual, así que «ir a» no cambia (lo comprueban
las pruebas existentes de la spec 002).

**Invariante (base de FR-017)**: al cortar con límite L, toda sala con distancia real menor o igual
que L quedó fijada con su distancia exacta, y toda sala no fijada tiene distancia tentativa (o real)
mayor que L. Para un cazador con rango r ≤ L:
- si su sala no está fijada, su d real es mayor que L ≥ r y espera, igual que sin corte;
- si está fijada con d ≤ r, cada vecina v de una ruta óptima tiene distancia d − costo < d ≤ L y está
  fijada con su valor exacto; una vecina no fijada da costo + tentativa > L ≥ d y no empata.

Por eso la decisión con corte es idéntica a la de una búsqueda completa desde cero. Se prueba con
una prueba de propiedad (muchos estados aleatorios, decisión con corte frente a sin corte) y con H4.

**Razón**: con el corte, el costo depende de la región del rango y no del tamaño de la cripta.

**Alternativas**: sin corte (recorre todo lo alcanzable, O(S log S) por recálculo); corte con
`parar_en` en la sala del cazador más lejano (no acota por costo y exige conocer las salas de todos).

**Medición H2**: mismo rango y misma densidad de cazadores con criptas de 200, 2 000 y 20 000 salas,
con corte y sin corte; se reportan salas fijadas y tiempo. Criterio: con corte, el tiempo de 2 000 a
20 000 salas crece menos de 1,5 veces; sin corte crece en proporción a S.

## D7. Qué límite usa la búsqueda compartida

**Decisión**: `L = rango_maximo`, el mayor rango de los cazadores registrados en la persecución.
`CombateControlador.activar_enemigo` registra el rango de cada cazador que se activa, y la
restauración de un guardado registra los de los cazadores activos. El valor solo crece durante la
partida; no se revierte ni baja al morir un cazador.

**Razón**: un límite mayor que el necesario es correcto por el invariante de D6 y solo cuesta
salas extra; un límite menor obligaría a recalcular. Registrar en la activación es O(1).

**Alternativas**:
- Máximo exacto de los cazadores vivos y activos en cada recálculo: O(C) por recálculo y exige una
  lista de cazadores en el modelo.
- Límite igual al rango del cazador que pide: recalcula cada vez que pide uno de rango mayor.

**Complejidad**: O(1) por registro. Si H1 muestra que la región de R domina con cazadores de rangos
muy distintos, se mide la alternativa del máximo exacto.

## D8. Invalidación de las distancias

**Decisión**: la persecución guarda la clave con la que calculó:
`(sala_jugador, agenda.cambios_puertas, historial.reversiones)` y el límite usado. Las distancias
se reutilizan solo si la clave coincide y el límite usado es mayor o igual que el rango del cazador
que pide; si no, se recalcula con `L = rango_maximo` (D7).

| Evento | Qué invalida | Cómo se detecta |
|--------|--------------|-----------------|
| El jugador cambia de sala | Todas las distancias | `sala_jugador` distinta |
| Se abre una puerta (`abrir_salida`) | Todas | `agenda.cambios_puertas` aumenta |
| Se cierra una puerta (`procesar_cierre_puerta`) | Todas | `agenda.cambios_puertas` aumenta |
| Pergamino de retroceso, acción fallida revertida | Todas (pueden volver puertas y sala) | `historial.reversiones` aumenta |
| Cargar una partida | Todas | La simulación y la persecución son nuevas |
| Se activa un cazador de rango mayor que el límite usado | Todas | Límite usado < rango que pide |
| Muere o se mueve otro actor | Nada (FR-018) | No se detecta |

`agenda.cambios_puertas` es un entero monótono de `HeapAgendaEventos` que suben solo las dos
funciones de `Puertas`; no pasa por el historial, así que un retroceso no lo baja.
`historial.reversiones` es un entero monótono nuevo de `Historial_Retroceso` que suben
`revertir_abierto` y `deshacer`. Sin historial (bench) vale 0. Comparar la clave cuesta O(1).

**Razón**: dentro de un ciclo de eventos la sala del jugador no cambia, así que con puertas
estables hay a lo sumo un recálculo por ciclo, y ninguno si el jugador no se movió ni cambiaron
puertas. Los contadores monótonos evitan el error de una versión revertible (volver a un valor que
ya se usó con otro estado).

**Alternativas**:
- Recalcular en cada turno de cada cazador (sin caché): siempre correcto, C búsquedas por ciclo.
- Recalcular una vez al inicio de cada ciclo: no necesita contadores, pero repite la búsqueda
  aunque nada haya cambiado y no detecta un cierre de puerta a mitad del ciclo sin el contador.
- Comparar el estado de las puertas de la región: O(A_R) por decisión.

**Medición H3**: reutilizar con la clave frente a recalcular en cada turno y frente a recalcular
una vez por ciclo, con puertas estables y con puertas inestables (muchas con cierre automático
corto y un jugador que las abre). Regla: se conserva la clave salvo que una alternativa correcta
gane por más de 2 veces en el caso de puertas inestables.

## D9. Ficha del cazador y validación del rango

**Decisión**: `FichaEnemigo` agrega `rango: int | None = None`. `parsear_ficha` valida: si el
comportamiento es `cazador` y el rango falta, no es entero (o es booleano) o es negativo, lanza
`ValueError` con el id de la ficha (FR-008, FR-009). Para otros comportamientos el campo se ignora.
`docs/api.md` agrega `cazador` a los comportamientos y el campo `rango`.

**Punto a confirmar C1**: las fichas llegan por lotes con el contenido de las salas, no siempre al
iniciar. El rechazo ocurre al incorporar la ficha; si es durante la partida, falla el movimiento que
necesitaba ese contenido con el mensaje de error, como cualquier contenido inválido. FR-009 dice «la
carga de la cripta se rechaza»: se propone precisar en la spec que el rechazo es al cargar la ficha.

## D10. Ensamblado, guardado y reproducción

**Decisión**:
- `EnemigoPartida.rango: int | None = None`; `FactoryDto_Partida` lo copia de la ficha;
  `CombateControlador.crear_enemigo` agrega el caso `cazador` y fija `rango`.
- Guardado: `_escribir_enemigo` escribe `entero(rango)` solo si `comportamiento == "cazador"`, y
  `_leer_enemigo` lo lee con la misma condición. Los guardados existentes no tienen cazadores, así
  que siguen siendo legibles sin subir `VERSION_CUERPO`. `Restauracion` pasa el rango y registra
  los cazadores activos en la persecución nueva (FR-023).
- El siguiente turno ya se guarda con los eventos de la agenda; no hay estado nuevo del cazador.
- Reproducción: el registro no cambia de formato; las decisiones salen del modelo y son
  deterministas (FR-022). Retroceso: los movimientos del cazador ya pasan por
  `agenda.cambiar` y las listas de sala con historial (FR-024).

**Alternativas**: subir `VERSION_CUERPO` a 3 y escribir el rango para todos los enemigos: invalida
todos los guardados existentes sin necesidad. Recuperar el rango de la ficha al restaurar: depende
de que la ficha esté en caché y puede costar solicitudes (principio V).

## D11. Vista

**Decisión**:
- Costos (FR-020): `escena.puertas` dibuja junto a cada puerta de la sala actual el costo que ya
  llega en `vecindad[i].costo` (100 si no se declaró). El minimapa conserva su texto emergente.
- Cazadores (FR-021): la vista lee `EnemigoPartida.comportamiento`. Un cazador vivo se dibuja con
  una marca propia (contorno de color distinto bajo los pies) y su texto emergente agrega
  «cazador · rango r». Los derrotados se ven como los demás (US4, escenario 3).
- La vista no calcula nada; los datos llegan por `EstadoPartida`.

**Alternativas**: textura distinta por comportamiento (depende de los paquetes de imágenes y no
distingue a un cazador con la misma ficha visual).

## D12. `--bench`: criptas sintéticas y escenarios

**Decisión**: `generar_cripta_cazadores(semilla, salas, cazadores, rango, puertas_inestables)`
reutiliza la cuadrícula de `generar_cripta_conocimiento` (costos de 1 a 300, 20 % sin costo,
puertas cerradas de un lado) y coloca cazadores y jugador con `random.Random(semilla)`. Para la
cripta de referencia se usa el esqueleto mayor de `datos_offline` (como K4) y se colocan los
cazadores con la misma semilla. Todo sin red, disco ni vista (FR-027).

---

## Mediciones previstas

| Id | Qué mide | Alternativa comparada | Respalda |
|----|----------|------------------------|----------|
| H1 | Decisión de C cazadores por ciclo con C = 1, 10, 50 y 100; rango pequeño (300) y grande (sin límite efectivo) | Búsqueda compartida frente a una búsqueda por cazador | D5, FR-025 |
| H2 | Salas fijadas y tiempo de un recálculo con 200, 2 000 y 20 000 salas, mismo rango | Con corte frente a sin corte | D6, FR-025 |
| H3 | Tiempo de los ciclos de una partida simulada de 200 decisiones del jugador | Clave de invalidación frente a recalcular por turno y por ciclo; puertas estables e inestables | D8 |
| H4 | Coincidencia de decisiones en 10 000 turnos aleatorios | Decisión con caché y corte frente a búsqueda completa desde cero | FR-017, SC-003 |
| H5 | Ciclo de eventos entre dos decisiones del jugador en la cripta de referencia con 10, 50 y 100 cazadores activos; media y máximo | Límite de 20 ms | FR-025, SC-004 |
| H6 | Agenda de eventos (§5.6) con la carga nueva: intervalos de costos 1 a 300 y velocidades variadas | Heap propio frente a lista ordenada (la de `_bench_simulacion`) | §5.6, FR-025 |
| H7 | Costo de la llamada al predicado por arista relajada | Predicado frente a arreglo de banderas por clave | D9 de la spec 002 |
| H8 | H1, H4 y H5 dos veces con la misma semilla | Resultados idénticos | FR-022, FR-026, SC-005 |

Todas imprimen en consola, no abren la vista y usan `random.Random(semilla)` (principios II y VI).
Los resultados se guardan en `specs/003-terreno-cazador/mediciones.txt` y se resumen en las
secciones 14 a 16 de `docs/decisiones.md` (§5.1, §5.2 y §5.6).

## Resumen de complejidad

| Operación | Costo |
|-----------|-------|
| Intervalo de un movimiento | O(1) |
| Decisión de un cazador con distancias válidas | O(4) |
| Recálculo de distancias | O((V_R + A_R) log V_R) |
| Recálculos por ciclo con puertas estables | a lo sumo 1 |
| Comparar la clave de validez | O(1) |
| Registrar un rango | O(1) |
