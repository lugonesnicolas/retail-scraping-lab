import requests

from retail_scraping_lab.core.exceptions import HttpClientError


class HttpClient:
    """Cliente HTTP delgado sobre requests.

    Responsabilidad unica: obtener contenido crudo desde una URL. No parsea HTML
    (ver scraping/parsers/) ni conoce el dominio de "producto".
    """

    def __init__(
        self, timeout_seconds: float = 10.0, user_agent: str = "retail-scraping-lab"
    ) -> None:
        self._timeout_seconds = timeout_seconds
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": user_agent})

    def get(self, url: str) -> str:
        try:
            response = self._session.get(url, timeout=self._timeout_seconds)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise HttpClientError(f"Error al obtener {url}: {exc}") from exc
        return response.text
