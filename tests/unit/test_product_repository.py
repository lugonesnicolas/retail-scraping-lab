from decimal import Decimal

from sqlalchemy.orm import Session

from retail_scraping_lab.repositories.product_repository import ProductRepository


def test_get_or_create_source_creates_then_reuses(db_session: Session) -> None:
    repo = ProductRepository(db_session)

    created = repo.get_or_create_source(name="demo-store", base_url="https://demo.test")
    reused = repo.get_or_create_source(name="demo-store", base_url="https://other.test")

    assert created.id == reused.id
    assert reused.base_url == "https://demo.test"


def test_get_or_create_product_dedupes_by_source_and_url(db_session: Session) -> None:
    repo = ProductRepository(db_session)
    source = repo.get_or_create_source(name="demo-store", base_url="https://demo.test")

    product, created = repo.get_or_create_product(
        source_id=source.id, product_url="https://demo.test/p/1", name="Producto 1"
    )
    same_product, created_again = repo.get_or_create_product(
        source_id=source.id,
        product_url="https://demo.test/p/1",
        name="Producto 1 (actualizado)",
    )

    assert created is True
    assert created_again is False
    assert product.id == same_product.id
    assert same_product.name == "Producto 1 (actualizado)"


def test_create_product_snapshot(db_session: Session) -> None:
    repo = ProductRepository(db_session)
    source = repo.get_or_create_source(name="demo-store", base_url="https://demo.test")
    product, _ = repo.get_or_create_product(
        source_id=source.id, product_url="https://demo.test/p/1", name="Producto 1"
    )

    snapshot = repo.create_product_snapshot(
        product_id=product.id, price=Decimal("100.00"), currency="ARS", available=True
    )

    assert snapshot.id is not None
    assert product.snapshots == [snapshot]


def test_scrape_run_lifecycle_and_errors(db_session: Session) -> None:
    repo = ProductRepository(db_session)
    source = repo.get_or_create_source(name="demo-store", base_url="https://demo.test")

    run = repo.create_scrape_run(source_id=source.id)
    repo.create_scrape_error(run_id=run.id, error_type="parse_error", message="boom")
    finished = repo.finish_scrape_run(
        run.id, status="partial", products_found=1, products_inserted=1, errors_count=1
    )

    assert finished.status == "partial"
    assert finished.finished_at is not None
    assert len(finished.errors) == 1
