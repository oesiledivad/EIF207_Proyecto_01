# Captura del servicio para la entrega

Descargada el 17/11/2026 con herramientas/descargar_paquete_offline.py. Contiene todas las criptas publicadas (02 a 06), sus versiones, todas las páginas del esqueleto, todo el contenido, fichas referenciadas, botín y ubicaciones de llaves. Las versiones se comprobaron durante la captura. Total: 83 solicitudes; cada sesión respetó el presupuesto publicado.

La referencia mayor es cripta-06: 300 salas, versión f9ed9afa683d. cripta-05 es no resoluble y sirve para demostrar el reporte de frontera y ciclos.

Uso sin red: `uv run cripta --offline --offline-dir datos_entrega`. Verificación: añadir `--verificar cripta-06` (salida 0) o `--verificar cripta-05` (salida 1). Use una carpeta de caché vacía para aislar esta captura de versiones descargadas anteriormente.

El paquete histórico datos_offline sigue separado porque sus versiones son necesarias para el replay incluido y para Stormlight. Las versiones de esta captura no se sustituyen manualmente en registros antiguos.
