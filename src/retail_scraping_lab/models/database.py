from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base declarativa de SQLAlchemy.

    Las entidades del modelo de datos (Source, Category, Product, ProductSnapshot,
    ScrapeRun, ScrapeError) se implementan en la spec 003-data-model. Ver
    docs/03_data_model.md para el diseno completo.
    """


def get_engine(database_url: str) -> Engine:
    return create_engine(database_url)


def init_db(engine: Engine) -> None:
    Base.metadata.create_all(engine)
