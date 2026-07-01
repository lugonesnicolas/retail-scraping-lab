from pathlib import Path

import pytest

from retail_scraping_lab.core.exceptions import ParsingError
from retail_scraping_lab.scraping.parsers.product_parser import parse_product

FIXTURE_PATH = Path(__file__).parents[1] / "fixtures" / "demo_product_page.html"


def test_parse_product_extracts_all_fields() -> None:
    html_content = FIXTURE_PATH.read_text(encoding="utf-8")

    result = parse_product(html_content)

    assert result["name"] == "Zapatillas Running Pro"
    assert result["price"] == "45999.90"
    assert result["currency"] == "ARS"
    assert result["availability"] == "in_stock"
    assert result["product_url"] == (
        "https://demo-store.example.com/products/zapatillas-running-pro"
    )
    assert result["image_url"] == (
        "https://demo-store.example.com/images/zapatillas-running-pro.jpg"
    )


def test_parse_product_raises_on_missing_fields() -> None:
    with pytest.raises(ParsingError):
        parse_product("<html><body><h1 class='product-name'>Solo nombre</h1></body></html>")
