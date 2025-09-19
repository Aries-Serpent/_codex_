from __future__ import annotations

from typing import Any, Dict

import pytest

from codex_ml.analysis.providers import ExternalWebSearch


class _DummyResponse:
    def __init__(self, payload: Dict[str, Any], *, content_type: str = "application/json") -> None:
        self._payload = payload
        self.headers = {"Content-Type": content_type}
        self.status_code = 200

    def json(self) -> Dict[str, Any]:
        return self._payload

    def raise_for_status(self) -> None:  # pragma: no cover - trivial
        return None

    @property
    def text(self) -> str:  # pragma: no cover - fallback path
        return ""


def test_external_search_reports_unavailable_without_endpoint(monkeypatch) -> None:
    monkeypatch.setenv("CODEX_ANALYSIS_SEARCH_ENABLED", "1")
    provider = ExternalWebSearch()
    outcome = provider.search("python")
    assert outcome["status"] == "unavailable"
    assert outcome["reason"] == "no-endpoint"


def test_external_search_success_normalises_payload(monkeypatch) -> None:
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
        assert params == {"q": "python"}
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
