from pathlib import Path

from retail_scraping_lab.core.exceptions import AcquisitionError


class LocalFileClient:
    """Cliente de acquisition sobre archivos locales (fixtures o capturas guardadas).

    Cumple el mismo contrato que `HttpClient` (`ContentClient`), de modo que el
    spider puede procesar una fuente local o una remota sin cambios.
    """

    def __init__(self, base_dir: Path) -> None:
        self._base_dir = base_dir

    def get(self, location: str) -> str:
        path = self._base_dir / location
        try:
            return path.read_text(encoding="utf-8")
        except OSError as exc:
            raise AcquisitionError(f"Error al leer {path}: {exc}") from exc
