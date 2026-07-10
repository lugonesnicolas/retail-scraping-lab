"""Modelos ORM de persistencia (SQLAlchemy).

Ver docs/03_data_model.md para el diseno completo del modelo de datos y la
diferencia entre `Product` (catalogo) y `ProductSnapshot` (historico). Estos
modelos son de persistencia; no confundir con `models.product.Product`, que es
el esquema Pydantic usado para validar datos recien scrapeados.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import (
    DateTime,
    Engine,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    sessionmaker,
)


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    """Base declarativa de SQLAlchemy para todas las entidades del modelo."""


class Source(Base):
    """Fuente de datos (un sitio o fixture de donde se obtienen productos)."""

    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    base_url: Mapped[str] = mapped_column(String(500))
    source_type: Mapped[str] = mapped_column(String(50))
    active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, onupdate=_utcnow)

    categories: Mapped[list["Category"]] = relationship(back_populates="source")
    products: Mapped[list["Product"]] = relationship(back_populates="source")
    scrape_runs: Mapped[list["ScrapeRun"]] = relationship(back_populates="source")


class Category(Base):
    """Categoria de producto, propia del dominio del proyecto."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    url: Mapped[str | None] = mapped_column(String(500))
    external_id: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, onupdate=_utcnow)

    source: Mapped[Source] = relationship(back_populates="categories")
    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Product(Base):
    """Identidad logica de un producto dentro de una fuente (el catalogo).

    No cambia entre scrapes; el estado en cada momento se registra en
    `ProductSnapshot`.
    """

    __tablename__ = "products"
    __table_args__ = (UniqueConstraint("source_id", "product_url", name="uq_products_source_url"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), index=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))
    external_id: Mapped[str | None] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(500))
    brand: Mapped[str | None] = mapped_column(String(255))
    normalized_name: Mapped[str | None] = mapped_column(String(500))
    product_url: Mapped[str] = mapped_column(String(500))
    image_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, onupdate=_utcnow)

    source: Mapped[Source] = relationship(back_populates="products")
    category: Mapped[Category | None] = relationship(back_populates="products")
    snapshots: Mapped[list["ProductSnapshot"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )


class ProductSnapshot(Base):
    """Estado de un producto en un momento dado (un registro por scrape exitoso)."""

    __tablename__ = "product_snapshots"
    __table_args__ = (
        Index("ix_product_snapshots_product_id_scraped_at", "product_id", "scraped_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    scraped_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    list_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    discount_percentage: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    currency: Mapped[str] = mapped_column(String(3))
    available: Mapped[bool]
    raw_hash: Mapped[str | None] = mapped_column(String(64))

    product: Mapped[Product] = relationship(back_populates="snapshots")


class ScrapeRun(Base):
    """Una ejecucion del scraper sobre una fuente."""

    __tablename__ = "scrape_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20))
    products_found: Mapped[int] = mapped_column(default=0)
    products_inserted: Mapped[int] = mapped_column(default=0)
    products_updated: Mapped[int] = mapped_column(default=0)
    errors_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    source: Mapped[Source] = relationship(back_populates="scrape_runs")
    errors: Mapped[list["ScrapeError"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )


class ScrapeError(Base):
    """Error de extraccion ocurrido durante una corrida de scraping."""

    __tablename__ = "scrape_errors"

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("scrape_runs.id"), index=True)
    url: Mapped[str | None] = mapped_column(String(500))
    error_type: Mapped[str] = mapped_column(String(100))
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    run: Mapped[ScrapeRun] = relationship(back_populates="errors")


def get_engine(database_url: str) -> Engine:
    return create_engine(database_url)


def get_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)


def init_db(engine: Engine) -> None:
    """Crea el esquema (todas las tablas) si no existe todavia.

    No usa un sistema de migraciones (Alembic queda fuera de alcance de esta
    etapa, ver docs/03_data_model.md); pensado para SQLite local y para tests.
    """
    database_path = engine.url.database
    if engine.url.drivername.startswith("sqlite") and database_path and database_path != ":memory:":
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(engine)


@contextmanager
def get_session(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    """Entrega una sesion, hace commit al salir sin errores y rollback si falla."""
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
