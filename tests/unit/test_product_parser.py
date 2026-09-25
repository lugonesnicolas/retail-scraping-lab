from pathlib import Path

import pytest

from retail_scraping_lab.core.exceptions import ParsingError
from retail_scraping_lab.scraping.parsers.product_parser import parse_catalog


def test_parse_catalog_extracts_raw_fields_of_every_card(demo_catalog_dir: Path) -> None:
    html_content = (demo_catalog_dir / "2026-09-01" / "catalog.html").read_text(encoding="utf-8")

    result = parse_catalog(html_content)

    assert len(result) == 10
    assert result[0] == {
        "name": "Zapatillas Running Pro",
        "brand": "Velox",
        "price": "$ 45.999,90",
        "currency": "ARS",
        "availability": "En stock",
        "product_url": "https://demo-store.example.com/products/zapatillas-running-pro",
        "image_url": "https://demo-store.example.com/images/zapatillas-running-pro.jpg",
    }


def test_parse_catalog_keeps_missing_fields_as_none() -> None:
    html_content = """
    <html><body>
      <article class="product-card">
        <h2 class="product-name">Sin precio ni marca</h2>
      </article>
    </body></html>
    """

    [raw] = parse_catalog(html_content)

    assert raw["name"] == "Sin precio ni marca"
    assert raw["brand"] is None
    assert raw["price"] is None


def test_parse_catalog_does_not_mix_fields_between_cards() -> None:
    html_content = """
    <html><body>
      <article class="product-card"><h2 class="product-name">A</h2></article>
      <article class="product-card">
        <h2 class="product-name">B</h2><span class="product-brand">Marca B</span>
      </article>
    </body></html>
    """

    first, second = parse_catalog(html_content)

    assert first["brand"] is None
    assert second["brand"] == "Marca B"


def test_parse_catalog_raises_when_page_has_no_cards() -> None:
    with pytest.raises(ParsingError):
        parse_catalog("<html><body><h1>Pagina rediseñada</h1></body></html>")
