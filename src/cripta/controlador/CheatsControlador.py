"""Ayudas de pruebas; no participan en las reglas ni los registros normales."""
from cripta.dto.ResultadoAccion import ResultadoAccion
from cripta.estructuras.Bitacora import Mensaje
from cripta.modelo.Efectos import cancelar_veneno


class CheatsControlador:
    """Aplica ayudas sobre los actores actuales y marca la sesión como prueba."""

    def __init__(self, aplicacion):
        """Conserva el contexto porque los actores cambian al iniciar o cargar."""
        self._app = aplicacion

    def activo(self, nombre):
        """Consulta los interruptores sin activar la sesión de pruebas."""
        atributo = "invulnerable" if nombre == "god_mode" else nombre
        jugador = self._app._jugador
        return (atributo in ["invulnerable", "insta_kill"] and jugador is not None
                and getattr(jugador, atributo, False))

    def aplicar(self, nombre):
        """Aplica una ayuda sin avanzar el tiempo ni generar un puntaje válido.

        Args:
            nombre: curar, ataque, defensa, god_mode, insta_kill, antidoto o vida.

        Returns:
            ResultadoAccion: Confirma la ayuda o explica por qué fue rechazada.
        """
        app = self._app
        if not app._partida_en_curso() or nombre not in ["curar", "ataque", "defensa", "god_mode", "insta_kill", "antidoto", "vida"]:
            return ResultadoAccion.fallo("Cheat inválido o partida inactiva.")
        if not app.trucos_activos:
            app._partida.trucos_activos = True
            app._partida.suspender_registro()
        app._gestor.historial.limpiar()
        jugador = app._jugador
        if nombre == "curar":
            jugador.vida = jugador.vida_max
        elif nombre == "ataque":
            jugador.ataque += 50
        elif nombre == "defensa":
            jugador.defensa += 50
        elif nombre == "god_mode":
            jugador.invulnerable = not self.activo(nombre)
            if jugador.invulnerable:
                jugador.vida = jugador.vida_max
        elif nombre == "insta_kill":
            jugador.insta_kill = not self.activo(nombre)
        elif nombre == "antidoto":
            cancelar_veneno(jugador, app._simulacion.agenda)
        elif nombre == "vida":
            jugador.vida_max += 100
            jugador.vida = jugador.vida_max
        app._sincronizar_estado()
        app._bitacora.append(Mensaje("sistema", f"Cheat: {nombre}. Modo pruebas: sin puntajes, guardado ni replay."))
        return ResultadoAccion.exito()
