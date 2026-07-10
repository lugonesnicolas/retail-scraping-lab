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

_DEFAULT_FIXTURE = Path("tests/fixtures/demo_product_page.html")


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
    html_source: Path = typer.Option(_DEFAULT_FIXTURE, help="HTML local a procesar"),
    persist: bool = typer.Option(
        False, "--persist", help="Guardar los productos scrapeados en la base de datos"
    ),
) -> None:
    """Corre el spider demo sobre un HTML local, exporta el resultado y opcionalmente persiste."""
    settings = get_settings()
    configure_logging(settings.log_level)

    session_factory = None
    if persist:
        engine = get_engine(settings.database_url)
        init_db(engine)
        session_factory = get_session_factory(engine)

    products, export_path = run_demo_scraping(
        html_source, settings.data_exports_dir, persist=persist, session_factory=session_factory
    )

    table = Table(title="Productos scrapeados")
    table.add_column("Nombre")
    table.add_column("Precio")
    table.add_column("Moneda")
    table.add_column("Disponibilidad")
    for product in products:
        table.add_row(product.name, str(product.price), product.currency, product.availability)
    console.print(table)
    console.print(f"[green]Export generado en:[/green] {export_path}")
    if persist:
        console.print(f"[green]Productos guardados en:[/green] {settings.database_url}")


if __name__ == "__main__":
    app()
