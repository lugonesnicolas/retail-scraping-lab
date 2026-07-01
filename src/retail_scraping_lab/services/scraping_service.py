from pathlib import Path

from retail_scraping_lab.models.product import Product
from retail_scraping_lab.scraping.pipelines.product_pipeline import export_products
from retail_scraping_lab.scraping.spiders.demo_store_spider import run_demo_spider


def run_demo_scraping(html_source: Path, output_dir: Path) -> tuple[list[Product], Path]:
    """Orquesta el caso de uso 'correr el scraper demo y exportar resultados'.

    Combina spider + pipeline. La integracion con repositories/ (persistencia)
    se agrega cuando 003-data-model este implementada.
    """
    products = run_demo_spider(html_source)
    export_path = export_products(products, output_dir)
    return products, export_path
