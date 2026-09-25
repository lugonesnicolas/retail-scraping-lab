"""Caso de uso: ingerir el catalogo demo (una o todas sus capturas).

Por cada captura: spider (acquisition -> parsing -> normalization ->
validation), export JSON y, opcionalmente, persistencia historica con un
`ScrapeRun` que registra el resultado y los errores.
"""

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Literal

from sqlalchemy.orm import Session, sessionmaker

from retail_scraping_lab.core.exceptions import AcquisitionError, ParsingError
from retail_scraping_lab.models.database import get_session
from retail_scraping_lab.models.product import Product
from retail_scraping_lab.repositories.product_repository import ProductRepository, SaveResult
from retail_scraping_lab.scraping.clients.local_file_client import LocalFileClient
from retail_scraping_lab.scraping.pipelines.product_pipeline import export_products
from retail_scraping_lab.scraping.spiders.demo_store_spider import (
    SOURCE_NAME,
    DemoCapture,
    ItemError,
    list_demo_captures,
    run_demo_spider,
)

RunStatus = Literal["success", "partial", "failed"]


@dataclass(frozen=True)
class CaptureResult:
    """Resultado de procesar una captura del catalogo demo.

    `errors` incluye tanto errores por item como, si la captura no pudo
    leerse o parsearse, un unico error de pagina. `saved` es None si no se
    persistio.
    """

    capture: DemoCapture
    status: RunStatus
    items_found: int
    products: list[Product]
    errors: list[ItemError]
    export_path: Path
    saved: SaveResult | None


def select_captures(catalog_dir: Path, capture_date: date | None = None) -> list[DemoCapture]:
    """Todas las capturas en orden cronologico, o solo la de `capture_date`."""
    captures = list_demo_captures(catalog_dir)
    if not captures:
        raise ValueError(f"No hay capturas en {catalog_dir}")
    if capture_date is None:
        return captures
    selected = [c for c in captures if c.captured_at.date() == capture_date]
    if not selected:
        available = ", ".join(c.captured_at.date().isoformat() for c in captures)
        raise ValueError(
            f"No existe la captura {capture_date.isoformat()} (disponibles: {available})"
        )
    return selected


def run_status(products: list[Product], errors: list[ItemError]) -> RunStatus:
    if not products:
        return "failed"
    return "partial" if errors else "success"


def scrape_capture(
    catalog_dir: Path, capture: DemoCapture
) -> tuple[int, list[Product], list[ItemError]]:
    """Corre el spider sobre una captura; devuelve (items encontrados, productos, errores).

    Una falla de acquisition o de estructura de pagina no aborta la ingesta de
    las demas capturas: se reporta como un error de la captura.
    """
    try:
        result = run_demo_spider(LocalFileClient(catalog_dir), capture)
    except (AcquisitionError, ParsingError) as exc:
        page_error = ItemError(error_type=type(exc).__name__, message=str(exc), url=None)
        return 0, [], [page_error]
    return len(result.products) + len(result.errors), result.products, result.errors


def _start_run(session_factory: sessionmaker[Session], catalog_dir: Path) -> tuple[int, int]:
    """Crea el ScrapeRun en su propia transaccion; devuelve (run_id, source_id)."""
    with get_session(session_factory) as session:
        repo = ProductRepository(session)
        source = repo.get_or_create_source(
            name=SOURCE_NAME, base_url=str(catalog_dir), source_type="fixture"
        )
        run = repo.create_scrape_run(source_id=source.id)
        return run.id, source.id


def _record_failed_run(
    session_factory: sessionmaker[Session], run_id: int, items_found: int, exc: Exception
) -> None:
    """Marca el run como fallido en una transaccion nueva (la anterior ya hizo rollback)."""
    with get_session(session_factory) as session:
        repo = ProductRepository(session)
        repo.create_scrape_error(run_id=run_id, error_type=type(exc).__name__, message=str(exc))
        repo.finish_scrape_run(run_id, status="failed", products_found=items_found, errors_count=1)


def _persist_capture(
    session_factory: sessionmaker[Session],
    catalog_dir: Path,
    items_found: int,
    products: list[Product],
    errors: list[ItemError],
) -> SaveResult:
    """Guarda snapshots y errores de una captura bajo un ScrapeRun.

    Usa transacciones separadas: el run se crea y commitea primero, asi que
    si guardar los datos falla (rollback), igual queda registrado como
    `failed` con el error que lo causo.
    """
    run_id, source_id = _start_run(session_factory, catalog_dir)
    try:
        with get_session(session_factory) as session:
            repo = ProductRepository(session)
            saved = repo.save_scraped_products(source_id, products)
            for error in errors:
                repo.create_scrape_error(
                    run_id=run_id, error_type=error.error_type, message=error.message, url=error.url
                )
            repo.finish_scrape_run(
                run_id,
                status=run_status(products, errors),
                products_found=items_found,
                products_inserted=saved.inserted,
                products_updated=saved.updated,
                snapshots_skipped=saved.skipped,
                errors_count=len(errors),
            )
    except Exception as exc:
        _record_failed_run(session_factory, run_id, items_found, exc)
        raise
    return saved


def run_demo_scraping(
    catalog_dir: Path,
    output_dir: Path,
    *,
    capture_date: date | None = None,
    persist: bool = False,
    session_factory: sessionmaker[Session] | None = None,
) -> list[CaptureResult]:
    """Procesa las capturas del catalogo demo en orden cronologico (o solo una).

    Cada captura se exporta a `<fuente>_<fecha>.json` y, con `persist=True`, se
    guarda como un ScrapeRun con sus snapshots y errores.
    """
    if persist and session_factory is None:
        raise ValueError("session_factory es requerido cuando persist=True")

    results = []
    for capture in select_captures(catalog_dir, capture_date):
        items_found, products, errors = scrape_capture(catalog_dir, capture)
        export_path = export_products(
            products,
            output_dir,
            filename_stem=f"{SOURCE_NAME}_{capture.captured_at.date().isoformat()}",
        )
        saved = None
        if persist and session_factory is not None:
            saved = _persist_capture(session_factory, catalog_dir, items_found, products, errors)
        results.append(
            CaptureResult(
                capture=capture,
                status=run_status(products, errors),
                items_found=items_found,
                products=products,
                errors=errors,
                export_path=export_path,
                saved=saved,
            )
        )
    return results
