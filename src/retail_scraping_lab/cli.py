from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from retail_scraping_lab.config.settings import get_settings
from retail_scraping_lab.core.logging import configure_logging
from retail_scraping_lab.models.database import get_engine, get_session_factory, init_db
from retail_scraping_lab.services.scraping_service import run_demo_scraping

app = typer.Typer(help="CLI de retail-scraping-lab")
console = Console()

_DEFAULT_CATALOG_DIR = Path("tests/fixtures/demo_store")


@app.command("init-db")
def init_db_command() -> None:
    """Crea las tablas de la base de datos (SQLite) si todavia no existen."""
    settings = get_settings()
    configure_logging(settings.log_level)

    engine = get_engine(settings.database_url)
    init_db(engine)
    console.print(f"[green]Base de datos inicializada en:[/green] {settings.database_url}")


@app.command("scrape-demo")
def scrape_demo(
    catalog_dir: Path = typer.Option(
        _DEFAULT_CATALOG_DIR, help="Directorio del catalogo demo (una carpeta por captura)"
    ),
    capture: datetime | None = typer.Option(
        None,
        formats=["%Y-%m-%d"],
        help="Fecha de la captura a procesar (YYYY-MM-DD). Por defecto, la mas reciente.",
    ),
    persist: bool = typer.Option(
        False, "--persist", help="Guardar los productos scrapeados en la base de datos"
    ),
) -> None:
    """Procesa una captura del catalogo demo, exporta el resultado y opcionalmente persiste."""
    settings = get_settings()
    configure_logging(settings.log_level)

    session_factory = None
    if persist:
        engine = get_engine(settings.database_url)
        init_db(engine)
        session_factory = get_session_factory(engine)

    try:
        result = run_demo_scraping(
            catalog_dir,
            settings.data_exports_dir,
            capture_date=capture.date() if capture else None,
            persist=persist,
            session_factory=session_factory,
        )
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc

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

    if result.errors:
        errors_table = Table(title="Items descartados", style="yellow")
        errors_table.add_column("Tipo")
        errors_table.add_column("Mensaje")
        errors_table.add_column("URL")
        for error in result.errors:
            errors_table.add_row(error.error_type, error.message, error.url or "-")
        console.print(errors_table)

    console.print(f"[green]Export generado en:[/green] {result.export_path}")
    if persist:
        console.print(f"[green]Productos guardados en:[/green] {settings.database_url}")


if __name__ == "__main__":
    app()
