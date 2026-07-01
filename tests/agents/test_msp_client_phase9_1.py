"""Unit tests for agents/msp_client.py (Phase 9.1 coverage push)."""

from __future__ import annotations

from typing import Any

import httpx
import pytest

from agents import msp_client as msp_module
from agents.msp_client import EnhancedMSPClient, MSPClient

# pragma: allowlist test secret # pragma: allowlist secret


class _FakeResponse:
    def __init__(
        self,
        json_data: Any = None,
        status_code: int = 200,
        raise_exc: Exception | None = None,
        text_chunks: list[str] | None = None,
    ) -> None:
        self._json = json_data if json_data is not None else {}
        self.status_code = status_code
        self._raise_exc = raise_exc
        self._chunks = text_chunks or []

    def raise_for_status(self) -> None:
        if self._raise_exc is not None:
            raise self._raise_exc
        if self.status_code >= 400:
            req = httpx.Request("GET", "http://testserver/fake")
            resp = httpx.Response(self.status_code, request=req)
            raise httpx.HTTPStatusError(
                f"Error response {self.status_code}",
                request=req,
                response=resp,
            )

    def json(self) -> Any:
        return self._json

    def iter_text(self):
        yield from self._chunks


class _FakeStream:
    def __init__(self, response: _FakeResponse) -> None:
        self._response = response

    def __enter__(self) -> _FakeResponse:
        return self._response

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        return None


class _FakeHttpxClient:
    """Mimics the subset of httpx.Client used by MSPClient/EnhancedMSPClient."""

    def __init__(self, **init_kwargs: Any) -> None:
        self.init_kwargs = init_kwargs
        self.calls: list[tuple[str, str, dict[str, Any]]] = []
        self.closed = False
        # Default responses keyed by (method, path). Tests can override.
        self.responses: dict[tuple[str, str], _FakeResponse | list[_FakeResponse]] = {}
        self.default_response = _FakeResponse({"ok": True})
        self.stream_response = _FakeResponse(text_chunks=["a", "b", ""])

    # ---- Helpers used by tests ----
    def set_response(self, method: str, path: str, response: _FakeResponse) -> None:
        self.responses[(method.upper(), path)] = response

    def set_sequence(self, method: str, path: str, responses: list[_FakeResponse]) -> None:
        self.responses[(method.upper(), path)] = list(responses)

    def _resolve(self, method: str, path: str) -> _FakeResponse:
        key = (method.upper(), path)
        resp = self.responses.get(key, self.default_response)
        if isinstance(resp, list):
            if not resp:
                raise AssertionError(f"No more queued responses for {key}")
            return resp.pop(0)
        return resp

    # ---- httpx.Client surface ----
    def request(self, method: str, path: str, **kwargs: Any) -> _FakeResponse:
        self.calls.append((method.upper(), path, kwargs))
        return self._resolve(method, path)

    def get(self, path: str, **kwargs: Any) -> _FakeResponse:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> _FakeResponse:
        return self.request("POST", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> _FakeResponse:
        return self.request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> _FakeResponse:
        return self.request("DELETE", path, **kwargs)

    def stream(self, method: str, path: str, **kwargs: Any) -> _FakeStream:
        self.calls.append((method.upper() + ":stream", path, kwargs))
        return _FakeStream(self.stream_response)

    def close(self) -> None:
        self.closed = True


@pytest.fixture
def fake_client_factory(monkeypatch):
    """Patch httpx.Client in msp_client module to return our fake.

    Returns a list collecting instantiated fakes so tests can inspect them.
    """
    instances: list[_FakeHttpxClient] = []

    def _factory(**kwargs: Any) -> _FakeHttpxClient:
        c = _FakeHttpxClient(**kwargs)
        instances.append(c)
        return c

    monkeypatch.setattr(msp_module.httpx, "Client", _factory)
    return instances


# --------------------------- MSPClient ---------------------------


def test_init_defaults_and_headers_without_api_key(fake_client_factory):
    client = MSPClient()
    assert client.base_url == "http://127.0.0.1:8080", "base_url is not valid"
    assert client.endpoint == "http://127.0.0.1:8080", "endpoint is not valid"
    assert client.timeout == 30.0, "timeout is not valid"
    fake = fake_client_factory[0]
    # Headers do not include Authorization when no api_key.
    headers = fake.init_kwargs["headers"]
    assert headers == {"Content-Type": "application/json"}, "Content must not be empty"
    assert fake.init_kwargs["base_url"] == "http://127.0.0.1:8080", "Condition must be true"


def test_init_endpoint_alias_used_when_base_url_default(fake_client_factory):
    client = MSPClient(endpoint="http://example.com/")
    # endpoint overrides default base_url, and trailing slash is stripped.
    assert client.base_url == "http://example.com", "base_url is not valid"
    assert client.endpoint == "http://example.com/", "endpoint is not valid"


def test_init_endpoint_alias_ignored_when_base_url_explicit(fake_client_factory):
    client = MSPClient(base_url="http://explicit/", endpoint="http://other")
    assert client.base_url == "http://explicit", "base_url is not valid"


def test_init_with_api_key_adds_authorization_header(fake_client_factory):
    MSPClient(api_key="test")  # pragma: allowlist secret
    fake = fake_client_factory[0]
    assert fake.init_kwargs["headers"]["Authorization"] == "Bearer " + "test", "Condition must be true"


def test_request_passes_method_and_path(fake_client_factory):
    client = MSPClient()
    fake = fake_client_factory[0]
    fake.set_response("POST", "/foo", _FakeResponse({"value": 1}))
    out = client.request("POST", "/foo", json={"x": 1})
    assert out == {"value": 1}, "Value must be initialized"
    assert ("POST", "/foo", {"json": {"x": 1}}) in fake.calls


def test_health_check(fake_client_factory):
    client = MSPClient()
    fake = fake_client_factory[0]
    fake.set_response("GET", "/health", _FakeResponse({"status": "ok"}))
    assert client.health_check() == {"status": "ok"}, "Condition must be true"


def test_infer_sends_full_payload(fake_client_factory):
    client = MSPClient()
    fake = fake_client_factory[0]
    fake.set_response("POST", "/v1/infer", _FakeResponse({"tokens": 5}))
    result = client.infer(
        tenant_id="t1",
        prompt="hello",
        max_tokens=10,
        temperature=0.3,
        top_p=0.8,
        options={"k": 1},
    )
    assert result == {"tokens": 5}, "Result must not be empty"
    payload = fake.calls[-1][2]["json"]
    assert payload == {
        "tenant_id": "t1",
        "prompt": "hello",
        "max_tokens": 10,
        "temperature": 0.3,
        "top_p": 0.8,
        "options": {"k": 1},
    }


def test_infer_default_options_empty_dict(fake_client_factory):
    client = MSPClient()
    fake = fake_client_factory[0]
    client.infer(tenant_id="t", prompt="p")
    assert fake.calls[-1][2]["json"]["options"] == {}, "Condition must be true"


def test_query_kb_with_and_without_filters(fake_client_factory):
    client = MSPClient()
    fake = fake_client_factory[0]
    client.query_kb("t", "q")
    assert fake.calls[-1][2]["json"]["filters"] == {}, "Condition must be true"
    client.query_kb("t", "q", top_k=3, filters={"a": 1}, include_metadata=False)
    last = fake.calls[-1][2]["json"]
    assert last["top_k"] == 3 and last["filters"] == {"a": 1}, "Condition must be true"
    assert last["include_metadata"] is False, "Data must not be empty"


def test_create_tenant_defaults(fake_client_factory):
    client = MSPClient()
    fake = fake_client_factory[0]
    client.create_tenant("tid", "Name", "k")
    payload = fake.calls[-1][2]["json"]
    assert payload["quota"] == {
        "requests_per_minute": 60,
        "tokens_per_minute": 10000,
    }
    assert payload["policies"] == [], "Condition must be true"
    assert payload["metadata"] == {}, "Data must not be empty"


def test_create_tenant_custom_values(fake_client_factory):
    client = MSPClient()
    fake = fake_client_factory[0]
    client.create_tenant("tid", "Name", "k", quota={"r": 1}, policies=["p"], metadata={"m": 1})
    payload = fake.calls[-1][2]["json"]
    assert payload["quota"] == {"r": 1}, "Condition must be true"
    assert payload["policies"] == ["p"], "Condition must be true"
    assert payload["metadata"] == {"m": 1}, "Data must not be empty"


def test_get_tenant_and_list_tenants(fake_client_factory):
    client = MSPClient()
    fake = fake_client_factory[0]
    fake.set_response("GET", "/admin/tenants/abc", _FakeResponse({"id": "abc"}))
    fake.set_response("GET", "/admin/tenants", _FakeResponse([{"id": "abc"}]))
    assert client.get_tenant("abc") == {"id": "abc"}, "Condition must be true"
    assert client.list_tenants() == [{"id": "abc"}], "Condition must be true"


def test_update_tenant_all_fields(fake_client_factory):
    client = MSPClient()
    fake = fake_client_factory[0]
    client.update_tenant(
        "tid",
        name="n",
        quota={"q": 1},
        policies=["p"],
        metadata={"m": 1},
        active=True,
    )
    body = fake.calls[-1][2]["json"]
    assert body == {
        "name": "n",
        "quota": {"q": 1},
        "policies": ["p"],
        "metadata": {"m": 1},
        "active": True,
    }


def test_update_tenant_partial_fields(fake_client_factory):
    client = MSPClient()
    fake = fake_client_factory[0]
    client.update_tenant("tid", active=False)
    assert fake.calls[-1][2]["json"] == {"active": False}, "Condition must be true"


def test_delete_tenant(fake_client_factory):
    client = MSPClient()
    fake = fake_client_factory[0]
    client.delete_tenant("tid")
    assert ("DELETE", "/admin/tenants/tid", {}) in fake.calls


def test_close_and_context_manager(fake_client_factory):
    with MSPClient() as client:
        assert isinstance(client, MSPClient)
    fake = fake_client_factory[0]
    assert fake.closed is True, "closed is not valid"


def test_request_raises_for_status(fake_client_factory):
    client = MSPClient()
    fake = fake_client_factory[0]
    err = httpx.HTTPStatusError(
        "boom",
        request=httpx.Request("GET", "http://x/health"),
        response=httpx.Response(500),
    )
    fake.set_response("GET", "/health", _FakeResponse(raise_exc=err))
    with pytest.raises(httpx.HTTPStatusError):
        client.health_check()


# --------------------------- EnhancedMSPClient ---------------------------


def test_request_with_retry_succeeds_first_try(fake_client_factory):
    client = EnhancedMSPClient()
    fake = fake_client_factory[0]
    fake.set_response("GET", "/x", _FakeResponse({"ok": 1}))
    assert client.request_with_retry("GET", "/x") == {"ok": 1}


def test_request_with_retry_recovers_after_failures(monkeypatch, fake_client_factory):
    client = EnhancedMSPClient()
    fake = fake_client_factory[0]
    err = httpx.ConnectError("nope")
    fake.set_sequence(
        "GET",
        "/x",
        [
            _FakeResponse(raise_exc=err),
            _FakeResponse(raise_exc=err),
            _FakeResponse({"ok": True}),
        ],
    )
    sleeps: list[float] = []
    monkeypatch.setattr(msp_module.time, "sleep", lambda s: sleeps.append(s))
    out = client.request_with_retry("GET", "/x", max_retries=3, backoff_factor=0.5)
    assert out == {"ok": True}, "out is not valid"
    # Two retries, so two sleeps (0.5, 1.0).
    assert sleeps == [0.5, 1.0]


def test_request_with_retry_exhausts_and_reraises(monkeypatch, fake_client_factory):
    client = EnhancedMSPClient()
    fake = fake_client_factory[0]
    err = httpx.TimeoutException("slow")
    fake.set_sequence("GET", "/x", [_FakeResponse(raise_exc=err) for _ in range(3)])
    monkeypatch.setattr(msp_module.time, "sleep", lambda s: None)
    with pytest.raises(httpx.TimeoutException):
        client.request_with_retry("GET", "/x", max_retries=3)


def test_request_with_retry_zero_retries_raises_runtime(monkeypatch, fake_client_factory):
    client = EnhancedMSPClient()
    monkeypatch.setattr(msp_module.time, "sleep", lambda s: None)
    with pytest.raises(RuntimeError):
        client.request_with_retry("GET", "/x", max_retries=0)


def test_batch_infer_calls_infer_per_prompt(fake_client_factory):
    client = EnhancedMSPClient()
    fake = fake_client_factory[0]
    fake.set_response("POST", "/v1/infer", _FakeResponse({"o": 1}))
    out = client.batch_infer("t", ["p1", "p2", "p3"])
    assert out == [{"o": 1}, {"o": 1}, {"o": 1}]
    posts = [c for c in fake.calls if c[0] == "POST" and c[1] == "/v1/infer"]
    assert len(posts) == 3, "Posts must not be empty"


def test_stream_infer_yields_non_empty_chunks(fake_client_factory):
    client = EnhancedMSPClient()
    fake = fake_client_factory[0]
    fake.stream_response = _FakeResponse(text_chunks=["x", "", "y"])
    chunks = list(client.stream_infer("t", "p"))
    assert chunks == ["x", "y"]
    # Verify stream call was issued with the expected payload.
    stream_calls = [c for c in fake.calls if c[0] == "POST:stream"]
    assert stream_calls, "stream_calls is not valid"
    assert stream_calls[0][2]["json"]["stream"] is True, "Condition must be true"


def test_get_usage_stats_with_and_without_bounds(fake_client_factory):
    client = EnhancedMSPClient()
    fake = fake_client_factory[0]
    client.get_usage_stats("t")
    assert fake.calls[-1][2]["params"] == {"tenant_id": "t"}, "Condition must be true"
    client.get_usage_stats("t", start_time="s", end_time="e")
    assert fake.calls[-1][2]["params"] == {
        "tenant_id": "t",
        "start_time": "s",
        "end_time": "e",
    }


def test_set_rate_limit(fake_client_factory):
    client = EnhancedMSPClient()
    fake = fake_client_factory[0]
    client.set_rate_limit("t", 10, 1000)
    body = fake.calls[-1][2]["json"]
    assert body == {"quota": {"requests_per_minute": 10, "tokens_per_minute": 1000}}


def test_get_model_info_with_and_without_id(fake_client_factory):
    client = EnhancedMSPClient()
    fake = fake_client_factory[0]
    client.get_model_info()
    assert fake.calls[-1][1] == "/v1/models", "Condition must be true"
    client.get_model_info(model_id="gpt-x")
    assert fake.calls[-1][1] == "/v1/models/gpt-x", "Condition must be true"


def test_validate_api_key_true(fake_client_factory):
    client = EnhancedMSPClient()
    fake = fake_client_factory[0]
    fake.set_response("GET", "/v1/validate", _FakeResponse(status_code=200))
    assert client.validate_api_key("k") is True, "Condition must be true"


def test_validate_api_key_false_on_non_200(fake_client_factory):
    client = EnhancedMSPClient()
    fake = fake_client_factory[0]
    fake.set_response("GET", "/v1/validate", _FakeResponse(status_code=401))
    assert client.validate_api_key("k") is False, "Condition must be true"


def test_validate_api_key_false_on_http_status_error(fake_client_factory):
    client = EnhancedMSPClient()
    fake = fake_client_factory[0]
    err = httpx.HTTPStatusError(
        "bad",
        request=httpx.Request("GET", "http://x/v1/validate"),
        response=httpx.Response(500),
    )
    fake.set_response("GET", "/v1/validate", _FakeResponse(raise_exc=err))
    # The except in validate_api_key only catches the response.status_code branch
    # path; raising on get itself isn't done by the implementation. So
    # simulate it by overriding `get` to raise directly.

    def _raise(path, **kwargs):  # noqa: ARG001
        raise err

    fake.get = _raise  # type: ignore[assignment]
    assert client.validate_api_key("k") is False, "Condition must be true"


def test_get_metrics(fake_client_factory):
    client = EnhancedMSPClient()
    fake = fake_client_factory[0]
    fake.set_response("GET", "/metrics", _FakeResponse({"m": 1}))
    assert client.get_metrics() == {"m": 1}, "Condition must be true"
