from typing import Protocol


class ContentClient(Protocol):
    """Contrato de la capa de acquisition: obtener contenido crudo desde una ubicacion.

    `location` es una URL para `HttpClient` o una ruta relativa para
    `LocalFileClient`. Es un Protocol (tipado estructural): cualquier clase con
    este metodo lo cumple sin heredar, y el spider no necesita saber de donde
    viene el contenido. Las fallas se reportan como `AcquisitionError`.
    """

    def get(self, location: str, /) -> str: ...
