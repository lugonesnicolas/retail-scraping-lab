class RetailScrapingLabError(Exception):
    """Excepcion base del dominio de retail-scraping-lab."""


class HttpClientError(RetailScrapingLabError):
    """Error al obtener contenido desde una fuente HTTP."""


class ParsingError(RetailScrapingLabError):
    """Error al extraer datos estructurados desde HTML."""


class ProductValidationError(RetailScrapingLabError):
    """Error al validar un producto parseado contra el esquema esperado."""
