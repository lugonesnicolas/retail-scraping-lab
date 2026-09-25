from pathlib import Path

import pytest
from sqlalchemy import func, select
from typer.testing import CliRunner

from retail_scraping_lab.cli import app
from retail_scraping_lab.models.database import ProductSnapshot, get_engine, get_session_factory

runner = CliRunner()


@pytest.fixture
def database_url(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> str:
    """Apunta el CLI a una base y un directorio de exports temporales."""
    url = f"sqlite:///{tmp_path / 'cli.db'}"
    monkeypatch.setenv("RSL_DATABASE_URL", url)
    monkeypatch.setenv("RSL_DATA_EXPORTS_DIR", str(tmp_path / "exports"))
    return url


def _count_snapshots(database_url: str) -> int:
    with get_session_factory(get_engine(database_url))() as session:
        return session.scalar(select(func.count()).select_from(ProductSnapshot)) or 0


def test_scrape_demo_persist_is_idempotent(database_url: str, demo_catalog_dir: Path) -> None:
    args = ["scrape-demo", "--persist", "--catalog-dir", str(demo_catalog_dir)]

    first = runner.invoke(app, args)
    second = runner.invoke(app, args)

    assert first.exit_code == 0, first.output
    assert second.exit_code == 0, second.output
    assert "partial" in first.output
    assert _count_snapshots(database_url) == 30


def test_scrape_demo_single_capture(database_url: str, demo_catalog_dir: Path) -> None:
    result = runner.invoke(
        app,
        ["scrape-demo", "--persist", "--catalog-dir", str(demo_catalog_dir)]
        + ["--capture", "2026-09-01"],
    )

    assert result.exit_code == 0, result.output
    assert _count_snapshots(database_url) == 10


def test_scrape_demo_unknown_capture_exits_with_error(
    database_url: str, demo_catalog_dir: Path
) -> None:
    result = runner.invoke(
        app, ["scrape-demo", "--catalog-dir", str(demo_catalog_dir), "--capture", "2020-01-01"]
    )

    assert result.exit_code == 1
    assert "No existe la captura" in result.output


def test_init_db_reset_drops_existing_data(database_url: str, demo_catalog_dir: Path) -> None:
    runner.invoke(app, ["scrape-demo", "--persist", "--catalog-dir", str(demo_catalog_dir)])

    result = runner.invoke(app, ["init-db", "--reset"])

    assert result.exit_code == 0, result.output
    assert _count_snapshots(database_url) == 0
