from lxml import html

from retail_scraping_lab.core.exceptions import ParsingError

_NAME_XPATH = "//h1[@class='product-name']/text()"
_PRICE_XPATH = "//span[@class='price-amount']/text()"
_CURRENCY_XPATH = "//span[@class='price-currency']/text()"
_AVAILABILITY_XPATH = "//p[@class='product-availability']/@data-status"
_PRODUCT_URL_XPATH = "//a[@class='product-link']/@href"
_IMAGE_URL_XPATH = "//img[@class='product-image']/@src"


def _first_or_none(values: list[str]) -> str | None:
    return values[0].strip() if values else None


def parse_product(html_content: str) -> dict[str, str | None]:
    """Extrae los campos crudos de un producto desde HTML usando XPath (lxml).

    Devuelve un dict con valores en bruto (strings); la validacion y el tipado
    final ocurren en models.product.Product.
    """
    tree = html.fromstring(html_content)

    name = _first_or_none(tree.xpath(_NAME_XPATH))
    price = _first_or_none(tree.xpath(_PRICE_XPATH))
    currency = _first_or_none(tree.xpath(_CURRENCY_XPATH))
    availability = _first_or_none(tree.xpath(_AVAILABILITY_XPATH))
    product_url = _first_or_none(tree.xpath(_PRODUCT_URL_XPATH))
    image_url = _first_or_none(tree.xpath(_IMAGE_URL_XPATH))

    if not all([name, price, currency, availability, product_url]):
        raise ParsingError("No se pudieron extraer todos los campos obligatorios del producto")

    return {
        "name": name,
        "price": price,
        "currency": currency,
        "availability": availability,
        "product_url": product_url,
        "image_url": image_url,
    }
