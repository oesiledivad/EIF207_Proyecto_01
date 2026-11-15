# Contrato: línea de comentario en `partida.log`

**Spec**: [../spec.md](../spec.md) (FR-033) | **Decisión**: D11 en [../research.md](../research.md)

## Formato

El registro sigue siendo un archivo de texto con un objeto JSON por línea:

1. Línea 1: la cabecera (sin cambios; `formato` sigue en 1).
2. Líneas siguientes: o una acción `["nombre", argumento]`, o una línea de comentario.

Una **línea de comentario** es toda línea cuyo texto, sin espacios iniciales, empieza por `#`. El
resto de la línea es texto libre de una sola línea.

## Línea que escribe la aplicación

```text
# ir_a <sala>
```

- `<sala>` es el id entero de la sala destino.
- Se escribe una sola vez por orden aceptada, antes del primer paso del viaje.
- NO se escribe para una orden rechazada (no tuvo efecto).
- Cada paso del viaje se escribe después como una acción normal.

Ejemplo de un viaje de tres pasos hacia la sala 12:

```text
{"cripta_id": "…", "version_cripta": "…", "version_catalogo": "…", "semilla": 7, "nombre_jugador": "Ana", "capacidad_cache": 25, "formato": 1}
["mover", "N"]
# ir_a 12
["mover", "E"]
["mover", "E"]
["mover", "N"]
```

## Reglas del escritor (`RegistroPartida.comentar`)

- Antepone `# ` al texto.
- Reemplaza cualquier salto de línea del texto por un espacio, para que la línea siga siendo una.
- Falla igual que `anexar`: un error de disco se convierte en `ErrorRegistro` y detiene la sesión.
- Sin encabezado escrito todavía, lanza el mismo error que `anexar`.

## Reglas del lector (`leer_partida`)

- Omite las líneas de comentario: no son acciones y no se validan.
- El número de línea que aparece en los mensajes de error cuenta también los comentarios, de modo
  que el número apunta a la línea real del archivo.
- Una línea vacía o que no empieza por `#` y no es `[accion, argumento]` sigue siendo inválida.
- La reproducción llega al mismo estado final con o sin los comentarios, porque cada paso del viaje
  es un `mover` por sí mismo (SC-005).

## Uso manual

Como el lector omite los comentarios, el equipo puede agregar a mano una línea como
`# FR-028 escenario: sala con enemigos dormidos` en un `partida.log` de evidencia. Así un registro
cita el FR del escenario de aceptación que demuestra (principio VII).

## Compatibilidad

`formato` no cambia: los registros existentes siguen leyéndose igual. Un lector anterior a este
cambio rechazaría un archivo con comentarios («Replay invalido en linea N»); se acepta porque
el registro y su lector se publican juntos.
