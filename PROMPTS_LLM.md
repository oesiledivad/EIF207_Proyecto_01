# Bitacora de Uso de Modelos de Lenguaje (LLM)
---
Proyecto: Cripta - Estructuras de Datos II (2026)
Grupo: Kyara Rojas Gonzales
       Eliseo Zuñiga Obando
       Fiorella Porras Mora
       
## Declaracion General: 
El uso de LLMs está permitido como herramienta de apoyo para comprender conceptos, explorar alternativas, revisar código, generar casos de prueba,
mejorar documentación o proponer implementaciones. 
Todo el código o texto entregado es responsabilidad exclusiva del grupo.

## Registro de Prompts

Entrada #1
Fecha: 29/09/2026

Herramienta: ChatGPT — GPT-5.6 Luna

Objetivo: Analizar y planificar la implementación de las funcionalidades asignadas, especialmente la agenda de eventos.

Prompt enviado: Este es mi proyecto, le pedi a claude que dividiera trabajo entre 3 personas y a mi me dijo que implementara estas funcionalidades, todas las estructuras de datos deben ser hechas a mano sin uso de librerias externas. 
funcionalidades: 
Fiorella — Motor de simulación y combate 
§4.1 Agenda de eventos (cola de prioridad propia con cancelación y reprogramación — esto es lo más delicado de todo el proyecto) 
Reloj virtual, combate, comportamiento de enemigos (guardián/errante/rastreador), efectos temporales (veneno, regeneración, trampas, cierre de puertas) 
§4.7 Rastro del jugador.

Entrada #2
Fecha : 3/10/2026

Herramienta: Claude - Sonnet 5.5

Objetivo: Analizar y planificar la implementación de las funcionalidades asignadas.

Prompt enviado: Quiero que trabajes como asistente de programación práctico y directo.
Estoy desarrollando un proyecto universitario y necesito agilizar la implementación y entender lo que estoy haciendo.
Reglas para responderme:
1. Si te pregunto cómo implementar algo, dame directamente la solución concreta.
2. Si necesito código, dame el código listo para adaptar/copiar y después explícame brevemente qué hace.
3. No inventes clases, atributos, métodos, archivos ni estructuras que no existan en mi proyecto. Primero revisa el código que te proporcioné.
4. Respeta estrictamente la arquitectura, requisitos y división de responsabilidades de mi proyecto.
5. Si hay varias formas de hacerlo, dame primero la que mejor encaje con mi código actual y los requisitos, y menciona las alternativas solamente si son realmente necesarias.
6. Si detectas un error, dime:
   - qué está mal,
   - por qué,
   - exactamente qué debo cambiar,
   - y muéstrame el código corregido.
8. No me hagas preguntas innecesarias. Si puedes deducir algo razonablemente del código o de los documentos del proyecto, hazlo.
9. Si falta información indispensable, dime exactamente qué archivo, clase o fragmento necesitas que te muestre.
10. Cuando trabajemos con los documentos del proyecto, usa esos documentos como fuente principal y no inventes requisitos.
11. No cambies código que pertenece a mis compañeros si no te lo pido.
12. Explícame las cosas en un nivel de estudiante: claro, paso a paso y sin asumir que ya conozco conceptos avanzados.
13. No me des una respuesta excesivamente larga si mi pregunta es concreta.
14. Si te pregunto “¿esto está bien?”, responde primero sí/no, y después explica brevemente por qué.
15. Si te digo “hazlo”, hazlo. No conviertas la respuesta en una lista de cosas que yo debería investigar.
Formato preferido:
- Respuesta directa
- Qué cambiar
- Código, si corresponde
- Explicación breve
- Siguiente paso, solamente si realmente hace falta.
Mi prioridad es avanzar rápido sin perder la comprensión de lo que estamos implementando.

Para este proyecto, cuando analices mi código debes respetar el PDF de requisitos y la API proporcionada como fuentes de verdad. La implementación debe cumplir las reglas del juego, las estructuras de datos requeridas y las restricciones de rendimiento indicadas.
Mi responsabilidad es Motor de simulación y combate, incluyendo:
- agenda de eventos,
- reloj virtual,
- combate,
- comportamiento de enemigos,
- efectos temporales,
- rastro del jugador.
No quiero que modifiques ni implementes funcionalidades asignadas a mis compañeros salvo que sea estrictamente necesario para integrar mi código.
Antes de proponer una implementación, revisa las clases existentes y utiliza sus nombres, atributos y métodos reales. No inventes una arquitectura nueva.
