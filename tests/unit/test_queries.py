from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from retail_scraping_lab.analytics import queries
from retail_scraping_lab.repositories.product_repository import ProductRepository


def _make_product(repo: ProductRepository, source_id: int, suffix: str) -> int:
    product, _ = repo.get_or_create_product(
        source_id=source_id,
        product_url=f"https://demo.test/p/{suffix}",
        name=f"Producto {suffix}",
    )
    return product.id


def test_count_products_and_snapshots_empty_db(db_session: Session) -> None:
    assert queries.count_products(db_session) == 0
    assert queries.count_snapshots(db_session) == 0


def test_count_products_and_snapshots(db_session: Session) -> None:
    repo = ProductRepository(db_session)
    source = repo.get_or_create_source(name="demo-store", base_url="https://demo.test")
    product_id = _make_product(repo, source.id, "1")
    repo.create_product_snapshot(
        product_id=product_id, price=Decimal("10.00"), currency="ARS", available=True
    )
    repo.create_product_snapshot(
        product_id=product_id, price=Decimal("12.00"), currency="ARS", available=True
    )

    assert queries.count_products(db_session) == 1
    assert queries.count_snapshots(db_session) == 2


def test_latest_snapshots_returns_most_recent_per_product(db_session: Session) -> None:
    repo = ProductRepository(db_session)
    source = repo.get_or_create_source(name="demo-store", base_url="https://demo.test")
    product_id = _make_product(repo, source.id, "1")

    older = datetime.now(UTC) - timedelta(hours=1)
    newer = datetime.now(UTC)
    repo.create_product_snapshot(
        product_id=product_id,
        price=Decimal("10.00"),
        currency="ARS",
        available=False,
        scraped_at=older,
    )
    repo.create_product_snapshot(
        product_id=product_id,
        price=Decimal("15.00"),
        currency="ARS",
        available=True,
        scraped_at=newer,
    )

    rows = queries.latest_snapshots(db_session)

    assert len(rows) == 1
    assert rows[0].price == Decimal("15.00")
    assert rows[0].available is True


def test_average_current_price_and_availability_breakdown(db_session: Session) -> None:
    repo = ProductRepository(db_session)
    source = repo.get_or_create_source(name="demo-store", base_url="https://demo.test")
    product_a = _make_product(repo, source.id, "a")
    product_b = _make_product(repo, source.id, "b")
    repo.create_product_snapshot(
        product_id=product_a, price=Decimal("10.00"), currency="ARS", available=True
    )
    repo.create_product_snapshot(
        product_id=product_b, price=Decimal("20.00"), currency="ARS", available=False
    )

    assert queries.average_current_price(db_session) == Decimal("15.00")
    assert queries.current_availability_breakdown(db_session) == {
        "in_stock": 1,
        "out_of_stock": 1,
    }


def test_average_current_price_none_when_no_data(db_session: Session) -> None:
    assert queries.average_current_price(db_session) is None
    assert queries.current_availability_breakdown(db_session) == {
        "in_stock": 0,
        "out_of_stock": 0,
    }


def test_price_history_orders_by_scraped_at(db_session: Session) -> None:
    repo = ProductRepository(db_session)
    source = repo.get_or_create_source(name="demo-store", base_url="https://demo.test")
    product_id = _make_product(repo, source.id, "1")

    now = datetime.now(UTC)
    repo.create_product_snapshot(
        product_id=product_id,
        price=Decimal("20.00"),
        currency="ARS",
        available=True,
        scraped_at=now,
    )
    repo.create_product_snapshot(
        product_id=product_id,
        price=Decimal("10.00"),
        currency="ARS",
        available=True,
        scraped_at=now - timedelta(days=1),
    )

    history = queries.price_history(db_session, product_id)

    assert [point.price for point in history] == [Decimal("10.00"), Decimal("20.00")]


def test_list_products(db_session: Session) -> None:
    repo = ProductRepository(db_session)
    source = repo.get_or_create_source(name="demo-store", base_url="https://demo.test")
    _make_product(repo, source.id, "1")
    _make_product(repo, source.id, "2")

    options = queries.list_products(db_session)

    assert [option.name for option in options] == ["Producto 1", "Producto 2"]


def test_recent_scrape_runs_includes_source_name(db_session: Session) -> None:
    repo = ProductRepository(db_session)
    source = repo.get_or_create_source(name="demo-store", base_url="https://demo.test")
    run = repo.create_scrape_run(source_id=source.id)
    repo.finish_scrape_run(run.id, status="success", products_found=2, products_inserted=2)

    runs = queries.recent_scrape_runs(db_session)

    assert len(runs) == 1
    assert runs[0].source_name == "demo-store"
    assert runs[0].status == "success"


def test_recent_errors_returns_latest_first(db_session: Session) -> None:
    repo = ProductRepository(db_session)
    source = repo.get_or_create_source(name="demo-store", base_url="https://demo.test")
    run = repo.create_scrape_run(source_id=source.id)
    repo.create_scrape_error(run_id=run.id, error_type="ParsingError", message="first")
    repo.create_scrape_error(run_id=run.id, error_type="HttpClientError", message="second")

    errors = queries.recent_errors(db_session)

    assert [error.message for error in errors] == ["second", "first"]
