"""Orquesta la verificación de resolubilidad de una cripta.

Reúne los datos con `CriptaService` (red, disco o paquete offline), llama al
modelo y da formato de texto al resultado. No contiene el algoritmo.

Cumple: FR-001, FR-007, FR-022.
"""

from __future__ import annotations

from cripta.adaptadores.Crypt_Data_Source import PresupuestoAgotado
from cripta.dto.Verificacion_dto import ResultadoVerificacion
from cripta.modelo.Resolubilidad import verificar
from cripta.servicio.CriptaService import CriptaService, UbicacionLlavesNoDisponible


class VerificacionControlador:
    """Verifica criptas usando un `CriptaService` ya construido.

    Args:
        servicio: Servicio con la fuente de datos y el almacén de la sesión.
    """

    def __init__(self, servicio: CriptaService) -> None:
        self._servicio = servicio
        self._presupuesto = 0

    def verificar_cripta(self, cripta_id: str) -> ResultadoVerificacion:
        """Obtiene los datos de la cripta y devuelve el resultado de verificarla.

        Si la ubicación de las llaves (o los datos básicos) no están
        disponibles, devuelve `no_verificable` sin invocar el modelo.
        """
        servicio = self._servicio
        try:
            detalles = servicio.obtener_detalles(cripta_id)
            self._presupuesto = detalles.presupuesto_solicitudes
            servicio.validar_cripta_en_disco(detalles)
            salas = servicio.cargar_esqueleto_salas(cripta_id, detalles.sala_salida)
        except (PresupuestoAgotado, RuntimeError, OSError, ValueError) as error:
            return ResultadoVerificacion(
                estado="no_verificable",
                motivo_no_verificable=f"No se pudieron obtener los datos de la cripta: {error}",
                cripta_id=cripta_id,
            )

        try:
            ubicaciones = servicio.obtener_ubicaciones_llaves(cripta_id)
        except UbicacionLlavesNoDisponible as error:
            return ResultadoVerificacion(
                estado="no_verificable",
                motivo_no_verificable=str(error),
                cripta_id=cripta_id,
                version=detalles.version,
            )
        return verificar(detalles, salas, ubicaciones)

    def formatear(self, resultado: ResultadoVerificacion) -> str:
        """Texto de la salida según contracts/verificar-cli.md (caso resoluble).

        La primera línea es siempre el veredicto. Los otros estados se
        completan en la historia siguiente (reporte de bloqueo).
        """
        if resultado.estado != "resoluble":
            etiqueta = "NO RESOLUBLE" if resultado.estado == "no_resoluble" else "resolubilidad no verificada"
            return f"Cripta {resultado.cripta_id}: {etiqueta}"

        lineas = [
            f"Cripta {resultado.cripta_id} (version {resultado.version}): RESOLUBLE",
            f"Orden de obtencion de llaves ({len(resultado.orden_llaves)} llaves):",
        ]
        for numero, entrada in enumerate(resultado.orden_llaves, start=1):
            linea = f"  {numero}. {entrada.llave} en sala {entrada.sala}"
            if entrada.enemigo is not None:
                linea += f" (suelta el enemigo {entrada.enemigo})"
            lineas.append(linea)
        lineas.append(f"Solicitudes de red: {self._servicio.requests_made}/{self._presupuesto}")
        return "\n".join(lineas)
