"""Acceptance tests for Cognitive Brain middleware discovery and planning."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from aries_serpent_core.agents.brain_client import BrainClient
from codex.cognitive_brain.route_execution import RouteExecutionStore
from cognitive_app.src.server.cli_api_server import app

UI_BOOTSTRAP_TOKEN = "test-ui-bootstrap-capability"


def test_codex_runtime_dir_honors_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    from cognitive_app.src.server import cli_api_server

    monkeypatch.setenv("CODEX_RUNTIME_DIR", "/tmp/codex-persistent-runtime")

    assert str(cli_api_server._codex_runtime_dir()) == "/tmp/codex-persistent-runtime"


@pytest.fixture(autouse=True)
def configure_ui_bootstrap(monkeypatch: pytest.MonkeyPatch):
    from cognitive_app.src.server import cli_api_server

    monkeypatch.setenv("CODEX_UI_BOOTSTRAP_TOKENS", UI_BOOTSTRAP_TOKEN)
    cli_api_server._consumed_ui_bootstraps.clear()
    yield
    cli_api_server._consumed_ui_bootstraps.clear()


def establish_ui_session(
    client: TestClient,
    *,
    origin: str = "http://localhost:5173",
):
    return client.post(
        "/api/session",
        headers={
            "Origin": origin,
            "X-Codex-Bootstrap": UI_BOOTSTRAP_TOKEN,
        },
    )


def test_capability_endpoint_uses_server_observed_state() -> None:
    response = TestClient(app).get("/api/capabilities")

    assert response.status_code == 200
    payload = response.json()
    assert payload["execution_enabled"] is False
    assert "github.read" in payload["routes"]
    assert "maintainer.read" in payload["routes"]
    assert payload["adapter_states"]["github_mcp"] == "unavailable"
    assert not any("token" in key.lower() for key in payload)


def test_maintainer_status_is_secret_free() -> None:
    response = TestClient(app).get("/api/maintainer/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["owner"] == {
        "human_login": "mbaetiong",
        "human_reviewers_required": 0,
        "ai_review": "exact_head_sha_required",
    }
    assert "value" not in response.text.lower()


def test_keepalive_touch_requires_operation_session(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Any
) -> None:
    monkeypatch.setenv("CODEX_RUNTIME_DIR", str(tmp_path))
    client = TestClient(app)

    denied = client.post("/api/maintainer/keepalive/touch")
    assert denied.status_code in {401, 503}

    established = establish_ui_session(client)
    assert established.status_code == 200
    allowed = client.post("/api/maintainer/keepalive/touch")

    assert allowed.status_code == 200
    assert (tmp_path / "agent-session.active").is_file()


def test_gh_binary_presence_is_installed_not_verified(monkeypatch: Any) -> None:
    from cognitive_app.src.server import cli_api_server

    monkeypatch.setattr(cli_api_server.shutil, "which", lambda name: f"/bin/{name}")

    states = cli_api_server._observed_adapter_states()

    assert states["gh"] == "installed"
    assert states["gh"] != "verified"


def test_github_preflight_uses_only_literal_api_user_url(monkeypatch: Any) -> None:
    from cognitive_app.src.server import cli_api_server

    calls: list[dict[str, Any]] = []

    def fake_get(url: str, **kwargs: Any) -> Any:
        calls.append({"url": url, **kwargs})
        status = 200 if kwargs["headers"]["Authorization"] == "Bearer live-token" else 401
        return SimpleNamespace(status_code=status)

    monkeypatch.setenv("CODEX_MASTER_KEY", "stale-token")
    monkeypatch.setenv("CODEX_BACKUP_KEY", "live-token")
    monkeypatch.setattr(cli_api_server.httpx, "get", fake_get)

    token, source = cli_api_server._github_token_preflight()

    assert (token, source) == ("live-token", "CODEX_BACKUP_KEY")
    assert [call["url"] for call in calls] == ["https://api.github.com/user"] * 2
    assert all(call["follow_redirects"] is False for call in calls)


def test_route_plan_endpoint_derives_write_from_action() -> None:
    response = TestClient(app).post(
        "/api/routes/plan",
        json={
            "capability": "github.write",
            "action": "create_pull_request",
            "target": "Aries-Serpent/_codex_",
            "mutating": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["decision"] == "dry_run_only"
    assert response.json()["execution_enabled"] is False
    assert response.json()["permission_family"] == "pull_requests"
    assert response.json()["risk"] == "medium"
    assert response.json()["rollback_class"] == "close"


def test_rest_route_plan_allows_repository_read() -> None:
    from cognitive_app.src.server import cli_api_server

    states = cli_api_server._observed_adapter_states()
    plan = cli_api_server._plan_route(
        cli_api_server._RouteRequest(
            capability="github.read",
            action="get_repository",
            target="Aries-Serpent/_codex_",
            idempotency_key="read-plan",
        ),
        states,
        allow_writes=False,
    )

    assert states["rest_graphql"] == "verified"
    assert plan.decision is cli_api_server._RouteDecision.ALLOW
    assert plan.preferred_adapter == "rest_graphql"


def test_route_plan_rejects_action_not_registered_for_capability() -> None:
    response = TestClient(app).post(
        "/api/routes/plan",
        json={
            "capability": "github.read",
            "action": "delete_repository",
            "target": "Aries-Serpent/_codex_",
        },
    )

    assert response.status_code == 200
    assert response.json()["decision"] == "deny"
    assert response.json()["preferred_adapter"] is None


def test_proxy_logs_fixed_fields_without_request_or_exception_text(
    monkeypatch: Any,
    caplog: Any,
) -> None:
    from cognitive_app.src.server import cli_api_server

    class SuccessfulClient:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        async def __aenter__(self) -> "SuccessfulClient":
            return self

        async def __aexit__(self, *args: Any) -> None:
            return None

        async def request(self, *args: Any, **kwargs: Any) -> Any:
            return SimpleNamespace(
                status_code=200,
                headers={},
                json=lambda: {"ok": True},
                text="ok",
                url="https://target.invalid/redacted",
            )

    monkeypatch.setattr(cli_api_server.httpx, "AsyncClient", SuccessfulClient)
    caplog.set_level("INFO")
    response = TestClient(app).post(
        "/api/request",
        json={"method": "GET", "url": "https://target.invalid/private-value"},
    )

    assert response.status_code == 200
    messages = "\n".join(caplog.messages)
    assert "target.invalid" not in messages
    assert "private-value" not in messages
    assert "api_proxy completed status=200" in messages


def test_proxy_failure_does_not_expose_transport_exception(
    monkeypatch: Any,
    caplog: Any,
) -> None:
    from cognitive_app.src.server import cli_api_server

    class FailingClient:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        async def __aenter__(self) -> "FailingClient":
            return self

        async def __aexit__(self, *args: Any) -> None:
            return None

        async def request(self, *args: Any, **kwargs: Any) -> Any:
            raise cli_api_server.httpx.ConnectError("secret-host\nstack-path-token")

    monkeypatch.setattr(cli_api_server.httpx, "AsyncClient", FailingClient)
    caplog.set_level("WARNING")
    response = TestClient(app).post(
        "/api/request",
        json={"method": "GET", "url": "https://target.invalid/private-value"},
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "Upstream connection failed"
    assert "secret-host" not in response.text
    assert "secret-host" not in "\n".join(caplog.messages)
    assert "stack-path-token" not in "\n".join(caplog.messages)


def test_proxy_rejects_upstream_redirects(monkeypatch: Any) -> None:
    from cognitive_app.src.server import cli_api_server

    class RedirectClient:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        async def __aenter__(self) -> "RedirectClient":
            return self

        async def __aexit__(self, *args: Any) -> None:
            return None

        async def request(self, *args: Any, **kwargs: Any) -> Any:
            return SimpleNamespace(status_code=302, headers={}, json=lambda: {}, text="redirect")

    monkeypatch.setattr(cli_api_server.httpx, "AsyncClient", RedirectClient)
    response = TestClient(app).post(
        "/api/request",
        json={"method": "GET", "url": "https://example.com/redirect"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Upstream redirects are not permitted"


def test_raw_github_token_endpoint_is_retired() -> None:
    response = TestClient(app).get("/api/github/token")

    assert response.status_code == 410
    assert "token" not in response.json()


def test_ui_session_cookie_authorizes_local_operation() -> None:
    with TestClient(app, base_url="http://localhost:8765") as client:
        denied = client.post("/api/cli/run", json={"command": "git status --short"})
        session = establish_ui_session(client)
        authorized = client.post("/api/cli/run", json={"command": "git status --short"})

    assert denied.status_code == 401
    assert session.status_code == 200
    assert session.json()["credential_transport"] == "httponly_cookie"
    assert "httponly" in session.headers["set-cookie"].lower()
    assert authorized.status_code == 200


def test_ui_session_requires_bootstrap_capability() -> None:
    response = TestClient(app).post(
        "/api/session",
        headers={"Origin": "http://localhost:5173"},
    )

    assert response.status_code == 401
    assert "codex_ui_session" not in response.cookies


def test_ui_session_bootstrap_cannot_be_replayed() -> None:
    with TestClient(app, base_url="http://localhost:8765") as client:
        first = establish_ui_session(client)
        replay = establish_ui_session(TestClient(app, base_url="http://localhost:8765"))

    assert first.status_code == 200
    assert replay.status_code == 401


def test_ui_session_rejects_unapproved_origin() -> None:
    response = TestClient(app).post(
        "/api/session",
        headers={"Origin": "https://attacker.example"},
    )

    assert response.status_code == 403
    assert "codex_ui_session" not in response.cookies


def test_ui_session_cookie_authenticates_websocket() -> None:
    with TestClient(app, base_url="http://localhost:8765") as client:
        session = establish_ui_session(client)
        assert session.status_code == 200
        session_cookie = client.cookies.get("codex_ui_session")
        assert session_cookie
        with client.websocket_connect(
            "/ws/cli",
            headers={
                "Origin": "http://localhost:5173",
                "Cookie": f"codex_ui_session={session_cookie}",
            },
        ) as websocket:
            websocket.send_json({"type": "resize", "cols": 80, "rows": 24})


def test_websocket_shell_requires_authentication() -> None:
    with TestClient(app) as client:
        try:
            with client.websocket_connect("/ws/cli"):
                raise AssertionError("unauthenticated websocket was accepted")
        except WebSocketDisconnect as exc:
            assert exc.code == 4401


def test_cli_and_mutating_proxy_require_authentication() -> None:
    client = TestClient(app)
    cli = client.post("/api/cli/run", json={"command": "git status --short"})
    proxy = client.post(
        "/api/request",
        json={
            "method": "POST",
            "url": "https://api.github.com/repos/Aries-Serpent/_codex_/issues",
            "body": {"title": "must-not-run"},
        },
    )

    github_read = client.post(
        "/api/request",
        json={
            "method": "GET",
            "url": "https://api.github.com/repos/Aries-Serpent/_codex_",
        },
    )
    history = client.get("/api/cli/history")

    assert cli.status_code == 401
    assert proxy.status_code == 401
    assert github_read.status_code == 401
    assert history.status_code == 401


def test_route_execute_requires_authentication() -> None:
    response = TestClient(app).post(
        "/api/routes/execute",
        json={
            "capability": "brain.read",
            "action": "capabilities",
            "target": "local",
            "idempotency_key": "auth-required",
        },
    )

    assert response.status_code == 401


def test_route_reconciliation_requires_authentication() -> None:
    client = TestClient(app)

    assert client.get("/api/routes/incomplete").status_code == 401
    assert (
        client.post(
            "/api/routes/reconcile",
            json={"operation_id": "probe", "state": "completed", "result": {}},
        ).status_code
        == 401
    )


def test_route_reconciliation_lists_and_resolves_verified_outcome(
    monkeypatch: Any, tmp_path: Any
) -> None:
    from cognitive_app.src.server import cli_api_server

    store = RouteExecutionStore(tmp_path / "route.sqlite3")
    payload = {
        "capability": "git.local",
        "action": "status",
        "target": "local",
        "arguments": {},
        "idempotency_key": "resume-operation",
    }
    claim = store.prepare(payload)
    with store._connect() as connection:
        connection.execute(
            "UPDATE route_operations SET owner_pid = ?, owner_start = ? WHERE operation_id = ?",
            (999999999, "dead-process", claim.operation_id),
        )
    monkeypatch.setattr(cli_api_server, "_ROUTE_EXECUTION_STORE", store)

    with TestClient(app, base_url="http://localhost:8765") as client:
        assert establish_ui_session(client).status_code == 200
        listed = client.get("/api/routes/incomplete")
        reconciled = client.post(
            "/api/routes/reconcile",
            json={
                "operation_id": claim.operation_id,
                "state": "completed",
                "result": {"status": "verified externally"},
            },
        )

    assert listed.status_code == 200
    assert listed.json()["operations"][0]["operation_id"] == claim.operation_id
    assert "arguments" not in listed.json()["operations"][0]
    assert reconciled.status_code == 200
    assert store.prepare(payload).state == "replayed"


def test_route_reconciliation_rejects_unverified_payload(monkeypatch: Any, tmp_path: Any) -> None:
    from cognitive_app.src.server import cli_api_server

    store = RouteExecutionStore(tmp_path / "route.sqlite3")
    monkeypatch.setattr(cli_api_server, "_ROUTE_EXECUTION_STORE", store)

    with TestClient(app, base_url="http://localhost:8765") as client:
        assert establish_ui_session(client).status_code == 200
        response = client.post(
            "/api/routes/reconcile",
            json={"operation_id": "not-started", "state": "completed"},
        )

    assert response.status_code == 422


def test_route_execute_replays_completed_operation(monkeypatch: Any, tmp_path: Any) -> None:
    from cognitive_app.src.server import cli_api_server

    calls = 0
    store = RouteExecutionStore(tmp_path / "route.sqlite3")

    def execute_operation(req: Any, adapter: str) -> dict[str, Any]:
        nonlocal calls
        calls += 1
        return {"adapter": adapter, "action": req.action}

    monkeypatch.setattr(cli_api_server, "_ROUTE_EXECUTION_STORE", store)
    monkeypatch.setattr(cli_api_server, "_execute_route_operation", execute_operation)
    payload = {
        "capability": "brain.read",
        "action": "capabilities",
        "target": "local",
        "idempotency_key": "replay-once",
    }

    with TestClient(app, base_url="http://localhost:8765") as client:
        assert establish_ui_session(client).status_code == 200
        first = client.post("/api/routes/execute", json=payload)
        second = client.post("/api/routes/execute", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["replayed"] is False
    assert second.json()["replayed"] is True
    assert calls == 1


def test_route_execute_rejects_changed_request_for_reused_key(
    monkeypatch: Any, tmp_path: Any
) -> None:
    from cognitive_app.src.server import cli_api_server

    monkeypatch.setattr(
        cli_api_server, "_ROUTE_EXECUTION_STORE", RouteExecutionStore(tmp_path / "route.sqlite3")
    )
    monkeypatch.setattr(cli_api_server, "_execute_route_operation", lambda req, adapter: {})
    payload = {
        "capability": "brain.read",
        "action": "capabilities",
        "target": "local",
        "arguments": {"view": "summary"},
        "idempotency_key": "single-request",
    }

    with TestClient(app, base_url="http://localhost:8765") as client:
        assert establish_ui_session(client).status_code == 200
        assert client.post("/api/routes/execute", json=payload).status_code == 200
        changed = {**payload, "arguments": {"view": "full"}}
        conflict = client.post("/api/routes/execute", json=changed)

    assert conflict.status_code == 409
    assert conflict.json()["code"] == "route_execution_conflict"
    assert "different request" not in conflict.json()["detail"]


def test_route_execute_keeps_writes_disabled_without_opt_in(
    monkeypatch: Any, tmp_path: Any
) -> None:
    from cognitive_app.src.server import cli_api_server

    called = False
    monkeypatch.setattr(
        cli_api_server, "_ROUTE_EXECUTION_STORE", RouteExecutionStore(tmp_path / "route.sqlite3")
    )

    def execute_operation(req: Any, adapter: str) -> dict[str, Any]:
        nonlocal called
        called = True
        return {}

    monkeypatch.setattr(cli_api_server, "_execute_route_operation", execute_operation)
    payload = {
        "capability": "github.write",
        "action": "create_dangling_blob",
        "target": "Aries-Serpent/_codex_",
        "arguments": {"content": "must-not-write"},
        "idempotency_key": "write-disabled",
    }

    with TestClient(app, base_url="http://localhost:8765") as client:
        assert establish_ui_session(client).status_code == 200
        response = client.post("/api/routes/execute", json=payload)

    assert response.status_code == 409
    assert called is False


def test_rest_route_executes_repository_read(monkeypatch: Any) -> None:
    from cognitive_app.src.server import cli_api_server

    class ReadResponse:
        status_code = 200

        def json(self) -> dict[str, Any]:
            return {"full_name": "Aries-Serpent/_codex_", "private": False}

    def fake_get(url: str, **kwargs: Any) -> ReadResponse:
        assert url == "https://api.github.com/repos/Aries-Serpent/_codex_"
        assert kwargs["headers"]["Accept"] == "application/vnd.github+json"
        return ReadResponse()

    monkeypatch.setattr(cli_api_server.gh_rate_limit, "discover_credentials", lambda: [])
    monkeypatch.setattr(cli_api_server.httpx, "get", fake_get)

    request = cli_api_server.RouteExecuteRequest(
        capability="github.read",
        action="get_repository",
        target="Aries-Serpent/_codex_",
        idempotency_key="rest-read",
    )

    result = cli_api_server._execute_route_operation(request, "rest_graphql")

    assert result["repository"]["full_name"] == "Aries-Serpent/_codex_"
    assert result["credential_source"] is None


def test_rest_route_rotates_expired_credential(monkeypatch: Any) -> None:
    from cognitive_app.src.server import cli_api_server

    credentials = [
        cli_api_server.gh_rate_limit.Credential("CODEX_MASTER_KEY", "expired"),
        cli_api_server.gh_rate_limit.Credential("CODEX_BACKUP_KEY", "valid"),
    ]
    attempted: list[str] = []

    def request(_method: str, _url: str, **kwargs: Any) -> Any:
        source = kwargs["credentials"][0].source
        attempted.append(source)
        if source == "CODEX_MASTER_KEY":
            return cli_api_server.gh_rate_limit.GitHubResponse(
                401, {"message": "Bad credentials"}, {}, source, 1
            )
        return cli_api_server.gh_rate_limit.GitHubResponse(
            200, {"full_name": "Aries-Serpent/_codex_"}, {}, source, 1
        )

    monkeypatch.setattr(cli_api_server.gh_rate_limit, "discover_credentials", lambda: credentials)
    monkeypatch.setattr(cli_api_server.gh_rate_limit, "request", request)

    result, source = cli_api_server._run_github_rest("repos/Aries-Serpent/_codex_")

    assert result["full_name"] == "Aries-Serpent/_codex_"
    assert source == "CODEX_BACKUP_KEY"
    assert attempted == ["CODEX_MASTER_KEY", "CODEX_BACKUP_KEY"]


def test_rest_route_rejects_stale_check_sha(monkeypatch: Any) -> None:
    from cognitive_app.src.server import cli_api_server

    request = cli_api_server.RouteExecuteRequest(
        capability="github.read",
        action="list_checks",
        target="Aries-Serpent/_codex_",
        arguments={"sha": "e12da35e1b"},
        idempotency_key="stale-check-sha",
    )

    with pytest.raises(cli_api_server.RouteExecutionConflict, match="40-character commit SHA"):
        cli_api_server._execute_route_operation(request, "rest_graphql")


def test_route_execute_rejects_client_authorized_write(monkeypatch: Any, tmp_path: Any) -> None:
    from cognitive_app.src.server import cli_api_server

    called = False
    monkeypatch.setattr(
        cli_api_server, "_ROUTE_EXECUTION_STORE", RouteExecutionStore(tmp_path / "route.sqlite3")
    )
    monkeypatch.setattr(
        cli_api_server,
        "_observed_adapter_states",
        lambda: {"gh": "verified"},
    )

    def execute_operation(req: Any, adapter: str) -> dict[str, Any]:
        nonlocal called
        called = True
        return {}

    monkeypatch.setattr(cli_api_server, "_execute_route_operation", execute_operation)
    payload = {
        "capability": "github.write",
        "action": "create_dangling_blob",
        "target": "Aries-Serpent/_codex_",
        "arguments": {"content": "must-not-write"},
        "idempotency_key": "client-write-spoof",
        "allow_write": True,
    }

    with TestClient(app, base_url="http://localhost:8765") as client:
        assert establish_ui_session(client).status_code == 200
        response = client.post("/api/routes/execute", json=payload)

    assert response.status_code == 409
    assert response.json()["plan"]["decision"] == "dry_run_only"
    assert called is False


def test_brain_client_delegates_discovery_and_planning(monkeypatch: Any) -> None:
    client = BrainClient(base_url="http://127.0.0.1:8765")
    calls: list[tuple[str, Any]] = []
    monkeypatch.setattr(
        client,
        "_get",
        lambda path, **kwargs: calls.append((path, kwargs)) or {"routes": {}},
    )
    monkeypatch.setattr(
        client,
        "_post",
        lambda path, body, **kwargs: calls.append((path, body, kwargs)) or {"decision": "allow"},
    )

    assert client.capabilities() == {"routes": {}}
    assert client.plan_route("github.read", "get_repository", "Aries-Serpent/_codex_") == {
        "decision": "allow"
    }
    assert calls[0] == ("/api/capabilities", {"authenticated": False})
    assert calls[1][0] == "/api/routes/plan"
    assert "mutating" not in calls[1][1]
    assert calls[1][2] == {"authenticated": False}

    monkeypatch.setattr(
        client,
        "_post",
        lambda path, body, **kwargs: calls.append((path, body, kwargs)) or {"state": "completed"},
    )
    assert client.execute_route(
        "brain.read",
        "capabilities",
        "local",
        idempotency_key="client-execute",
    ) == {"state": "completed"}
    assert calls[2][0] == "/api/routes/execute"
    assert "allow_write" not in calls[2][1]
    assert calls[2][2] == {}


def test_brain_client_does_not_forward_token_to_unapproved_origin(monkeypatch: Any) -> None:
    monkeypatch.setenv("CODEX_MASTER_KEY", "DUMMY_TOKEN")
    client = BrainClient(base_url="http://untrusted.example")

    assert client._auth_header() == {}
