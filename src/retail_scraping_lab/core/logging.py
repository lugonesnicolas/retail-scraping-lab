import logging

from rich.logging import RichHandler


def configure_logging(level: str = "INFO") -> None:
    """Configura logging del proyecto usando rich para salida legible por consola."""
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, show_path=False)],
    )
