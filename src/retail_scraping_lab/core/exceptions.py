class RetailScrapingLabError(Exception):
    """Excepcion base del dominio de retail-scraping-lab."""


class AcquisitionError(RetailScrapingLabError):
    """Error al obtener contenido crudo desde una fuente (red, archivo local, etc.)."""


class HttpClientError(AcquisitionError):
    """Error al obtener contenido desde una fuente HTTP."""


class ParsingError(RetailScrapingLabError):
    """Error al extraer datos estructurados desde HTML."""


class NormalizationError(RetailScrapingLabError):
    """Error al convertir un valor crudo (ej. un precio en texto) a un tipo del dominio."""


class ProductValidationError(RetailScrapingLabError):
    """Error al validar un producto parseado contra el esquema esperado."""
