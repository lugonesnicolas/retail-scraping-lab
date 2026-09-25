from dataclasses import dataclass
from datetime import date
from pathlib import Path

from sqlalchemy.orm import Session, sessionmaker

from retail_scraping_lab.models.database import get_session
from retail_scraping_lab.models.product import Product
from retail_scraping_lab.repositories.product_repository import ProductRepository
from retail_scraping_lab.scraping.clients.local_file_client import LocalFileClient
from retail_scraping_lab.scraping.pipelines.product_pipeline import export_products
from retail_scraping_lab.scraping.spiders.demo_store_spider import (
    SOURCE_NAME,
    DemoCapture,
    ItemError,
    list_demo_captures,
    run_demo_spider,
)


@dataclass(frozen=True)
class DemoScrapeResult:
    """Resultado de procesar una captura del catalogo demo."""

    capture: DemoCapture
    products: list[Product]
    errors: list[ItemError]
    export_path: Path


def select_capture(catalog_dir: Path, capture_date: date | None = None) -> DemoCapture:
    """Devuelve la captura de `capture_date`, o la mas reciente si no se indica fecha."""
    captures = list_demo_captures(catalog_dir)
    if not captures:
        raise ValueError(f"No hay capturas en {catalog_dir}")
    if capture_date is None:
        return captures[-1]
    for capture in captures:
        if capture.captured_at.date() == capture_date:
            return capture
    available = ", ".join(capture.captured_at.date().isoformat() for capture in captures)
    raise ValueError(f"No existe la captura {capture_date.isoformat()} (disponibles: {available})")


def _persist_products(
    session_factory: sessionmaker[Session], catalog_dir: Path, products: list[Product]
) -> None:
    """Crea un ScrapeRun, guarda los productos como snapshots y registra errores."""
    with get_session(session_factory) as session:
        repo = ProductRepository(session)
        source = repo.get_or_create_source(
            name=SOURCE_NAME, base_url=str(catalog_dir), source_type="fixture"
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
    catalog_dir: Path,
    output_dir: Path,
    *,
    capture_date: date | None = None,
    persist: bool = False,
    session_factory: sessionmaker[Session] | None = None,
) -> DemoScrapeResult:
    """Orquesta el caso de uso 'procesar una captura del catalogo demo'.

    Elige la captura, la procesa con el spider (acquisition -> parsing ->
    normalization -> validation), exporta los productos validos y, si se
    pide, los persiste via `ProductRepository`.
    """
    capture = select_capture(catalog_dir, capture_date)
    spider_result = run_demo_spider(LocalFileClient(catalog_dir), capture)
    export_path = export_products(spider_result.products, output_dir)

    if persist:
        if session_factory is None:
            raise ValueError("session_factory es requerido cuando persist=True")
        _persist_products(session_factory, catalog_dir, spider_result.products)

    return DemoScrapeResult(
        capture=capture,
        products=spider_result.products,
        errors=spider_result.errors,
        export_path=export_path,
    )
