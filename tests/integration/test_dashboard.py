"""Smoke test del dashboard: corre `dashboard/app.py` sin servidor con AppTest."""

import sqlite3
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from retail_scraping_lab.models.database import get_engine, get_session_factory, init_db
from retail_scraping_lab.services.scraping_service import run_demo_scraping

APP_PATH = Path(__file__).parents[2] / "dashboard" / "app.py"


def _run_app(database_url: str, monkeypatch: pytest.MonkeyPatch) -> AppTest:
    monkeypatch.setenv("RSL_DATABASE_URL", database_url)
    return AppTest.from_file(str(APP_PATH), default_timeout=30).run()


def test_dashboard_renders_history(
    demo_catalog_dir: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database_url = f"sqlite:///{tmp_path / 'dashboard.db'}"
    engine = get_engine(database_url)
    init_db(engine)
    run_demo_scraping(
        demo_catalog_dir, tmp_path, persist=True, session_factory=get_session_factory(engine)
    )

    app = _run_app(database_url, monkeypatch)

    assert not app.exception
    assert [header.value for header in app.header] == [
        "Overview",
        "Latest products",
        "Price changes",
        "Price history",
        "Scrape runs",
        "Errors",
    ]
    metrics = {metric.label: metric.value for metric in app.metric}
    assert metrics["Total de productos"] == "11"
    assert metrics["Total de snapshots"] == "30"
    assert metrics["En stock / sin stock / desconocida"] == "9 / 1 / 1"


def test_dashboard_without_database_shows_instructions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app = _run_app(f"sqlite:///{tmp_path / 'missing.db'}", monkeypatch)

    assert not app.exception
    assert "No se encontro la base de datos" in app.warning[0].value


def test_dashboard_with_outdated_schema_shows_instructions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Regresion: una base con el esquema previo a 007 (available bool) no debe
    romper el dashboard con una excepcion de SQL, sino mostrar un aviso claro.
    """
    db_path = tmp_path / "outdated.db"
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "CREATE TABLE product_snapshots ("
            "id INTEGER PRIMARY KEY, product_id INTEGER, scraped_at DATETIME, "
            "price NUMERIC, currency VARCHAR(3), available BOOLEAN)"
        )

    app = _run_app(f"sqlite:///{db_path}", monkeypatch)

    assert not app.exception
    assert "esquema de una version anterior" in app.warning[0].value
    assert "make reset-db" in app.code[0].value
