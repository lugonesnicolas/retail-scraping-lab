"""Consultas de negocio de solo lectura sobre datos ya persistidos.

Ver docs/05_business_questions.md para las preguntas que motivan estas
consultas y docs/03_data_model.md para el modelo subyacente. Cada funcion
recibe una `Session` ya abierta (no crea engine ni conexion propia): quien
llama (CLI, dashboard, tests) decide el ciclo de vida de la sesion.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session, aliased

from retail_scraping_lab.models.database import (
    Product,
    ProductSnapshot,
    ScrapeError,
    ScrapeRun,
    Source,
)
from retail_scraping_lab.models.product import Availability


@dataclass(frozen=True)
class ProductOption:
    """Par (id, nombre) usado para poblar selectores de producto."""

    id: int
    name: str


@dataclass(frozen=True)
class LatestProductRow:
    """Ultimo snapshot conocido de un producto, con su fuente y datos de catalogo."""

    product_id: int
    source_name: str
    name: str
    brand: str | None
    product_url: str
    price: Decimal
    currency: str
    availability: str
    scraped_at: datetime


@dataclass(frozen=True)
class PricePoint:
    """Un punto de la serie historica de precio de un producto."""

    scraped_at: datetime
    price: Decimal


@dataclass(frozen=True)
class PriceChangeRow:
    """Variacion de precio de un producto entre sus dos observaciones mas recientes."""

    product_id: int
    name: str
    previous_price: Decimal
    current_price: Decimal
    previous_scraped_at: datetime
    current_scraped_at: datetime

    @property
    def change(self) -> Decimal:
        return self.current_price - self.previous_price

    @property
    def change_pct(self) -> Decimal:
        """Variacion porcentual respecto del precio anterior (0 si el anterior era 0)."""
        if self.previous_price == 0:
            return Decimal("0")
        return self.change / self.previous_price * 100


@dataclass(frozen=True)
class ScrapeRunRow:
    """Resumen de una corrida de scraping, con el nombre de la fuente resuelto."""

    id: int
    source_name: str
    started_at: datetime
    finished_at: datetime | None
    status: str
    products_found: int
    products_inserted: int
    products_updated: int
    snapshots_skipped: int
    errors_count: int


@dataclass(frozen=True)
class ScrapeErrorRow:
    """Un error de extraccion registrado durante una corrida."""

    id: int
    run_id: int
    error_type: str
    message: str
    url: str | None
    created_at: datetime


def count_products(session: Session) -> int:
    """Cantidad total de productos en el catalogo."""
    return session.scalar(select(func.count()).select_from(Product)) or 0


def count_snapshots(session: Session) -> int:
    """Cantidad total de snapshots historicos guardados."""
    return session.scalar(select(func.count()).select_from(ProductSnapshot)) or 0


def list_products(session: Session) -> list[ProductOption]:
    """Lista (id, nombre) de todos los productos, para selectores en el dashboard."""
    stmt = select(Product.id, Product.name).order_by(Product.name)
    return [ProductOption(id=product_id, name=name) for product_id, name in session.execute(stmt)]


def latest_snapshots(session: Session) -> list[LatestProductRow]:
    """Ultimo snapshot (precio, moneda, disponibilidad) de cada producto.

    Usa una subquery que calcula el `scraped_at` mas reciente por producto y
    la joinea contra `product_snapshots` para traer el snapshot completo. Es
    la base tanto de la tabla "Latest products" como de las metricas de
    precio promedio y disponibilidad actual, para no repetir la logica de
    "cual es el ultimo snapshot" en varios lugares.
    """
    latest_ids = (
        select(
            ProductSnapshot.product_id,
            func.max(ProductSnapshot.scraped_at).label("max_scraped_at"),
        )
        .group_by(ProductSnapshot.product_id)
        .subquery()
    )
    snapshot = aliased(ProductSnapshot)

    # La restriccion unica (product_id, scraped_at) garantiza una sola fila por producto.
    stmt = (
        select(Product, Source.name, snapshot)
        .join(Source, Source.id == Product.source_id)
        .join(latest_ids, latest_ids.c.product_id == Product.id)
        .join(
            snapshot,
            (snapshot.product_id == latest_ids.c.product_id)
            & (snapshot.scraped_at == latest_ids.c.max_scraped_at),
        )
        .order_by(Product.name)
    )

    return [
        LatestProductRow(
            product_id=product.id,
            source_name=source_name,
            name=product.name,
            brand=product.brand,
            product_url=product.product_url,
            price=snap.price,
            currency=snap.currency,
            availability=snap.availability,
            scraped_at=snap.scraped_at,
        )
        for product, source_name, snap in session.execute(stmt).all()
    ]


def average_current_price(session: Session) -> Decimal | None:
    """Precio promedio, tomando solo el ultimo snapshot de cada producto."""
    rows = latest_snapshots(session)
    if not rows:
        return None
    total = sum((row.price for row in rows), Decimal("0"))
    return total / len(rows)


def current_availability_breakdown(session: Session) -> dict[str, int]:
    """Cantidad de productos por estado de disponibilidad, segun el ultimo snapshot.

    Siempre incluye los tres estados (en 0 si no hay productos en alguno).
    """
    counts = {status.value: 0 for status in Availability}
    for row in latest_snapshots(session):
        counts[row.availability] += 1
    return counts


def price_history(session: Session, product_id: int) -> list[PricePoint]:
    """Serie historica de precio de un producto, ordenada de mas antigua a mas reciente."""
    stmt = (
        select(ProductSnapshot.scraped_at, ProductSnapshot.price)
        .where(ProductSnapshot.product_id == product_id)
        .order_by(ProductSnapshot.scraped_at)
    )
    return [
        PricePoint(scraped_at=scraped_at, price=price)
        for scraped_at, price in session.execute(stmt)
    ]


def price_changes(session: Session) -> list[PriceChangeRow]:
    """Productos cuyo precio cambio entre sus dos observaciones mas recientes.

    Numera los snapshots de cada producto del mas nuevo al mas viejo con una
    window function (`row_number() OVER (PARTITION BY product_id ORDER BY
    scraped_at DESC)`) y joinea la observacion 1 (actual) con la 2 (anterior).
    Productos con una sola observacion no aparecen. Ordena por mayor
    variacion porcentual absoluta.
    """
    ranked = select(
        ProductSnapshot.product_id,
        ProductSnapshot.price,
        ProductSnapshot.scraped_at,
        func.row_number()
        .over(partition_by=ProductSnapshot.product_id, order_by=ProductSnapshot.scraped_at.desc())
        .label("recency"),
    )
    current = ranked.subquery("current")
    previous = ranked.subquery("previous")

    stmt = (
        select(
            Product.id,
            Product.name,
            previous.c.price,
            current.c.price,
            previous.c.scraped_at,
            current.c.scraped_at,
        )
        .join(current, (current.c.product_id == Product.id) & (current.c.recency == 1))
        .join(previous, (previous.c.product_id == Product.id) & (previous.c.recency == 2))
        .where(current.c.price != previous.c.price)
    )

    rows = [
        PriceChangeRow(
            product_id=product_id,
            name=name,
            previous_price=previous_price,
            current_price=current_price,
            previous_scraped_at=previous_scraped_at,
            current_scraped_at=current_scraped_at,
        )
        for (
            product_id,
            name,
            previous_price,
            current_price,
            previous_scraped_at,
            current_scraped_at,
        ) in session.execute(stmt).all()
    ]
    return sorted(rows, key=lambda row: abs(row.change_pct), reverse=True)


def recent_scrape_runs(session: Session, limit: int = 10) -> list[ScrapeRunRow]:
    """Ultimas corridas de scraping, mas recientes primero."""
    stmt = (
        select(ScrapeRun, Source.name)
        .join(Source, Source.id == ScrapeRun.source_id)
        .order_by(ScrapeRun.started_at.desc())
        .limit(limit)
    )
    return [
        ScrapeRunRow(
            id=run.id,
            source_name=source_name,
            started_at=run.started_at,
            finished_at=run.finished_at,
            status=run.status,
            products_found=run.products_found,
            products_inserted=run.products_inserted,
            products_updated=run.products_updated,
            snapshots_skipped=run.snapshots_skipped,
            errors_count=run.errors_count,
        )
        for run, source_name in session.execute(stmt).all()
    ]


def recent_errors(session: Session, limit: int = 20) -> list[ScrapeErrorRow]:
    """Ultimos errores de extraccion registrados, mas recientes primero."""
    stmt = select(ScrapeError).order_by(ScrapeError.created_at.desc()).limit(limit)
    return [
        ScrapeErrorRow(
            id=error.id,
            run_id=error.run_id,
            error_type=error.error_type,
            message=error.message,
            url=error.url,
            created_at=error.created_at,
        )
        for error in session.scalars(stmt).all()
    ]
