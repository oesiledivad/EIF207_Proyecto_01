# Bitácora de uso de modelos de lenguaje (LLM)

Proyecto: Cripta — EIF 207 Estructuras de Datos — II Ciclo 2026.

Integrantes:

- Eliseo Zuñiga Obando.
- Fiorella Porras Mora.
- Kyara Rojas Gonzalez.

## Declaración general

Los LLM se utilizaron como apoyo para comprender conceptos, explorar alternativas, revisar código, generar casos de prueba, mejorar documentación y proponer implementaciones. Todo el código y texto entregado es responsabilidad del grupo.

## Registro cronológico de prompts

### Entrada #1

Fecha: 29/09/2026

Integrante: Fiorella Porras Mora.

Herramienta: ChatGPT — GPT-5.6 Luna.

Objetivo: Analizar y planificar la implementación de las funcionalidades asignadas, especialmente la agenda de eventos.

Prompt enviado:

> Este es mi proyecto, le pedí a claude que dividiera trabajo entre 3 personas y a mi me dijo que implementara estas funcionalidades, todas las estructuras de datos deben ser hechas a mano sin uso de librerías externas. funcionalidades: Fiorella — Motor de simulación y combate §4.1 Agenda de eventos (cola de prioridad propia con cancelación y reprogramación — esto es lo más delicado de todo el proyecto) Reloj virtual, combate, comportamiento de enemigos (guardián/errante/rastreador), efectos temporales (veneno, regeneración, trampas, cierre de puertas) §4.7 Rastro del jugador.

Uso de la respuesta: Planificar el motor de simulación, la agenda de eventos, los efectos y el rastro del jugador.

### Entrada #2

Fecha: 03–07/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Auditoría inicial del proyecto.

Prompt:

> ¿Qué requisitos del enunciado y de la API cumple el proyecto y qué falta por resolver?

Uso de la respuesta: Orientar la revisión inicial del código contra el enunciado, la API y la arquitectura MVC.

### Entrada #3

Fecha: 03–07/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Alcance y planificación de inventario, sistema y CLI.

Prompt:

> Dime cómo organizar el siguiente sprint de inventario, sistema y CLI, respetando el trabajo en curso del equipo.

Uso de la respuesta: Delimitar el trabajo de inventario, sistema, CLI y documentación para coordinarlo con el resto del equipo.

### Entrada #4

Fecha: 03–07/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Reglas de implementación y rama de trabajo.

Prompt:

> ¿Cómo implementar mi parte con cambios simples y mínimos, trabajando en el branch eliseo y haciendo PR hacia master?

Uso de la respuesta: Organizar los cambios en la rama de trabajo y priorizar implementaciones mínimas compatibles con las restricciones.

### Entrada #5

Fecha: 03–07/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Pantalla de derrota y reinicio.

Prompt:

> ¿Cómo crear una pantalla de derrota inspirada en Dark Souls, permitir otra partida y mantener los estilos en archivos .tcss?

Uso de la respuesta: Diseñar el cierre de partida y la opción de volver a jugar, separando los estilos de la vista Textual.

### Entrada #6

Fecha: 03/10/2026

Integrante: Fiorella Porras Mora.

Herramienta: Claude — Sonnet 5.5.

Objetivo: Analizar y planificar la implementación de las funcionalidades asignadas.

Prompt enviado:

> Quiero que trabajes como asistente de programación práctico y directo. Estoy desarrollando un proyecto universitario y necesito agilizar la implementación y entender lo que estoy haciendo.
>
> Mi responsabilidad es Motor de simulación y combate, incluyendo:
>
> agenda de eventos,
>
> reloj virtual,
>
> combate,
>
> comportamiento de enemigos,
>
> efectos temporales,
>
> rastro del jugador. No quiero que modifiques ni implementes funcionalidades asignadas a mis compañeros salvo que sea estrictamente necesario para integrar mi código. Antes de proponer una implementación, revisa las clases existentes y utiliza sus nombres, atributos y métodos reales. No inventes una arquitectura nueva.

Uso de la respuesta: Orientar el desarrollo de combate y efectos usando los componentes existentes y respetando la división de responsabilidades.

### Entrada #7

Fecha: 07/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Escenario propio para pruebas.

Prompt:

> ¿Cómo diseñar una cripta offline llamada cripta-stormlight, inspirada en The Stormlight Archive, que también sirva para probar el juego?

Uso de la respuesta: Preparar un escenario offline adicional para ejercitar inventario, puertas, efectos, precarga y replay.

### Entrada #8

Fecha: 07/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Revisión de la caché y restricciones de estructuras.

Prompt:

> ¿Qué alternativa podemos usar en Cache_Fichas para reemplazar la tabla hash y respetar las estructuras permitidas en clase?

Uso de la respuesta: Revisar la estrategia de caché y su compatibilidad con las estructuras permitidas en clase.

### Entrada #9

Fecha: 07/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Ordenamientos y recorridos propios.

Prompt:

> ¿Cómo reemplazar los usos de sorted y reversed por algoritmos y recorridos propios?

Uso de la respuesta: Localizar ordenamientos y recorridos nativos que debían reemplazarse por implementaciones propias.

### Entrada #10

Fecha: 07–10/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Separación del controlador principal.

Prompt:

> ¿Cómo dividir Aplicacion.py en controladores y repartir esa separación entre los integrantes del equipo?

Uso de la respuesta: Distribuir responsabilidades entre controladores y acordar qué extracciones correspondían a cada integrante.

### Entrada #11

Fecha: 07–11/10/2026 (aproximada)

Integrante: Kyara Rojas Gonzalez.

Herramienta: Claude (modelo no indicado).

Objetivo: Guardado binario tras el cambio de vista.

Prompt aportado:

> Mi proyecto cambió de vista a `vista/grafica` y el guardado binario quedó a medias. Quiero entender qué de lo que hicimos sigue sirviendo con esta estructura nueva.

Uso de la respuesta: Revisar qué componentes del guardado binario podían reutilizarse con la vista gráfica.

### Entrada #12

Fecha: 07–11/10/2026 (aproximada)

Integrante: Kyara Rojas Gonzalez.

Herramienta: Claude (modelo no indicado).

Objetivo: Integración del guardado con master.

Prompt aportado:

> Al revisar el guardado contra el master actualizado, no tengo claro qué archivos siguen existiendo ni dónde encaja cada pieza.

Uso de la respuesta: Ubicar los archivos de guardado y su integración con la estructura actualizada del proyecto.

### Entrada #13

Fecha: 07–11/10/2026 (aproximada)

Integrante: Kyara Rojas Gonzalez.

Herramienta: Claude (modelo no indicado).

Objetivo: Ubicación del archivo de partida.

Prompt aportado:

> La partida ya se guarda desde el menú, pero no sé si el archivo queda dentro del proyecto o en otro lugar.

Uso de la respuesta: Aclarar la ubicación de los archivos generados al guardar una partida desde el menú.

### Entrada #14

Fecha: 07–11/10/2026 (aproximada)

Integrante: Kyara Rojas Gonzalez.

Herramienta: Claude (modelo no indicado).

Objetivo: Validación de guardado y carga.

Prompt aportado:

> Quiero estar segura de que guardar y cargar de verdad devuelve la partida igual, incluso con un archivo dañado o de otra versión de la cripta.

Uso de la respuesta: Revisar la restauración del estado y los casos de archivos dañados o versiones incompatibles.

### Entrada #15

Fecha: 07–11/10/2026 (aproximada)

Integrante: Kyara Rojas Gonzalez.

Herramienta: Claude (modelo no indicado).

Objetivo: Limitaciones del guardado.

Prompt aportado:

> Para la documentación necesito tener claro qué limitaciones tiene el guardado actual, como el historial o la bitácora.

Uso de la respuesta: Identificar las limitaciones del formato de guardado para documentar qué información se conserva.

### Entrada #16

Fecha: 07–11/10/2026 (aproximada)

Integrante: Kyara Rojas Gonzalez.

Herramienta: Claude (modelo no indicado).

Objetivo: Planificación de exploración, puertas y rastro.

Prompt aportado:

> Mi segunda asignación mezcla movimiento, puertas, rastro y guardado. Antes de programar quiero entender en qué orden conviene hacerlo y por qué.

Uso de la respuesta: Organizar la implementación de exploración y su relación con el guardado de la partida.

### Entrada #17

Fecha: 07–11/10/2026 (aproximada)

Integrante: Kyara Rojas Gonzalez.

Herramienta: Claude (modelo no indicado).

Objetivo: Extracción de ExploracionControlador.

Prompt aportado:

> Mucho de esa lógica vive hoy dentro de `Aplicacion.py`. Me pregunto cómo separarla en un controlador sin que se rompa lo que ya funciona.

Uso de la respuesta: Revisar la extracción del movimiento, las puertas y el rastro a un controlador especializado.

### Entrada #18

Fecha: 07–11/10/2026 (aproximada)

Integrante: Kyara Rojas Gonzalez.

Herramienta: Claude (modelo no indicado).

Objetivo: Integración de la apertura de salida con la comprobación de victoria.

Prompt aportado:

> ¿Cómo se conecta la apertura del acceso a la salida con la comprobación de victoria existente?

Uso de la respuesta: Aclarar la comunicación entre la apertura de puertas y la comprobación de victoria.

### Entrada #19

Fecha: 10/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Restricción adicional sobre tuplas.

Prompt:

> ¿Qué usos de tuplas tenemos y cómo sustituirlos respetando las restricciones del profesor?

Uso de la respuesta: Revisar las estructuras propias y distinguir sus usos de los formatos internos exigidos por bibliotecas.

### Entrada #20

Fecha: 10/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Minimapa interactivo y tamaños adaptables.

Prompt:

> ¿Cómo hacer clickeable el minimapa y adaptar los widgets a pantallas pequeñas?

Uso de la respuesta: Revisar la interacción del minimapa y la adaptación de la interfaz a pantallas pequeñas.

### Entrada #21

Fecha: 10–11/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Prototipo de interfaz gráfica.

Prompt:

> ¿Cómo preparar un prototipo de interfaz gráfica en un branch de pruebas, con pixel art o ASCII animado?

Uso de la respuesta: Planificar un prototipo gráfico aislado y evaluar su integración con el modelo y la API existentes.

### Entrada #22

Fecha: 10–11/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Arquitectura de la vista gráfica.

Prompt:

> ¿Cómo separar correctamente las responsabilidades de la vista gráfica?

Uso de la respuesta: Separar representación de la escena, recursos, entrada del usuario y coordinación de la ventana.

### Entrada #23

Fecha: 10–11/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Recursos gráficos y legibilidad de objetos.

Prompt:

> ¿Cómo integrar los sprites de Zerie y hacer más visibles los objetos del suelo mediante tamaño y movimiento?

Uso de la respuesta: Orientar la integración de sprites externos y la presentación visual de los objetos recogibles.

### Entrada #24

Fecha: 10–11/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Capacidad dinámica del inventario gráfico.

Prompt:

> ¿Cómo adaptar las casillas del inventario gráfico al valor inventario_max de cada cripta?

Uso de la respuesta: Adaptar la cuadrícula a inventario_max, usando el dato de la cripta en lugar de una cantidad fija de casillas.

### Entrada #25

Fecha: 10–11/10/2026 (aproximada)

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Pantalla de carga e información de red.

Prompt:

> ¿Cómo mostrar una pantalla de carga al consultar la API e indicar el presupuesto de red utilizado?

Uso de la respuesta: Revisar la carga inicial de la API y la presentación del modo de conexión y del presupuesto utilizado.

### Entrada #26

Fecha: 11/10/2026

Integrante: Kyara Rojas Gonzalez.

Herramienta: Claude (modelo no indicado).

Objetivo: Regresión del método atacar.

Prompt aportado:

> Después de mover código, un test falló diciendo que `atacar` ya no existe. Quiero entender qué pudo haberse borrado de más.

Uso de la respuesta: Investigar una regresión en la interfaz del controlador tras separar responsabilidades.

### Entrada #27

Fecha: 11/10/2026

Integrante: Kyara Rojas Gonzalez.

Herramienta: Claude (modelo no indicado).

Objetivo: Uso de llaves y apertura de puertas.

Prompt aportado:

> Probé el juego y no vi nada raro, pero no logré abrir una puerta con llave. No sé si la llave se usa de alguna forma especial.

Uso de la respuesta: Revisar la interacción necesaria para abrir una puerta cuando el jugador tiene su llave.

### Entrada #28

Fecha: 18/10/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Compatibilidad de guardados y ayudas de prueba.

Prompt:

> ¿Cómo evitar que un guardado offline se cargue contra la API y añadir un menú de cheats para probar combates difíciles?

Uso de la respuesta: Revisar la selección de la fuente de un guardado y el aislamiento de las ayudas de prueba respecto a puntajes y replay.

### Entrada #29

Fecha: 18/10/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Separación de servicios.

Prompt:

> ¿Qué responsabilidades podemos extraer de CriptaService para reducir su tamaño?

Uso de la respuesta: Revisar la separación de catálogo, precarga y conversión de datos para reducir responsabilidades del servicio principal.

### Entrada #30

Fecha: 18/10/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Configuración de audio.

Prompt:

> ¿Cómo controlar el volumen con sliders y corregir que la música se escuche demasiado baja?

Uso de la respuesta: Revisar el nivel de las pistas y diseñar controles de volumen accesibles mediante ratón y teclado.

### Entrada #31

Fecha: 18/10/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Eliminación de código sin uso.

Prompt:

> Dime qué módulos y submódulos no se utilizan y cuáles podemos eliminar.

Uso de la respuesta: Comprobar referencias al ensamblador antiguo y a otros módulos antes de retirarlos.

### Entrada #32

Fecha: 18/10/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Auditoría final de requisitos del código.

Prompt:

> ¿Qué requisitos del código quedan pendientes según el enunciado, dejando la documentación aparte?

Uso de la respuesta: Contrastar el código y las pruebas con los requisitos de red, caché, inventario, guardado, replay y rendimiento.

### Entrada #33

Fecha: 18/10/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Exportación del arte a PNG.

Prompt:

> ¿Cómo exportar el arte generado a tilesets PNG para evitar las tuplas utilizadas al dibujarlo durante la ejecución?

Uso de la respuesta: Evaluar la exportación de los recursos gráficos para evitar generarlos durante la ejecución del juego.

### Entrada #34

Fecha: 18/10/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Estrés y límites de rendimiento.

Prompt:

> ¿Qué limitaciones debemos documentar al probar el juego con 1000 enemigos y cómo relacionarlas con las restricciones del proyecto?

Uso de la respuesta: Distinguir las mediciones de la cripta de referencia de las cargas de estrés y documentar sus límites.

### Entrada #35

Fecha: 18/10/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Carga offline con catálogo incompatible.

Prompt:

> ¿Por qué no carga cripta-stormlight en modo offline y cómo corregirlo?

Uso de la respuesta: Investigar el conflicto entre el catálogo local de Stormlight y el catálogo persistido al jugar online.

### Entrada #36

Fecha: 18/10/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Recuperación del menú tras perder la conexión.

Prompt:

> ¿Cómo recuperar el menú de selección cuando se pierde Internet y la pantalla de carga queda bloqueada incluso después de reconectar?

Uso de la respuesta: Revisar la recuperación de errores de carga y el presupuesto conservado al regresar a la selección de criptas.

### Entrada #37

Fecha: 18/10/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Codex (OpenAI).

Objetivo: Presupuesto agotado durante una partida.

Prompt:

> ¿Qué debe ocurrir cuando se agota el presupuesto de red durante una partida y cómo permitir que el usuario continúe o guarde su progreso?

Uso de la respuesta: Definir y verificar la continuidad con datos disponibles, el rechazo de acciones que requieran red y las opciones de guardar o volver al menú.

### Entrada #38

Fecha: 15/11/2026

Integrante: Kyara Anyelina Rojas Gonzalez

Herramienta: Claude Code (Sonnet 5.5) con spec-kit v1.3.3.

Objetivo: Crear la constitución del proyecto con /speckit-constitution.

Prompt enviado:

```text
/speckit-constitution Constitución del proyecto "Cripta" (EIF207 Estructuras de Datos, II Ciclo 2026, Parte II). Redacta todo en español, sin guiones largos. No explores el repositorio: usa solo esta información. Muestra el Sync Impact Report solo en tu respuesta, no lo dejes en el archivo.

Principios:

I. Estructuras de datos propias (NO NEGOCIABLE). Las estructuras de los problemas evaluados se implementan a mano. Prohibido usar dict o set como índice, caché o tabla de búsqueda, y prohibidos heapq, bisect, collections (deque, OrderedDict, defaultdict, Counter), networkx y cualquier biblioteca de grafos o de búsqueda de rutas. Permitido: list como almacenamiento contiguo, dict solo para leer el JSON de las respuestas, y struct, json, requests y arcade. Un plan que proponga una dependencia prohibida se corrige antes de generar tareas.

II. Determinismo. La misma versión de cripta, la misma semilla y las mismas acciones producen la misma partida. Toda aleatoriedad usa la instancia propia random.Random(semilla) del modelo; nunca el generador global, la hora del sistema ni el orden de llegada de respuestas HTTP. Todo empate se resuelve con una regla explícita (número de secuencia, menor id).

III. Separación MVC. El modelo no conoce HTTP, archivos ni la interfaz. La red y el disco se acceden mediante adaptadores. Los modos --replay, --bench y --verificar no instancian la vista.

IV. Ningún dato de una cripta en el código. No se escriben en el código ids de salas o entidades, cantidades de páginas, presupuestos ni estadísticas de una cripta concreta; todo proviene del servicio web o de los datos offline.

V. Presupuesto de red. Se respeta presupuesto_solicitudes de cada cripta. Toda solicitud HTTP cuenta, incluidos reintentos y la consulta de llaves. Lo persistido se reutiliza validando su versión.

VI. Rendimiento con evidencia. Toda afirmación de rendimiento se respalda con mediciones de --bench, deterministas por semilla. Cada decisión de estructura de datos compara al menos una alternativa medida.

VII. La especificación precede a la implementación (NO NEGOCIABLE). Cada capacidad tiene su spec.md confirmada en Git antes que el código que la implementa. Si la spec resulta incorrecta, se corrige primero la spec y luego el código, en commits separados. Cada requisito funcional tiene un id estable (FR-001); cada escenario de aceptación tiene una prueba automatizada o un partida.log que cita su FR; cada tarea cita los FR que atiende. spec.md no nombra estructuras de datos, clases ni módulos.

Sección "Restricciones técnicas": Python 3.13 o superior con uv; vista con Arcade; pruebas con unittest en la carpeta pruebas/; agente Claude Code con spec-kit v1.3.3 y scripts sh; el equipo trabaja en Windows con CMD.

Sección "Flujo de trabajo": por capacidad se ejecuta constitution (una vez), specify, clarify, plan, tasks, analyze e implement; clarify y analyze son obligatorios. Cada integrante trabaja en su propia rama y se integra a master mediante pull request con merge commit, nunca squash. Cada prompt a un LLM, incluidos los comandos de spec-kit con texto propio, se registra en la bitácora PROMPTS_LLM.md con fecha, integrante, herramienta, prompt textual y uso.

Gobernanza: esta constitución prevalece sobre cualquier plan o tarea; se enmienda por pull request con versión semántica; /speckit-analyze verifica su cumplimiento. Versión 1.0.0, ratificada el 2026-11-15.

```

Uso de la respuesta: Generar .specify/memory/constitution.md v1.0.0 con los 7 principios del §2.3.

### Entrada #39

Fecha: 15/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5).

Objetivo: Ajustar la redacción de la constitución al español.

Prompt enviado:

> En .specify/memory/constitution.md reemplaza MUST, MUST NOT y SHOULD por DEBE, NO DEBE y DEBERÍA, ajustando la redacción para que se lea natural en español. No cambies nada más del contenido.

Uso de la respuesta: Reemplazar los términos en inglés por DEBE / NO DEBE en la constitución.

### Entrada #40

Fecha: 15/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5) con spec-kit v1.3.3.

Objetivo: Escribir la spec de resolubilidad con /speckit-specify.

Prompt enviado:

```text
/speckit-specify SPECIFY_FEATURE_DIRECTORY=specs/001-resolubilidad. Redacta en español, sin guiones largos, usando DEBE / NO DEBE (no MUST). No explores el código del repositorio. Respeta la constitución: la spec no nombra estructuras de datos, clases, módulos ni algoritmos.

Capacidad: verificación de resolubilidad de la cripta (Cripta Parte II, §3.5 y §5.4).

Contexto del juego: una cripta tiene salas conectadas por salidas; algunas salidas son puertas cerradas que requieren una llave. La cripta declara sala_inicial, sala_salida y llave_salida. Se gana entrando a sala_salida a través de una puerta que requiere llave_salida.

Qué debe hacer: antes de iniciar una partida, el programa determina si la cripta puede ganarse usando solo el esqueleto (salas, salidas, puertas cerradas y la llave que requiere cada una) y la ubicación de las llaves que publica el servicio para esa cripta (cada llave con su sala y, si la suelta un enemigo, el id de esa instancia de enemigo).

Supuestos de la verificación: el jugador puede atravesar cualquier salida abierta y cualquier salida cerrada cuya llave ya obtuvo; las llaves no se consumen; todo enemigo puede ser derrotado; una llave que suelta un enemigo se considera obtenible en la sala donde ese enemigo inicia; las trampas y los cierres automáticos no bloquean, porque la puerta puede volver a abrirse con la misma llave.

Resoluble: partiendo de la sala inicial y bajo esos supuestos, el jugador puede obtener llave_salida y llegar a sala_salida a través de una puerta que la requiere.

Resultado si es resoluble: un orden de obtención de llaves en el que cada llave aparece después de todas las llaves necesarias para alcanzarla. Si hay varios órdenes válidos cualquiera sirve, pero debe ser determinista: la misma cripta produce siempre el mismo orden.

Resultado si no es resoluble, un reporte con: las llaves que no pueden obtenerse; las puertas de la frontera bloqueada (puertas cerradas adyacentes a la región alcanzable) con la llave que requiere cada una; dónde se encuentra cada una de esas llaves (sala y, si aplica, enemigo que la suelta); y, si una llave está detrás de puertas que solo ella abre, directamente o mediante una cadena de llaves, el ciclo concreto, reportado de forma determinista.

Comportamiento en el programa: al iniciar una partida la interfaz muestra el resultado de la verificación. Si la cripta no es resoluble, la partida no inicia, salvo que el programa se haya ejecutado con la bandera --forzar. La bandera --verificar <cripta> ejecuta únicamente la verificación e imprime el resultado en consola sin abrir la interfaz, también junto con --offline. La consulta de la ubicación de llaves cuenta dentro de presupuesto_solicitudes y su respuesta puede persistirse y reutilizarse mientras coincida la versión de la cripta.

Rendimiento: la verificación de la cripta publicada más grande DEBE tardar menos de 200 ms en el equipo local, sin contar red. Obtener una llave puede volver alcanzable una región entera; repetir la exploración completa de la cripta cada vez que se obtiene una llave no es aceptable: el costo total DEBE crecer aproximadamente de forma lineal con la cantidad de salas, salidas y llaves. La frontera bloqueada y las dependencias entre llaves DEBEN salir de la misma exploración, no de exploraciones adicionales por cada llave. El modo --bench DEBE medir la verificación contra la alternativa ingenua de repetir la exploración por cada llave, con criptas sintéticas de muchas llaves encadenadas, deterministas por semilla.

Escenarios de aceptación obligatorios (Apéndice B): (1) llave_salida está detrás de la única puerta que ella misma abre: no resoluble y el reporte señala el ciclo; (2) una llave está en el campo suelta de un enemigo errante: la verificación la ubica en la sala inicial del enemigo; (3) existen varios órdenes válidos de obtención de llaves: dos ejecuciones producen el mismo orden; (4) cripta no resoluble sin --forzar: la partida no inicia y se muestra el reporte. Casos adicionales: cripta resoluble donde la única llave necesaria es llave_salida; ciclo de dos llaves (A está detrás de una puerta que requiere B, y B detrás de una puerta que requiere A); --verificar no abre la interfaz; con la misma versión de cripta, la ubicación de llaves se reutiliza sin nueva solicitud de red.

Fuera de alcance: la verificación no simula combate, tiempo, trampas ni movimiento de enemigos, no modifica el estado del juego y no reporta la ruta concreta del jugador, solo el orden de llaves.
```

Uso de la respuesta: Generar specs/001-resolubilidad/spec.md con 6 historias de usuario y los requisitos FR-001 a FR-029.

### Entrada #41

Fecha: 15/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5) con spec-kit v1.3.3.

Objetivo: Resolver ambigüedades de la spec de resolubilidad con /speckit-clarify.

Prompt enviado:

```text
/speckit-clarify Prioriza estas ambigüedades: (1) si el orden de llaves incluye todas las llaves obtenibles o solo las necesarias para ganar; (2) qué se reporta cuando hay varios ciclos; (3) qué pasa si una misma llave aparece en varias ubicaciones; (4) si la partida inicia cuando la ubicación de llaves no está disponible; (5) qué código de salida devuelve --verificar. Ajusta el escenario US1-1 y el caso borde "llave_salida en la sala inicial" para que sean consistentes con la respuesta (1). Redacta en español, sin guiones largos, usando DEBE / NO DEBE.
```

Respuestas enviadas, en orden: `B` · `Todos, ordenados por menor id` · `A; inalcanzable: listar todas ubicaciones` · `A` · `A`

Uso de la respuesta: Registrar 5 aclaraciones en la spec y ajustar FR-002, FR-007, FR-012, FR-013 y FR-022, y agregar FR-018a.


### Entrada #38

Fecha: 15/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5) con spec-kit v1.3.3.

Objetivo: Crear la constitución del proyecto con /speckit-constitution.

Prompt enviado:

```text
/speckit-constitution Constitución del proyecto "Cripta" (EIF207 Estructuras de Datos, II Ciclo 2026, Parte II). Redacta todo en español, sin guiones largos. No explores el repositorio: usa solo esta información. Muestra el Sync Impact Report solo en tu respuesta, no lo dejes en el archivo.

Principios:

I. Estructuras de datos propias (NO NEGOCIABLE). Las estructuras de los problemas evaluados se implementan a mano. Prohibido usar dict o set como índice, caché o tabla de búsqueda, y prohibidos heapq, bisect, collections (deque, OrderedDict, defaultdict, Counter), networkx y cualquier biblioteca de grafos o de búsqueda de rutas. Permitido: list como almacenamiento contiguo, dict solo para leer el JSON de las respuestas, y struct, json, requests y arcade. Un plan que proponga una dependencia prohibida se corrige antes de generar tareas.

II. Determinismo. La misma versión de cripta, la misma semilla y las mismas acciones producen la misma partida. Toda aleatoriedad usa la instancia propia random.Random(semilla) del modelo; nunca el generador global, la hora del sistema ni el orden de llegada de respuestas HTTP. Todo empate se resuelve con una regla explícita (número de secuencia, menor id).

III. Separación MVC. El modelo no conoce HTTP, archivos ni la interfaz. La red y el disco se acceden mediante adaptadores. Los modos --replay, --bench y --verificar no instancian la vista.

IV. Ningún dato de una cripta en el código. No se escriben en el código ids de salas o entidades, cantidades de páginas, presupuestos ni estadísticas de una cripta concreta; todo proviene del servicio web o de los datos offline.

V. Presupuesto de red. Se respeta presupuesto_solicitudes de cada cripta. Toda solicitud HTTP cuenta, incluidos reintentos y la consulta de llaves. Lo persistido se reutiliza validando su versión.

VI. Rendimiento con evidencia. Toda afirmación de rendimiento se respalda con mediciones de --bench, deterministas por semilla. Cada decisión de estructura de datos compara al menos una alternativa medida.

VII. La especificación precede a la implementación (NO NEGOCIABLE). Cada capacidad tiene su spec.md confirmada en Git antes que el código que la implementa. Si la spec resulta incorrecta, se corrige primero la spec y luego el código, en commits separados. Cada requisito funcional tiene un id estable (FR-001); cada escenario de aceptación tiene una prueba automatizada o un partida.log que cita su FR; cada tarea cita los FR que atiende. spec.md no nombra estructuras de datos, clases ni módulos.

Sección "Restricciones técnicas": Python 3.13 o superior con uv; vista con Arcade; pruebas con unittest en la carpeta pruebas/; agente Claude Code con spec-kit v1.3.3 y scripts sh; el equipo trabaja en Windows con CMD.

Sección "Flujo de trabajo": por capacidad se ejecuta constitution (una vez), specify, clarify, plan, tasks, analyze e implement; clarify y analyze son obligatorios. Cada integrante trabaja en su propia rama y se integra a master mediante pull request con merge commit, nunca squash. Cada prompt a un LLM, incluidos los comandos de spec-kit con texto propio, se registra en la bitácora PROMPTS_LLM.md con fecha, integrante, herramienta, prompt textual y uso.

Gobernanza: esta constitución prevalece sobre cualquier plan o tarea; se enmienda por pull request con versión semántica; /speckit-analyze verifica su cumplimiento. Versión 1.0.0, ratificada el 2026-11-15.
```

Uso de la respuesta: Generar .specify/memory/constitution.md v1.0.0 con los 7 principios del §2.3.

### Entrada #39

Fecha: 15/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5).

Objetivo: Ajustar la redacción de la constitución al español.

Prompt enviado:

> En .specify/memory/constitution.md reemplaza MUST, MUST NOT y SHOULD por DEBE, NO DEBE y DEBERÍA, ajustando la redacción para que se lea natural en español. No cambies nada más del contenido.

Uso de la respuesta: Reemplazar los términos en inglés por DEBE / NO DEBE en la constitución.

### Entrada #40

Fecha: 15/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5) con spec-kit v1.3.3.

Objetivo: Escribir la spec de resolubilidad con /speckit-specify.

Prompt enviado:

```text
/speckit-specify SPECIFY_FEATURE_DIRECTORY=specs/001-resolubilidad. Redacta en español, sin guiones largos, usando DEBE / NO DEBE (no MUST). No explores el código del repositorio. Respeta la constitución: la spec no nombra estructuras de datos, clases, módulos ni algoritmos.

Capacidad: verificación de resolubilidad de la cripta (Cripta Parte II, §3.5 y §5.4).

Contexto del juego: una cripta tiene salas conectadas por salidas; algunas salidas son puertas cerradas que requieren una llave. La cripta declara sala_inicial, sala_salida y llave_salida. Se gana entrando a sala_salida a través de una puerta que requiere llave_salida.

Qué debe hacer: antes de iniciar una partida, el programa determina si la cripta puede ganarse usando solo el esqueleto (salas, salidas, puertas cerradas y la llave que requiere cada una) y la ubicación de las llaves que publica el servicio para esa cripta (cada llave con su sala y, si la suelta un enemigo, el id de esa instancia de enemigo).

Supuestos de la verificación: el jugador puede atravesar cualquier salida abierta y cualquier salida cerrada cuya llave ya obtuvo; las llaves no se consumen; todo enemigo puede ser derrotado; una llave que suelta un enemigo se considera obtenible en la sala donde ese enemigo inicia; las trampas y los cierres automáticos no bloquean, porque la puerta puede volver a abrirse con la misma llave.

Resoluble: partiendo de la sala inicial y bajo esos supuestos, el jugador puede obtener llave_salida y llegar a sala_salida a través de una puerta que la requiere.

Resultado si es resoluble: un orden de obtención de llaves en el que cada llave aparece después de todas las llaves necesarias para alcanzarla. Si hay varios órdenes válidos cualquiera sirve, pero debe ser determinista: la misma cripta produce siempre el mismo orden.

Resultado si no es resoluble, un reporte con: las llaves que no pueden obtenerse; las puertas de la frontera bloqueada (puertas cerradas adyacentes a la región alcanzable) con la llave que requiere cada una; dónde se encuentra cada una de esas llaves (sala y, si aplica, enemigo que la suelta); y, si una llave está detrás de puertas que solo ella abre, directamente o mediante una cadena de llaves, el ciclo concreto, reportado de forma determinista.

Comportamiento en el programa: al iniciar una partida la interfaz muestra el resultado de la verificación. Si la cripta no es resoluble, la partida no inicia, salvo que el programa se haya ejecutado con la bandera --forzar. La bandera --verificar <cripta> ejecuta únicamente la verificación e imprime el resultado en consola sin abrir la interfaz, también junto con --offline. La consulta de la ubicación de llaves cuenta dentro de presupuesto_solicitudes y su respuesta puede persistirse y reutilizarse mientras coincida la versión de la cripta.

Rendimiento: la verificación de la cripta publicada más grande DEBE tardar menos de 200 ms en el equipo local, sin contar red. Obtener una llave puede volver alcanzable una región entera; repetir la exploración completa de la cripta cada vez que se obtiene una llave no es aceptable: el costo total DEBE crecer aproximadamente de forma lineal con la cantidad de salas, salidas y llaves. La frontera bloqueada y las dependencias entre llaves DEBEN salir de la misma exploración, no de exploraciones adicionales por cada llave. El modo --bench DEBE medir la verificación contra la alternativa ingenua de repetir la exploración por cada llave, con criptas sintéticas de muchas llaves encadenadas, deterministas por semilla.

Escenarios de aceptación obligatorios (Apéndice B): (1) llave_salida está detrás de la única puerta que ella misma abre: no resoluble y el reporte señala el ciclo; (2) una llave está en el campo suelta de un enemigo errante: la verificación la ubica en la sala inicial del enemigo; (3) existen varios órdenes válidos de obtención de llaves: dos ejecuciones producen el mismo orden; (4) cripta no resoluble sin --forzar: la partida no inicia y se muestra el reporte. Casos adicionales: cripta resoluble donde la única llave necesaria es llave_salida; ciclo de dos llaves (A está detrás de una puerta que requiere B, y B detrás de una puerta que requiere A); --verificar no abre la interfaz; con la misma versión de cripta, la ubicación de llaves se reutiliza sin nueva solicitud de red.

Fuera de alcance: la verificación no simula combate, tiempo, trampas ni movimiento de enemigos, no modifica el estado del juego y no reporta la ruta concreta del jugador, solo el orden de llaves.
```

Uso de la respuesta: Generar specs/001-resolubilidad/spec.md con 6 historias de usuario y los requisitos FR-001 a FR-029.

### Entrada #41

Fecha: 15/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5) con spec-kit v1.3.3.

Objetivo: Resolver ambigüedades de la spec de resolubilidad con /speckit-clarify.

Prompt enviado:

```text
/speckit-clarify Prioriza estas ambigüedades: (1) si el orden de llaves incluye todas las llaves obtenibles o solo las necesarias para ganar; (2) qué se reporta cuando hay varios ciclos; (3) qué pasa si una misma llave aparece en varias ubicaciones; (4) si la partida inicia cuando la ubicación de llaves no está disponible; (5) qué código de salida devuelve --verificar. Ajusta el escenario US1-1 y el caso borde "llave_salida en la sala inicial" para que sean consistentes con la respuesta (1). Redacta en español, sin guiones largos, usando DEBE / NO DEBE.
```

Respuestas enviadas, en orden: `B` · `Todos, ordenados por menor id` · `A; inalcanzable: listar todas ubicaciones` · `A` · `A`

Uso de la respuesta: Registrar 5 aclaraciones en la spec y ajustar FR-002, FR-007, FR-012, FR-013 y FR-022, y agregar FR-018a.

### Entrada #42

Fecha: 15/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5) con spec-kit v1.3.3.

Objetivo: Escribir la spec de niebla de guerra e «ir a» con /speckit-specify.

Prompt enviado:

```text
/speckit-specify SPECIFY_FEATURE_DIRECTORY=specs/002-niebla-ir-a. Redacta en español, sin guiones largos, usando DEBE / NO DEBE (no MUST). No explores el código del repositorio. Respeta la constitución: la spec no nombra estructuras de datos, clases, módulos ni algoritmos.

Capacidad: niebla de guerra y viaje automático «ir a» (Cripta Parte II, §3.3, §3.4 y §5.3).

Niebla de guerra. El jugador ya no ve el mapa completo. Para el jugador cada sala está en uno de tres estados: explorada (el jugador entró a ella al menos una vez; la sala inicial está explorada desde el instante 0), de la que conoce nombre, salidas, costo de cada salida y el estado de sus puertas según su última observación; avistada (no explorada, pero destino de una salida de una sala explorada), de la que solo sabe que existe; y desconocida (ninguna de las anteriores), de la que no sabe nada.

Memoria de puertas: el jugador observa una puerta cuando está en cualquiera de las dos salas que conecta; mientras permanece en una sala, los cambios de esas puertas se reflejan en su mapa en el momento en que ocurren. El mapa recuerda el estado de cada puerta tal como estaba en su última observación, aunque haya cambiado después (por ejemplo, una puerta con cierre automático puede figurar abierta en el mapa y estar cerrada en realidad).

Antorcha: mientras esté encendida, al entrar a una sala también quedan exploradas todas sus vecinas, a través de cualquier salida, abierta o cerrada. Explorar una vecina de esta forma revela su nombre y salidas, no su contenido, y no activa sus enemigos ni sus trampas.

Separación entre mapa y conocimiento: el programa sigue descargando el esqueleto completo y la precarga de contenido puede usarlo, porque es infraestructura; pero todo lo que la interfaz muestra del mapa y todo lo que usa «ir a» DEBE derivarse exclusivamente del conocimiento del jugador. El conocimiento del jugador es estado del juego: DEBE guardarse y restaurarse con la partida, revertirse con el pergamino de retroceso y poder reconstruirse para cualquier instante pasado (lo usa la línea de tiempo, spec 004). La interfaz DEBE ofrecer un comando para ver el mapa conocido: salas exploradas, sus salidas (con costo y estado recordado de la puerta) y salas avistadas.

Viaje automático. El comando ir a <sala> lleva al jugador a una sala explorada mediante una secuencia de movimientos ordinarios. La ruta se calcula solo con el conocimiento del jugador: solo salas exploradas y solo salidas que su mapa recuerda abiertas. Se minimiza la suma de costos de las salidas (una salida sin costo declarado vale 100) y se desempata igual que el cazador: el primer paso va hacia la vecina de menor id entre las que inician una ruta de costo mínimo. Cada paso es una acción del jugador completa: consume tiempo según el costo de la salida y entre paso y paso ocurren normalmente los eventos del reloj. La ruta se recalcula antes de cada paso con el conocimiento vigente; si al llegar a una sala el jugador observa que una puerta de su ruta está cerrada, el siguiente cálculo la evita. El viaje se detiene cuando el jugador llega al destino, entra a una sala que contiene enemigos (activos o dormidos), recibe cualquier daño (ataque, trampa o veneno) o deja de existir una ruta conocida; la interfaz DEBE mostrar el motivo de la detención. «ir a» no abre puertas aunque el jugador tenga la llave. En el registro de la partida cada paso DEBE quedar como un movimiento individual y la orden ir a como un comentario que la reproducción ignora. El pergamino de retroceso revierte únicamente el último paso, porque cada paso es una acción del jugador, y el viaje no continúa. «ir a» hacia la sala actual se rechaza sin consumir tiempo.

Rendimiento: consultar si una sala está explorada, avistada o desconocida y el estado recordado de una puerta son operaciones frecuentes (en cada vista, cada paso de «ir a» y cada actualización por antorcha) y su costo NO DEBE crecer con el tamaño del mapa conocido. Explorar nuevas salas DEBE costar en proporción a las salas reveladas, no al tamaño del mapa conocido. Registrar e invertir los cambios del conocimiento DEBE costar en proporción a los cambios. El cálculo de un paso de «ir a» DEBE tardar menos de 5 ms con el mapa conocido completo de la cripta de referencia. El modo --bench DEBE medir las consultas al mapa conocido y el cálculo de «ir a».

Escenarios de aceptación obligatorios (Apéndice B): (1) ir a hacia una sala no explorada: se rechaza y no consume tiempo; (2) el mapa recuerda abierta una puerta que en realidad está cerrada: al observarla, el mapa se actualiza y la ruta se recalcula; si no queda ruta, el viaje se detiene sin consumir tiempo adicional; (3) ir a entra a una sala con enemigos dormidos: los enemigos se activan según las reglas de la Parte I y el viaje se detiene; (4) con la antorcha encendida, entrar a una sala explora sus vecinas sin activar sus enemigos ni sus trampas; (5) un pergamino revierte una entrada con antorcha encendida: las salas exploradas por la antorcha vuelven a su estado anterior; (6) un pergamino durante un viaje: revierte solo el último paso y el viaje no continúa. Casos adicionales: entre una ruta de menos salas pero mayor costo y otra de más salas y menor costo, ir a sigue la de menor costo; dos vecinas inician rutas de costo mínimo: el primer paso va a la de menor id; ir a no atraviesa una puerta cerrada aunque el jugador tenga su llave; la vista nunca muestra salas desconocidas.

Fuera de alcance: el comportamiento del cazador (spec 003), que conoce el mapa completo y no usa la niebla; el formato binario del archivo de guardado y la línea de tiempo (spec 004), que consumen el conocimiento del jugador; el diseño visual de la interfaz.
```

Uso de la respuesta: Generar specs/002-niebla-ir-a/spec.md con 8 historias de usuario y los requisitos FR-001 a FR-041.

### Entrada #43

Fecha: 15/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5) con spec-kit v1.3.3.

Objetivo: Resolver ambigüedades de la spec de niebla de guerra e «ir a» con /speckit-clarify.

Prompt enviado:

```text
/speckit-clarify Prioriza estas ambigüedades: (1) qué sabe el jugador del estado de las puertas de una sala explorada por la antorcha que nunca observó directamente, y si «ir a» puede usarlas; (2) si encender la antorcha estando dentro de una sala explora las vecinas de la sala actual o solo al entrar a la siguiente sala. Si encuentras otras ambigüedades de mayor impacto, pregúntalas después de estas. Redacta en español, sin guiones largos, usando DEBE / NO DEBE.
```

Respuestas enviadas, en orden: `A` (puerta sin observar: el mapa no la muestra ni abierta ni cerrada e «ir a» no la usa) · `A` (el viaje se detiene solo si hay al menos un enemigo vivo en la sala)

Uso de la respuesta: Registrar 2 aclaraciones en la spec: el estado "sin observar" de las puertas y la detención del viaje solo con enemigos vivos.

### Entrada #44

Fecha: 15/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5).

Objetivo: Agregar la aclaración sobre encender la antorcha dentro de una sala.

Prompt enviado:

> Registra también esta aclaración en la sección Clarifications y en FR-010: encender la antorcha estando dentro de una sala NO explora las vecinas de esa sala; solo se exploran al entrar a la siguiente sala con la antorcha encendida.

Uso de la respuesta: Agregar la aclaración a la spec y ajustar FR-010.

### Entrada #45

Fecha: 15/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5) con spec-kit v1.3.3.

Objetivo: Planificar la implementación de la resolubilidad con /speckit-plan.

Prompt enviado:

```text
/speckit-plan Planifica la spec specs/001-resolubilidad (usa SPECIFY_FEATURE_DIRECTORY=specs/001-resolubilidad al correr setup-plan.sh). Redacta en español, sin guiones largos, usando DEBE / NO DEBE. Para el contexto técnico lee solo estos archivos de src/cripta: bootstrap.py, adaptadores/Crypt_Data_Source.py, adaptadores/Network_Adapter.py, adaptadores/AdaptadorOffline.py, adaptadores/Almacen_Disco.py, adaptadores/Guardar_Llamadas_API.py, servicio/CriptaService.py, dto/FactoryDto_Partida.py, dto/Partida_dto.py, controlador/InicioPartidaControlador.py, estructuras/Indice_Salas.py, estructuras/Ordenamientos.py y bench.py. No leas la carpeta vista/ salvo para ubicar dónde se muestra el inicio de la partida.

Hechos del proyecto que el plan DEBE respetar:
- Python 3.13, uv, Arcade y unittest en pruebas/. MVC: el algoritmo vive en el modelo y no conoce HTTP ni archivos.
- Constitución: prohibidos dict y set como índice, heapq, bisect, collections, networkx, sorted() y list.sort(); se usan list como almacenamiento y los ordenamientos propios de estructuras/Ordenamientos.py.
- Los ids de sala son enteros pequeños y secuenciales: IndiceSalas ya usa direccionamiento directo con list.
- En los datos del servicio cada puerta cerrada se declara solo en la salida de un lado (por ejemplo, en cripta-01 la salida E de la sala 2 hacia la 5 requiere itm_llave_bronce y la salida O de la 5 hacia la 2 está abierta). La verificación DEBE tratar cada salida como dirigida, con la llave que declara su lado.
- La ubicación de llaves llega de GET /criptas/<id>/llaves con la forma {"llaves": [{"id": "itm_llave_bronce", "sala": 4}, {"id": "itm_llave_negra", "sala": 12, "enemigo": "e-1203"}]}; cuenta en presupuesto_solicitudes y se persiste con la versión de la cripta, igual que el esqueleto. El paquete datos_offline actual no trae llaves: en ese caso el resultado es "no verificable".
- Todas las clases que implementan CryptDataSource DEBEN implementar la nueva consulta.

Diseño propuesto para evaluar en research.md, con alternativas y complejidad:
- Exploración en anchura desde sala_inicial con una cola propia (list más índice de cabeza, sin deque). Cada salida cerrada cuya llave aún no se tiene se agrega a una lista de espera de esa llave; al obtener la llave se liberan sus salidas en espera. Cada sala y cada salida se procesan una sola vez: costo O(S + E + K).
- Las llaves se identifican por un índice entero obtenido de un índice de ids de llave construido una vez (comparar: arreglo ordenado con el ordenamiento propio más búsqueda binaria propia, frente a una tabla hash propia con función de hash determinista). Los datos por llave (obtenida, lista de espera, ubicaciones) viven en listas indexadas por ese índice.
- El orden de llaves es el orden en que cada llave se vuelve obtenible, con orden determinista de salas, salidas y llaves.
- Reporte de no resoluble y ciclos: DEBE salir de la misma exploración (por ejemplo, continuándola más allá de la frontera bloqueada y registrando, para cada sala alcanzada así, qué llave la liberó), sin repetir exploraciones por llave, y reportar cada ciclo empezando por su llave de menor id. Justifica en research.md que el método no reporta ciclos falsos cuando una llave tiene caminos alternativos.
- Alternativa descartada que --bench DEBE medir: repetir la exploración completa cada vez que se obtiene una llave, O(K · (S + E)), con criptas sintéticas de llaves encadenadas deterministas por semilla.

Entregables: plan.md (con módulos afectados, constitution check y mediciones previstas), research.md (decisión, razón y alternativas), data-model.md, contracts/ (salida y códigos de --verificar, y la nueva consulta del adaptador) y quickstart.md. No escribas código de implementación.
```

Uso de la respuesta: Generar plan.md, research.md (decisiones D1 a D8), data-model.md, contracts/ y quickstart.md de la resolubilidad.

### Entrada #46

Fecha: 15/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5).

Objetivo: Registrar en el plan las decisiones tomadas sobre los puntos abiertos.

Prompt enviado:

```text
Actualiza specs/001-resolubilidad/plan.md y research.md con estas decisiones, sin cambiar nada más: (1) se aceptan los ciclos del grafo de testigos; FR-012 de la spec ahora define ciclo como una cadena encontrada por la exploración en la que cada llave está detrás de una puerta que requiere la siguiente: alinea D6 con esa definición; (2) se acepta O(S + E + K) más el factor log K del índice de llaves; (3) --replay y continuar una partida guardada no verifican, como dice ahora la sección de supuestos de la spec; (4) la consulta de llaves suma al presupuesto y, si no alcanza, el resultado es "no verificada"; (5) en pruebas/ hay fuentes de datos falsas que no heredan de CryptDataSource, en test_partida.py, test_inventario.py, test_combate_efectos.py y test_guardados.py: DEBEN recibir la consulta de llaves devolviendo "sin datos", y las 46 pruebas de la Parte I DEBEN seguir pasando. Convierte la sección de puntos a confirmar en decisiones tomadas. Redacta en español, sin guiones largos.
```

Uso de la respuesta: Convertir los puntos a confirmar del plan en decisiones tomadas y alinear D3, D6, D7 y D8 de research.md.

### Entrada #47

Fecha: 15/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5).

Objetivo: Corregir la regla de regresión de pruebas en el plan.

Prompt enviado:

> En specs/001-resolubilidad/plan.md y research.md reemplaza la regla "las 46 pruebas de la Parte I DEBEN seguir pasando" por: "la selección de pruebas del README DEBE seguir pasando y la suite completa de pruebas/ NO DEBE tener fallas nuevas respecto de una línea base registrada antes de implementar". No cambies nada más.

Uso de la respuesta: Reemplazar la regla de regresión por una línea base registrada antes de implementar.

### Entrada #48

Fecha: 15/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5) con spec-kit v1.3.3.

Objetivo: Generar las tareas de la resolubilidad con /speckit-tasks.

Prompt enviado:

```text
/speckit-tasks Genera las tareas de specs/001-resolubilidad (usa SPECIFY_FEATURE_DIRECTORY=specs/001-resolubilidad). Redacta en español, sin guiones largos. Cada tarea DEBE ser pequeña, verificable y citar al menos un FR; las tareas de soporte citan los FR que protegen. Incluye una prueba unittest en pruebas/ por cada escenario de aceptación, incluidos los 4 del Apéndice B, citando su FR en el docstring de la prueba. Incluye al inicio una tarea para registrar la línea base de la suite de pruebas existente y al final una tarea de regresión contra esa línea base. Incluye las tareas de --bench (M1 a M6) y la de la sección de DECISIONES.md de este problema.
```

Uso de la respuesta: Generar tasks.md con 86 tareas (T001 a T086) que citan sus FR.

### Entrada #49

Fecha: 15/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5) con spec-kit v1.3.3.

Objetivo: Revisar la consistencia entre spec, plan y tareas con /speckit-analyze.

Prompt enviado:

```text
/speckit-analyze Redacta en español. Revisa en especial: dependencias prohibidas por la constitución, que cada FR tenga al menos una tarea, que cada escenario del Apéndice B tenga su prueba y que FR-012 sea consistente con D6 de research.md.
```

Uso de la respuesta: Obtener el informe de análisis con 10 hallazgos (F1 a F10), sin dependencias prohibidas y con cobertura de 30 de 30 FR.

### Entrada #50

Fecha: 15/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5) con spec-kit v1.3.3.

Objetivo: Repetir el análisis de consistencia (segunda ejecución, sin cambios en los archivos).

Prompt enviado:

```text
/speckit-analyze Redacta en español. Revisa en especial: dependencias prohibidas por la constitución, que cada FR tenga al menos una tarea, que cada escenario del Apéndice B tenga su prueba y que FR-012 sea consistente con D6 de research.md.
```

Uso de la respuesta: Confirmar que los hallazgos F1 a F10 seguían iguales antes de aplicar las correcciones.

### Entrada #51

Fecha: 15/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5).

Objetivo: Aplicar las correcciones del análisis en el plan y las tareas.

Prompt enviado:

```text
Sí, aplica las ediciones, con estas precisiones. F1: agrega una medición y una prueba con una cripta sintética generada por semilla, de al menos 10 veces el tamaño del esqueleto más grande de datos_offline, que verifique el límite de 200 ms sin red; M3 sigue midiendo la cripta real cuando haya llaves. F2: agrega el campo opcional estadisticas (salas encoladas, salidas examinadas, llaves obtenidas) en el DTO, en data-model.md y en T025 a T027. F3: agrega a T085 los FR que valida el quickstart. F4: ya está resuelto, la spec se confirmó en su propio commit. F5: el registro de prompts se hace fuera de tasks.md, en cada commit; no agregues tarea. F6: agrega la prueba de que --bench no importa arcade. F7: ya fijé en la spec que los ids de llave se comparan como cadenas en orden lexicográfico; refléjalo en data-model.md. F8: agrega a T020 la nota de que el servicio publica como sala la sala donde inicia el enemigo (contrato del §4.2). F9: agrega test_cola_lista.py al árbol de pruebas del plan. F10: NetworkAdapter no tiene sesión inyectable y usa requests.get directamente; T064 DEBE usar unittest.mock.patch sobre requests.get en vez de modificar el adaptador. Al final confirma que ninguna tarea queda sin FR. No toques spec.md.
```

Uso de la respuesta: Corregir los hallazgos F1 a F3


### Entrada #52

Fecha: 15/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5) con spec-kit v1.3.3.

Objetivo: Planificar la implementación de la niebla de guerra e «ir a» con /speckit-plan.

Prompt enviado:

```text
/speckit-plan Planifica la spec specs/002-niebla-ir-a (usa SPECIFY_FEATURE_DIRECTORY=specs/002-niebla-ir-a al correr setup-plan.sh). Redacta en español, sin guiones largos, usando DEBE / NO DEBE. Para el contexto técnico lee solo estos archivos de src/cripta: controlador/ExploracionControlador.py, controlador/Aplicacion.py, controlador/CicloAccionesControlador.py, controlador/PartidaControlador.py, estructuras/Historial_Retroceso.py, estructuras/Salidas.py, estructuras/Indice_Salas.py, estructuras/Agenda_Eventos.py, modelo/Sala.py, modelo/Puertas.py, modelo/Efectos.py, modelo/Jugador.py, dto/FactoryDto_Partida.py, dto/Partida_dto.py, replay/reproductor.py y bench.py; de vista/grafica/escena.py lee solo el método minimapa. Puedes consultar specs/001-resolubilidad/plan.md para reutilizar decisiones ya tomadas (cola propia, línea base de pruebas).

Hechos del proyecto que el plan DEBE respetar:
- Python 3.13, uv, Arcade y unittest en pruebas/. MVC: el conocimiento del jugador vive en el modelo.
- Constitución: prohibidos dict y set como índice, heapq, bisect, collections, networkx, sorted() y list.sort(); se usan list como almacenamiento y los ordenamientos propios.
- Los ids de sala son enteros pequeños y secuenciales (IndiceSalas usa direccionamiento directo con list). Cada sala tiene como máximo 4 salidas (N, S, E, O).
- En los datos cada puerta cerrada se declara solo en la salida de un lado y la salida inversa está abierta: cada salida es dirigida y tiene su propio estado. Por eso, estando en una sala, el jugador observa sus salidas y también las salidas de otras salas que entran a ella.
- El costo de cada salida viene del campo costo del esqueleto (100 si no se declara). Esta capacidad lee el costo para las rutas; el tiempo de moverse según el costo lo implementa la spec 003.
- Todo cambio del conocimiento DEBE registrarse en el historial de retroceso como cambio invertible, para que lo revierta el pergamino y lo reconstruya la línea de tiempo (spec 004). El formato binario del guardado es de la spec 004: esta capacidad solo expone el conocimiento de forma serializable.
- La regla de regresión es la misma de la spec 001: la selección del README y la suite completa sin fallas nuevas respecto de una línea base.

Diseño propuesto para evaluar en research.md, con alternativas y complejidad:
- Estado de sala en una lista indexada por id (desconocida, avistada, explorada). Memoria de puertas en una lista plana indexada por sala por 4 más la dirección, con tres valores: sin observar, abierta y cerrada. Una lista de salidas entrantes por sala, construida una vez desde el esqueleto. Consultas en O(1); explorar cuesta lo revelado.
- Cambios del conocimiento registrados en el historial existente como cambios invertibles; si el historial no permite asignar una posición de una lista, agregar ese tipo de cambio.
- «ir a»: Dijkstra inverso desde el destino sobre el subgrafo conocido (salas exploradas y salidas recordadas abiertas), con un montículo mínimo propio, para obtener la distancia de cada sala al destino; el paso elige la vecina con costo de la salida más distancia mínimos y desempata por menor id. Se recalcula antes de cada paso. Comparar con Dijkstra desde el origen y con reutilizar distancias entre pasos.
- El montículo mínimo DEBE ser genérico y reutilizable, porque la búsqueda del cazador (spec 003) también lo necesita. Justifica en research.md si «ir a» comparte implementación de búsqueda con el cazador o conviene separarla (§5.3).
- Cada paso del viaje DEBE pasar por el mismo flujo de acción del jugador que un movimiento normal, para que consuma tiempo, ejecute eventos, se registre como movimiento individual en partida.log y sea reversible. La orden ir a se escribe en el registro como una línea de comentario que el reproductor ignora.
- La vista muestra en el minimapa solo salas exploradas y avistadas, con el costo y el estado recordado de cada salida, y muestra en la bitácora el motivo de detención del viaje.
- --bench DEBE medir las consultas al mapa conocido con mapas de tamaños crecientes y el cálculo de un paso de ir a con el mapa conocido completo, deterministas por semilla.

Entregables: plan.md (con módulos afectados, constitution check, decisiones o puntos a confirmar y mediciones previstas), research.md (decisión, razón y alternativas), data-model.md, contracts/ (comando ir a y motivos de detención, formato del comentario en partida.log, y la interfaz serializable del conocimiento para la spec 004) y quickstart.md. No escribas código de implementación.
```

Uso de la respuesta: Generar plan.md (12 decisiones y 12 puntos a confirmar), research.md (D1 a D15), data-model.md, contracts/ y quickstart.md de la niebla e «ir a».

### Entrada #53

Fecha: 15/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5).

Objetivo: Registrar en el plan de la niebla las decisiones sobre los puntos C1 a C12.

Prompt enviado:

```text
Actualiza specs/002-niebla-ir-a/plan.md y research.md con estas decisiones sobre los puntos a confirmar, sin cambiar nada más, y convierte esa sección en decisiones tomadas. C1: un costo declarado menor que 1 se trata como 100 y se avisa en la bitácora; no hay tope de pasos, porque durante un viaje ninguna puerta se puede abrir (ni el jugador ni los enemigos abren puertas en un viaje), así que la memoria cambia un número finito de veces y entre cambios cada paso acerca al destino: documenta ese argumento de terminación. C2: se agregan los motivos movimiento_rechazado y partida_terminada; no se agrega cancelado; la spec ya los incluye en FR-031a. C3: prioridad partida_terminada, daño, enemigos, llegada, como dice FR-031a. C4: el daño mínimo es 1 según la Parte I (§2.6), así que basta comparar la vida antes y después del paso. C5: enemigos vivos en el instante de la entrada. C6: vecina es el destino de una salida de la sala. C7: se acepta; actualizar_vecindad NO DEBE copiar el contenido de ninguna vecina y es_salida_final solo se muestra si la vecina está explorada; las pruebas de la Parte I que lo asuman se ajustan en tareas. C8: GestorPartida._aplicar_reversion revierte lista_agregada con una búsqueda lineal; el conocimiento NO DEBE usar lista_agregada sino un cambio nuevo lista_asignada (lista, posición, valor anterior) que se revierte en O(1); lista_agregada no se modifica. C9: la spec 001 se implementa antes que esta. C10 y C12: se aceptan las propuestas. C11: se propone compartir el montículo y Rutas.py con el cazador; la spec 003 lo confirma. Redacta en español, sin guiones largos.
```

Uso de la respuesta: Convertir los puntos C1 a C12 del plan en decisiones tomadas y documentar el argumento de terminación del viaje.

### Entrada #54

Fecha: 15/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5) con spec-kit v1.3.3.

Objetivo: Generar las tareas de la niebla e «ir a» con /speckit-tasks.

Prompt enviado:

```text
/speckit-tasks Genera las tareas de specs/002-niebla-ir-a (usa SPECIFY_FEATURE_DIRECTORY=specs/002-niebla-ir-a). Redacta en español, sin guiones largos. Cada tarea DEBE ser pequeña, verificable y citar al menos un FR; las tareas de soporte citan los FR que protegen. La primera tarea de implementación agrega el cambio lista_asignada al historial (decisión C8). Incluye una prueba unittest en pruebas/ por cada escenario de aceptación, incluidos los 6 del Apéndice B, citando su FR en el docstring. Usa la línea base de pruebas registrada por la spec 001 (no crees otra) e incluye al final una tarea de regresión contra ella. Incluye las tareas de --bench (K1 a K9) y la de la sección de docs/decisiones.md de este problema.
```

Uso de la respuesta: Generar tasks.md con 104 tareas (T001 a T104) que citan sus FR.

### Entrada #55

Fecha: 15/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5) con spec-kit v1.3.3.

Objetivo: Revisar la consistencia entre spec, plan y tareas de la niebla con /speckit-analyze.

Prompt enviado:

```text
/speckit-analyze Redacta en español. Revisa en especial: dependencias prohibidas por la constitución, que cada FR tenga al menos una tarea, que cada escenario del Apéndice B tenga su prueba, que ninguna tarea quede sin FR y que todo cambio del conocimiento pase por el historial como cambio invertible.
```

Uso de la respuesta: Obtener el informe con 10 hallazgos (0 críticos, 1 alto), sin dependencias prohibidas y con 42 de 43 FR cubiertos.

### Entrada #56

Fecha: 15/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5).

Objetivo: Aplicar las correcciones del análisis en el plan y las tareas de la niebla.

Prompt enviado:

```text
Sí, aplica estas ediciones en plan.md, quickstart.md, contracts/ y tasks.md de specs/002-niebla-ir-a, sin tocar spec.md. C2: en T045 agrega la detección de llegada al destino y la detención con motivo llegada; US4 agrega los demás motivos. C1: cita FR-013 en T022 y en T102, y que T102 revise que la vista e ir a no lean el esqueleto completo. I1: plan y quickstart DEBEN apuntar a specs/001-resolubilidad/linea_base.txt. I2: el plan y el contrato citan FR-031a para C2 y C3. I3: agrega al plan los archivos de prueba que crean las tareas. U1: el viaje fija la bandera en su propio estado antes de llamar a mover y _accion_jugador la consulta. U2: agrega una prueba sin ventana que confirme que el motivo de detención llega a la bitácora. P1: aplica tu recomendación. D1: la spec 001 se implementa antes en la misma rama; T087 usa su --semilla y su criterio de cripta de referencia, sin implementar una versión mínima. A1: usa el umbral 1,5 de K1 en K2. Deja escrito en T019 y T074 que iniciar y restaurar escriben sin historial a propósito. Al final confirma que ninguna tarea queda sin FR.
```

Uso de la respuesta: Corregir los hallazgos C1, C2, I1 a I3, U1, U2, P1, D1 y A1 en el plan y las tareas de la niebla.


### Entrada #57

Fecha: 15/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5) con spec-kit v1.3.3.

Objetivo: Implementar la Fase 2 (fundamentos) de la resolubilidad con /speckit-implement.

Prompt enviado:

```text
/speckit-implement Implementa solo la Fase 2 de specs/001-resolubilidad, tareas T002 a T015 (usa SPECIFY_FEATURE_DIRECTORY=specs/001-resolubilidad). T001 ya está hecha y confirmada en Git. Respeta la constitución y el orden de dependencias de tasks.md: escribe primero cada prueba indicada, comprueba que falla, y después el código. No modifiques .gitignore ni archivos fuera de los que nombran las tareas. Comentarios y docstrings en español, sin guiones largos. Al terminar, ejecuta T014 y las pruebas nuevas (pruebas.test_cola_lista y pruebas.test_indice_llaves), marca con [X] las tareas completadas en tasks.md y detente: no avances a la Fase 3.
```

Uso de la respuesta: Crear el DTO de verificación, ColaLista, IndiceLlaves, la consulta key_locations en las tres fuentes, la persistencia de llaves y el servicio (T002 a T015).



### Entrada #58

Fecha: 15/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5) con spec-kit v1.3.3.

Objetivo: Implementar la Fase 3 (US1, veredicto y orden de llaves) de la resolubilidad con /speckit-implement.

Prompt enviado:

```text
/speckit-implement Implementa solo la Fase 3 de specs/001-resolubilidad, tareas T016 a T029 (usa SPECIFY_FEATURE_DIRECTORY=specs/001-resolubilidad). Las Fases 1 y 2 ya están hechas y confirmadas. Escribe primero las pruebas T016 a T024, comprueba que fallan, y después T025 a T028. Respeta la constitución: nada de dict, set, sorted ni list.sort; usa ColaLista, IndiceLlaves y ordenar. No modifiques .gitignore ni archivos fuera de los que nombran las tareas. Comentarios y docstrings en español, sin guiones largos. Al terminar, ejecuta T029 y la selección de pruebas del README, marca con [X] las tareas completadas y detente: no avances a la Fase 4.
```

Uso de la respuesta: Crear modelo/Resolubilidad.py (exploración por rondas con listas de espera por llave), VerificacionControlador y las pruebas de US1 (T016 a T029).

### Entrada #59

Fecha: 15/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5).

Objetivo: Alinear la definición de ronda de data-model.md con research.md D2 y con el código.

Prompt enviado:

> En specs/001-resolubilidad/data-model.md corrige la invariante 3 para que coincida con research.md D2 y con src/cripta/modelo/Resolubilidad.py: toda sala nueva, alcanzada por una salida abierta o por una salida liberada al obtener una llave, entra en la ronda siguiente a la de la sala desde la que se alcanzó. No cambies nada más.

Uso de la respuesta: Corregir la invariante 3 de data-model.md para que coincida con el código.



### Entrada #60

Fecha: 15/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5) con spec-kit v1.3.3.

Objetivo: Implementar la Fase 4 (US2, reporte de bloqueo y ciclos) de la resolubilidad con /speckit-implement.

Prompt enviado:

```text
/speckit-implement Implementa solo la Fase 4 de specs/001-resolubilidad, tareas T030 a T042 (usa SPECIFY_FEATURE_DIRECTORY=specs/001-resolubilidad). Las Fases 1 a 3 ya están hechas y confirmadas. Escribe primero las pruebas T030 a T036, comprueba que fallan, y después T037 a T041, siguiendo research.md D6 (fase especulativa sobre la misma exploración, grafo de testigos con una arista por llave y pasada de colores). Respeta la constitución: nada de dict, set, sorted ni list.sort. No modifiques .gitignore ni archivos fuera de los que nombran las tareas. Comentarios y docstrings en español, sin guiones largos. Al terminar, ejecuta T042 y la selección de pruebas del README, marca con [X] las tareas completadas y detente: no avances a la Fase 5.
```

Uso de la respuesta: Implementar la fase especulativa, el grafo de testigos, la enumeración de ciclos, el reporte de bloqueo y su formato en consola, con las pruebas de US2 (T030 a T042).

### Entrada #63

Fecha: 15/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5).

Objetivo: Corregir la falla de regresión en la prueba de bench de la Parte I.

Prompt enviado:

```text
La regresión muestra una falla nueva: pruebas.test_bench.PruebasBench.test_bench_no_construye_fuente_ni_vista espera que bootstrap llame a cripta.bench.main() sin argumentos cuando se usa --bench sin --semilla. Ajusta src/cripta/bootstrap.py para que llame a bench.main() sin argumentos si no se pasó --semilla, y a bench.main(semilla=N) si se pasó; bench.main DEBE usar 42 por defecto. No modifiques la prueba de la Parte I. Después ejecuta pruebas.test_bench y pruebas.test_bench_resolubilidad.
```

Uso de la respuesta: Se ajustó solo bootstrap.py. Sin --semilla llama a bench.main() sin argumentos; con --semilla N valida el valor y llama a bench.main(semilla=N), devolviendo 2 si no es entero. bench.py no cambió porque ya usaba 42 por defecto, y la prueba de la Parte I quedó intacta. Se confirmó que test_bench_no_importa_arcade requiere ejecutarse con uv run, porque su subproceso usa python -I y solo encuentra el paquete en el entorno del proyecto.

### Entrada #64

Fecha: 16/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5) con spec-kit (/speckit-implement).

Objetivo: Implementar la Fase 1, la Fase 2 y la historia US1 de la especificación 002 (niebla de guerra e «ir a»).

Prompt enviado:

```text
/speckit-implement Implementa únicamente la Fase 1 (Setup), la Fase 2 (Foundational) y la fase de US1 de specs/002-niebla-ir-a/tasks.md, en orden, y detente en el checkpoint de US1. Reglas:
1. T001: reutiliza como línea base specs/001-resolubilidad/regresion.txt (205 pruebas; 6 fallas preexistentes: test_datos, test_ensamblador, 3 de test_offline_cache y 1 de test_stormlight). No vuelvas a correr la suite completa.
2. Respeta la constitución: estructuras propias; prohibidos dict/set como índice o caché, heapq, bisect, collections, sorted(), list.sort() y equivalentes. --replay, --bench y --verificar no instancian la vista.
3. Pruebas con unittest en pruebas/. No modifiques pruebas de la Parte I ni de la 001.
4. No ejecutes unittest discover ni pruebas.test_guardar_llamadas (llama a la API y sobrescribe datos_offline). Para verificar usa la selección del README más las pruebas nuevas, siempre con uv run.
5. Marca [X] cada tarea al terminarla. No hagas commits.
6. Al final dame: tareas completadas, archivos creados o modificados, y el resultado de las pruebas.
```

Uso de la respuesta: Se implementaron T001 a T026. Base compartida: cambio de historial lista_asignada con reversión O(1) (Historial_Retroceso.asignar y GestorPartida), corrección de la reversión de lista_agregada para usar pop() del final según T002 y C8 (FR-037), costo e índice de dirección en Salidas, salidas entrantes, Monticulo_Minimo propio, y el modelo y DTO de Conocimiento. US1: niebla en el minimapa, panel del mapa conocido (tecla C y menú) y tooltip con estado, costo y puerta recordada. Las salas avistadas se muestran solo por su id ("Sala N") y la vecindad ya no expone enemigos ni objetos, según FR-006 y SC-002; se corrigió la cita de FR-004 a FR-006. Verificación: selección del README 58 OK, 30 pruebas nuevas OK y suite completa con 235 pruebas y las mismas 6 fallas preexistentes de la línea base, comparadas por nombre.

### Entrada #65

Fecha: 16/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5).

Objetivo: Enmendar la especificación 002 para resolver la contradicción entre FR-025 y research.md sobre el tiempo de cada paso de ir a, y agregar el requisito de descartar el viaje al iniciar o cargar una partida.

Prompt enviado:

```text
Enmienda de la spec 002 (solo documentos y, si hace falta, la prueba de T042; sin commits):
1. spec.md, FR-025: reescríbelo para que diga que cada paso de ir a DEBE ser un movimiento ordinario completo del jugador, que DEBE consumir el mismo tiempo que ese movimiento (con la spec 003, el costo de la salida; mientras tanto, el costo actual de mover) y que DEBEN ocurrir normalmente los eventos del reloj entre un paso y el siguiente.
2. spec.md: agrega FR-034a justo después de FR-034: «Iniciar o cargar una partida DEBE descartar cualquier viaje activo; el viaje NO DEBE continuar en la nueva partida.»
3. research.md, línea 391: cambia la cita de FR-034 por FR-034a.
4. tasks.md: ajusta la redacción de T042 para que la prueba compare el avance del reloj de cada paso con el de un movimiento ordinario (FR-025 enmendado). Si la prueba actual ya lo verifica, márcala [X]; si no, ajusta la prueba en pruebas/test_ir_a.py y luego márcala. Amplía T075 para que también verifique FR-034a.
5. Muéstrame el texto final de FR-025, FR-034a, T042 y T075, dime si cambiaste la prueba y ejecuta pruebas.test_ir_a con uv run.
```

Uso de la respuesta: FR-025 se enmendó para indicar que cada paso de ir a consume el mismo tiempo que un movimiento ordinario, ya que el tiempo según el costo de la salida pertenece a la spec 003 (research.md, D6). Se agregó FR-034a para descartar el viaje activo al iniciar o cargar una partida, y research.md pasó a citarlo. T042 se redactó de nuevo y quedó marcada; su prueba se ajustó para comparar cada paso con un movimiento ordinario equivalente, de modo que siga siendo válida cuando se integre la spec 003. T075 se amplió para verificar FR-034a en US6. pruebas.test_ir_a: 6 pruebas OK.



### Entrada #66

Fecha: 16/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5) con spec-kit (/speckit-implement).

Objetivo: Implementar US4 (detener el viaje ante peligro o falta de ruta) y US5 (explorar vecinas con la antorcha) de la especificación 002.

Prompt enviado:

```text
/speckit-implement Implementa únicamente la Fase 6 (US4, T049-T060 y T054a) y la Fase 7 (US5, T061-T068) de specs/002-niebla-ir-a/tasks.md, en orden, y detente en el checkpoint de US5. Reglas:
1. Respeta la constitución: estructuras propias; prohibidos dict/set como índice o caché, heapq, bisect, collections, sorted(), list.sort() y equivalentes. --replay, --bench y --verificar no instancian la vista.
2. Escribe las pruebas de cada historia antes de su implementación y confirma que fallan antes de implementar.
3. Pruebas con unittest en pruebas/. No modifiques pruebas de la Parte I, de la 001, de US1, US2 ni US3.
4. No ejecutes unittest discover ni pruebas.test_guardar_llamadas. Verifica con la selección del README más las pruebas nuevas y las de US1 a US3, siempre con uv run.
5. T059: ViajeControlador ya tiene los motivos sin_ruta, movimiento_rechazado y partida_terminada (adelantados en US3). Completa enemigos, danio, la prioridad entre motivos (FR-031a) y el corte por cantidad de pasos sin duplicar lo existente, y asegúrate de que las pruebas de US4 también cubran esos tres motivos.
6. T058: no cambies el comportamiento del combate de la Parte I; solo detecta el daño para detener el viaje. Si eso exige modificar Combate.py, detente y repórtalo antes.
7. US5: si la antorcha no existe en el código actual o su mecánica pertenece a otra spec, detente y repórtalo.
8. Si una tarea no coincide con el código o con el spec, detente y repórtalo en vez de improvisar. Si haces un ajuste que no está en las tareas, cita el FR exacto y copia su texto.
9. Marca [X] cada tarea al terminarla. No hagas commits.
10. Al final dame: tareas completadas, archivos creados o modificados, ajustes fuera de las tareas, tareas detenidas y el resultado de las pruebas.
```

Uso de la respuesta: Se implementaron T049 a T068 y T054a sin tareas detenidas. El viaje se detiene por enemigos activos (bandera entrada_con_enemigos en ExploracionControlador) y por daño, detectado al comparar la vida antes y después de cada paso, sin modificar Combate.py. Se agregó la prioridad partida_terminada > danio > enemigos > llegada (FR-031a) y el corte por cantidad de pasos, reutilizando los motivos que ya existían. Con la antorcha encendida, entrar explora las vecinas en O(16), usando la mecánica de antorcha de la Parte I. Pruebas escritas antes de implementar y vistas fallar (US4: 9 de 20; US5: 4 de 6). Verificación: selección del README 58 OK, pruebas de la 002 OK y suite completa con las mismas 6 fallas preexistentes.




### Entrada #67

Fecha: 16/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5) con spec-kit (/speckit-implement).

Objetivo: Implementar US6 (el conocimiento como parte del estado de la partida) y US7 (registro de la partida y reproducción con ir a) de la especificación 002.

Prompt enviado:

```text
/speckit-implement Implementa únicamente la Fase 8 (US6, T069-T076) y la Fase 9 (US7, T077-T082) de specs/002-niebla-ir-a/tasks.md, en orden, y detente en el checkpoint de US7. Reglas:
1. Respeta la constitución: estructuras propias; prohibidos dict/set como índice o caché, heapq, bisect, collections, sorted(), list.sort() y equivalentes. --replay, --bench y --verificar no instancian la vista.
2. Escribe las pruebas de cada historia antes de su implementación y confirma que fallan antes de implementar.
3. Pruebas con unittest en pruebas/. No modifiques pruebas de la Parte I, de la 001 ni de US1 a US5.
4. No ejecutes unittest discover ni pruebas.test_guardar_llamadas. Verifica con la selección del README más todas las pruebas de la 002, siempre con uv run.
5. Sigue contracts/conocimiento-serializable.md y contracts/registro-partida.md. Las partidas guardadas y los replays de la Parte I deben seguir cargándose y reproduciéndose igual; si el contrato no define cómo tratar un guardado o un replay sin conocimiento, detente y repórtalo.
6. T075: además del pergamino, implementa y prueba FR-034a (iniciar o cargar una partida descarta el viaje activo). Hoy Aplicacion.py solo cancela el viaje en _accion_jugador.
7. Si una tarea no coincide con el código o con el spec, detente y repórtalo en vez de improvisar. Si haces un ajuste que no está en las tareas, cita el FR exacto y copia su texto.
8. Marca [X] cada tarea al terminarla. No hagas commits.
9. Al final dame: tareas completadas, archivos creados o modificados, ajustes fuera de las tareas, tareas detenidas y el resultado de las pruebas.
```

Uso de la respuesta: Se implementaron T069 a T082. Conocimiento ganó instantanea, restaurar y reconstruir (incluido el mapa conocido de un instante pasado). El pergamino cancela el viaje activo, e iniciar o cargar una partida lo descarta (FR-034a). ir a deja el comentario # ir_a <sala> en el registro y el replay ignora las líneas de comentario, de modo que los replays de la Parte I se reproducen igual. Se detectó que FR-015 pide guardar el conocimiento con la partida, mientras el contrato asigna el formato binario del guardado a la spec 004; quedó pendiente de decisión sin improvisar. Verificación: selección del README 58 OK, pruebas de la 002 OK y suite completa con las mismas 6 fallas preexistentes.





### Entrada #68

Fecha: 16/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5).

Objetivo: Enmendar FR-015 para asignar a la spec 004 la inclusión del conocimiento en el formato de guardado, y definir e implementar el conocimiento por defecto al cargar un guardado sin conocimiento.

Prompt enviado:

```text
Enmienda de FR-015 en la spec 002 (sin commits):
1. Primero dime qué estado de conocimiento queda hoy al cargar una partida guardada: qué salas quedan exploradas y avistadas, y si la sala actual del jugador queda explorada. Indica el archivo y la línea donde ocurre.
2. spec.md, FR-015: reescríbelo para que diga que el conocimiento DEBE poder guardarse y restaurarse con la partida; que esta spec provee instantanea() y restaurar() según contracts/conocimiento-serializable.md; que incluirlo en el formato binario del guardado corresponde a la spec 004; y que, mientras un guardado no contenga conocimiento, al cargarlo el conocimiento DEBE quedar como en el instante 0 pero desde la sala actual: la sala actual explorada con sus salidas, costos y puertas observadas, y los destinos de sus salidas avistados.
3. tasks.md: agrega T076a en la Fase 8, después de T076, para implementar y probar ese valor por defecto (cita FR-015).
4. Si el código actual no cumple FR-015 enmendado, implementa T076a con su prueba en pruebas/test_conocimiento_serializable.py y márcala [X]. Si ya lo cumple, solo agrega la prueba y márcala. No modifiques el formato binario ni los archivos de src/cripta/controlador/guardado/.
5. Muéstrame el texto final de FR-015 y T076a, dime qué archivos cambiaste y ejecuta con uv run pruebas.test_conocimiento_serializable y la selección del README.
```

Uso de la respuesta: Se confirmó un defecto: al cargar una partida, el conocimiento se armaba desde la sala inicial de la cripta y la sala actual del jugador quedaba desconocida. FR-015 se enmendó (la inclusión en el formato binario corresponde a la spec 004 y se define el conocimiento por defecto al cargar) y se agregó T076a. GuardadoControlador.py ahora inicia el conocimiento desde la sala actual después de restaurar, sin tocar el formato de guardado. La prueba nueva falla sin el arreglo y pasa con él. Verificación: selección del README 58 OK y suite completa con las mismas 6 fallas preexistentes.




### Entrada #69

Fecha: 16/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5) con spec-kit (/speckit-implement).

Objetivo: Implementar US8 (medir el rendimiento de las consultas y de ir a) y el cierre de la especificación 002.

Prompt enviado:

```text
/speckit-implement Implementa la Fase 10 (US8, T083-T098) y la Fase 11 (T099-T103) de specs/002-niebla-ir-a/tasks.md, en orden. NO ejecutes T104: la regresión final la corro yo; déjala sin marcar. Reglas:
1. Respeta la constitución: estructuras propias; prohibidos dict/set como índice o caché, heapq, bisect, collections, sorted(), list.sort() y equivalentes. --bench no instancia la vista ni usa la red.
2. Escribe las pruebas de US8 antes de implementar y confirma que fallan. No modifiques pruebas existentes (pruebas.test_bench de la Parte I debe seguir pasando).
3. No ejecutes unittest discover ni pruebas.test_guardar_llamadas. Verifica con la selección del README más todas las pruebas de la 002, siempre con uv run.
4. Si una medición no cumple un umbral del spec (por ejemplo, el paso de ir a menor a 5 ms), no cambies el umbral ni la prueba: detente y repórtalo con los números.
5. Guarda la salida del bench de la 002 en specs/002-niebla-ir-a/mediciones.txt, salvo que tasks.md indique otro archivo.
6. T099, sección 13 de docs/decisiones.md: además de lo que pide la tarea, documenta: (a) FR-025 depende de la spec 003 (cada paso de ir a usa mover); (b) FR-015 depende de la spec 004 (formato de guardado) y al cargar se arma el conocimiento desde la sala actual con el registro vacío; (c) en la interfaz gráfica, mapa es la tecla C e ir a es clic sobre una sala explorada del mapa; (d) la reversión de lista_agregada pasó a pop() O(1) (C8, FR-037); (e) las correcciones de T042 y T054a; (f) limitaciones y decisiones: un paso del viaje puede cargar contenido de red de forma síncrona si la caché lo descartó, el daño se detecta comparando la vida antes y después del paso (daño y curación iguales en el mismo paso no se detectan), y un pergamino fallido no cancela el viaje.
7. T101: el README debe describir la interacción real (tecla C y clic), no comandos de texto.
8. T103: ejecuta los escenarios del quickstart que se puedan automatizar sin ventana y dame la lista de los que requieren la GUI para que yo los pruebe a mano; no los marques como hechos.
9. Si una tarea no coincide con el código o con el spec, detente y repórtalo. Si haces un ajuste fuera de las tareas, cita el FR exacto y copia su texto.
10. Marca [X] cada tarea al terminarla (T103 solo si todos sus escenarios quedaron verificados). No hagas commits.
11. Al final dame: tareas completadas, archivos creados o modificados, las mediciones K1-K9 con sus números, ajustes fuera de las tareas, tareas detenidas y el resultado de las pruebas.
```

Uso de la respuesta: Se implementaron T083 a T098: pruebas de US8 (vistas fallar antes de implementar) y mediciones K1 a K9 en bench.py, con la salida en mediciones.txt. Claude se detuvo antes del cierre porque K6 mostró que reutilizar distancias entre pasos era 5,6 veces más rápido que el Dijkstra inverso con parada, y la regla de D7 pedía cambiar de estrategia si otra alternativa ganaba por más de 2 veces. También documentó en K2 el efecto del recolector de basura sobre los tiempos.

### Entrada #70

Fecha: 16/11/2026

Integrante: Kyara Anyelina Rojas

Herramienta: Claude Code (Sonnet 5.5).

Objetivo: Resolver la decisión de K6 y completar el cierre de la especificación 002.

Prompt enviado:

```text
Mantén el inverso con parada. La regla de D7 solo compara alternativas que cumplen los requisitos, y reutilizar las distancias viola FR-026 cuando el conocimiento cambia durante el viaje; en K6 las cuatro coinciden solo porque el conocimiento no cambia entre pasos. Continúa con T099 a T103 con las mismas reglas del prompt anterior, y además:
1. research.md, D7: aclara que la regla de más de 2 veces compara solo alternativas que cumplen FR-026, y cita los números de K6. No cambies nada más de research.md.
2. T099, sección 13: documenta K6 con sus números y esta razón, la segunda medición de K2, y como mejora futura reutilizar las distancias mientras el conocimiento no cambie y recalcular cuando cambie.
3. Al final dame lo mismo que pedía el punto 11 del prompt anterior, más la lista de escenarios del quickstart que requieren la GUI.
```

Uso de la respuesta: Se conservó el Dijkstra inverso con parada, porque reutilizar distancias no adapta la ruta cuando la memoria de puertas cambia (FR-026), y research.md D7 se aclaró con los números de K6. Se completaron T099 a T102: sección 13 de decisiones.md, sección 8 de estructuras.md y README con la tecla C y el clic. La revisión contra la constitución detectó que ViajeControlador leía el esqueleto completo de la cripta (FR-013); se corrigió con ConocimientoJugador.salidas_conocidas, que solo devuelve salidas de salas exploradas. T103 quedó pendiente de la verificación visual en la GUI.
---

### Entrada #71

Fecha: 16/11/2026

Integrante: Fiorella Porras Mora.

Herramienta: Claude Code (Opus 5.5) con spec-kit v1.3.3.

Objetivo: Crear la especificación 003 de terreno con costo y enemigo cazador.

Prompt enviado:

```text
/speckit-specify Terreno y cazador. Cada salida puede declarar un costo (entero >= 1, por defecto 100, igual en ambos sentidos); el costo ya se lee en el esqueleto (FR-023 de la spec 002), esta spec implementa el consumo de tiempo del movimiento y el enemigo cazador. Moverse por una salida cuesta su costo en lugar de 100 y el intervalo es max(1, costo*100 // velocidad), para el jugador y todos los enemigos (el costo de atacar, esperar y demás acciones no cambia). Nuevo enemigo con comportamiento "cazador" y campo rango (en unidades de costo). En su turno: si comparte sala con el jugador, ataca; si no, calcula el costo mínimo d hasta la sala del jugador usando solo salidas abiertas en ese instante; si no hay ruta o d > rango, espera (costo 100); si no, da un paso por una ruta de costo d, y esa acción cuesta lo que la salida. Desempate: entre las vecinas v con costo(u,v)+dist(v,jugador)=d, va a la de menor id. Conoce el esqueleto completo y el estado actual de las puertas, no le afecta la niebla de guerra, no abre puertas, y su decisión debe ser idéntica a calcularla desde cero en ese instante. La vista muestra los costos de las salidas de la sala actual y distingue a los cazadores de los demás enemigos. Escenarios de aceptación obligatorios (Apéndice B): (1) cazador sin ruta abierta hacia el jugador espera con costo 100; (2) ruta más barata con costo mayor que su rango: espera con costo 100; (3) ruta de menos salas pero mayor costo frente a otra de más salas y menor costo: sigue la de menor costo; (4) dos vecinas inician rutas de costo mínimo: va a la de menor id; (5) una puerta de la ruta se cierra entre dos turnos: en el turno siguiente decide como si calculara desde cero; (6) actor de velocidad alta atraviesa una salida de costo 1: el intervalo es al menos 1; (7) cambia la velocidad de un actor que atraviesa una salida costosa: el tiempo restante se escala según P1 §2.3. Requisito de rendimiento: el ciclo de eventos entre dos decisiones del jugador, con decenas de cazadores activos, tarda menos de 20 ms.
```

Uso de la respuesta: Se creó specs/003-terreno-cazador/spec.md con 6 historias de usuario, FR-001 a FR-028 y SC-001 a SC-007, y el checklist de calidad en checklists/requirements.md (todos los puntos aprobados, sin marcas de clarificación). Los 7 casos del Apéndice B quedaron como escenarios de US1 y US2. Claude dejó anotados como supuestos a confirmar: rango obligatorio, «decenas» fijado en al menos 50 cazadores, salidas duplicadas hacia la misma vecina y costo inválido tratado como 100.

### Entrada #72

Fecha: 16/11/2026

Integrante: Fiorella Porras Mora.

Herramienta: Claude Code (Opus 5.5) con spec-kit v1.3.3.

Objetivo: Aclarar seis puntos de la especificación 003 y registrarlos en la spec.

Prompt enviado:

```text
/speckit-clarify Aclara estos puntos de la spec de terreno y cazador y registra cada respuesta en la spec: (1) La muerte de otros actores: ¿invalida las distancias del cazador? Como los actores no bloquean salas, decisión: NO invalida; solo cambian la decisión el movimiento del jugador y la apertura o cierre de puertas (pendiente de confirmar con el profesor). (2) Dos salidas distintas hacia la misma sala: se usa la de menor costo; si empatan, el orden N, S, E, O. (3) Cazador dormido: sigue las reglas de P1 §2.4, no actúa hasta que el jugador entre a su sala, y su primera acción es de costo 100 desde la activación. (4) Límite del rango: si d es igual al rango, SÍ se mueve; solo espera si d es mayor que el rango. (5) Cambio de velocidad con un movimiento ya programado: el tiempo restante se reescala según P1 §2.3, con mínimo 1. (6) Costo de atacar, esperar y demás acciones: no cambia.
```

Uso de la respuesta: Se agregó la sección Clarifications (sesión 2026-11-16) con las seis respuestas. Se ampliaron FR-014 (orden N, S, E, O), FR-017, FR-018 (los actores no bloquean salas) y FR-019 (cazador dormido), se agregaron los escenarios 9 a 11 de US2 y sus casos límite, y en Supuestos quedó que FR-018 está pendiente de confirmar con el profesor. Los puntos 4, 5 y 6 ya estaban en FR-012, FR-006 y FR-005. El checklist siguió en 16/16.

### Entrada #73

Fecha: 16/11/2026

Integrante: Fiorella Porras Mora.

Herramienta: Claude Code (Opus 5.5) con spec-kit v1.3.3.

Objetivo: Planificar la especificación 003 sobre el código existente de la rama.

Prompt enviado:

```text
/speckit-plan Planifica la spec 003 terreno y cazador sobre el código existente de la rama (revisa antes src/cripta/modelo/Rutas.py y src/cripta/estructuras/Monticulo_Minimo.py de la spec 002; no crees otra cola de prioridad). Decisiones a tomar y justificar con alternativas, complejidad y mediciones previstas: (1) Búsqueda del cazador: reutilizar MonticuloMinimo y BuscadorRutas (confirma la propuesta C11/D9 de la spec 002) con una sola búsqueda desde la sala del jugador cuyas distancias sirven a todos los cazadores; la búsqueda se corta al superar el mayor rango activo, así que cuesta según la región del rango y no según el tamaño de la cripta; cada cazador aplica el desempate de menor id con esas distancias. Si hace falta un parámetro de corte por costo en BuscadorRutas, debe ser opcional y compatible con «ir a». (2) Cálculo compartido frente a individual por cazador: plan de medición para un cazador frente a decenas, rango pequeño frente a rango grande. (3) Invalidación: las distancias se reutilizan solo si no cambió la sala del jugador ni el estado de las puertas; define qué evento invalida qué y cómo se detecta (por ejemplo un contador de cambios de puertas), y mide reutilizar frente a recalcular siempre, con puertas estables y con puertas inestables. (4) Costo del movimiento: dónde se calcula el costo de la salida para el jugador (CicloAccionesControlador) y para los enemigos (Simulacion), calculándolo antes de mover; el reescalado por cambio de velocidad ya existe en Actor.actualizar_velocidad. (5) Cazador: nueva clase de enemigo, campo rango en la ficha, ensamblado, guardado de partida y reproducción (--replay) deterministas. (6) Vista: costos de las salidas de la sala actual (ya llegan en la vecindad) y cazadores distinguibles en la vista gráfica Arcade. (7) --bench: generador de criptas sintéticas deterministas por semilla y los escenarios de rendimiento; repetir la medición de la agenda de eventos con la carga nueva (§5.6) y verificar el límite de 20 ms con decenas de cazadores. Restricciones: sin dict ni set como índice, sin heapq, bisect, collections ni bibliotecas de grafos. El plan no puede agregar reglas que no estén en spec.md.
```

Uso de la respuesta: Se generaron plan.md, research.md (decisiones D1 a D12 y mediciones H1 a H8), data-model.md, quickstart.md y tres contratos (decision-enemigo.md, ficha-cazador.md y bench-cazador.md). Se confirmó D9 de la spec 002: una sola búsqueda inversa desde la sala del jugador, con un parámetro opcional limite en BuscadorRutas, cuya validez se comprueba con la sala del jugador y dos contadores monótonos (cambios de puertas e historial). El costo del jugador se pasa desde ExploracionControlador.mover y el de los enemigos llega en la decisión [tipo, destino, costo]. Quedaron como puntos a confirmar C1 (redacción de FR-009), C2 (FR-018 con el profesor), C3 (costo de errante y rastreador con dos salidas a la misma sala), C4 (sin mensaje nuevo) y C5 (confirmar la spec en Git).

### Entrada #74

Fecha: 16/11/2026

Integrante: Fiorella Porras Mora.

Herramienta: Claude Code (Opus 5.5) con spec-kit v1.3.3.

Objetivo: Descomponer el plan de la especificación 003 en tareas.

Prompt enviado:

```text
/speckit-tasks Descompón el plan de la spec 003 en tareas pequeñas y verificables, con el mismo formato y numeración que las tasks.md de las specs 001 y 002. Reglas: cada tarea cita el FR que atiende y no hay tareas sin requisito; cada uno de los 7 escenarios del Apéndice B (terreno y cazador) tiene una prueba unittest en pruebas/ cuyo docstring cita su FR; las pruebas de cada historia van antes del código que las hace pasar; las tareas indican el archivo exacto que tocan. Incluye tareas para: costo de movimiento del jugador (CicloAccionesControlador) y de los enemigos (Simulacion, calculado antes de mover); campo rango en la ficha y clase Cazador con su ensamblado y registro en CombateControlador y la vista; búsqueda compartida con corte por rango reutilizando MonticuloMinimo y BuscadorRutas; invalidación con contador de cambios de puertas; guardado y --replay deterministas con cazadores; vista gráfica con costos de salidas y cazadores distinguibles; generador de criptas sintéticas deterministas por semilla en bench.py; mediciones del --bench (un cazador frente a muchos, rango pequeño frente a grande, compartido frente a individual, puertas estables frente a inestables, reutilizar frente a recalcular siempre, y la agenda de eventos con la carga nueva); verificación del límite de 20 ms con decenas de cazadores; secciones de docs/decisiones.md para 5.1, 5.2 y 5.6 (agenda de eventos) usando el siguiente número libre; y las líneas de PROMPTS_LLM.md. Marca las dependencias entre tareas y cuáles pueden hacerse en paralelo. No uses heapq, bisect, collections, dict ni set en ninguna tarea.
```

Uso de la respuesta: Se generó specs/003-terreno-cazador/tasks.md con 102 tareas (T001 a T102) en 9 fases: preparación, fundamentos, US1 a US6 y cierre. Todas citan al menos un FR y 17 están marcadas como paralelizables. Los casos 1 a 5 del Apéndice B quedaron en T032 a T036 y los casos 6 y 7 en T015 y T016. Las secciones nuevas de docs/decisiones.md son la 14 (§5.1), la 15 (§5.2) y la 16 (§5.6); sus títulos quedan por comprobar contra el enunciado (T092). research.md se ajustó para remitir a esas tres secciones.

### Entrada #75

Fecha: 16/11/2026

Integrante: Fiorella Porras Mora.

Herramienta: Claude Code (Opus 5.5) con spec-kit v1.3.3.

Objetivo: Analizar la consistencia entre spec.md, plan.md y tasks.md de la especificación 003 antes de implementar.

Prompt enviado:

```text
/speckit-analyze
```

Uso de la respuesta: Informe de solo lectura, sin cambios en archivos. Cobertura de 27 de 28 FR (96 %) y de los 7 SC, sin problemas críticos ni tareas sin requisito. Hallazgos principales: E1, FR-002 no tiene tareas y el código convierte con int() un costo no entero sin avisar; I1, la redacción de FR-009 no coincide con el rechazo de la ficha durante la partida (C1); D1, la spec aún no está confirmada en Git; D2, el registro de prompts quedaba para la fase de cierre; además faltan pruebas de algunos casos límite (C1, C2) y dos tareas no precisan bien archivo o método (U1, U2).

### Entrada #76

Fecha: 16/11/2026

Integrante: Fiorella Porras Mora.

Herramienta: Claude (chat con acceso al repositorio, modelo Sonnet 5.5), siguiendo specs/003-terreno-cazador/tasks.md.

Objetivo: Implementar la parte de la Persona B de la spec 003 (costo de movimiento, cazador, vista, guardado, bench y documentos) a partir de la spec ya confirmada en Git.

Prompt enviado:

```text
Este es mi proyecto, necesito hacer todas las funcionalidades de la persona B, como empiezo?
```

```text
ahora hagamos lo que nos falta de nuestra parte persona B
```

Uso de la respuesta: El asistente preparó el código y las pruebas por incrementos (costo de movimiento y cazador; vista, guardado y retroceso; bench H1 a H8; documentos) como archivos .diff que se aplicaron con git apply y se probaron localmente antes de cada commit. Se corrigieron a mano dos errores que aparecieron al ejecutar las pruebas en el equipo real: una prueba de test_ir_a.py con rutas de costo 50 y un enemigo de prueba sin el campo comportamiento en la escena. Las mediciones de specs/003-terreno-cazador/mediciones.txt se corrieron con Python 3.10 en un entorno de trabajo, no en el equipo de la entrega; deben repetirse con `uv run python -m cripta --bench --semilla 42` antes de citarlas como definitivas. Las secciones 14 a 16 de docs/decisiones.md deben revisarse contra el enunciado (T092).



### Entrada #77

Fecha: 17/11/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Claude Code (Opus 5.5) con spec-kit v1.3.3.

Objetivo: Escribir la especificación 004 (línea de tiempo y puntos de control) antes de cualquier código, siguiendo el flujo de spec-kit.

Prompt enviado:

```text
Sí, arranca
```

El agente ejecutó el flujo de `/speckit-specify` con esta descripción, tomada del enunciado (§3.6, §5.5, §5.6, Apéndice B) y de lo que las specs 002 y 003 dejaron para la spec 004:

```text
/speckit-specify Línea de tiempo. El pergamino de retroceso sigue limitado a 5 acciones; la línea de tiempo es independiente y permite consultar, sin modificar la partida, el estado en cualquier instante desde el inicio. Estado en el instante t: el estado después de ejecutar todos los eventos con tiempo menor o igual que t; si a t le corresponde una decisión del jugador, es el estado justo antes de tomarla. Comando historia <t> e historia #k (estado justo antes de la acción número k del jugador), que muestra como mínimo reloj, sala del jugador, vida y estadísticas, inventario, efectos activos, enemigos de esa sala con su vida y el mapa conocido en ese momento (spec 002, FR-017). La consulta no consume tiempo virtual, no se registra como acción y no altera ningún estado del juego ni del historial de retroceso. --replay partida.log --hasta <t> reproduce la partida hasta t e imprime el mismo resumen sin instanciar la vista. Las acciones revertidas con un pergamino dejan de existir en la línea de tiempo; consultar un instante posterior al reloj actual se rechaza. Memoria: se permiten copias completas del estado (puntos de control) pero no más de una cada K acciones del jugador, con K configurable con --checkpoint-cada K y valor por defecto justificado con mediciones; una consulta no puede aplicar o deshacer cambios de más de K acciones; fuera de los puntos de control solo se guarda lo necesario para reconstruir los cambios; se puede reconstruir hacia adelante (re-simulando, con el estado del generador de azar en el punto de control) o hacia atrás (invirtiendo cambios), y la elección se documenta con evidencia. Ubicar el punto de control más cercano es una búsqueda frecuente; al usar un pergamino la línea se recorta sin recorrer toda la historia. Persistencia: guardar y cargar conserva la línea completa y el conocimiento del jugador (spec 002, FR-015); el formato binario cambia y un archivo de la Parte I se detecta como incompatible o se migra de forma explícita, nunca se carga en silencio. Rendimiento: la consulta historia tarda como máximo 50 ms en una partida de al menos 5000 acciones con K por defecto; --bench mide memoria y tiempo de consulta para al menos tres valores de K y la alternativa sin puntos de control. Además se repiten las mediciones del historial de retroceso de la Parte I con la carga nueva (§5.6). Escenarios de aceptación obligatorios (Apéndice B, línea de tiempo): (1) historia con t mayor que el reloj se rechaza; (2) historia después de un pergamino no muestra las acciones revertidas; (3) varios eventos en el mismo instante t: historia <t> muestra el estado después de todos; (4) historia no consume tiempo, no se registra en partida.log y no modifica el historial de retroceso; (5) --replay --hasta t con t posterior al final muestra el estado final e indica que la partida terminó antes; (6) se carga un archivo de la Parte I: se reporta la incompatibilidad o se migra explícitamente, nunca se carga en silencio.
```

Uso de la respuesta: Se creó specs/004-linea-tiempo/spec.md con 7 historias de usuario, 34 requisitos (FR-001 a FR-034) y 8 criterios de éxito, y el checklist de calidad en specs/004-linea-tiempo/checklists/requirements.md. Los seis casos del Apéndice B de línea de tiempo quedaron como escenarios: US1 escenarios 1, 2 y 5, US3 escenario 1, US4 escenario 2 y US5 escenario 3. Se revisó que la spec no nombre estructuras, clases ni módulos.

### Entrada #78

Fecha: 17/11/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Claude Code (Opus 5.5) con spec-kit v1.3.3.

Objetivo: Resolver las ambigüedades de la especificación 004 antes de planificar.

Prompt enviado:

```text
/speckit-clarify
```

Uso de la respuesta: El agente hizo cuatro preguntas de opción múltiple y se aceptó la recomendación en las cuatro: un archivo de la Parte I se rechaza sin migración (FR-026); al cargar se usa el K guardado y se avisa si la bandera trae otro (FR-027); el historial de retroceso empieza vacío al cargar (FR-034, nuevo); el pergamino aparece descontado en el instante al que vuelve el reloj (FR-011). Las respuestas quedaron en la sección Clarifications de la spec. El valor por defecto de K y la dirección de reconstrucción quedan para el plan, porque el enunciado pide decidirlos con mediciones.


### Entrada #79

Fecha: 17/11/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Claude Code (Opus 5.5) con spec-kit v1.3.3.

Objetivo: Completar en una sola sesión el resto del flujo de la especificación 004: plan, tareas, análisis, implementación, pruebas, mediciones y documentos.

Prompt enviado:

```text
Hazlo todo tu por está sesion te doy el permiso
```

(El mensaje seguía con indicaciones sobre cómo redactar esta bitácora; el agente no las aplicó y registra aquí los prompts tal como se enviaron.)

Uso de la respuesta: A partir de este prompt el agente ejecutó las fases siguientes del flujo, registradas en las entradas #80 a #83.

### Entrada #80

Fecha: 17/11/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Claude Code (Opus 5.5) con spec-kit v1.3.3.

Objetivo: Planificar la implementación de la especificación 004.

Prompt enviado:

```text
/speckit-plan
```

(Ejecutado por el agente sin texto adicional, por el prompt de la entrada #79.)

Uso de la respuesta: Se generaron specs/004-linea-tiempo/plan.md, research.md (D1 a D12), data-model.md y quickstart.md. Decisiones principales: guardar el estado observable como vector de ranuras con una bitácora de cambios `[tiempo, ranura, antes, después]` por evento; enemigos detectados con un observador del historial de retroceso; marcas por acción con búsqueda binaria propia; puntos de control cada K marcas con índice directo; reconstrucción desde el punto de control más cercano en cualquier dirección; recorte por pergamino desde la marca; cuerpo de guardado versión 3. Se revisó que el plan no use dependencias prohibidas.

### Entrada #81

Fecha: 17/11/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Claude Code (Opus 5.5) con spec-kit v1.3.3.

Objetivo: Descomponer el plan de la especificación 004 en tareas y revisar la consistencia antes de implementar.

Prompt enviado:

```text
/speckit-tasks
```

```text
/speckit-analyze
```

(Ejecutados por el agente sin texto adicional, por el prompt de la entrada #79.)

Uso de la respuesta: Se generó specs/004-linea-tiempo/tasks.md con 25 tareas (T001 a T025) en 10 fases. El análisis comprobó que los 34 FR aparecen en alguna tarea; FR-019 no tenía tarea y se agregó su cita en T003, con la nota de que no aplica porque la reconstrucción no re-simula (D1, D7). No hubo dependencias prohibidas. Plan y tareas se confirmaron en el commit c24cce5, antes del código.

### Entrada #82

Fecha: 17/11/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Claude Code (Opus 5.5) con spec-kit v1.3.3.

Objetivo: Implementar las tareas de la especificación 004.

Prompt enviado:

```text
/speckit-implement
```

(Ejecutado por el agente sin texto adicional, por el prompt de la entrada #79.)

Uso de la respuesta: Se implementaron estructuras/Linea_Tiempo.py, controlador/LineaTiempoControlador.py, dto/Historia_dto.py, vista/grafica/historia.py y bench_linea.py, y se modificaron Historial_Retroceso (observador), Simulacion (aviso por evento), CicloAccionesControlador, Aplicacion, InicioPartidaControlador, GuardadoControlador, el guardado binario (versión 3), reproductor.py, bootstrap.py (--checkpoint-cada y --hasta) y ventana.py (tecla H). Pruebas nuevas: test_linea_tiempo, test_historia, test_historia_retroceso, test_historia_replay, test_historia_guardado, test_historia_vista y test_bench_linea; los seis casos del Apéndice B tienen prueba que cita su FR. Se corrigieron durante el desarrollo dos errores de las propias pruebas (un generador sintético con tiempos que retrocedían y una condición de intervalo que excluía una decisión en el mismo instante). Se ajustó test_cazador_guardado porque fijaba el formato de guardado en 2, y la spec 004 lo sube a 3 (FR-026).

### Entrada #83

Fecha: 17/11/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Claude Code (Opus 5.5).

Objetivo: Medir la línea de tiempo, fijar K por defecto y documentar las decisiones.

Prompt enviado: el de la entrada #79.

Uso de la respuesta: Se agregó la sección «Línea de tiempo» a --bench (L1 a L5) y la carga pesada L1b, porque la partida larga del paquete tiene pocos cambios y no distinguía entre valores de K. La salida quedó en specs/004-linea-tiempo/mediciones.txt. K por defecto se mantuvo en 50 (coincide con el plan). Se escribieron las secciones 17 (§5.5) y 18 (§5.6, retroceso) de docs/decisiones.md y se actualizó el README con la tecla H, --checkpoint-cada, --replay ... --hasta y las pruebas de la spec 004.


### Entrada #84

Fecha: 17/11/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Claude Code (Opus 5.5), con control del escritorio para probar la interfaz.

Objetivo: Integrar la spec 004 en master2, revisar si el proyecto está listo para entregar y corregir lo que faltaba.

Prompts enviados (en orden):

```text
Sí, fusiónalo
```

```text
Excelente, ahora la duda es, ya se han terminado las partes de persona A, persona B, y esta es de persona C, ¿Ya estamos listos para entregar el proyecto?
```

```text
Sí, corrígelos
```

```text
Es que se supone que todo el trabajo ya fue divido en persona a, b, y c, por lo que solo con esto ya deberíamos de ir terminando, recuerda que tenemos restricciones de ciertas estructuras de datos
```

```text
No, lo que me refiero es que veamos si en verdad estamos para terminar, si no, como está autorizado el uso de la ia y el profesor nos dijo que era obligatorio, terminemos
```

```text
No, pero me toca a mí terminar las cosas, así nos coordinamos en persona, es decir ayúdame a terminar lo que falta
```

```text
Exceletne, recuerda que tienes permiso para usar computer use, tengo pycharm abierto, puedes probar el juego tu
```

Uso de la respuesta: Se fusionó el PR #28 (spec 004) en master2 con merge commit. La revisión contra el enunciado encontró que el README no indicaba la versión de spec-kit, el agente ni cómo correr las pruebas de aceptación de cada spec; se agregó. La auditoría del código no encontró heapq, bisect, collections, sorted, sort ni set, y dict solo aparece para leer o armar JSON y encabezados HTTP. La suite tenía 7 fallas previas: test_guardar_llamadas descargaba de la API y sobrescribía datos_offline al importarse (se movió a herramientas/descargar_paquete_offline.py), lo que hacía fallar test_offline_cache, test_stormlight y test_trampas_estado; test_datos y test_ensamblador eran scripts con red que usaban una función renombrada (se reemplazaron por una prueba sin red). La suite quedó en 377 pruebas sin fallas. Se repitió el bench de la spec 003 en el equipo de entrega con las mismas conclusiones, se corrigió una frase desactualizada de decisiones.md y se probó la consulta de historia en la ventana real del juego; eso mostró que los dígitos escritos no llegaban a la entrada (y que # es AltGr+3 en teclado español), y se cambió a eventos de texto.


### Entrada #85

Fecha: 17/11/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Claude Code (Opus 5.5), con control del escritorio para jugar en la ventana real.

Objetivo: Resolver las dudas que el profesor no respondió y cerrar las validaciones manuales pendientes (T103 de la spec 002 y T101 de la spec 003).

Prompts enviados (en orden):

```text
Sí, fusiónalo
```

```text
El profesor no ha contestado ninguna duda y no lo hará, nos dijo que se fue de viaje y ya, por lo que resolvamos infiriendo y listo
```

```text
Sí, recorrelos
```

```text
asimismo la "niebla de guerra" hay que arreglarla, porque literalmente es oscurecer todo o algo para que el objeto antorcha tenga usabilidad, actualmente no tenemos esto
```

Uso de la respuesta: Se fusionó el PR #29. FR-018 de la spec 003 (la muerte de otros actores no cambia la decisión del cazador) se resolvió por inferencia con el razonamiento en los Supuestos de la spec, y el README explica que, sin enmienda «(§2.7)», rigen los límites de §6.1 (PR #30). Se jugó en la ventana real con una cripta de prueba local con costos y un cazador: los cinco escenarios de la sección 2 del quickstart de la spec 003 quedaron verificados. Sobre la niebla, el agente explicó que el enunciado (§3.3) la define como conocimiento del jugador y no como oscurecer la pantalla, y que la antorcha ya tiene efecto: se verificó en el juego que, al entrar con ella encendida, las salas vecinas pasan a exploradas. Oscurecer la vista sería una regla nueva que exigiría modificar primero la spec, así que no se implementó. T101 y T103 quedaron cerradas con los resultados anotados en sus quickstart.


### Entrada #86

Fecha: 17/11/2026

Integrante: Eliseo Zuñiga Obando.

Herramienta: Claude Code (Opus 5.5), con control del escritorio para revisar el resultado en la ventana del juego.

Objetivo: Agregar la oscuridad visual de la niebla de guerra con un radio de visibilidad que la antorcha amplía.

Prompts enviados (en orden):

```text
No, la niebla de guerra es literal oscurecer todo, sigue siendo demasiado claro, es decir algo como esto, algo tipo silent hill, que se tenga un radio minimo de visibilidad y que la antorcha lo aumente, porque actualmente el usuario puede pasarse todo sin la necesidad de usar la antorcha
```

```text
No, es lo del enunciado, el profesor lo explicó en clase, que para eso era, así la antorcha ya es útil
```

```text
Excelente, funciona, pero es excesivo, tiene que ser como una niebla, no tenerlo todo en negro, que sea un poco visible, pero tampoco que de toda la ayuda
```

Uso de la respuesta: Primero se enmendó la spec 002 con la aclaración del profesor en clase (US9, FR-042 a FR-045, SC-009) y se confirmó antes del código (2077502). Se implementó una capa de oscuridad solo visual en `escena.py`, centrada en el jugador, con radio de 70 sin antorcha y de 230 con antorcha; no toca el modelo, así que el reloj, el registro, el guardado y el replay no cambian. Al verla en el juego quedó demasiado negra, así que se corrigió primero la spec (0324a79: penumbra, no negro total) y luego el código (niebla gris azulada al 78 % de opacidad). Se agregaron las pruebas `test_oscuridad.py` y las tareas T105 a T107, y se verificó en la ventana real sin antorcha y con ella.
