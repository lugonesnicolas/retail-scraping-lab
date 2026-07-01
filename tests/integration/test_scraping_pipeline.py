import json
from pathlib import Path

from retail_scraping_lab.scraping.pipelines.product_pipeline import export_products
from retail_scraping_lab.scraping.spiders.demo_store_spider import run_demo_spider

FIXTURE_PATH = Path(__file__).parents[1] / "fixtures" / "demo_product_page.html"


def test_demo_spider_and_pipeline_export_json(tmp_path: Path) -> None:
    products = run_demo_spider(FIXTURE_PATH)
    assert len(products) == 1

    export_path = export_products(products, tmp_path, export_format="json")

    assert export_path.exists()
    exported = json.loads(export_path.read_text(encoding="utf-8"))
    assert exported[0]["name"] == "Zapatillas Running Pro"


def test_demo_spider_and_pipeline_export_csv(tmp_path: Path) -> None:
    products = run_demo_spider(FIXTURE_PATH)

    export_path = export_products(products, tmp_path, export_format="csv")

    assert export_path.exists()
    assert export_path.suffix == ".csv"
