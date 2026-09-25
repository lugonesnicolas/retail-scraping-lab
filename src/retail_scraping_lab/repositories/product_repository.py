"""Repositorio de productos: unica capa que hace queries sobre la base.

No parsea ni valida datos (eso ocurre en scraping/parsers y models/product.py);
recibe una `Session` ya creada e inserta/actualiza entidades de
models/database.py. Ver docs/03_data_model.md para el diseno del modelo.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from retail_scraping_lab.models.database import (
    Product,
    ProductSnapshot,
    ScrapeError,
    ScrapeRun,
    Source,
)
from retail_scraping_lab.models.product import Availability
from retail_scraping_lab.models.product import Product as ScrapedProduct


@dataclass(frozen=True)
class SaveResult:
    """Resumen de guardar una captura: productos nuevos/existentes y snapshots omitidos."""

    inserted: int
    updated: int
    skipped: int


def _normalize_name(name: str) -> str:
    """Normaliza un nombre de producto para comparaciones simples (sin acentos ni casing)."""
    return " ".join(name.strip().lower().split())


class ProductRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_or_create_source(
        self, name: str, base_url: str, source_type: str = "fixture"
    ) -> Source:
        source = self._session.scalar(select(Source).where(Source.name == name))
        if source is not None:
            return source

        source = Source(name=name, base_url=base_url, source_type=source_type)
        self._session.add(source)
        self._session.flush()
        return source

    def get_or_create_product(
        self,
        source_id: int,
        product_url: str,
        name: str,
        category_id: int | None = None,
        external_id: str | None = None,
        brand: str | None = None,
        image_url: str | None = None,
    ) -> tuple[Product, bool]:
        """Devuelve (producto, fue_creado). Evita duplicados por source_id + product_url."""
        product = self._session.scalar(
            select(Product).where(
                Product.source_id == source_id, Product.product_url == product_url
            )
        )
        if product is not None:
            # El catalogo guarda el ultimo valor observado; el historico vive en los snapshots.
            product.name = name
            product.normalized_name = _normalize_name(name)
            product.brand = brand
            product.image_url = image_url
            return product, False

        product = Product(
            source_id=source_id,
            category_id=category_id,
            external_id=external_id,
            name=name,
            brand=brand,
            normalized_name=_normalize_name(name),
            product_url=product_url,
            image_url=image_url,
        )
        self._session.add(product)
        self._session.flush()
        return product, True

    def create_product_snapshot(
        self,
        product_id: int,
        price: Decimal,
        currency: str,
        availability: Availability,
        list_price: Decimal | None = None,
        discount_percentage: Decimal | None = None,
        raw_hash: str | None = None,
        scraped_at: datetime | None = None,
    ) -> ProductSnapshot:
        snapshot = ProductSnapshot(
            product_id=product_id,
            scraped_at=scraped_at or datetime.now(UTC),
            price=price,
            list_price=list_price,
            discount_percentage=discount_percentage,
            currency=currency,
            availability=availability.value,
            raw_hash=raw_hash,
        )
        self._session.add(snapshot)
        self._session.flush()
        return snapshot

    def snapshot_exists(self, product_id: int, scraped_at: datetime) -> bool:
        return bool(
            self._session.scalar(
                select(
                    exists().where(
                        ProductSnapshot.product_id == product_id,
                        ProductSnapshot.scraped_at == scraped_at,
                    )
                )
            )
        )

    def create_scrape_run(self, source_id: int) -> ScrapeRun:
        run = ScrapeRun(source_id=source_id, status="running")
        self._session.add(run)
        self._session.flush()
        return run

    def finish_scrape_run(
        self,
        run_id: int,
        status: str,
        products_found: int = 0,
        products_inserted: int = 0,
        products_updated: int = 0,
        snapshots_skipped: int = 0,
        errors_count: int = 0,
    ) -> ScrapeRun:
        run = self._session.get(ScrapeRun, run_id)
        if run is None:
            raise ValueError(f"ScrapeRun {run_id} no existe")

        run.finished_at = datetime.now(UTC)
        run.status = status
        run.products_found = products_found
        run.products_inserted = products_inserted
        run.products_updated = products_updated
        run.snapshots_skipped = snapshots_skipped
        run.errors_count = errors_count
        self._session.flush()
        return run

    def create_scrape_error(
        self, run_id: int, error_type: str, message: str, url: str | None = None
    ) -> ScrapeError:
        error = ScrapeError(run_id=run_id, url=url, error_type=error_type, message=message)
        self._session.add(error)
        self._session.flush()
        return error

    def save_scraped_products(
        self, source_id: int, products: Iterable[ScrapedProduct]
    ) -> SaveResult:
        """Guarda observaciones validadas (Pydantic) como Product + ProductSnapshot.

        El snapshot se fecha con `captured_at` (cuando se observo el dato). Si ya
        existe un snapshot de ese producto en esa fecha, se omite: reprocesar una
        captura no duplica el historico.
        """
        inserted = updated = skipped = 0
        for scraped in products:
            product, created = self.get_or_create_product(
                source_id=source_id,
                product_url=str(scraped.product_url),
                name=scraped.name,
                brand=scraped.brand,
                image_url=str(scraped.image_url) if scraped.image_url else None,
            )
            inserted += int(created)
            updated += int(not created)

            if self.snapshot_exists(product.id, scraped.captured_at):
                skipped += 1
                continue

            self.create_product_snapshot(
                product_id=product.id,
                price=scraped.price,
                currency=scraped.currency,
                availability=scraped.availability,
                scraped_at=scraped.captured_at,
            )

        return SaveResult(inserted=inserted, updated=updated, skipped=skipped)
