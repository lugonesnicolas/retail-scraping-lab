from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl


class Availability(StrEnum):
    IN_STOCK = "in_stock"
    OUT_OF_STOCK = "out_of_stock"
    UNKNOWN = "unknown"


class Product(BaseModel):
    """Producto parseado y validado, listo para exportar o persistir.

    Ver docs/03_data_model.md para el modelo de datos completo (esta clase valida
    un snapshot de producto, no el esquema de persistencia).
    """

    name: str = Field(min_length=1)
    price: Decimal = Field(ge=0)
    currency: str = Field(min_length=3, max_length=3)
    availability: Availability
    product_url: HttpUrl
    image_url: HttpUrl | None = None
