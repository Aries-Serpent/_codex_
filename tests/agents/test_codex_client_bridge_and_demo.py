from __future__ import annotations

from dataclasses import dataclass

import builtins
import importlib
import sys
import tomllib
from pathlib import Path

import httpx
import pytest

from agents.codex_client.codex_client import demo_plan_and_call as demo
from agents.codex_client.codex_client.bridge import CodexBridgeClient
from agents.codex_client.codex_client.config import ClientConfig

pytest.importorskip("tenacity")


def test_codex_bridge_declares_tenacity_dependency() -> None:
    pyproject = Path(__file__).resolve().parents[2] / "agents" / "codex_client" / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    dependencies = data["project"]["dependencies"]
    assert any(dep.startswith("tenacity") for dep in dependencies)


def test_bridge_module_falls_back_when_tenacity_is_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "tenacity" or name.startswith("tenacity."):
            raise ModuleNotFoundError("No module named 'tenacity'")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    for name in list(sys.modules):
        if name == "tenacity" or name.startswith("tenacity."):
            sys.modules.pop(name, None)
    sys.modules.pop("agents.codex_client.codex_client.bridge", None)
    module = importlib.import_module("agents.codex_client.codex_client.bridge")

    attempts = {"count": 0}

    @module.retry(
        reraise=True,
        retry=lambda exc: isinstance(exc, ValueError),
        stop=3,
        wait=lambda *_: 0,
    )
    def flaky() -> str:
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise ValueError("retry me")
        return "ok"

    assert flaky() == "ok"
    assert attempts["count"] == 3


@dataclass
class _FakeResponse:
    payload: dict

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self.payload


class _FakeHttpClient:
    def __init__(self, timeout: float) -> None:
        self.timeout = timeout
        self.calls: list[tuple[str, str, dict | None, dict | None, dict]] = []
        self.closed = False

    def request(self, method: str, url: str, *, json=None, params=None, headers=None):
        self.calls.append((method, url, json, params, headers or {}))
        return _FakeResponse({"ok": True})

    def close(self) -> None:
        self.closed = True


@dataclass
class _MockUUID:
    """Mock UUID object for testing."""

    hex: str = "rid-123"


def test_bridge_request_builds_url_headers_and_closes(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_http = _FakeHttpClient(timeout=12.5)

    monkeypatch.setattr(
        "agents.codex_client.codex_client.bridge.httpx.Client", lambda timeout: fake_http
    )
    monkeypatch.setattr(
        "agents.codex_client.codex_client.bridge.uuid.uuid4",
        _MockUUID)
    config = ClientConfig(ita_url="https://ita.example", api_key="secret", request_timeout=12.5)
    with CodexBridgeClient(config) as client:
        assert client.base_headers == {"X-API-Key": "secret"}, "base_headers is not valid"
        response = client._request(
            "POST", "/kb/search", json_body={"query": "q"}, params={"top_k": 3}
        )

    assert response.json() == {"ok": True}, "Response must not be empty"
    assert fake_http.closed is True, "closed is not valid"
    method, url, json_body, params, headers = fake_http.calls[0]
    assert method == "POST", "method is not valid"
    assert url == "https://ita.example/kb/search", "url is not valid"
    assert json_body == {"query": "q"}, "json_body is not valid"
    assert params == {"top_k": 3}, "params is not valid"
    assert headers["X-API-Key"] == "secret", "Condition must be true"
    assert headers["X-Request-Id"] == "rid-123", "Condition must be true"


def test_bridge_endpoint_methods_validate_payloads(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "agents.codex_client.codex_client.bridge.httpx.Client",
        lambda timeout: _FakeHttpClient(timeout=timeout))
    config = ClientConfig(ita_url="https://ita.example", api_key="secret")
    client = CodexBridgeClient(config)

    def fake_request(method: str, path: str, *, json_body=None, params=None):
        if path == "/kb/search":
            assert json_body == {"query": "find", "top_k": 2}
            return _FakeResponse({"results": [{"snippet": "s", "source": "doc", "score": 0.9}]})
        if path == "/repo/hygiene":
            assert json_body == {"diff": "d", "checks": ["lint"]}
            return _FakeResponse(
                {"issues": [{"type": "lint", "path": "a.py", "message": "m", "severity": "low"}]}
            )
        if path == "/tests/run":
            assert json_body == {"targets": ["tests/a.py"], "timeout_s": 10}
            return _FakeResponse(
                {
                    "summary": {"total": 1, "passed": 1, "failed": 0, "duration_s": 0.5},
                    "failures": [],
                }
            )
        if path == "/git/create-pr":
            assert json_body == {
                "repo": "owner/repo",
                "title": "t",
                "body": "b",
                "base": "main",
                "head": "feat",
                "labels": ["automation"],
            }
            assert params == {"dry_run": True, "confirm": False}
            return _FakeResponse(
                {
                    "simulated": True,
                    "pr_url": "https://github.com/owner/repo/pull/1",
                    "message": "ok",
                }
            )
        raise AssertionError(path)

    monkeypatch.setattr(client, "_request", fake_request)

    assert client.kb_search("find", top_k=2).results[0].source == "doc"
    assert client.repo_hygiene("d", checks=["lint"]).issues[0].type == "lint"
    assert client.tests_run(["tests/a.py"], timeout_s=10).summary.passed == 1
    assert client.git_create_pr(
        repo="owner/repo",
        title="t",
        body="b",
        base="main",
        head="feat",
        labels=["automation"],
    ).simulated is True


def test_bridge_repo_hygiene_without_checks_and_git_pr_without_labels(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "agents.codex_client.codex_client.bridge.httpx.Client",
        lambda timeout: _FakeHttpClient(timeout=timeout
    ))
    config = ClientConfig(ita_url="https://ita.example", api_key="secret")
    client = CodexBridgeClient(config)

    calls = []

    def fake_request(method: str, path: str, *, json_body=None, params=None):
        calls.append((path, json_body, params))
        if path == "/repo/hygiene":
            return _FakeResponse({"issues": []})
        return _FakeResponse({"simulated": True, "message": "ok"})

    monkeypatch.setattr(client, "_request", fake_request)

    assert client.repo_hygiene("diff", checks=[]).issues == []
    assert client.git_create_pr(
        repo="owner/repo",
        title="title",
        body="body",
        base="main",
        head="feature",
        dry_run=False,
        confirm=True,
    ).simulated is True

    assert calls[0] == ("/repo/hygiene", {"diff": "diff"}, None)
    assert calls[1] == (
        "/git/create-pr",
        {
            "repo": "owner/repo",
            "title": "title",
            "body": "body",
            "base": "main",
            "head": "feature",
        },
        {"dry_run": False, "confirm": True},
    )


class _FakeModel:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def model_dump(self) -> dict:
        return self._payload


class _FakeDemoClient:
    def __init__(self, _config: ClientConfig) -> None:
        self.calls: list[tuple[str, object]] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return None

    def kb_search(self, query: str):
        self.calls.append(("kb", query))
        return _FakeModel({"results": [{"snippet": query}]})

    def repo_hygiene(self, diff: str, checks):
        self.calls.append(("hygiene", (diff, list(checks))))
        return _FakeModel({"issues": []})

    def tests_run(self, targets):
        self.calls.append(("tests", list(targets)))
        return _FakeModel({"summary": {"total": 1}})

    def git_create_pr(self, **kwargs):
        self.calls.append(("pr", kwargs))
        return _FakeModel({"simulated": True, "confirm": kwargs["confirm"]})


def test_demo_parse_args_and_format_section() -> None:
    args = demo.parse_args(["--query", "hello", "--run-tests", "tests/a.py", "--confirm"])
    assert args.query == "hello", "query is not valid"
    assert args.run_tests == ["tests/a.py"], "run_tests is not valid"
    assert args.confirm is True, "confirm is not valid"
    assert demo._format_section("X") == "\n=\nX\n=", "Condition must be true"


def test_demo_main_outputs_all_sections(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        demo.ClientConfig,
        "from_environment",
        classmethod(lambda cls: ClientConfig("http://ita", "k")))
    created: list[_FakeDemoClient] = []

    def make_client(config: ClientConfig) -> _FakeDemoClient:
        client = _FakeDemoClient(config)
        created.append(client)
        return client

    monkeypatch.setattr(demo, "CodexBridgeClient", make_client)

    rc = demo.main(["--query", "needle", "--run-tests", "tests/a.py", "--confirm"])
    out = capsys.readouterr().out

    assert rc == 0, "rc is not valid"
    assert "Knowledge Search" in out, "Condition must be true"
    assert "Repo Hygiene" in out, "Condition must be true"
    assert "Tests" in out, "Condition must be true"
    assert "Pull Request" in out, "Condition must be true"
    assert '"simulated": true' in out, "Condition must be true"

    client = created[0]
    assert ("kb", "needle") in client.calls
    assert any(call[0] == "tests" for call in client.calls), "Condition must be true"


def test_demo_main_skips_tests_section_without_targets(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        demo.ClientConfig,
        "from_environment",
        classmethod(lambda cls: ClientConfig("http://ita", "k")))
    monkeypatch.setattr(demo, "CodexBridgeClient", _FakeDemoClient)

    rc = demo.main(["--query", "needle"])
    out = capsys.readouterr().out

    assert rc == 0, "rc is not valid"
    assert "Tests" not in out, "Condition must be true"


def test_demo_entrypoint_raises_system_exit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(demo, "main", lambda argv=None: 3)
    with pytest.raises(SystemExit) as exc:
        code = (
            "if True:\n"
            "    from agents.codex_client.codex_client import demo_plan_and_call as m\n"
            "    raise SystemExit(m.main())"
        )
        exec(code)
    assert exc.value.code == 3, "Value must be initialized"


def test_bridge_request_propagates_http_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    class _ErrResponse(_FakeResponse):
        def raise_for_status(self) -> None:
            raise httpx.HTTPStatusError(
                "boom",
                request=httpx.Request("GET", "https://ita.example/x"),
                response=httpx.Response(500))
    class _ErrClient(_FakeHttpClient):
        def request(self, method: str, url: str, *, json=None, params=None, headers=None):
            return _ErrResponse({})

    monkeypatch.setattr(
        "agents.codex_client.codex_client.bridge.httpx.Client",
        lambda timeout: _ErrClient(timeout=timeout))
    config = ClientConfig(ita_url="https://ita.example", api_key="secret")
    client = CodexBridgeClient(config)

    with pytest.raises(httpx.HTTPStatusError):
        client._request("GET", "/x")
