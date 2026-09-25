from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from retail_scraping_lab.config.settings import get_settings
from retail_scraping_lab.core.logging import configure_logging
from retail_scraping_lab.models.database import (
    get_engine,
    get_session_factory,
    init_db,
    reset_db,
)
from retail_scraping_lab.services.scraping_service import CaptureResult, run_demo_scraping

app = typer.Typer(help="CLI de retail-scraping-lab")
console = Console()

_DEFAULT_CATALOG_DIR = Path("tests/fixtures/demo_store")
_STATUS_STYLE = {
    "success": "[green]success[/green]",
    "partial": "[yellow]partial[/yellow]",
    "failed": "[red]failed[/red]",
}


@app.command("init-db")
def init_db_command(
    reset: bool = typer.Option(
        False, "--reset", help="Borrar y recrear todas las tablas (destruye los datos)"
    ),
) -> None:
    """Crea las tablas de la base de datos (SQLite) si todavia no existen."""
    settings = get_settings()
    configure_logging(settings.log_level)

    engine = get_engine(settings.database_url)
    if reset:
        reset_db(engine)
        console.print(f"[yellow]Base de datos recreada en:[/yellow] {settings.database_url}")
    else:
        init_db(engine)
        console.print(f"[green]Base de datos inicializada en:[/green] {settings.database_url}")


def _print_products(result: CaptureResult) -> None:
    captured_on = result.capture.captured_at.date().isoformat()
    table = Table(title=f"Productos de la captura {captured_on}")
    table.add_column("Nombre")
    table.add_column("Marca")
    table.add_column("Precio", justify="right")
    table.add_column("Moneda")
    table.add_column("Disponibilidad")
    for product in result.products:
        table.add_row(
            product.name,
            product.brand or "-",
            str(product.price),
            product.currency,
            product.availability,
        )
    console.print(table)


def _print_summary(results: list[CaptureResult]) -> None:
    table = Table(title="Resumen por captura")
    table.add_column("Captura")
    table.add_column("Estado")
    table.add_column("Items", justify="right")
    table.add_column("Validos", justify="right")
    table.add_column("Errores", justify="right")
    table.add_column("Snapshots nuevos", justify="right")
    table.add_column("Snapshots omitidos", justify="right")
    for result in results:
        saved = result.saved
        table.add_row(
            result.capture.captured_at.date().isoformat(),
            _STATUS_STYLE[result.status],
            str(result.items_found),
            str(len(result.products)),
            str(len(result.errors)),
            str(len(result.products) - saved.skipped) if saved else "-",
            str(saved.skipped) if saved else "-",
        )
    console.print(table)


def _print_errors(results: list[CaptureResult]) -> None:
    table = Table(title="Errores", style="yellow")
    table.add_column("Captura")
    table.add_column("Tipo")
    table.add_column("Mensaje")
    table.add_column("URL")
    for result in results:
        for error in result.errors:
            table.add_row(
                result.capture.captured_at.date().isoformat(),
                error.error_type,
                error.message,
                error.url or "-",
            )
    console.print(table)


@app.command("scrape-demo")
def scrape_demo(
    catalog_dir: Path = typer.Option(
        _DEFAULT_CATALOG_DIR, help="Directorio del catalogo demo (una carpeta por captura)"
    ),
    capture: datetime | None = typer.Option(
        None,
        formats=["%Y-%m-%d"],
        help="Procesar solo la captura de esta fecha (YYYY-MM-DD). Por defecto, todas.",
    ),
    persist: bool = typer.Option(
        False, "--persist", help="Guardar el historico en la base de datos"
    ),
) -> None:
    """Procesa las capturas del catalogo demo, exporta cada una y opcionalmente persiste."""
    settings = get_settings()
    configure_logging(settings.log_level)

    session_factory = None
    if persist:
        engine = get_engine(settings.database_url)
        init_db(engine)
        session_factory = get_session_factory(engine)

    try:
        results = run_demo_scraping(
            catalog_dir,
            settings.data_exports_dir,
            capture_date=capture.date() if capture else None,
            persist=persist,
            session_factory=session_factory,
        )
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc

    _print_products(results[-1])
    _print_summary(results)
    if any(result.errors for result in results):
        _print_errors(results)

    console.print(f"[green]Exports generados en:[/green] {settings.data_exports_dir}")
    if persist:
        console.print(f"[green]Historico guardado en:[/green] {settings.database_url}")
    if any(result.status == "failed" for result in results):
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
