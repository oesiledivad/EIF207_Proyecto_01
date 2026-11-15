# Feature Specification: Niebla de guerra y viaje automático «ir a»

**Feature Branch**: `kyara`

**Created**: 2026-11-15

**Status**: Draft

**Input**: User description: "Niebla de guerra y viaje automático «ir a» (Cripta Parte II, §3.3, §3.4 y §5.3): el jugador solo conoce lo que ha explorado, avistado u observado; el comando ir a lo lleva a una sala explorada con una secuencia de movimientos ordinarios calculada solo con su conocimiento."

## Clarifications

### Session 2026-11-15

- Q: ¿Qué debe mostrar el mapa conocido para una puerta que el jugador nunca ha observado (por ejemplo, de una sala explorada solo por la antorcha)? → A: Figura como «sin observar»: ni abierta ni cerrada, y ir a no la usa hasta que el jugador la observe.
- Q: Cuando ir a entra a una sala, ¿debe detenerse solo si hay enemigos vivos o también si solo quedan derrotados? → A: Solo si hay al menos un enemigo vivo (activo o dormido); los derrotados no cuentan.
- Q: Si el jugador enciende la antorcha estando dentro de una sala, ¿se exploran las vecinas de esa sala? → A: No; las vecinas solo se exploran al entrar a una sala con la antorcha ya encendida, es decir, a partir de la siguiente entrada.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ver solo lo que el jugador conoce (Priority: P1)

El jugador ya no ve el mapa completo. Cada sala está, para él, en uno de tres estados: explorada (entró al menos una vez; la sala inicial lo está desde el instante 0), avistada (no explorada, pero es destino de una salida de una sala explorada) o desconocida. De una sala explorada conoce nombre, salidas, costo de cada salida y estado de sus puertas según su última observación (una puerta que nunca ha observado figura «sin observar»). De una avistada solo sabe que existe. De una desconocida no sabe nada. La interfaz ofrece un comando para ver el mapa conocido.

**Why this priority**: Es la base de la capacidad. Sin conocimiento del jugador no hay niebla ni viaje automático.

**Independent Test**: Se inicia una partida, se consulta el mapa conocido en el instante 0, se mueve el jugador a una sala vecina y se consulta de nuevo, comprobando que solo aparecen salas exploradas y avistadas.

**Acceptance Scenarios**:

1. **Given** una partida recién iniciada, **When** el jugador consulta el mapa conocido, **Then** la sala inicial figura explorada con sus salidas, costos y estado de puertas, los destinos de esas salidas figuran avistados y ninguna sala desconocida aparece.
2. **Given** una sala avistada, **When** el jugador entra a ella, **Then** pasa a explorada y los destinos de sus salidas que no estén explorados pasan a avistados.
3. **Given** cualquier momento de la partida, **When** el jugador consulta el mapa conocido, **Then** la vista nunca muestra salas desconocidas ni datos de salas avistadas más allá de su existencia.
4. **Given** el mapa conocido, **When** se muestra una sala explorada, **Then** cada salida indica su costo y el estado recordado de su puerta (abierta, cerrada o sin observar).
5. **Given** una sala explorada por la antorcha cuyas otras puertas el jugador no ha observado, **When** el jugador consulta el mapa conocido, **Then** esas puertas figuran «sin observar», no abiertas ni cerradas.

---

### User Story 2 - Recordar el estado de las puertas tal como se observó (Priority: P1)

El jugador observa una puerta cuando está en cualquiera de las dos salas que conecta. Mientras permanece en una sala, los cambios de esas puertas se reflejan en su mapa en el momento en que ocurren. Al irse, el mapa conserva el estado de cada puerta de su última observación, aunque la puerta cambie después (por ejemplo, una puerta con cierre automático puede figurar abierta en el mapa y estar cerrada en realidad).

**Why this priority**: Sin memoria de puertas el mapa conocido sería una copia del estado real y la niebla no tendría efecto.

**Independent Test**: Se observa una puerta abierta, el jugador se aleja, la puerta se cierra sola, y se comprueba que el mapa la sigue mostrando abierta hasta que el jugador vuelve a observarla.

**Acceptance Scenarios**:

1. **Given** una puerta con cierre automático observada abierta, **When** el jugador se aleja y la puerta se cierra, **Then** el mapa conocido la sigue mostrando abierta.
2. **Given** el jugador en una sala, **When** una puerta de esa sala cambia de estado, **Then** el mapa conocido refleja el cambio en el mismo momento.
3. **Given** el jugador en una de las dos salas que conecta una puerta, **When** la puerta cambia, **Then** el mapa conocido refleja el cambio, sea cual sea de las dos salas en la que esté.
4. **Given** una puerta recordada con un estado distinto del real, **When** el jugador vuelve a una de sus dos salas, **Then** el mapa se actualiza al estado real.
5. **Given** una puerta «sin observar», **When** el jugador entra a una de sus dos salas, **Then** el mapa pasa a recordar su estado real.

---

### User Story 3 - Viajar automáticamente a una sala explorada con «ir a» (Priority: P1)

El comando ir a <sala> lleva al jugador a una sala explorada mediante una secuencia de movimientos ordinarios. La ruta se calcula solo con el conocimiento del jugador: solo salas exploradas y solo salidas que su mapa recuerda abiertas. Se minimiza la suma de costos de las salidas (una salida sin costo declarado vale 100). Si dos vecinas inician rutas de costo mínimo, el primer paso va hacia la de menor id, igual que el cazador. Cada paso es una acción completa del jugador: consume tiempo según el costo de la salida y entre paso y paso ocurren normalmente los eventos del reloj. La ruta se recalcula antes de cada paso con el conocimiento vigente.

**Why this priority**: Es la funcionalidad visible principal de la capacidad y la razón de ser del conocimiento del jugador.

**Independent Test**: Se explora una porción del mapa, se ejecuta ir a hacia una sala explorada lejana y se comprueba que el jugador llega por la ruta de menor costo, que cada paso consumió tiempo y que cada paso quedó registrado como un movimiento individual.

**Acceptance Scenarios**:

1. **Given** una sala no explorada (avistada o desconocida), **When** el jugador ejecuta ir a hacia ella, **Then** la orden se rechaza y no consume tiempo.
2. **Given** dos rutas conocidas, una con menos salas y mayor costo total y otra con más salas y menor costo total, **When** el jugador ejecuta ir a, **Then** sigue la de menor costo total.
3. **Given** dos vecinas que inician rutas de costo mínimo, **When** el jugador ejecuta ir a, **Then** el primer paso va hacia la de menor id.
4. **Given** una puerta cerrada en la ruta y el jugador con la llave que la abre, **When** el jugador ejecuta ir a, **Then** el viaje no atraviesa la puerta ni la abre.
5. **Given** una salida sin costo declarado, **When** se calcula la ruta, **Then** esa salida cuenta con costo 100.
6. **Given** el jugador en la sala indicada, **When** ejecuta ir a hacia la sala actual, **Then** la orden se rechaza sin consumir tiempo.
7. **Given** un viaje en curso, **When** el jugador llega al destino, **Then** el viaje termina y la interfaz muestra que se detuvo por llegada al destino.

---

### User Story 4 - Detener el viaje ante peligro o falta de ruta (Priority: P1)

El viaje se detiene cuando el jugador llega al destino, entra a una sala que contiene enemigos vivos (activos o dormidos), recibe cualquier daño (ataque, trampa o veneno) o deja de existir una ruta conocida. La interfaz muestra el motivo de la detención. Si al llegar a una sala el jugador observa que una puerta de su ruta está cerrada, el mapa se actualiza y el siguiente cálculo la evita; si no queda ruta, el viaje se detiene sin consumir tiempo adicional.

**Why this priority**: Evita que el viaje automático ponga al jugador en peligro sin control y garantiza que la niebla afecte las rutas.

**Independent Test**: Se prepara una ruta que atraviesa una sala con enemigos dormidos y se comprueba que el viaje se detiene al entrar a esa sala, que los enemigos se activan según las reglas de la Parte I y que la interfaz muestra el motivo.

**Acceptance Scenarios**:

1. **Given** el mapa recuerda abierta una puerta de la ruta que en realidad está cerrada, **When** el jugador llega a una sala desde la que la observa, **Then** el mapa se actualiza y la ruta se recalcula evitándola.
2. **Given** el caso anterior sin ruta alternativa conocida, **When** se recalcula, **Then** el viaje se detiene sin consumir tiempo adicional y la interfaz muestra que ya no existe ruta conocida.
3. **Given** una sala de la ruta con enemigos dormidos, **When** el viaje entra a ella, **Then** los enemigos se activan según las reglas de la Parte I y el viaje se detiene mostrando ese motivo.
4. **Given** una sala de la ruta con enemigos activos, **When** el viaje entra a ella, **Then** el viaje se detiene mostrando ese motivo.
5. **Given** un viaje en curso, **When** el jugador recibe daño de un ataque, una trampa o veneno, **Then** el viaje se detiene y la interfaz muestra el daño como motivo.
6. **Given** cualquier detención, **When** ocurre, **Then** la interfaz muestra el motivo de la detención.

---

### User Story 5 - Explorar vecinas con la antorcha (Priority: P2)

Mientras la antorcha esté encendida, al entrar a una sala también quedan exploradas todas sus vecinas, a través de cualquier salida, abierta o cerrada. Explorar una vecina de esta forma revela su nombre y salidas, no su contenido, y no activa sus enemigos ni sus trampas.

**Why this priority**: Amplía el conocimiento del jugador y, con él, el alcance de ir a, pero la capacidad funciona sin antorcha.

**Independent Test**: Con la antorcha encendida se entra a una sala que tiene vecinas con enemigos y trampas, y se comprueba que las vecinas aparecen exploradas sin que sus enemigos ni trampas se activen.

**Acceptance Scenarios**:

1. **Given** la antorcha encendida, **When** el jugador entra a una sala, **Then** todas sus vecinas, por salidas abiertas o cerradas, quedan exploradas.
2. **Given** una vecina explorada por la antorcha que contiene enemigos y trampas, **When** queda explorada, **Then** no se activan sus enemigos ni sus trampas.
3. **Given** una vecina explorada por la antorcha, **When** se muestra en el mapa, **Then** se conocen su nombre y salidas, pero no su contenido.
4. **Given** la antorcha apagada, **When** el jugador entra a una sala, **Then** sus vecinas solo quedan avistadas, no exploradas.
5. **Given** el jugador dentro de una sala con la antorcha apagada, **When** enciende la antorcha, **Then** las vecinas de esa sala no quedan exploradas y solo se exploran las vecinas de la siguiente sala a la que entre.

---

### User Story 6 - Conocimiento como parte del estado de la partida (Priority: P2)

El conocimiento del jugador es estado del juego. Se guarda y se restaura con la partida, se revierte con el pergamino de retroceso y puede reconstruirse para cualquier instante pasado (lo usa la línea de tiempo, spec 004). El pergamino de retroceso revierte únicamente el último paso de un viaje, porque cada paso es una acción del jugador, y el viaje no continúa.

**Why this priority**: Garantiza la coherencia entre mapa, guardado, retroceso y línea de tiempo, pero depende de que la niebla ya exista.

**Independent Test**: Se hace una entrada con antorcha encendida, se usa un pergamino de retroceso y se comprueba que las salas exploradas por la antorcha vuelven a su estado anterior; se repite durante un viaje.

**Acceptance Scenarios**:

1. **Given** una entrada a una sala con la antorcha encendida, **When** el jugador usa un pergamino de retroceso, **Then** las salas exploradas por la antorcha vuelven a su estado anterior.
2. **Given** un viaje en curso, **When** el jugador usa un pergamino de retroceso, **Then** se revierte solo el último paso y el viaje no continúa.
3. **Given** una partida guardada con conocimiento parcial, **When** se restaura, **Then** el mapa conocido es idéntico al del momento de guardar.
4. **Given** una partida con historia, **When** se pide el conocimiento de un instante pasado, **Then** se obtiene exactamente el mapa conocido de ese instante.

---

### User Story 7 - Registro de la partida y reproducción (Priority: P2)

En el registro de la partida cada paso de un viaje queda como un movimiento individual y la orden ir a queda como un comentario que la reproducción ignora.

**Why this priority**: Mantiene reproducibles las partidas, pero depende de que el viaje ya funcione.

**Independent Test**: Se ejecuta un viaje de varios pasos, se inspecciona el registro y se reproduce, comprobando que el estado final coincide con el de la partida original.

**Acceptance Scenarios**:

1. **Given** un viaje de varios pasos, **When** se inspecciona el registro, **Then** cada paso figura como un movimiento individual y la orden ir a figura como un comentario.
2. **Given** un registro con órdenes ir a, **When** se reproduce, **Then** la reproducción ignora los comentarios y llega al mismo estado final.

---

### User Story 8 - Medir el rendimiento de las consultas y de «ir a» (Priority: P3)

Quien evalúa el proyecto quiere evidencia medida de que consultar el conocimiento del jugador es barato y de que cada paso de ir a es rápido con el mapa conocido completo de la cripta de referencia.

**Why this priority**: Es evidencia exigida por la constitución, pero depende de que la capacidad ya funcione.

**Independent Test**: Se ejecuta el modo --bench con una semilla y se comprueba que reporta tiempos de las consultas al mapa conocido y del cálculo de un paso de ir a.

**Acceptance Scenarios**:

1. **Given** el modo --bench con una semilla, **When** se ejecuta, **Then** se miden las consultas al mapa conocido y el cálculo de un paso de ir a, y se imprimen los tiempos.
2. **Given** el mapa conocido completo de la cripta de referencia, **When** se mide un paso de ir a, **Then** tarda menos de 5 ms.
3. **Given** mapas conocidos de tamaños crecientes, **When** se miden las consultas de estado de sala y de estado recordado de puerta, **Then** el costo por consulta no crece con el tamaño del mapa conocido.

---

### Edge Cases

- ir a hacia una sala avistada o desconocida: se rechaza sin consumir tiempo.
- ir a hacia la sala actual: se rechaza sin consumir tiempo.
- ir a hacia una sala explorada pero sin ruta conocida (por ejemplo, toda ruta pasa por una puerta recordada cerrada): se rechaza sin consumir tiempo.
- La puerta recordada abierta está cerrada en realidad y no hay alternativa: el viaje se detiene al observarla, sin consumir tiempo adicional.
- El jugador tiene la llave de una puerta cerrada en la ruta: ir a no la abre ni la atraviesa.
- Entrada a una sala con enemigos dormidos durante un viaje: se activan según la Parte I y el viaje se detiene.
- Entrada a una sala donde solo quedan enemigos derrotados: el viaje no se detiene por ese motivo.
- Daño recibido por veneno entre dos pasos: el viaje se detiene.
- Antorcha encendida en una sala con vecinas ya exploradas: no se altera lo ya conocido.
- Ruta cuya única salida pasa por una puerta «sin observar»: ir a se rechaza sin consumir tiempo, igual que con una puerta recordada cerrada.
- Retroceso de una entrada con antorcha encendida: las salas exploradas por la antorcha vuelven a su estado anterior, incluidos los estados de puertas recordados y las salas avistadas.
- Una puerta cambia dos veces mientras el jugador permanece en la sala: el mapa conserva el último estado.
- Salida sin costo declarado: vale 100 para el cálculo de la ruta.
- Conocimiento en el instante 0: solo la sala inicial explorada y sus destinos avistados.

## Requirements *(mandatory)*

### Functional Requirements

**Niebla de guerra**

- **FR-001**: Para el jugador, cada sala DEBE estar en exactamente uno de tres estados: explorada, avistada o desconocida.
- **FR-002**: Una sala DEBE considerarse explorada si el jugador entró a ella al menos una vez. La sala inicial DEBE estar explorada desde el instante 0.
- **FR-003**: Una sala DEBE considerarse avistada si no está explorada y es destino de una salida de una sala explorada.
- **FR-004**: Toda sala que no sea explorada ni avistada DEBE considerarse desconocida.
- **FR-005**: De una sala explorada el jugador DEBE conocer su nombre, sus salidas, el costo de cada salida y el estado de sus puertas según su última observación. Una puerta que el jugador nunca ha observado DEBE figurar «sin observar», distinta de abierta y de cerrada.
- **FR-006**: De una sala avistada el jugador DEBE conocer únicamente que existe. De una sala desconocida NO DEBE conocer nada.
- **FR-007**: El jugador DEBE observar una puerta cuando está en cualquiera de las dos salas que conecta.
- **FR-008**: Mientras el jugador permanece en una sala, los cambios de las puertas observables desde ella DEBEN reflejarse en su mapa en el momento en que ocurren.
- **FR-009**: El mapa DEBE recordar el estado de cada puerta tal como estaba en su última observación, aunque haya cambiado después.
- **FR-009a**: Explorar una sala por la antorcha NO DEBE observar las puertas de esa sala; solo se observan las puertas de las salas en las que el jugador entra (FR-007). Una puerta «sin observar» pasa a recordar su estado real cuando el jugador entra a una de sus dos salas.
- **FR-010**: Mientras la antorcha esté encendida, al entrar a una sala DEBEN quedar exploradas también todas sus vecinas, a través de cualquier salida, abierta o cerrada. Encender la antorcha estando dentro de una sala NO DEBE explorar las vecinas de esa sala; solo se exploran al entrar a la siguiente sala con la antorcha ya encendida.
- **FR-011**: Explorar una vecina por la antorcha DEBE revelar su nombre y sus salidas, NO DEBE revelar su contenido y NO DEBE activar sus enemigos ni sus trampas.
- **FR-012**: Con la antorcha apagada, entrar a una sala NO DEBE explorar sus vecinas.

**Separación entre mapa y conocimiento**

- **FR-013**: El programa PUEDE seguir descargando el esqueleto completo de la cripta y usarlo para la precarga de contenido, porque es infraestructura.
- **FR-014**: Todo lo que la interfaz muestra del mapa y todo lo que usa ir a DEBE derivarse exclusivamente del conocimiento del jugador.
- **FR-015**: El conocimiento del jugador DEBE ser parte del estado del juego: DEBE guardarse y restaurarse con la partida.
- **FR-016**: El conocimiento del jugador DEBE revertirse con el pergamino de retroceso. Revertir una entrada con antorcha encendida DEBE devolver las salas exploradas por la antorcha a su estado anterior.
- **FR-017**: El conocimiento del jugador DEBE poder reconstruirse para cualquier instante pasado, para uso de la línea de tiempo (spec 004).
- **FR-018**: La interfaz DEBE ofrecer un comando para ver el mapa conocido, que muestre las salas exploradas, sus salidas con costo y estado recordado de la puerta (abierta, cerrada o sin observar), y las salas avistadas. NO DEBE mostrar salas desconocidas.

**Viaje automático «ir a»**

- **FR-019**: El comando ir a <sala> DEBE llevar al jugador a una sala explorada mediante una secuencia de movimientos ordinarios.
- **FR-020**: ir a hacia una sala no explorada DEBE rechazarse sin consumir tiempo.
- **FR-021**: ir a hacia la sala actual DEBE rechazarse sin consumir tiempo.
- **FR-022**: La ruta DEBE calcularse solo con el conocimiento del jugador: solo salas exploradas y solo salidas que su mapa recuerda abiertas; una salida con puerta cerrada o «sin observar» NO DEBE usarse.
- **FR-023**: La ruta DEBE minimizar la suma de costos de las salidas, y una salida sin costo declarado DEBE valer 100. Entre dos rutas, DEBE preferirse la de menor costo total aunque tenga más salas.
- **FR-024**: Si varias vecinas inician rutas de costo mínimo, el primer paso DEBE ir hacia la de menor id, con la misma regla de desempate que el cazador.
- **FR-025**: Cada paso DEBE ser una acción completa del jugador: DEBE consumir tiempo según el costo de la salida y DEBEN ocurrir normalmente los eventos del reloj entre un paso y el siguiente.
- **FR-026**: La ruta DEBE recalcularse antes de cada paso con el conocimiento vigente. Si al llegar a una sala el jugador observa que una puerta de su ruta está cerrada, el mapa DEBE actualizarse y el siguiente cálculo DEBE evitarla.
- **FR-027**: El viaje DEBE detenerse cuando el jugador llegue al destino.
- **FR-028**: El viaje DEBE detenerse cuando el jugador entre a una sala que contiene al menos un enemigo vivo, activo o dormido; los enemigos derrotados no cuentan. Los enemigos dormidos DEBEN activarse según las reglas de la Parte I.
- **FR-029**: El viaje DEBE detenerse cuando el jugador reciba cualquier daño: ataque, trampa o veneno.
- **FR-030**: El viaje DEBE detenerse cuando deje de existir una ruta conocida, sin consumir tiempo adicional.
- **FR-031**: La interfaz DEBE mostrar el motivo de la detención del viaje.
- **FR-032**: ir a NO DEBE abrir puertas, aunque el jugador tenga la llave.
- **FR-033**: En el registro de la partida, cada paso de un viaje DEBE quedar como un movimiento individual y la orden ir a DEBE quedar como un comentario que la reproducción ignora.
- **FR-034**: El pergamino de retroceso DEBE revertir únicamente el último paso de un viaje, y el viaje NO DEBE continuar.

**Rendimiento y evidencia**

- **FR-035**: Consultar si una sala está explorada, avistada o desconocida, y consultar el estado recordado de una puerta, DEBEN tener un costo que NO DEBE crecer con el tamaño del mapa conocido.
- **FR-036**: Explorar nuevas salas DEBE costar en proporción a las salas reveladas, no al tamaño del mapa conocido.
- **FR-037**: Registrar e invertir los cambios del conocimiento DEBE costar en proporción a los cambios.
- **FR-038**: El cálculo de un paso de ir a DEBE tardar menos de 5 ms con el mapa conocido completo de la cripta de referencia.
- **FR-039**: El modo --bench DEBE medir las consultas al mapa conocido y el cálculo de ir a, con resultados deterministas por semilla.
- **FR-040**: El modo --bench NO DEBE abrir la interfaz.
- **FR-041**: Esta capacidad NO DEBE contener datos de una cripta concreta; todo dato DEBE provenir del servicio o de los datos sin conexión.

### Key Entities

- **Conocimiento del jugador**: lo que el jugador sabe del mapa en un instante: qué salas explora, cuáles avista y qué recuerda de cada puerta. Es parte del estado del juego.
- **Estado de sala para el jugador**: explorada, avistada o desconocida.
- **Memoria de puerta**: estado de una puerta (abierta, cerrada o sin observar) según su última observación, que puede diferir del real.
- **Sala**: lugar de la cripta con nombre, salidas, enemigos y trampas; solo su nombre y sus salidas se revelan al explorarla por antorcha.
- **Salida**: conexión entre dos salas con un costo (100 si no declara costo) y una puerta con estado.
- **Viaje automático**: secuencia de pasos hacia una sala explorada, que termina por un motivo de detención.
- **Motivo de detención**: llegada al destino, entrada a sala con enemigos, daño recibido o ausencia de ruta conocida.
- **Antorcha**: objeto del jugador que, encendido, hace que entrar a una sala explore también sus vecinas.
- **Pergamino de retroceso**: objeto que revierte la última acción del jugador y el conocimiento asociado.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los escenarios del Apéndice B de esta capacidad (ir a hacia sala no explorada, puerta recordada abierta que está cerrada, sala con enemigos dormidos, antorcha sin activar enemigos ni trampas, retroceso de entrada con antorcha, retroceso durante un viaje) se cumplen en pruebas automatizadas o en un registro de partida que cita su FR.
- **SC-002**: En el 100% de las consultas del mapa conocido probadas, ninguna sala desconocida aparece y de las avistadas solo se muestra su existencia.
- **SC-003**: Un paso de ir a tarda menos de 5 ms con el mapa conocido completo de la cripta de referencia.
- **SC-004**: Al multiplicar por 10 el tamaño del mapa conocido, el costo medido de las consultas de estado de sala y de estado recordado de puerta no aumenta de forma apreciable, y el de explorar nuevas salas crece en proporción a las salas reveladas.
- **SC-005**: Dos partidas con la misma cripta, la misma semilla y las mismas acciones producen el mismo mapa conocido y los mismos viajes en el 100% de los casos probados.
- **SC-006**: Tras revertir con el pergamino, el mapa conocido es idéntico al anterior a la acción revertida en el 100% de los casos probados.
- **SC-007**: En el 100% de los viajes detenidos, la interfaz muestra el motivo de la detención.
- **SC-008**: Con --bench, el resultado de las consultas al mapa conocido y del cálculo de ir a aparece en consola y 0 ventanas de la interfaz se abren.

## Assumptions

- Se conservan las reglas de la Parte I para los enemigos (activación, daño), las trampas, el veneno, el reloj y el pergamino de retroceso; esta capacidad solo las consume.
- La cripta de referencia es la cripta publicada más grande; su tamaño proviene del servicio o de los datos sin conexión, no del código.
- El cazador (spec 003) conoce el mapa completo y no usa la niebla; su regla de desempate por menor id se reutiliza como criterio de ir a.
- El formato binario del guardado y la línea de tiempo (spec 004) consumen el conocimiento del jugador, pero quedan fuera de alcance de esta spec.
- El diseño visual de la interfaz queda fuera de alcance; esta spec solo exige qué información se muestra.

## Out of Scope

- El comportamiento del cazador (spec 003).
- El formato binario del archivo de guardado y la línea de tiempo (spec 004).
- El diseño visual de la interfaz.
