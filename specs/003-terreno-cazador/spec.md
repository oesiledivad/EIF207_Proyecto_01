# Feature Specification: Terreno con costo y enemigo cazador

**Feature Branch**: `fiore`

**Created**: 2026-11-16

**Status**: Draft

**Input**: User description: "Terreno y cazador. Cada salida puede declarar un costo (entero >= 1, por defecto 100, igual en ambos sentidos); el costo ya se lee en el esqueleto (FR-023 de la spec 002), esta spec implementa el consumo de tiempo del movimiento y el enemigo cazador. Moverse por una salida cuesta su costo en lugar de 100 y el intervalo es max(1, costo*100 // velocidad), para el jugador y todos los enemigos (el costo de atacar, esperar y demás acciones no cambia). Nuevo enemigo con comportamiento \"cazador\" y campo rango (en unidades de costo). En su turno: si comparte sala con el jugador, ataca; si no, calcula el costo mínimo d hasta la sala del jugador usando solo salidas abiertas en ese instante; si no hay ruta o d > rango, espera (costo 100); si no, da un paso por una ruta de costo d, y esa acción cuesta lo que la salida. Desempate: entre las vecinas v con costo(u,v)+dist(v,jugador)=d, va a la de menor id. Conoce el esqueleto completo y el estado actual de las puertas, no le afecta la niebla de guerra, no abre puertas, y su decisión debe ser idéntica a calcularla desde cero en ese instante. La vista muestra los costos de las salidas de la sala actual y distingue a los cazadores de los demás enemigos. Escenarios de aceptación obligatorios (Apéndice B): (1) a (7). Requisito de rendimiento: el ciclo de eventos entre dos decisiones del jugador, con decenas de cazadores activos, tarda menos de 20 ms."

## Clarifications

### Session 2026-11-16

- Q: ¿La muerte de otros actores invalida las distancias que calcula el cazador? → A: No. Los actores no bloquean salas; solo cambian la decisión del cazador el movimiento del jugador y la apertura o cierre de puertas (pendiente de confirmar con el profesor).
- Q: Si dos salidas distintas de la sala del cazador llevan a la misma vecina, ¿cuál usa? → A: La de menor costo; si empatan en costo, la primera en el orden N, S, E, O.
- Q: ¿Cómo actúa un cazador dormido? → A: Sigue las reglas de la Parte I §2.4: no actúa hasta que el jugador entra a su sala, y su primera acción es una acción base de costo 100 contada desde el instante de la activación.
- Q: Si el costo mínimo d es igual al rango, ¿el cazador se mueve o espera? → A: Se mueve; solo espera si d es estrictamente mayor que el rango.
- Q: ¿Qué pasa si cambia la velocidad de un actor con un movimiento ya programado? → A: El tiempo restante se reescala según la Parte I §2.3, con mínimo 1.
- Q: ¿Cambia el costo de atacar, esperar y las demás acciones que no son moverse? → A: No; conservan el costo de la Parte I.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - El movimiento consume el costo de la salida (Priority: P1)

Cada salida tiene un costo de terreno: el que declara la cripta (un entero mayor o igual que 1) o 100 si no declara ninguno, igual en ambos sentidos. Cuando el jugador o cualquier enemigo se mueve por una salida, la acción cuesta el costo de esa salida en lugar del costo fijo de 100, y el tiempo hasta su siguiente turno es max(1, costo × 100 // velocidad). Las demás acciones (atacar, esperar, usar objetos, etc.) conservan su costo de la Parte I.

**Why this priority**: Es la base de la capacidad: sin costo de terreno el cazador no tiene qué minimizar y el tiempo de «ir a» (spec 002, FR-025) no refleja el mapa.

**Independent Test**: Se prepara una cripta con salidas de costos distintos (sin costo, costo 1, costo 250), se mueve el jugador por cada una y se comprueba en el reloj que su siguiente turno ocurre exactamente al intervalo que da la fórmula; se repite con un enemigo errante.

**Acceptance Scenarios**:

1. **Given** una salida sin costo declarado y un actor de velocidad 100, **When** el actor se mueve por ella, **Then** su siguiente turno ocurre 100 unidades de tiempo después, igual que en la Parte I.
2. **Given** una salida de costo 250 y un actor de velocidad 100, **When** el actor se mueve por ella, **Then** su siguiente turno ocurre 250 unidades de tiempo después.
3. **Given** un actor de velocidad alta (por ejemplo, 1000) y una salida de costo 1, **When** el actor la atraviesa, **Then** el intervalo hasta su siguiente turno es 1, nunca 0 (Apéndice B, caso 6).
4. **Given** un actor que acaba de atravesar una salida costosa y aún no llega su siguiente turno, **When** cambia su velocidad (por ejemplo, por una poción), **Then** el tiempo restante se reescala según la Parte I §2.3: restante nuevo = max(1, restante × velocidad anterior // velocidad nueva) (Apéndice B, caso 7).
5. **Given** un actor en una sala con salidas de costo distinto de 100, **When** ataca, espera o usa un objeto, **Then** la acción cuesta lo mismo que en la Parte I, sin depender de ningún costo de salida.
6. **Given** una salida de costo c entre las salas A y B, **When** un actor la atraviesa de A a B o de B a A, **Then** en ambos sentidos cuesta c.
7. **Given** un enemigo errante o rastreador que se mueve por una salida de costo c, **When** se agenda su siguiente turno, **Then** se usa el mismo intervalo que para el jugador con esa salida y esa velocidad.

---

### User Story 2 - El cazador persigue al jugador por la ruta más barata (Priority: P1)

Existe un nuevo comportamiento de enemigo, «cazador», con un campo rango expresado en unidades de costo. En cada turno el cazador decide así: si está en la misma sala que el jugador, ataca; si no, calcula el costo mínimo d desde su sala hasta la sala del jugador usando solo las salidas cuyas puertas están abiertas en ese instante. Si no existe ruta o d es mayor que su rango, espera (costo 100). En otro caso da un paso hacia una vecina que inicie una ruta de costo d, y ese paso cuesta lo que la salida atravesada.

**Why this priority**: Es el enemigo nuevo que da sentido al terreno con costo y el núcleo de los escenarios obligatorios del Apéndice B.

**Independent Test**: Se arma una cripta pequeña con un cazador y el jugador en salas distintas, unidas por varias rutas de costos conocidos, y se comprueba turno a turno a qué sala se mueve el cazador y cuánto tiempo consume cada acción.

**Acceptance Scenarios**:

1. **Given** un cazador cuya sala no tiene ninguna ruta de salidas abiertas hasta la sala del jugador, **When** llega su turno, **Then** espera y la acción cuesta 100 (Apéndice B, caso 1).
2. **Given** un cazador cuya ruta más barata hasta el jugador cuesta más que su rango, **When** llega su turno, **Then** espera y la acción cuesta 100 (Apéndice B, caso 2).
3. **Given** dos rutas abiertas hasta el jugador, una con menos salas y mayor costo total y otra con más salas y menor costo total, **When** llega el turno del cazador, **Then** da su paso por la de menor costo total (Apéndice B, caso 3).
4. **Given** dos vecinas del cazador que inician rutas de costo mínimo hasta el jugador, **When** llega su turno, **Then** se mueve a la de menor id (Apéndice B, caso 4).
5. **Given** un cazador que sigue una ruta y una puerta de esa ruta que se cierra entre dos de sus turnos, **When** llega su turno siguiente, **Then** su decisión es la misma que se obtendría calculándola desde cero con el estado de las puertas de ese instante (Apéndice B, caso 5).
6. **Given** un cazador en la misma sala que el jugador, **When** llega su turno, **Then** ataca con las reglas y el costo de ataque de la Parte I.
7. **Given** un cazador cuya ruta más barata cuesta exactamente su rango, **When** llega su turno, **Then** da el paso (la condición de espera es d estrictamente mayor que el rango).
8. **Given** un cazador que da un paso por una salida de costo c, **When** se agenda su siguiente turno, **Then** el intervalo es max(1, c × 100 // velocidad del cazador).
9. **Given** dos salidas distintas de la sala del cazador hacia la misma vecina, ambas abiertas y con el mismo costo, y esa vecina es la elegida, **When** el cazador da el paso, **Then** usa la primera de ellas en el orden N, S, E, O.
10. **Given** un cazador dormido, **When** el jugador está fuera de su sala, **Then** el cazador no actúa; **When** el jugador entra a su sala, **Then** se activa según la Parte I §2.4 y su primera acción es una acción base de costo 100 contada desde el instante de la activación.
11. **Given** un cazador que sigue una ruta y otro enemigo que muere en una sala de esa ruta entre dos turnos del cazador, sin que el jugador se mueva ni cambie ninguna puerta, **When** llega el turno siguiente del cazador, **Then** su decisión es la misma que habría tomado si ese enemigo siguiera vivo.

---

### User Story 3 - El cazador no ve niebla ni abre puertas (Priority: P1)

El cazador conoce el esqueleto completo de la cripta y el estado real de todas las puertas en el instante de su turno. La niebla de guerra del jugador (spec 002) no le afecta, y nunca abre puertas, aunque una puerta cerrada forme parte de la ruta más corta del mapa.

**Why this priority**: Define qué información usa el cazador; sin esta regla su comportamiento dependería del conocimiento del jugador y no sería verificable.

**Independent Test**: Se coloca un cazador en una zona que el jugador nunca ha explorado y una puerta cerrada en la ruta más corta, y se comprueba que el cazador persigue igual por la ruta abierta y que la puerta sigue cerrada.

**Acceptance Scenarios**:

1. **Given** un cazador en salas que el jugador no ha explorado ni avistado, **When** llega su turno, **Then** decide igual que si el jugador conociera todo el mapa.
2. **Given** una puerta que el mapa del jugador recuerda abierta pero que en realidad está cerrada, **When** el cazador calcula su ruta, **Then** usa el estado real (cerrada) y no la atraviesa.
3. **Given** una puerta cerrada en la ruta de menor costo del esqueleto, **When** llega el turno del cazador, **Then** no la abre, y solo considera rutas por puertas abiertas.

---

### User Story 4 - Ver costos de las salidas y reconocer a los cazadores (Priority: P2)

La interfaz muestra el costo de cada salida de la sala actual del jugador y distingue visualmente a los cazadores de los demás enemigos, para que el jugador pueda planear movimientos y reconocer la amenaza.

**Why this priority**: Mejora la decisión del jugador, pero el modelo funciona sin ella.

**Independent Test**: Se entra a una sala con salidas de costos distintos y con un cazador y un errante, y se comprueba que la vista muestra cada costo y marca al cazador de forma diferente al errante.

**Acceptance Scenarios**:

1. **Given** el jugador en una sala con salidas de costos 1, 100 (sin declarar) y 250, **When** la vista muestra la sala, **Then** cada salida indica su costo, y la que no declara costo indica 100.
2. **Given** una sala con un cazador y un enemigo de otro comportamiento, **When** la vista muestra la sala, **Then** el cazador se distingue del otro enemigo.
3. **Given** un cazador derrotado, **When** la vista muestra la sala, **Then** se presenta como los demás enemigos derrotados.

---

### User Story 5 - Coherencia con guardado, retroceso y reproducción (Priority: P2)

Los movimientos con costo y las decisiones del cazador son parte de la partida: se reproducen idénticos con la misma semilla y las mismas acciones, se revierten con el pergamino de retroceso como cualquier acción de enemigo y se conservan al guardar y cargar.

**Why this priority**: Mantiene el determinismo exigido por la constitución, pero depende de que el terreno y el cazador ya funcionen.

**Independent Test**: Se juega una partida con cazadores, se reproduce su registro y se comprueba que el estado final coincide; se guarda y carga a mitad de una persecución y se comprueba que el cazador continúa igual.

**Acceptance Scenarios**:

1. **Given** un registro de partida con cazadores y salidas de costos distintos, **When** se reproduce con la misma semilla, **Then** cada acción del cazador y cada instante del reloj coinciden con los de la partida original.
2. **Given** una partida guardada con un cazador a mitad de una persecución, **When** se carga, **Then** el cazador conserva su comportamiento, su rango y su siguiente turno, y su próxima decisión es la que habría tomado sin guardar.
3. **Given** un movimiento del jugador por una salida costosa, **When** usa el pergamino de retroceso, **Then** el reloj y las posiciones vuelven al estado previo, incluidas las acciones de cazadores ocurridas en ese intervalo.

---

### User Story 6 - Medir el ciclo de eventos con muchos cazadores (Priority: P3)

Quien evalúa el proyecto quiere evidencia medida de que, con decenas de cazadores activos, el procesamiento de todos los eventos entre dos decisiones del jugador es rápido.

**Why this priority**: Es evidencia exigida por la constitución, pero depende de que la capacidad ya funcione.

**Independent Test**: Se ejecuta el modo --bench con una semilla sobre la cripta de referencia con al menos 50 cazadores activos y se comprueba que reporta el tiempo del ciclo de eventos entre dos decisiones del jugador.

**Acceptance Scenarios**:

1. **Given** el modo --bench con una semilla y la cripta de referencia con al menos 50 cazadores activos, **When** se ejecuta, **Then** imprime el tiempo del ciclo de eventos entre dos decisiones del jugador y ese tiempo es menor que 20 ms.
2. **Given** el modo --bench, **When** se ejecuta dos veces con la misma semilla, **Then** las decisiones de los cazadores medidas son idénticas.

---

### Edge Cases

- Salida con costo declarado menor que 1 o no entero: se trata como costo 100 y se avisa en la bitácora, igual que en la spec 002.
- Actor con velocidad muy alta y salida de costo 1: el intervalo es 1, nunca 0.
- Actor con velocidad baja y salida de costo alto: el intervalo puede ser mucho mayor que 100; no hay tope.
- Cambio de velocidad con un movimiento costoso pendiente: se reescala solo el tiempo restante, con mínimo 1.
- Cazador con rango 0 en una sala distinta de la del jugador: siempre espera, porque toda ruta cuesta al menos 1.
- Cazador cuya ruta cuesta exactamente su rango: da el paso.
- Jugador y cazador en la misma sala tras el paso del cazador: el cazador ataca en su turno siguiente, no en el mismo.
- La puerta de la ruta del cazador se abre o se cierra entre turnos: cada turno se decide con el estado de ese instante, sin memoria de turnos anteriores.
- Varias vecinas empatan en costo mínimo y el jugador cambia de sala entre turnos: el desempate se aplica sobre la nueva situación.
- Dos salidas de la sala del cazador llevan a la misma vecina con costos distintos: cuenta la más barata que esté abierta; si empatan en costo, la primera en el orden N, S, E, O.
- Cazador dormido: no actúa ni calcula rutas hasta que el jugador entra a su sala; al activarse (Parte I §2.4), su primera acción es de costo 100 desde la activación.
- Muere otro enemigo, o un actor distinto del jugador se mueve: no cambia la decisión del cazador, porque los actores no bloquean salas.
- Cazador cuya ruta pasa por salas con trampas o con otros enemigos: las trampas y los enemigos no alteran el costo de la ruta; se aplican las reglas de la Parte I para enemigos en esas salas.
- El jugador muere o la partida termina: los cazadores no toman más decisiones.
- Cazador sin campo rango, o con rango negativo o no entero: la cripta se rechaza al cargar con un mensaje que nombra al enemigo.

## Requirements *(mandatory)*

### Functional Requirements

**Costo de terreno**

- **FR-001**: Cada salida DEBE tener un costo: el entero mayor o igual que 1 que declara la cripta, o 100 si no declara ninguno. El costo DEBE ser el mismo en ambos sentidos de la salida.
- **FR-002**: Un costo declarado menor que 1 o no entero DEBE tratarse como 100 y DEBE avisarse en la bitácora.
- **FR-003**: Moverse por una salida DEBE costar el costo de esa salida, en lugar del costo fijo de 100, para el jugador y para todos los enemigos, sea cual sea su comportamiento.
- **FR-004**: El intervalo hasta el siguiente turno de un actor que se mueve por una salida DEBE ser max(1, costo × 100 // velocidad), con división entera.
- **FR-005**: El costo de atacar, esperar, usar objetos y toda acción distinta de moverse por una salida NO DEBE cambiar respecto de la Parte I.
- **FR-006**: Si cambia la velocidad de un actor con un turno pendiente, el tiempo restante DEBE reescalarse según la Parte I §2.3: restante nuevo = max(1, restante × velocidad anterior // velocidad nueva), también cuando la acción pendiente es un movimiento costoso.
- **FR-007**: Cada paso de «ir a» (spec 002, FR-025) DEBE consumir el costo de la salida atravesada según FR-003 y FR-004.

**Enemigo cazador**

- **FR-008**: DEBE existir el comportamiento de enemigo «cazador», con un campo rango obligatorio: un entero mayor o igual que 0 expresado en unidades de costo.
- **FR-009**: Un cazador sin rango, o con rango negativo o no entero, DEBE hacer que la carga de la cripta se rechace con un mensaje que identifique al enemigo.
- **FR-010**: En su turno, si el cazador está en la misma sala que el jugador, DEBE atacar con las reglas y el costo de ataque de la Parte I.
- **FR-011**: Si no comparte sala con el jugador, el cazador DEBE calcular d, el costo mínimo desde su sala hasta la sala del jugador, sumando costos de salidas y usando solo las salidas cuya puerta está abierta en ese instante.
- **FR-012**: Si no existe ruta de salidas abiertas o d es estrictamente mayor que su rango, el cazador DEBE esperar, y esa acción DEBE costar 100.
- **FR-013**: En otro caso, el cazador DEBE moverse a una vecina v por una salida abierta tal que costo(sala, v) + dist(v, jugador) = d, y la acción DEBE costar el costo de esa salida según FR-003 y FR-004.
- **FR-014**: Si varias vecinas cumplen FR-013, el cazador DEBE moverse a la de menor id. Si varias salidas abiertas llevan a la misma vecina, DEBE usar la de menor costo y, si empatan en costo, la primera en el orden N, S, E, O.
- **FR-015**: El cazador DEBE conocer el esqueleto completo de la cripta y el estado real de todas las puertas en el instante de su turno. La niebla de guerra y el conocimiento del jugador NO DEBEN influir en su decisión.
- **FR-016**: El cazador NO DEBE abrir puertas.
- **FR-017**: La decisión del cazador DEBE ser idéntica a la que se obtendría calculándola desde cero con el estado de ese instante (sala del cazador, sala del jugador, estado de las puertas y costos), sin depender de decisiones o cálculos de turnos anteriores.
- **FR-018**: Las trampas, otros enemigos y objetos NO DEBEN alterar el costo de las rutas del cazador. Los actores no bloquean salas: la muerte o el movimiento de un actor distinto del jugador NO DEBE cambiar la decisión del cazador; solo la cambian la sala del jugador y el estado de las puertas.
- **FR-019**: El cazador DEBE seguir las reglas de la Parte I para daño, muerte y lo que suelta. Un cazador dormido NO DEBE actuar hasta que el jugador entre a su sala; al activarse según la Parte I §2.4, su primera acción DEBE ser una acción base de costo 100 contada desde el instante de la activación. Esta spec solo define su decisión de turno.

**Vista**

- **FR-020**: La interfaz DEBE mostrar el costo de cada salida de la sala actual del jugador; una salida sin costo declarado DEBE mostrarse con costo 100.
- **FR-021**: La interfaz DEBE distinguir a los cazadores vivos de los enemigos de otros comportamientos.

**Determinismo, guardado y retroceso**

- **FR-022**: La misma cripta, la misma semilla y las mismas acciones del jugador DEBEN producir las mismas decisiones de todos los cazadores y los mismos instantes del reloj.
- **FR-023**: Guardar y cargar una partida DEBE conservar el comportamiento, el rango y el siguiente turno de cada cazador.
- **FR-024**: El pergamino de retroceso DEBE revertir los movimientos con costo y las acciones de los cazadores igual que cualquier otra acción de la Parte I.

**Rendimiento y evidencia**

- **FR-025**: El procesamiento de todos los eventos entre dos decisiones consecutivas del jugador DEBE tardar menos de 20 ms en la cripta de referencia con al menos 50 cazadores activos.
- **FR-026**: El modo --bench DEBE medir el ciclo de eventos entre dos decisiones del jugador con cazadores activos y la decisión de un cazador, con resultados deterministas por semilla.
- **FR-027**: El modo --bench NO DEBE abrir la interfaz.
- **FR-028**: Esta capacidad NO DEBE contener datos de una cripta concreta; todo dato DEBE provenir del servicio o de los datos sin conexión.

### Key Entities

- **Salida**: conexión entre dos salas con una puerta y un costo de terreno (100 si no declara costo), igual en ambos sentidos.
- **Costo de terreno**: valor entero mayor o igual que 1 que determina cuánto cuesta moverse por una salida.
- **Actor**: jugador o enemigo, con velocidad y siguiente turno en el reloj; su intervalo depende del costo de la acción y de su velocidad.
- **Cazador**: enemigo con comportamiento «cazador» y rango; persigue al jugador por la ruta abierta de menor costo si cabe en su rango.
- **Rango**: máximo costo total de ruta que un cazador está dispuesto a recorrer para perseguir al jugador.
- **Decisión del cazador**: atacar, esperar o moverse a una vecina, calculada en cada turno con el estado de ese instante.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los siete escenarios del Apéndice B de esta capacidad (sin ruta abierta, ruta fuera de rango, menor costo frente a menos salas, desempate por menor id, puerta cerrada entre turnos, intervalo mínimo 1 con costo 1, reescalado por cambio de velocidad) se cumplen en pruebas automatizadas o en un registro de partida que cita su FR.
- **SC-002**: En el 100% de los movimientos probados, el intervalo hasta el siguiente turno coincide exactamente con max(1, costo × 100 // velocidad).
- **SC-003**: En el 100% de los turnos de cazador probados, la decisión coincide con la de un cálculo independiente desde cero sobre el mismo estado.
- **SC-004**: Con al menos 50 cazadores activos en la cripta de referencia, el ciclo de eventos entre dos decisiones del jugador tarda menos de 20 ms según --bench.
- **SC-005**: Dos partidas con la misma cripta, la misma semilla y las mismas acciones producen las mismas decisiones de cazadores en el 100% de los casos probados.
- **SC-006**: En el 100% de las salas mostradas, cada salida indica su costo y cada cazador vivo se distingue de los demás enemigos.
- **SC-007**: Con --bench se imprimen las mediciones en consola y 0 ventanas de la interfaz se abren.

## Assumptions

- La lectura del costo de cada salida desde el esqueleto ya existe (spec 002, FR-023); esta spec la consume.
- Se conservan las reglas de la Parte I para combate, activación y sueño de enemigos, trampas, veneno, reloj y pergamino de retroceso; la fórmula de reescalado por cambio de velocidad es la de la Parte I §2.3.
- El empate entre eventos del reloj en un mismo instante se sigue resolviendo como en la Parte I.
- Los ids de sala son comparables, de modo que «menor id» está bien definido; es la misma regla de desempate de «ir a» (spec 002, FR-024).
- «Decenas de cazadores activos» se fija en al menos 50 para la medición, y la cripta de referencia es la cripta publicada más grande; su tamaño proviene del servicio o de los datos sin conexión.
- Que la muerte de otros actores no afecte la decisión del cazador (FR-018) está pendiente de confirmar con el profesor; si cambia, se corrige primero esta spec.
- El rango es obligatorio para el cazador, en coherencia con el rechazo de campos obligatorios ausentes que ya hace la lectura de enemigos.
- El diseño visual de cómo se muestran los costos y cómo se distingue al cazador queda fuera de alcance; esta spec solo exige qué información se muestra.

## Out of Scope

- La niebla de guerra y el cálculo de «ir a» (spec 002); esta spec solo cambia el tiempo que consume cada paso.
- Cambios a los comportamientos guardián, errante y rastreador, salvo el costo de sus movimientos.
- Que el cazador abra puertas, recuerde rutas o prediga movimientos del jugador.
- El formato binario del guardado y la línea de tiempo (spec 004), más allá de conservar los datos del cazador.
- El diseño visual de la interfaz.
