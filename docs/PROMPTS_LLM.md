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
---