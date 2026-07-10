from pathlib import Path

from sqlalchemy.orm import Session, sessionmaker

from retail_scraping_lab.models.database import get_session
from retail_scraping_lab.models.product import Product
from retail_scraping_lab.repositories.product_repository import ProductRepository
from retail_scraping_lab.scraping.pipelines.product_pipeline import export_products
from retail_scraping_lab.scraping.spiders.demo_store_spider import run_demo_spider

DEMO_SOURCE_NAME = "demo-store"


def _persist_products(
    session_factory: sessionmaker[Session], html_source: Path, products: list[Product]
) -> None:
    """Crea un ScrapeRun, guarda los productos como snapshots y registra errores."""
    with get_session(session_factory) as session:
        repo = ProductRepository(session)
        source = repo.get_or_create_source(
            name=DEMO_SOURCE_NAME, base_url=str(html_source), source_type="fixture"
        )
        run = repo.create_scrape_run(source_id=source.id)

        try:
            inserted, updated = repo.save_scraped_products(source.id, products)
        except Exception as exc:
            repo.create_scrape_error(run_id=run.id, error_type=type(exc).__name__, message=str(exc))
            repo.finish_scrape_run(
                run.id, status="failed", products_found=len(products), errors_count=1
            )
            raise

        repo.finish_scrape_run(
            run.id,
            status="success",
            products_found=len(products),
            products_inserted=inserted,
            products_updated=updated,
        )


def run_demo_scraping(
    html_source: Path,
    output_dir: Path,
    *,
    persist: bool = False,
    session_factory: sessionmaker[Session] | None = None,
) -> tuple[list[Product], Path]:
    """Orquesta el caso de uso 'correr el scraper demo y exportar resultados'.

    Combina spider + pipeline y, opcionalmente, persiste los productos en base
    de datos vía `repositories.product_repository.ProductRepository`.
    """
    products = run_demo_spider(html_source)
    export_path = export_products(products, output_dir)

    if persist:
        if session_factory is None:
            raise ValueError("session_factory es requerido cuando persist=True")
        _persist_products(session_factory, html_source, products)

    return products, export_path
