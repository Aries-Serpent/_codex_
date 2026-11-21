"""Tests for the shared quota-aware GitHub REST transport."""

from __future__ import annotations

import io
import json
import time
import urllib.error
from email.message import Message
from typing import Any

import pytest

from scripts.ci import _gh_api
from scripts.ci import github_api_trickle as trickle
from scripts.ci import github_rate_limit as rate_limit


class Response:
    def __init__(self, status: int, payload: Any, headers: dict[str, str] | None = None) -> None:
        self.status = status
        self.headers = headers or {}
        if isinstance(payload, bytes):
            self._raw = payload
        elif isinstance(payload, str):
            self._raw = payload.encode("utf-8")
        else:
            self._raw = json.dumps(payload).encode("utf-8")

    def __enter__(self) -> "Response":
        return self

    def __exit__(self, *_args: Any) -> None:
        return None

    def read(self, size: int = -1) -> bytes:
        return self._raw if size < 0 else self._raw[:size]


def http_error(status: int, payload: Any, headers: dict[str, str] | None = None):
    message = Message()
    for name, value in (headers or {}).items():
        message[name] = value
    raw = json.dumps(payload).encode("utf-8")
    return urllib.error.HTTPError(
        "https://api.github.com/resource",
        status,
        "error",
        message,
        io.BytesIO(raw),
    )


@pytest.fixture(autouse=True)
def reset_tracker(monkeypatch: pytest.MonkeyPatch):
    tracker = rate_limit._QuotaTracker()
    monkeypatch.setattr(rate_limit, "_TRACKER", tracker)
    return tracker


def test_discovery_deduplicates_token_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CODEX_MASTER_KEY", "same")
    monkeypatch.setenv("CODEX_BACKUP_KEY", "different")
    monkeypatch.setenv("GH_TOKEN", "same")

    credentials = rate_limit.discover_credentials(
        sources=("CODEX_MASTER_KEY", "CODEX_BACKUP_KEY", "GH_TOKEN")
    )

    assert [item.source for item in credentials] == ["CODEX_MASTER_KEY", "CODEX_BACKUP_KEY"]
    assert "same" not in repr(credentials)


def test_429_rotates_to_distinct_credential_without_sleep() -> None:
    credentials = [
        rate_limit.Credential("primary", "one"),
        rate_limit.Credential("backup", "two"),
    ]
    calls: list[str] = []

    def opener(request: Any, timeout: int) -> Response:
        calls.append(request.get_header("Authorization"))
        if len(calls) == 1:
            raise http_error(429, {"message": "secondary rate limit"}, {"Retry-After": "1"})
        return Response(200, {"ok": True}, {"X-RateLimit-Remaining": "4999"})

    response = rate_limit.request(
        "GET",
        "https://api.github.com/rate_limit",
        credentials=credentials,
        opener=opener,
        sleep=lambda _seconds: pytest.fail("rotation should avoid sleeping"),
    )

    assert response.status == 200
    assert response.source == "backup"
    assert response.attempts == 2
    assert calls == ["Bearer one", "Bearer two"]


def test_permission_403_is_returned_without_retry() -> None:
    calls = 0

    def opener(request: Any, timeout: int) -> Response:
        nonlocal calls
        calls += 1
        raise http_error(403, {"message": "Resource not accessible by integration"})

    response = rate_limit.request(
        "GET",
        "https://api.github.com/repos/o/r",
        token="credential",
        opener=opener,
        sleep=lambda _seconds: pytest.fail("permission 403 must not be retried"),
    )

    assert response.status == 403
    assert calls == 1


def test_single_credential_honors_bounded_retry_after() -> None:
    sleeps: list[float] = []
    calls = 0

    def opener(request: Any, timeout: int) -> Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise http_error(429, {"message": "rate limit"}, {"Retry-After": "2"})
        return Response(200, {"ok": True})

    response = rate_limit.request(
        "GET",
        "https://api.github.com/user",
        token="credential",
        opener=opener,
        sleep=sleeps.append,
        now=lambda: 100.0,
    )

    assert response.status == 200
    assert response.attempts == 2
    assert sleeps == [3.0]


def test_post_network_failure_is_not_retried() -> None:
    calls = 0

    def opener(request: Any, timeout: int) -> Response:
        nonlocal calls
        calls += 1
        raise OSError("connection reset")

    with pytest.raises(OSError, match="connection reset"):
        rate_limit.request(
            "POST",
            "https://api.github.com/repos/o/r/issues",
            token="credential",
            body={"title": "one"},
            opener=opener,
            sleep=lambda _seconds: pytest.fail("POST ambiguity must not be retried"),
        )

    assert calls == 1


def test_deferred_credential_exceeding_wait_budget_fails_without_request() -> None:
    credential = rate_limit.Credential("primary", "credential")
    rate_limit._TRACKER.defer(credential, time.time() + 3_600)

    with pytest.raises(rate_limit.GitHubRateLimitError):
        rate_limit.request(
            "GET",
            "https://api.github.com/user",
            credentials=[credential],
            max_wait_seconds=30,
            opener=lambda *args, **kwargs: pytest.fail("must not issue a request"),
        )


def test_successful_get_cache_avoids_duplicate_request(tmp_path: Any) -> None:
    calls = 0

    def opener(request: Any, timeout: int) -> Response:
        nonlocal calls
        calls += 1
        return Response(200, {"items": [1]}, {"X-RateLimit-Remaining": "4999"})

    first = rate_limit.request(
        "GET",
        "https://api.github.com/repos/o/r/issues",
        token="credential",
        cache_dir=tmp_path,
        opener=opener,
    )
    second = rate_limit.request(
        "GET",
        "https://api.github.com/repos/o/r/issues",
        token="credential",
        cache_dir=tmp_path,
        opener=lambda *args, **kwargs: pytest.fail("cache must avoid a request"),
    )

    assert calls == 1
    assert first.payload == second.payload == {"items": [1]}
    assert second.cached is True


def test_rotated_response_cache_is_bound_to_backup_credential(tmp_path: Any) -> None:
    credentials = [
        rate_limit.Credential("primary", "one"),
        rate_limit.Credential("backup", "two"),
    ]
    calls: list[str] = []

    def opener(request: Any, timeout: int) -> Response:
        calls.append(request.get_header("Authorization"))
        if len(calls) == 1:
            raise http_error(429, {"message": "rate limit"}, {"Retry-After": "1"})
        return Response(200, {"from": "backup"})

    first = rate_limit.request(
        "GET",
        "https://api.github.com/repos/o/r",
        credentials=credentials,
        cache_dir=tmp_path,
        opener=opener,
        sleep=lambda _seconds: None,
    )
    cached = rate_limit.request(
        "GET",
        "https://api.github.com/repos/o/r",
        credentials=credentials,
        cache_dir=tmp_path,
        opener=lambda *args, **kwargs: pytest.fail("primary cache must not contain backup data"),
    )

    assert first.source == "backup"
    assert cached.source == "backup"
    assert cached.cached is True
    assert calls == ["Bearer one", "Bearer two"]


def test_legacy_api_cache_keys_are_credential_scoped() -> None:
    url = "https://api.github.com/repos/o/r/issues"

    assert _gh_api._cache_key(url, "credential-one") != _gh_api._cache_key(url, "credential-two")
    assert "credential-one" not in _gh_api._cache_key(url, "credential-one")


def test_shared_gh_api_preserves_public_get_contract(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, Any]] = []

    def request(method: str, url: str, **kwargs: Any) -> rate_limit.GitHubResponse:
        calls.append({"method": method, "url": url, **kwargs})
        return rate_limit.GitHubResponse(200, {"ok": True}, {"header": "value"}, "backup", 1)

    monkeypatch.setattr(_gh_api.gh_rate_limit, "request", request)
    payload, headers = _gh_api.api_get(
        "https://api.github.com/repos/o/r",
        "primary",
        page_sleep=0,
        min_remaining=50,
    )

    assert payload == {"ok": True}
    assert headers == {"header": "value"}
    assert calls[0]["method"] == "GET"
    assert calls[0]["min_remaining"] == 50
    assert [credential.token for credential in calls[0]["credentials"]] == ["primary"]


def test_shared_gh_api_preserves_unprocessable_post_behavior(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        _gh_api.gh_rate_limit,
        "request",
        lambda *args, **kwargs: rate_limit.GitHubResponse(
            422, {"message": "unsupported"}, {}, "primary", 1
        ),
    )

    payload, headers = _gh_api.api_post(
        "https://api.github.com/repos/o/r/autofixes",
        "primary",
        {"rule": "fixture"},
        inter_call_sleep=0,
    )

    assert payload == {"error": "unsupported", "status": 422}
    assert headers == {}


def test_trickle_rest_and_graphql_do_not_burn_preflight_quota(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, str, Any]] = []

    def request(method: str, url: str, **kwargs: Any) -> rate_limit.GitHubResponse:
        calls.append((method, url, kwargs.get("body")))
        payload = {"data": {"ok": True}} if url.endswith("/graphql") else {"ok": True}
        return rate_limit.GitHubResponse(200, payload, {}, "backup", len(calls))

    monkeypatch.setattr(trickle, "request", request)

    rest, rest_error = trickle.rest_get("/repos/o/r", tokens=["primary", "backup"])
    graphql, graphql_error = trickle.graphql("query { viewer { login } }", tokens=["primary"])

    assert rest_error is None and rest == {"ok": True}
    assert graphql_error is None and graphql == {"ok": True}
    assert [call[1] for call in calls] == [
        "https://api.github.com/repos/o/r",
        "https://api.github.com/graphql",
    ]
    assert all("/rate_limit" not in url for _method, url, _body in calls)


def test_quota_status_never_contains_token_value() -> None:
    credential = rate_limit.Credential("primary", "super-private-token")
    rate_limit._TRACKER.observe(
        credential,
        {"X-RateLimit-Remaining": "4", "X-RateLimit-Reset": "123"},
    )

    serialized = json.dumps(rate_limit.quota_status([credential]))

    assert "super-private-token" not in serialized
    assert "primary" in serialized
    assert '"remaining": 4' in serialized
