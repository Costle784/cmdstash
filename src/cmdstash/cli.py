from cyclopts import App

app = App(
    name="cmdstash",
    help="CLI for stashing, organizing, and finding terminal commands.",
)


def main() -> None:
    """Entrypoint for the cmdstash console script."""
    app()
