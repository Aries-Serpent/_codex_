from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pytest

from codex_ml.analysis.providers import ExternalWebSearch


class _DummyResponse:
    def __init__(
        self,
        payload: Dict[str, Any],
        *,
        content_type: str = "application/json",
        status_code: int = 200,
        raise_error: Exception | None = None,
    ) -> None:
        self._payload = payload
        self.headers = {"Content-Type": content_type}
        self.status_code = status_code
        self._raise_error = raise_error

    def json(self) -> Dict[str, Any]:
        return self._payload

    def raise_for_status(self) -> None:
        if self._raise_error:
            raise self._raise_error

    @property
    def text(self) -> str:  # pragma: no cover - fallback path
        return json.dumps(self._payload)


def test_external_search_uses_default_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CODEX_ANALYSIS_SEARCH_ENABLED", raising=False)
    monkeypatch.delenv("CODEX_ANALYSIS_SEARCH_ENDPOINT", raising=False)
    monkeypatch.delenv("CODEX_ANALYSIS_SEARCH_TIMEOUT", raising=False)

    payload = {
        "RelatedTopics": [
            {"Text": "Python", "FirstURL": "https://example.com/python"},
        ]
    }
    response = _DummyResponse(payload)
    captured: Dict[str, Any] = {}

    def fake_get(endpoint: str, params: Dict[str, Any], timeout: float) -> _DummyResponse:
        captured["endpoint"] = endpoint
        captured["params"] = params
        captured["timeout"] = timeout
        return response

    provider = ExternalWebSearch(enabled=True, http_get=fake_get, timeout=3.5)
    outcome = provider.search("python")

    assert outcome["status"] == "ok"
    assert captured["endpoint"] == ExternalWebSearch.DEFAULT_ENDPOINT
    assert captured["params"] == {
        "format": "json",
        "no_html": 1,
        "no_redirect": 1,
        "q": "python",
    }
    assert captured["timeout"] == pytest.approx(3.5)
    assert outcome["results"]


def test_external_search_reports_unavailable_without_endpoint() -> None:
    provider = ExternalWebSearch(endpoint="", enabled=True)
    outcome = provider.search("python")
    assert outcome["status"] == "unavailable"
    assert outcome["reason"] == "no-endpoint"


def test_external_search_captures_http_errors() -> None:
    def failing_get(*_args: Any, **_kwargs: Any) -> Any:
        raise RuntimeError("boom")

    provider = ExternalWebSearch(
        endpoint="https://search.example/api",
        enabled=True,
        http_get=failing_get,
    )

    outcome = provider.search("python")
    assert outcome["status"] == "error"
    assert "boom" in outcome["error"]


def test_external_search_handles_http_status_errors() -> None:
    payload: Dict[str, Any] = {}
    response = _DummyResponse(payload, raise_error=RuntimeError("bad response"), status_code=503)

    def fake_get(*_args: Any, **_kwargs: Any) -> _DummyResponse:
        return response

    provider = ExternalWebSearch(
        endpoint="https://search.example/api",
        enabled=True,
        http_get=fake_get,
    )
    outcome = provider.search("python")
    assert outcome["status"] == "error"
    assert outcome["status_code"] == 503
    assert "bad response" in outcome["error"]


def test_external_search_success_normalises_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CODEX_ANALYSIS_SEARCH_ENABLED", "1")

    payload = {
        "RelatedTopics": [
            {"Text": "Python", "FirstURL": "https://example.com/python"},
            {
                "Topics": [
                    {"Text": "PyPI", "FirstURL": "https://pypi.org"},
                ]
            },
        ]
    }

    response = _DummyResponse(payload)

    def fake_get(endpoint: str, params: Dict[str, Any], timeout: float) -> _DummyResponse:
        assert endpoint == "https://search.example/api"
        assert params["q"] == "python"
        assert params["format"] == "json"
        assert timeout == pytest.approx(2.5)
        return response

    provider = ExternalWebSearch(
        endpoint="https://search.example/api",
        timeout=2.5,
        enabled=True,
        http_get=fake_get,
    )
    outcome = provider.search("python")

    assert outcome["status"] == "ok"
    titles = [item["title"] for item in outcome["results"]]
    assert "Python" in titles
    assert "PyPI" in titles
    assert all(item["provider"] == "external_web" for item in outcome["results"])


def test_external_search_supports_offline_index(tmp_path: Path) -> None:
    index = tmp_path / "index.json"
    index.write_text(
        json.dumps(
            {
                "python": [
                    {"title": "Python", "url": "https://example.com/python", "snippet": "Lang"}
                ],
                "other": [],
            }
        ),
        encoding="utf-8",
    )

    provider = ExternalWebSearch(endpoint=str(index), enabled=True)
    outcome = provider.search("python")

    assert outcome["status"] == "ok"
    assert outcome["results"][0]["title"] == "Python"


def test_external_search_missing_offline_index(tmp_path: Path) -> None:
    provider = ExternalWebSearch(endpoint=str(tmp_path / "missing.json"), enabled=True)
    outcome = provider.search("python")
    assert outcome["status"] == "error"
    assert outcome["reason"] == "offline-missing"


def test_external_search_invalid_endpoint() -> None:
    provider = ExternalWebSearch(endpoint="ftp://example.com/index", enabled=True)
    outcome = provider.search("python")
    assert outcome["status"] == "unavailable"
    assert outcome["reason"] == "invalid-endpoint"
