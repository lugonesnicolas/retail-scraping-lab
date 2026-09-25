from pathlib import Path
from typing import Any

import pytest
import requests

from retail_scraping_lab.core.exceptions import AcquisitionError, HttpClientError
from retail_scraping_lab.scraping.clients.http_client import HttpClient
from retail_scraping_lab.scraping.clients.local_file_client import LocalFileClient


def test_local_file_client_reads_relative_location(tmp_path: Path) -> None:
    (tmp_path / "2026-09-01").mkdir()
    (tmp_path / "2026-09-01" / "catalog.html").write_text("<html>ok</html>", encoding="utf-8")

    content = LocalFileClient(tmp_path).get("2026-09-01/catalog.html")

    assert content == "<html>ok</html>"


def test_local_file_client_raises_acquisition_error_when_missing(tmp_path: Path) -> None:
    with pytest.raises(AcquisitionError):
        LocalFileClient(tmp_path).get("no-existe.html")


def _fake_response(status_code: int, body: str) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response._content = body.encode("utf-8")
    response.encoding = "utf-8"
    return response


def test_http_client_returns_body_and_sends_timeout_and_user_agent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict[str, Any]] = []

    def fake_get(self: requests.Session, url: str, **kwargs: Any) -> requests.Response:
        calls.append({"url": url, "user_agent": self.headers["User-Agent"], **kwargs})
        return _fake_response(200, "<html>catalogo</html>")

    monkeypatch.setattr(requests.Session, "get", fake_get)

    client = HttpClient(timeout_seconds=3.0, user_agent="test-agent")
    content = client.get("https://demo.test/catalog")

    assert content == "<html>catalogo</html>"
    assert calls == [
        {"url": "https://demo.test/catalog", "user_agent": "test-agent", "timeout": 3.0}
    ]


def test_http_client_translates_http_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(self: requests.Session, url: str, **kwargs: Any) -> requests.Response:
        return _fake_response(503, "caido")

    monkeypatch.setattr(requests.Session, "get", fake_get)

    with pytest.raises(HttpClientError):
        HttpClient().get("https://demo.test/catalog")


def test_http_client_translates_network_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(self: requests.Session, url: str, **kwargs: Any) -> requests.Response:
        raise requests.ConnectionError("sin red")

    monkeypatch.setattr(requests.Session, "get", fake_get)

    with pytest.raises(AcquisitionError):
        HttpClient().get("https://demo.test/catalog")
