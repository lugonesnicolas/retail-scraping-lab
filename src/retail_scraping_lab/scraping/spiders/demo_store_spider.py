from pathlib import Path

from pydantic import ValidationError

from retail_scraping_lab.core.exceptions import ParsingError
from retail_scraping_lab.models.product import Product
from retail_scraping_lab.scraping.parsers.product_parser import parse_product


def run_demo_spider(html_source: Path) -> list[Product]:
    """Corre el spider demo sobre un archivo HTML local (fixture o export similar).

    No hace requests de red: lee el HTML directamente del disco. El uso de
    HttpClient para una fuente real se agrega en un spider especifico de esa
    fuente, reutilizando el mismo parser y flujo de validacion.
    """
    html_content = html_source.read_text(encoding="utf-8")

    raw_product = parse_product(html_content)
    try:
        product = Product.model_validate(raw_product)
    except ValidationError as exc:
        raise ParsingError(f"Producto invalido en {html_source}: {exc}") from exc

    return [product]
