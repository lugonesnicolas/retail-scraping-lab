"""Normalizacion: de texto crudo del parser a valores del dominio.

Funciones puras, sin I/O. Se ubican entre el parser (que solo extrae texto) y
la validacion Pydantic (que verifica el contrato final), para que ninguno de
los dos tenga que conocer el formato particular de la fuente.
"""

import re
from datetime import datetime
from decimal import Decimal

from retail_scraping_lab.core.exceptions import NormalizationError
from retail_scraping_lab.models.product import Availability
from retail_scraping_lab.scraping.parsers.product_parser import RawProduct

_AVAILABILITY_BY_TEXT = {
    "en stock": Availability.IN_STOCK,
    "disponible": Availability.IN_STOCK,
    "sin stock": Availability.OUT_OF_STOCK,
    "agotado": Availability.OUT_OF_STOCK,
}

_PRICE_PATTERN = re.compile(r"^\d{1,3}(\.\d{3})*(,\d+)?$|^\d+(,\d+)?$")


def clean_text(value: str | None) -> str | None:
    """Colapsa espacios internos y bordes; un texto vacio pasa a ser None."""
    if value is None:
        return None
    cleaned = " ".join(value.split())
    return cleaned or None


def parse_price(value: str | None) -> Decimal | None:
    """Convierte un precio en formato es-AR ("$ 45.999,90") a Decimal.

    El formato es explicito y no se adivina: "." separa miles y "," decimales,
    como publica la fuente demo. Una fuente con otro formato necesita su propio
    normalizador. None se devuelve tal cual (campo ausente, lo decide Pydantic).
    """
    if value is None:
        return None
    amount = value.replace("$", "").strip()
    if not _PRICE_PATTERN.match(amount):
        raise NormalizationError(f"Precio con formato no reconocido: {value!r}")
    return Decimal(amount.replace(".", "").replace(",", "."))


def normalize_availability(value: str | None) -> Availability:
    """Mapea el texto de disponibilidad de la fuente; lo desconocido es UNKNOWN."""
    text = clean_text(value)
    if text is None:
        return Availability.UNKNOWN
    return _AVAILABILITY_BY_TEXT.get(text.lower(), Availability.UNKNOWN)


def normalize_product(raw: RawProduct, *, source: str, captured_at: datetime) -> dict[str, object]:
    """Arma el payload normalizado de un producto, listo para validar con Pydantic."""
    currency = clean_text(raw.get("currency"))
    return {
        "source": source,
        "captured_at": captured_at,
        "name": clean_text(raw.get("name")),
        "brand": clean_text(raw.get("brand")),
        "price": parse_price(raw.get("price")),
        "currency": currency.upper() if currency else None,
        "availability": normalize_availability(raw.get("availability")),
        "product_url": clean_text(raw.get("product_url")),
        "image_url": clean_text(raw.get("image_url")),
    }
