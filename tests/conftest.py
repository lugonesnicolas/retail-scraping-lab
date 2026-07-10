from collections.abc import Iterator

import pytest
from sqlalchemy.orm import Session

from retail_scraping_lab.models.database import get_engine, get_session_factory, init_db


@pytest.fixture
def db_session() -> Iterator[Session]:
    """Sesion sobre una base SQLite en memoria, aislada por test."""
    engine = get_engine("sqlite:///:memory:")
    init_db(engine)
    session_factory = get_session_factory(engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
