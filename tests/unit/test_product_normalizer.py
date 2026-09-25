from datetime import UTC, datetime
from decimal import Decimal

import pytest

from retail_scraping_lab.core.exceptions import NormalizationError
from retail_scraping_lab.models.product import Availability
from retail_scraping_lab.scraping.normalizers.product_normalizer import (
    clean_text,
    normalize_availability,
    normalize_product,
    parse_price,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("$ 45.999,90", Decimal("45999.90")),
        ("$189.999,00", Decimal("189999.00")),
        ("  $ 9.899,00 ", Decimal("9899.00")),
        ("850", Decimal("850")),
        ("850,5", Decimal("850.5")),
        (None, None),
    ],
)
def test_parse_price_es_ar_format(raw: str | None, expected: Decimal | None) -> None:
    assert parse_price(raw) == expected


@pytest.mark.parametrize("raw", ["Consultar precio", "", "$", "45.99.90", "1,234.56", "-10"])
def test_parse_price_rejects_unrecognized_formats(raw: str) -> None:
    with pytest.raises(NormalizationError):
        parse_price(raw)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("En stock", Availability.IN_STOCK),
        ("  DISPONIBLE ", Availability.IN_STOCK),
        ("Sin stock", Availability.OUT_OF_STOCK),
        ("Agotado", Availability.OUT_OF_STOCK),
        ("Consultar disponibilidad", Availability.UNKNOWN),
        (None, Availability.UNKNOWN),
    ],
)
def test_normalize_availability(raw: str | None, expected: Availability) -> None:
    assert normalize_availability(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("  Remera   Dry\nFit ", "Remera Dry Fit"), ("   ", None), (None, None)],
)
def test_clean_text(raw: str | None, expected: str | None) -> None:
    assert clean_text(raw) == expected


def test_normalize_product_builds_payload_for_validation() -> None:
    captured_at = datetime(2026, 9, 1, tzinfo=UTC)
    raw = {
        "name": " Remera  Dry Fit ",
        "brand": None,
        "price": "$ 12.999,00",
        "currency": "ars",
        "availability": "Sin stock",
        "product_url": "https://demo-store.example.com/products/remera-dry-fit",
        "image_url": None,
    }

    payload = normalize_product(raw, source="demo-store", captured_at=captured_at)

    assert payload == {
        "source": "demo-store",
        "captured_at": captured_at,
        "name": "Remera Dry Fit",
        "brand": None,
        "price": Decimal("12999.00"),
        "currency": "ARS",
        "availability": Availability.OUT_OF_STOCK,
        "product_url": "https://demo-store.example.com/products/remera-dry-fit",
        "image_url": None,
    }
