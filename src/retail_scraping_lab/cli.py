from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from retail_scraping_lab.config.settings import get_settings
from retail_scraping_lab.core.logging import configure_logging
from retail_scraping_lab.services.scraping_service import run_demo_scraping

app = typer.Typer(help="CLI de retail-scraping-lab")
console = Console()

_DEFAULT_FIXTURE = Path("tests/fixtures/demo_product_page.html")


@app.command("scrape-demo")
def scrape_demo(
    html_source: Path = typer.Option(_DEFAULT_FIXTURE, help="HTML local a procesar"),
) -> None:
    """Corre el spider demo sobre un HTML local y exporta el resultado."""
    settings = get_settings()
    configure_logging(settings.log_level)

    products, export_path = run_demo_scraping(html_source, settings.data_exports_dir)

    table = Table(title="Productos scrapeados")
    table.add_column("Nombre")
    table.add_column("Precio")
    table.add_column("Moneda")
    table.add_column("Disponibilidad")
    for product in products:
        table.add_row(product.name, str(product.price), product.currency, product.availability)
    console.print(table)
    console.print(f"[green]Export generado en:[/green] {export_path}")


if __name__ == "__main__":
    app()
