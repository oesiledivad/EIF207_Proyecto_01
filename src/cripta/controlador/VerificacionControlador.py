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
            servicio.fijar_presupuesto(self._presupuesto)
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
        """Texto de la salida según contracts/verificar-cli.md.

        La primera línea es siempre el veredicto (o la falta de veredicto).
        Las listas salen en el orden que ya trae el resultado: llaves por id,
        puertas por (llave, inserción) y ciclos por su llave de menor id.
        """
        if resultado.estado == "no_verificable":
            return (
                f"Cripta {resultado.cripta_id}: resolubilidad no verificada\n"
                f"Motivo: {resultado.motivo_no_verificable}"
            )
        if resultado.estado == "no_resoluble":
            return self._formatear_bloqueo(resultado)

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

    def _formatear_bloqueo(self, resultado: ResultadoVerificacion) -> str:
        """Texto del caso no resoluble: motivo, llaves, puertas y ciclos."""
        reporte = resultado.reporte
        if reporte.motivo == "llave_salida_inobtenible":
            motivo = "llave de salida no obtenible"
        else:
            motivo = "ninguna puerta con la llave de salida llega a la sala de salida"
        lineas = [
            f"Cripta {resultado.cripta_id} (version {resultado.version}): NO RESOLUBLE",
            f"Motivo: {motivo}",
            f"Llaves que no pueden obtenerse ({len(reporte.llaves_inobtenibles)}):",
        ]
        for llave in reporte.llaves_inobtenibles:
            lineas.append(_linea_llave(llave))

        lineas.append(f"Puertas bloqueadas en la frontera ({len(reporte.frontera)}):")
        for puerta in reporte.frontera:
            lineas.append(
                f"  - sala {puerta.sala_origen} salida {puerta.direccion} "
                f"hacia sala {puerta.sala_destino} exige {puerta.llave}")

        lineas.append(f"Ciclos de dependencia ({len(reporte.ciclos)}):")
        for numero, ciclo in enumerate(reporte.ciclos, start=1):
            nombres = ""
            for paso in ciclo.pasos:
                nombres += f"{paso.llave} -> "
            nombres += ciclo.pasos[0].llave
            lineas.append(f"  Ciclo {numero}: {nombres}")
            for j, paso in enumerate(ciclo.pasos):
                siguiente = ciclo.pasos[(j + 1) % len(ciclo.pasos)].llave
                p = paso.puerta
                lineas.append(
                    f"    {paso.llave} esta en sala {paso.sala} detras de la puerta sala {p.sala_origen} "
                    f"salida {p.direccion} hacia sala {p.sala_destino} que exige {siguiente}")

        lineas.append(f"Solicitudes de red: {self._servicio.requests_made}/{self._presupuesto}")
        return "\n".join(lineas)


def _texto_ubicacion(ubicacion) -> str:
    """Sala de una ubicación y, si la suelta un enemigo, su id."""
    texto = f"sala {ubicacion.sala}"
    if ubicacion.enemigo is not None:
        texto += f" (enemigo {ubicacion.enemigo})"
    return texto


def _linea_llave(llave) -> str:
    """Línea de una llave inobtenible con sus ubicaciones y su causa."""
    if not llave.ubicaciones:
        if llave.causa == "sin_ubicacion":
            return f"  - {llave.llave}: sin ubicacion publicada"
        return f"  - {llave.llave}: sin ubicacion ; {llave.causa}"
    causas = {
        "en_ciclo": "en ciclo",
        "sala_desconectada": "sala desconectada",
        "ubicacion_invalida": "ubicacion invalida",
    }
    if llave.causa == "depende_de":
        causa = f"depende de {llave.depende_de}"
    else:
        causa = causas.get(llave.causa, llave.causa)
    if len(llave.ubicaciones) == 1:
        lugar = _texto_ubicacion(llave.ubicaciones[0])
        return f"  - {llave.llave}: {lugar} ; {causa}"
    lugares = ""
    for u in llave.ubicaciones:
        if lugares:
            lugares += ", "
        lugares += _texto_ubicacion(u)
    return f"  - {llave.llave}: ubicaciones: {lugares} ; {causa}"
