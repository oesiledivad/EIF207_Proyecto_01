from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static


class Consola(App):

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("¡Hola! Textual está funcionando.")
        yield Footer()


if __name__ == "__main__":
    Consola().run()




'''from rich.console import Console

console = Console()

def mostrar_bienvenida() -> None:
    console.print("[bold cyan]CRIPTA[/bold cyan] — Proyecto de Estructuras de Datos II")
    console.print("[dim]Escriba 'ayuda' para ver los comandos disponibles.[/dim]")


def mostrar_estado_sala(sala) -> None:
    # TODO: depende de que modelo/sala.py exista.
    raise NotImplementedError("TODO: renderizar sala actual (salidas, enemigos, objetos)")


def mostrar_mensajes(mensajes) -> None:
    # TODO: depende del buffer circular de bitácora
    raise NotImplementedError("TODO: renderizar últimos 20 mensajes")
'''