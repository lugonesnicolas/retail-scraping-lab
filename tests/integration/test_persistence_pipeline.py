from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from retail_scraping_lab.analytics import queries
from retail_scraping_lab.models.database import Product as ProductModel
from retail_scraping_lab.models.database import (
    ProductSnapshot,
    ScrapeError,
    ScrapeRun,
    get_engine,
    get_session_factory,
    init_db,
)
from retail_scraping_lab.repositories.product_repository import ProductRepository
from retail_scraping_lab.services.scraping_service import run_demo_scraping, select_captures


@pytest.fixture
def session_factory(tmp_path: Path) -> sessionmaker[Session]:
    engine = get_engine(f"sqlite:///{tmp_path / 'test.db'}")
    init_db(engine)
    return get_session_factory(engine)


def test_select_captures_all_or_one(demo_catalog_dir: Path) -> None:
    assert len(select_captures(demo_catalog_dir)) == 3
    [only] = select_captures(demo_catalog_dir, date(2026, 9, 8))
    assert only.location == "2026-09-08/catalog.html"
    with pytest.raises(ValueError, match="2026-09-01"):
        select_captures(demo_catalog_dir, date(2020, 1, 1))


def test_ingesting_all_captures_builds_history(
    demo_catalog_dir: Path, tmp_path: Path, session_factory: sessionmaker[Session]
) -> None:
    results = run_demo_scraping(
        demo_catalog_dir, tmp_path, persist=True, session_factory=session_factory
    )

    assert [result.status for result in results] == ["success", "partial", "success"]
    assert [result.export_path.name for result in results] == [
        "demo-store_2026-09-01.json",
        "demo-store_2026-09-08.json",
        "demo-store_2026-09-15.json",
    ]

    with session_factory() as session:
        # 10 + 9 validos (1 descartado) + 11 = 30 observaciones de 11 productos.
        assert queries.count_products(session) == 11
        assert queries.count_snapshots(session) == 30
        assert queries.current_availability_breakdown(session) == {
            "in_stock": 9,
            "out_of_stock": 1,
            "unknown": 1,
        }
        changes = {change.name: change for change in queries.price_changes(session)}
        # La botella no tiene observacion valida el 08/09: compara 01/09 contra 15/09.
        assert changes["Botella Térmica 750 ml"].previous_price == Decimal("15490.00")
        assert changes["Zapatillas Trail X"].change == Decimal("-3501.00")
        assert "Short Running Liviano" not in changes

        runs = session.scalars(select(ScrapeRun).order_by(ScrapeRun.id)).all()
        assert [(run.status, run.products_found, run.errors_count) for run in runs] == [
            ("success", 10, 0),
            ("partial", 10, 1),
            ("success", 11, 0),
        ]
        [error] = session.scalars(select(ScrapeError)).all()
        assert error.run_id == runs[1].id
        assert error.error_type == "NormalizationError"
        assert error.url == "https://demo-store.example.com/products/botella-termica-750"


def test_reprocessing_captures_is_idempotent(
    demo_catalog_dir: Path, tmp_path: Path, session_factory: sessionmaker[Session]
) -> None:
    run_demo_scraping(demo_catalog_dir, tmp_path, persist=True, session_factory=session_factory)
    results = run_demo_scraping(
        demo_catalog_dir, tmp_path, persist=True, session_factory=session_factory
    )

    assert [result.saved.skipped for result in results if result.saved] == [10, 9, 11]
    with session_factory() as session:
        assert session.query(ProductModel).count() == 11
        assert session.query(ProductSnapshot).count() == 30
        assert session.query(ScrapeRun).count() == 6


def test_unexpected_persistence_failure_is_recorded_as_failed_run(
    demo_catalog_dir: Path,
    tmp_path: Path,
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regresion: antes el rollback borraba tambien el run fallido y su error."""

    def broken_save(*args: object, **kwargs: object) -> None:
        raise RuntimeError("disco lleno")

    monkeypatch.setattr(ProductRepository, "save_scraped_products", broken_save)

    with pytest.raises(RuntimeError):
        run_demo_scraping(
            demo_catalog_dir,
            tmp_path,
            capture_date=date(2026, 9, 1),
            persist=True,
            session_factory=session_factory,
        )

    with session_factory() as session:
        [run] = session.scalars(select(ScrapeRun)).all()
        [error] = session.scalars(select(ScrapeError)).all()
        assert run.status == "failed"
        assert run.finished_at is not None
        assert error.error_type == "RuntimeError"
        assert error.message == "disco lleno"
        assert session.query(ProductSnapshot).count() == 0


def test_unreadable_capture_is_a_failed_run_without_stopping_the_others(
    tmp_path: Path, session_factory: sessionmaker[Session]
) -> None:
    catalog_dir = tmp_path / "catalog"
    (catalog_dir / "2026-09-01").mkdir(parents=True)
    (catalog_dir / "2026-09-01" / "catalog.html").write_text(
        "<html><body>rediseño</body></html>", encoding="utf-8"
    )

    [result] = run_demo_scraping(
        catalog_dir, tmp_path / "exports", persist=True, session_factory=session_factory
    )

    assert result.status == "failed"
    assert [error.error_type for error in result.errors] == ["ParsingError"]
    with session_factory() as session:
        [run] = session.scalars(select(ScrapeRun)).all()
        assert run.status == "failed"
        assert run.errors_count == 1


def test_run_demo_scraping_without_persist_needs_no_database(
    demo_catalog_dir: Path, tmp_path: Path
) -> None:
    results = run_demo_scraping(demo_catalog_dir, tmp_path)

    assert all(result.saved is None for result in results)
    assert all(result.export_path.exists() for result in results)
