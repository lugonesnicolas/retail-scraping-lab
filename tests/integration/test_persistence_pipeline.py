from datetime import date
from pathlib import Path

import pytest
from sqlalchemy.orm import Session, sessionmaker

from retail_scraping_lab.models.database import Product as ProductModel
from retail_scraping_lab.models.database import (
    ProductSnapshot,
    get_engine,
    get_session_factory,
    init_db,
)
from retail_scraping_lab.services.scraping_service import run_demo_scraping, select_capture


def _session_factory(tmp_path: Path) -> sessionmaker[Session]:
    engine = get_engine(f"sqlite:///{tmp_path / 'test.db'}")
    init_db(engine)
    return get_session_factory(engine)


def test_select_capture_defaults_to_latest(demo_catalog_dir: Path) -> None:
    assert select_capture(demo_catalog_dir).captured_at.date() == date(2026, 9, 15)
    assert select_capture(demo_catalog_dir, date(2026, 9, 1)).location == (
        "2026-09-01/catalog.html"
    )


def test_select_capture_rejects_unknown_date(demo_catalog_dir: Path) -> None:
    with pytest.raises(ValueError, match="2026-09-01"):
        select_capture(demo_catalog_dir, date(2020, 1, 1))


def test_run_demo_scraping_persists_products_and_snapshots(
    demo_catalog_dir: Path, tmp_path: Path
) -> None:
    session_factory = _session_factory(tmp_path)

    result = run_demo_scraping(
        demo_catalog_dir,
        tmp_path,
        capture_date=date(2026, 9, 1),
        persist=True,
        session_factory=session_factory,
    )

    assert result.export_path.exists()
    assert len(result.products) == 10

    with session_factory() as session:
        stored_products = session.query(ProductModel).all()
        stored_snapshots = session.query(ProductSnapshot).all()

    assert len(stored_products) == 10
    assert len(stored_snapshots) == 10


def test_run_demo_scraping_two_captures_reuses_products(
    demo_catalog_dir: Path, tmp_path: Path
) -> None:
    """Procesar dos capturas no duplica productos, pero si agrega snapshots."""
    session_factory = _session_factory(tmp_path)

    for capture_date in (date(2026, 9, 1), date(2026, 9, 8)):
        run_demo_scraping(
            demo_catalog_dir,
            tmp_path,
            capture_date=capture_date,
            persist=True,
            session_factory=session_factory,
        )

    with session_factory() as session:
        stored_products = session.query(ProductModel).count()
        stored_snapshots = session.query(ProductSnapshot).count()

    # 10 productos en la primera captura; en la segunda, 9 validos (1 descartado).
    assert stored_products == 10
    assert stored_snapshots == 19


def test_run_demo_scraping_without_persist_needs_no_database(
    demo_catalog_dir: Path, tmp_path: Path
) -> None:
    result = run_demo_scraping(demo_catalog_dir, tmp_path)

    assert result.export_path.exists()
    assert len(result.products) == 11
