from pathlib import Path

from retail_scraping_lab.models.database import Product as ProductModel
from retail_scraping_lab.models.database import (
    ProductSnapshot,
    get_engine,
    get_session_factory,
    init_db,
)
from retail_scraping_lab.services.scraping_service import run_demo_scraping

FIXTURE_PATH = Path(__file__).parents[1] / "fixtures" / "demo_product_page.html"


def test_run_demo_scraping_persists_products_and_snapshots(tmp_path: Path) -> None:
    engine = get_engine(f"sqlite:///{tmp_path / 'test.db'}")
    init_db(engine)
    session_factory = get_session_factory(engine)

    products, export_path = run_demo_scraping(
        FIXTURE_PATH, tmp_path, persist=True, session_factory=session_factory
    )

    assert export_path.exists()
    assert len(products) == 1

    with session_factory() as session:
        stored_products = session.query(ProductModel).all()
        stored_snapshots = session.query(ProductSnapshot).all()

    assert len(stored_products) == 1
    assert stored_products[0].name == "Zapatillas Running Pro"
    assert len(stored_snapshots) == 1
    assert stored_snapshots[0].product_id == stored_products[0].id


def test_run_demo_scraping_persist_twice_reuses_product(tmp_path: Path) -> None:
    """Correr el scrape dos veces no duplica el producto, pero si agrega snapshots."""
    engine = get_engine(f"sqlite:///{tmp_path / 'test.db'}")
    init_db(engine)
    session_factory = get_session_factory(engine)

    run_demo_scraping(FIXTURE_PATH, tmp_path, persist=True, session_factory=session_factory)
    run_demo_scraping(FIXTURE_PATH, tmp_path, persist=True, session_factory=session_factory)

    with session_factory() as session:
        stored_products = session.query(ProductModel).all()
        stored_snapshots = session.query(ProductSnapshot).all()

    assert len(stored_products) == 1
    assert len(stored_snapshots) == 2


def test_run_demo_scraping_without_persist_needs_no_database(tmp_path: Path) -> None:
    products, export_path = run_demo_scraping(FIXTURE_PATH, tmp_path)

    assert export_path.exists()
    assert len(products) == 1
