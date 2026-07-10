from sqlalchemy import inspect

from retail_scraping_lab.models.database import get_engine, init_db


def test_init_db_creates_expected_tables() -> None:
    engine = get_engine("sqlite:///:memory:")

    init_db(engine)

    tables = set(inspect(engine).get_table_names())
    assert tables == {
        "sources",
        "categories",
        "products",
        "product_snapshots",
        "scrape_runs",
        "scrape_errors",
    }
