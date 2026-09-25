"""Spider de la fuente demo "demo-store": un catalogo local con capturas fechadas.

Cada captura es un directorio `<YYYY-MM-DD>/catalog.html` dentro del catalogo
(ver tests/fixtures/demo_store/). El spider combina las capas de ingesta:

    acquisition (ContentClient) -> parsing -> normalization -> validation (Pydantic)

y procesa cada producto de forma independiente: un item invalido se reporta
como `ItemError` sin descartar el resto de la captura.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from pydantic import ValidationError

from retail_scraping_lab.core.exceptions import NormalizationError
from retail_scraping_lab.models.product import Product
from retail_scraping_lab.scraping.clients.base import ContentClient
from retail_scraping_lab.scraping.normalizers.product_normalizer import normalize_product
from retail_scraping_lab.scraping.parsers.product_parser import parse_catalog

SOURCE_NAME = "demo-store"
CATALOG_FILENAME = "catalog.html"
_CAPTURE_DATE_FORMAT = "%Y-%m-%d"


@dataclass(frozen=True)
class DemoCapture:
    """Una captura del catalogo: cuando se observo y donde esta su contenido."""

    captured_at: datetime
    location: str


@dataclass(frozen=True)
class ItemError:
    """Un producto que no pudo normalizarse o validarse."""

    error_type: str
    message: str
    url: str | None


@dataclass(frozen=True)
class SpiderResult:
    products: list[Product]
    errors: list[ItemError]


def list_demo_captures(catalog_dir: Path) -> list[DemoCapture]:
    """Capturas disponibles en `catalog_dir`, de la mas antigua a la mas reciente.

    Solo cuentan los directorios cuyo nombre es una fecha valida y que contienen
    un `catalog.html`; cualquier otro archivo o carpeta se ignora.
    """
    captures = []
    for entry in catalog_dir.iterdir():
        if not (entry / CATALOG_FILENAME).is_file():
            continue
        try:
            captured_on = datetime.strptime(entry.name, _CAPTURE_DATE_FORMAT)
        except ValueError:
            continue
        captures.append(
            DemoCapture(
                captured_at=captured_on.replace(tzinfo=UTC),
                location=f"{entry.name}/{CATALOG_FILENAME}",
            )
        )
    return sorted(captures, key=lambda capture: capture.captured_at)


def _format_validation_error(exc: ValidationError) -> str:
    return "; ".join(
        f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}" for error in exc.errors()
    )


def run_demo_spider(client: ContentClient, capture: DemoCapture) -> SpiderResult:
    """Obtiene, parsea, normaliza y valida todos los productos de una captura.

    Errores de acquisition o de estructura de pagina (`AcquisitionError`,
    `ParsingError`) se propagan: sin pagina no hay nada que procesar. Errores de
    un producto individual se acumulan en `SpiderResult.errors`.
    """
    html_content = client.get(capture.location)
    raw_products = parse_catalog(html_content)

    products: list[Product] = []
    errors: list[ItemError] = []
    for raw in raw_products:
        url = raw.get("product_url")
        try:
            payload = normalize_product(raw, source=SOURCE_NAME, captured_at=capture.captured_at)
            products.append(Product.model_validate(payload))
        except NormalizationError as exc:
            errors.append(ItemError(error_type=type(exc).__name__, message=str(exc), url=url))
        except ValidationError as exc:
            errors.append(
                ItemError(
                    error_type="ProductValidationError",
                    message=_format_validation_error(exc),
                    url=url,
                )
            )

    return SpiderResult(products=products, errors=errors)
