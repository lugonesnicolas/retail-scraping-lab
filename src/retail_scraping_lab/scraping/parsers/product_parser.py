from lxml import html

from retail_scraping_lab.core.exceptions import ParsingError

RawProduct = dict[str, str | None]
"""Campos crudos de una card de producto, tal como aparecen en el HTML (o None)."""

_CARD_XPATH = "//article[@class='product-card']"

# XPath relativos a cada card (empiezan con "."), para no mezclar campos entre productos.
_FIELD_XPATHS = {
    "name": ".//h2[@class='product-name']/text()",
    "brand": ".//span[@class='product-brand']/text()",
    "price": ".//span[@class='price-amount']/text()",
    "currency": ".//span[@class='price-currency']/text()",
    "availability": ".//p[@class='product-availability']/text()",
    "product_url": ".//a[@class='product-link']/@href",
    "image_url": ".//img[@class='product-image']/@src",
}


def _first_or_none(values: list[str]) -> str | None:
    return values[0] if values else None


def parse_catalog(html_content: str) -> list[RawProduct]:
    """Extrae los campos crudos de cada card de producto de un catalogo (lxml + XPath).

    No valida ni convierte tipos: un campo faltante queda en None y la decision
    de si es obligatorio se toma mas adelante (normalizacion + Pydantic). Solo
    falla si la pagina no tiene ninguna card, senal de que cambio la estructura.
    """
    tree = html.fromstring(html_content)
    cards = tree.xpath(_CARD_XPATH)
    if not cards:
        raise ParsingError("No se encontraron cards de producto en el catalogo")

    return [
        {field: _first_or_none(card.xpath(xpath)) for field, xpath in _FIELD_XPATHS.items()}
        for card in cards
    ]
