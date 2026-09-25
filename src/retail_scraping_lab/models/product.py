from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl


class Availability(StrEnum):
    IN_STOCK = "in_stock"
    OUT_OF_STOCK = "out_of_stock"
    UNKNOWN = "unknown"


class Product(BaseModel):
    """Observacion normalizada y validada de un producto, lista para exportar o persistir.

    Es el contrato de datos entre la ingesta (parser + normalizador) y el resto
    del sistema. Ver docs/03_data_model.md para el esquema de persistencia (esta
    clase valida una observacion, no define tablas).
    """

    source: str = Field(min_length=1)
    captured_at: datetime
    name: str = Field(min_length=1)
    brand: str | None = None
    price: Decimal = Field(ge=0)
    currency: str = Field(min_length=3, max_length=3)
    availability: Availability
    product_url: HttpUrl
    image_url: HttpUrl | None = None
