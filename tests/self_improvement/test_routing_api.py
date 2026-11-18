"""Acceptance tests for Cognitive Brain middleware discovery and planning."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from aries_serpent_core.agents.brain_client import BrainClient
from cognitive_app.src.server.cli_api_server import app


def test_capability_endpoint_uses_server_observed_state() -> None:
    response = TestClient(app).get("/api/capabilities")

    assert response.status_code == 200
    payload = response.json()
    assert payload["execution_enabled"] is False
    assert "github.read" in payload["routes"]
    assert payload["adapter_states"]["github_mcp"] == "unavailable"
    assert not any("token" in key.lower() for key in payload)


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
        session = client.post(
            "/api/session",
            headers={"Origin": "http://localhost:5173"},
        )
        authorized = client.post("/api/cli/run", json={"command": "git status --short"})

    assert denied.status_code == 401
    assert session.status_code == 200
    assert session.json()["credential_transport"] == "httponly_cookie"
    assert "httponly" in session.headers["set-cookie"].lower()
    assert authorized.status_code == 200


def test_ui_session_rejects_unapproved_origin() -> None:
    response = TestClient(app).post(
        "/api/session",
        headers={"Origin": "https://attacker.example"},
    )

    assert response.status_code == 403
    assert "codex_ui_session" not in response.cookies


def test_ui_session_cookie_authenticates_websocket() -> None:
    with TestClient(app, base_url="http://localhost:8765") as client:
        session = client.post("/api/session", headers={"Origin": "http://localhost:5173"})
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


def test_brain_client_does_not_forward_token_to_unapproved_origin(monkeypatch: Any) -> None:
    monkeypatch.setenv("CODEX_MASTER_KEY", "DUMMY_TOKEN")
    client = BrainClient(base_url="http://untrusted.example")

    assert client._auth_header() == {}
