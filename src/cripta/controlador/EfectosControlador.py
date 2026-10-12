"""Controlador de efectos (P2): pociones, antídotos, antorchas, veneno,
velocidad, regeneración y trampas (§2.7, §2.10).

No guarda estado del juego: recibe en cada llamada el jugador y la
simulación que le pasa Aplicacion. Todos los cambios pasan por
`agenda.cambiar`/`agenda.insertar`, así el retroceso los puede invertir.
"""

from __future__ import annotations

from cripta.adaptadores.Crypt_Data_Source import PresupuestoAgotado
from cripta.controlador.GestorPartida import GestorPartida
from cripta.dto.Partida_dto import TrampaPartida
from cripta.dto.ResultadoAccion import ResultadoAccion
from cripta.estructuras.Bitacora import Bitacora, Mensaje
from cripta.modelo.Combate import esta_vivo
from cripta.modelo.Efectos import (
    activar_regeneracion,
    aplicar_modificador_velocidad,
    cancelar_veneno,
    curar,
    disparar_trampa,
    encender_antorcha,
)
from cripta.modelo.Trampa import TrampaJuego
from cripta.servicio.CriptaService import CriptaService


class EfectosControlador:
    def __init__(self, gestor: GestorPartida, bitacora: Bitacora, servicio: CriptaService) -> None:
        self._gestor = gestor
        self._bitacora = bitacora
        self._servicio = servicio

    #  Objetos consumibles (lo que usa el inventario)

    def usar(self, instancia_id: str, jugador, simulacion, consumir) -> ResultadoAccion:
        """Acción "usar": busca el objeto, aplica su efecto y lo consume.

        Args:
            consumir: operación del inventario que retira el objeto y registra
                su delta (InventarioControlador.consumir). Se recibe como
                función para no depender del controlador de inventario.
        """
        inv = self._gestor.inventario
        item = inv.buscar_por_id(instancia_id) if inv is not None else None
        if item is None:
            return ResultadoAccion.fallo("No tienes ese objeto.")

        resultado = self.aplicar_consumible(item, jugador, simulacion)
        if not resultado.ok:
            return resultado
        consumir(item)
        self._bitacora.append(Mensaje("jugador", resultado.datos))
        return ResultadoAccion.exito()

    def aplicar_consumible(self, item, jugador, simulacion) -> ResultadoAccion:
        """Aplica el efecto de un consumible sin retirarlo del inventario.

        Returns:
            exito(datos=texto para la bitácora) o fallo(motivo). Si falla, no
            cambió nada (Apéndice B: una acción rechazada no consume tiempo).
        """
        try:
            ficha = self._servicio.obtener_ficha_garantizada(item.tipo_id)
        except (PresupuestoAgotado, RuntimeError) as e:
            return ResultadoAccion.fallo(f"No se pudo resolver {item.nombre}: {e}")
        if ficha is None:
            return ResultadoAccion.fallo(f"Ficha desconocida: {item.tipo_id}")

        tiempo = simulacion.reloj.tiempo_actual
        agenda = simulacion.agenda

        match ficha.clase:
            case "pocion":
                partes: list[str] = []
                if ficha.cura:
                    partes.append(f"recuperás {curar(jugador, ficha.cura, agenda)} de vida")
                if ficha.modificador_velocidad and ficha.duracion:
                    aplicar_modificador_velocidad(jugador, ficha.modificador_velocidad,
                                                  ficha.duracion, tiempo, agenda)
                    partes.append(f"tu velocidad pasa a {jugador.velocidad} por {ficha.duracion}")
                if not partes:
                    return ResultadoAccion.fallo("Esa poción no tiene efecto.")
                texto = f"Bebés {ficha.nombre}: {', '.join(partes)}."
            case "antidoto":
                if jugador.evento_veneno is None:
                    return ResultadoAccion.fallo("No estás envenenado.")
                cancelar_veneno(jugador, agenda)
                texto = f"Usás {ficha.nombre}: el veneno desaparece."
            case "antorcha":
                texto = encender_antorcha(jugador, ficha.duracion, tiempo, agenda)
            case "llave":
                return ResultadoAccion.fallo("Las llaves no se usan: sirven para abrir puertas.")
            case "arma" | "armadura":
                return ResultadoAccion.fallo("Ese objeto se equipa, no se usa.")
            case "pergamino_retroceso":
                return ResultadoAccion.fallo("Usá la acción de pergamino de retroceso.")
            case otra:
                return ResultadoAccion.fallo(f"No se puede usar un objeto de clase {otra}.")
        return ResultadoAccion.exito(datos=texto)

    #  Trampas (§2.10)

    @staticmethod
    def crear_trampa(dto: TrampaPartida) -> TrampaJuego:
        return TrampaJuego(
            instancia=dto.id, armada=dto.activa, dano=dto.dano,
            rearme=dto.rearme, efecto=dto.efecto, tipo=dto.tipo,
        )

    def disparar_trampas(self, sala, jugador, simulacion) -> None:
        """Cada trampa armada se activa al entrar, antes del siguiente evento."""
        tiempo = simulacion.reloj.tiempo_actual
        for trampa in sala.trampas:
            if trampa.armada:
                texto = disparar_trampa(trampa, jugador, tiempo, simulacion.agenda)
                self._bitacora.append(Mensaje("combate", texto))
                if not esta_vivo(jugador):
                    break

    #  Regeneración (§2.10)

    @staticmethod
    def iniciar_regeneracion(enemigo, simulacion) -> None:
        """Si la ficha declara regeneración, programa su primer pulso."""
        if enemigo.regeneracion_objetivo:
            activar_regeneracion(enemigo, enemigo.regeneracion_objetivo,
                                 simulacion.reloj.tiempo_actual, simulacion.agenda)

    #  Vista

    @staticmethod
    def describir(jugador) -> list[str]:
        """Efectos activos del jugador, para el panel de la vista."""
        efectos: list[str] = []
        if jugador.evento_veneno is not None:
            efectos.append(f"Envenenado (-{jugador.dano_veneno}/pulso hasta t={jugador.fin_veneno})")
        if jugador.evento_fin_velocidad is not None:
            efectos.append(f"Velocidad alterada ({jugador.velocidad})")
        if jugador.antorcha_encendida:
            efectos.append("Antorcha encendida")
        return efectos
