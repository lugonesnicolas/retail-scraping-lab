import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from retail_scraping_lab.models.product import Availability
from retail_scraping_lab.scraping.clients.local_file_client import LocalFileClient
from retail_scraping_lab.scraping.pipelines.product_pipeline import export_products
from retail_scraping_lab.scraping.spiders.demo_store_spider import (
    SOURCE_NAME,
    list_demo_captures,
    run_demo_spider,
)


def test_list_demo_captures_is_chronological_and_ignores_other_entries(
    demo_catalog_dir: Path, tmp_path: Path
) -> None:
    captures = list_demo_captures(demo_catalog_dir)

    assert [capture.captured_at for capture in captures] == [
        datetime(2026, 9, 1, tzinfo=UTC),
        datetime(2026, 9, 8, tzinfo=UTC),
        datetime(2026, 9, 15, tzinfo=UTC),
    ]
    assert captures[0].location == "2026-09-01/catalog.html"

    (tmp_path / "notas").mkdir()
    (tmp_path / "notas" / "catalog.html").write_text("<html/>", encoding="utf-8")
    (tmp_path / "2026-10-01").mkdir()  # fecha valida pero sin catalog.html
    assert list_demo_captures(tmp_path) == []


def test_spider_normalizes_and_validates_every_product(demo_catalog_dir: Path) -> None:
    [first_capture, *_] = list_demo_captures(demo_catalog_dir)

    result = run_demo_spider(LocalFileClient(demo_catalog_dir), first_capture)

    assert len(result.products) == 10
    assert result.errors == []
    product = result.products[0]
    assert product.source == SOURCE_NAME
    assert product.captured_at == first_capture.captured_at
    assert product.name == "Zapatillas Running Pro"
    assert product.brand == "Velox"
    assert product.price == Decimal("45999.90")
    assert product.availability == Availability.IN_STOCK
    unbranded = [p for p in result.products if p.brand is None]
    assert [p.name for p in unbranded] == ["Gorra Running Ultralight"]


def test_spider_reports_invalid_item_without_dropping_the_capture(
    demo_catalog_dir: Path,
) -> None:
    second_capture = list_demo_captures(demo_catalog_dir)[1]

    result = run_demo_spider(LocalFileClient(demo_catalog_dir), second_capture)

    assert len(result.products) == 9
    [error] = result.errors
    assert error.error_type == "NormalizationError"
    assert "Consultar precio" in error.message
    assert error.url == "https://demo-store.example.com/products/botella-termica-750"


def test_spider_maps_unknown_availability(demo_catalog_dir: Path) -> None:
    last_capture = list_demo_captures(demo_catalog_dir)[-1]

    result = run_demo_spider(LocalFileClient(demo_catalog_dir), last_capture)

    by_name = {product.name: product for product in result.products}
    assert len(result.products) == 11
    assert by_name["Campera Rompeviento"].availability == Availability.UNKNOWN
    assert by_name["Reloj GPS Sport"].availability == Availability.OUT_OF_STOCK


def test_spider_and_pipeline_export_json_and_csv(demo_catalog_dir: Path, tmp_path: Path) -> None:
    capture = list_demo_captures(demo_catalog_dir)[0]
    products = run_demo_spider(LocalFileClient(demo_catalog_dir), capture).products

    json_path = export_products(products, tmp_path, export_format="json")
    csv_path = export_products(products, tmp_path, export_format="csv")

    exported = json.loads(json_path.read_text(encoding="utf-8"))
    assert len(exported) == 10
    assert exported[0]["source"] == SOURCE_NAME
    assert exported[0]["captured_at"].startswith("2026-09-01")
    assert csv_path.suffix == ".csv"
