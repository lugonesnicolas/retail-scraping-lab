from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from retail_scraping_lab.models.database import Product as ProductModel
from retail_scraping_lab.models.product import Availability
from retail_scraping_lab.models.product import Product as ScrapedProduct
from retail_scraping_lab.repositories.product_repository import ProductRepository, SaveResult


def _scraped(captured_at: datetime, price: str, brand: str | None = "Velox") -> ScrapedProduct:
    return ScrapedProduct.model_validate(
        {
            "source": "demo-store",
            "captured_at": captured_at,
            "name": "Zapatillas Running Pro",
            "brand": brand,
            "price": Decimal(price),
            "currency": "ARS",
            "availability": Availability.UNKNOWN,
            "product_url": "https://demo.test/p/1",
        }
    )


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
        product_id=product.id,
        price=Decimal("100.00"),
        currency="ARS",
        availability=Availability.IN_STOCK,
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


def test_save_scraped_products_uses_captured_at_and_skips_existing_snapshots(
    db_session: Session,
) -> None:
    repo = ProductRepository(db_session)
    source = repo.get_or_create_source(name="demo-store", base_url="https://demo.test")
    day_1 = datetime(2026, 9, 1, tzinfo=UTC)
    day_2 = datetime(2026, 9, 8, tzinfo=UTC)

    first = repo.save_scraped_products(source.id, [_scraped(day_1, "100.00")])
    repeated = repo.save_scraped_products(source.id, [_scraped(day_1, "100.00")])
    second = repo.save_scraped_products(source.id, [_scraped(day_2, "120.00", brand="Velox Pro")])

    assert first == SaveResult(inserted=1, updated=0, skipped=0)
    assert repeated == SaveResult(inserted=0, updated=1, skipped=1)
    assert second == SaveResult(inserted=0, updated=1, skipped=0)

    product, _ = repo.get_or_create_product(
        source_id=source.id, product_url="https://demo.test/p/1", name="Zapatillas Running Pro"
    )
    snapshots = sorted(product.snapshots, key=lambda snapshot: snapshot.scraped_at)
    assert [snapshot.scraped_at.date() for snapshot in snapshots] == [day_1.date(), day_2.date()]
    assert [snapshot.price for snapshot in snapshots] == [Decimal("100.00"), Decimal("120.00")]
    assert snapshots[0].availability == "unknown"


def test_save_scraped_products_keeps_latest_brand_in_catalog(db_session: Session) -> None:
    repo = ProductRepository(db_session)
    source = repo.get_or_create_source(name="demo-store", base_url="https://demo.test")

    repo.save_scraped_products(source.id, [_scraped(datetime(2026, 9, 1, tzinfo=UTC), "1")])
    repo.save_scraped_products(
        source.id, [_scraped(datetime(2026, 9, 8, tzinfo=UTC), "1", brand="Velox Pro")]
    )

    product = db_session.scalars(select(ProductModel)).one()
    assert product.brand == "Velox Pro"
