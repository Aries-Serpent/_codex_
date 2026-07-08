from __future__ import annotations

import pytest

pytest.importorskip("parso")
"""
Test External Web Search

Test module for external web search.
"""

from codex_ml.analysis.providers import ExternalWebSearch


class _DummyResponse:
    def __init__(
        self,
        payload: dict[str, Any],
        *,
        content_type: str = "application/json",
        status_code: int = 200,
        raise_error: Exception | None = None,
    ) -> None:
        self._payload = payload
        self.headers = {"Content-Type": content_type}
        self.status_code = status_code
        self._raise_error = raise_error

    def json(self) -> dict[str, Any]:
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
    captured: dict[str, Any] = {}

    def fake_get(endpoint: str, params: dict[str, Any], timeout: float) -> _DummyResponse:
        captured["endpoint"] = endpoint
        captured["params"] = params
        captured["timeout"] = timeout
        return response

    provider = ExternalWebSearch(enabled=True, http_get=fake_get, timeout=3.5)
    outcome = provider.search("python")

    assert outcome["status"] == "ok", "Condition must be true"
    assert captured["endpoint"] == ExternalWebSearch.DEFAULT_ENDPOINT, "Condition must be true"
    assert outcome["results"], "Result must not be empty"


def test_external_search_reports_unavailable_without_endpoint() -> None:
    provider = ExternalWebSearch(endpoint="", enabled=True)
    outcome = provider.search("python")
    assert outcome["status"] == "unavailable", "Condition must be true"
    assert outcome["reason"] == "no-endpoint", "Condition must be true"


def test_external_search_captures_http_errors() -> None:
    def failing_get(*_args: Any, **_kwargs: Any) -> Any:
        raise RuntimeError("boom")

    provider = ExternalWebSearch(
        endpoint="https://search.example/api",
        enabled=True,
        http_get=failing_get,
    )

    outcome = provider.search("python")
    assert outcome["status"] == "error", "Error should be raised or set"
    assert "boom" in outcome["error"], "Error should be raised or set"


def test_external_search_handles_http_status_errors() -> None:
    payload: dict[str, Any] = {}
    response = _DummyResponse(payload, raise_error=RuntimeError("bad response"), status_code=503)

    def fake_get(*_args: Any, **_kwargs: Any) -> _DummyResponse:
        return response

    provider = ExternalWebSearch(
        endpoint="https://search.example/api",
        enabled=True,
        http_get=fake_get,
    )
    outcome = provider.search("python")
    assert outcome["status"] == "error", "Error should be raised or set"
    assert outcome["status_code"] == 503, "Condition must be true"
    assert "bad response" in outcome["error"], "Response must not be empty"


def test_external_search_success_normalises_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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

    def fake_get(endpoint: str, params: dict[str, Any], timeout: float) -> _DummyResponse:
        assert endpoint == "https://search.example/api", "endpoint is not valid"
        assert params["q"] == "python", "Condition must be true"
        assert params["format"] == "json", "Condition must be true"
        assert timeout == pytest.approx(2.5), "timeout is not valid"
        return response

    provider = ExternalWebSearch(
        endpoint="https://search.example/api",
        timeout=2.5,
        enabled=True,
        http_get=fake_get,
    )
    outcome = provider.search("python")

    assert outcome["status"] == "ok", "Condition must be true"
    titles = [item["title"] for item in outcome["results"]]
    assert "Python" in titles, "Condition must be true"
    assert "PyPI" in titles, "Condition must be true"
    assert all(item["provider"] == "external_web" for item in outcome["results"]), "Result must not be empty"


def test_external_search_supports_offline_index(tmp_path: Path) -> None:
    index = tmp_path / "index.json"
    index.write_text(
        json.dumps(
            {
                "python": [
                    {
                        "title": "Python",
                        "url": "https://example.com/python",
                        "snippet": "Lang",
                    }
                ],
                "other": [],
            }
        ),
        encoding="utf-8",
    )

    provider = ExternalWebSearch(endpoint=str(index), enabled=True)
    outcome = provider.search("python")

    assert outcome["status"] == "ok", "Condition must be true"
    assert outcome["results"][0]["title"] == "Python", "Result must not be empty"


def test_external_search_missing_offline_index(tmp_path: Path) -> None:
    provider = ExternalWebSearch(endpoint=str(tmp_path / "missing.json"), enabled=True)
    outcome = provider.search("python")
    assert outcome["status"] == "error", "Error should be raised or set"
    assert outcome["reason"] == "offline-missing", "Condition must be true"


def test_external_search_invalid_endpoint() -> None:
    provider = ExternalWebSearch(endpoint="ftp://example.com/index", enabled=True)
    outcome = provider.search("python")
    assert outcome["status"] == "unavailable", "Condition must be true"
    assert outcome["reason"] == "invalid-endpoint", "Condition must be true"
