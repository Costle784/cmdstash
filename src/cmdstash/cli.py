from cyclopts import App
from rich.console import Console
from rich.panel import Panel

app = App(
    name="cmdstash",
    help="CLI for stashing, organizing, and finding terminal commands.",
)
console = Console()


def _print_stub(title: str, body: str, *, border_style: str = "cyan") -> None:
    """Render a consistent placeholder message for early development steps."""
    console.print(
        Panel.fit(
            body,
            title=f"[bold]{title}[/bold]",
            border_style=border_style,
        )
    )


@app.command
def add(command: str) -> None:
    """Stash a command (placeholder)."""
    _print_stub(
        "cmdstash add (stub)",
        "[bold]Command received:[/bold]\n"
        f"[bold bright_cyan]{command}[/bold bright_cyan]\n\n"
        "[dim]Next: enrich with AI metadata and save to SQLite.[/dim]",
    )


@app.command
def find(text: str) -> None:
    """Find stashed commands (placeholder)."""
    breakpoint()
    _print_stub(
        "cmdstash find (stub)",
        "[bold]Search query:[/bold]\n"
        f"[bold bright_cyan]{text}[/bold bright_cyan]\n\n"
        "[dim]Next: query command text, descriptions, and tags.[/dim]",
        border_style="blue",
    )


@app.command
def tags() -> None:
    """List available tags (placeholder)."""
    _print_stub(
        "cmdstash tags (stub)",
        "[bold]Tag taxonomy is not wired yet.[/bold]\n\n"
        "[dim]Next: print the real, stable taxonomy list.[/dim]",
        border_style="magenta",
    )


def main() -> None:
    """Entrypoint for the cmdstash console script."""
    app()
