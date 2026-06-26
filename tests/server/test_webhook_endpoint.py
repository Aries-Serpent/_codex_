"""
Tests for the inbound GitHub webhook endpoints:
  POST /webhook/github        — HMAC-SHA256 verified event receiver
  GET  /api/webhooks/recent   — recent event log query
"""

from __future__ import annotations

import hashlib
import hmac
import importlib
import json

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

 # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SAMPLE_SECRET = "test-webhook-secret-1234"
_SAMPLE_PAYLOAD = {"action": "opened", "number": 42}


def _sign(secret: str, body: bytes) -> str:
    """Compute X-Hub-Signature-256 for a given body and secret."""
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def _make_client(db_path: str, monkeypatch, **extra_env: str) -> TestClient:
    """Reload cli_api_server with the given env vars and return a TestClient."""
    monkeypatch.setenv("CODEX_DB_PATH", db_path)
    monkeypatch.delenv("WEBHOOK_SECRET", raising=False)
    monkeypatch.delenv("CODEX_WEBHOOK_DEV_MODE", raising=False)
    monkeypatch.delenv("CODEX_MASTER_KEY", raising=False)
    monkeypatch.delenv("CODEX_BACKUP_KEY", raising=False)
    for key, value in extra_env.items():
        monkeypatch.setenv(key, value)

    import cognitive_app.src.server.cli_api_server as _mod

    importlib.reload(_mod)
    from cognitive_app.src.server.cli_api_server import app

    return TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def db_path(tmp_path):
    """Provide a fresh SQLite DB path for each test."""
    return str(tmp_path / "test_cli_history.db")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestWebhookValidSignature:
    """POST /webhook/github — happy path with valid HMAC."""

    def test_returns_200_accepted(self, db_path, monkeypatch):
        client = _make_client(db_path, monkeypatch, WEBHOOK_SECRET=_SAMPLE_SECRET)
        body = json.dumps(_SAMPLE_PAYLOAD).encode()
        with client:
            resp = client.post(
                "/webhook/github",
                content=body,
                headers={
                    "Content-Type": "application/json",
                    "X-Hub-Signature-256": _sign(_SAMPLE_SECRET, body),
                    "X-GitHub-Event": "pull_request",
                    "X-GitHub-Delivery": "abc-123",
                },
            )
        assert resp.status_code == 200, "status_code is not valid"
        data = resp.json()
        assert data["status"] == "accepted", "Data must not be empty"
        assert data["delivery_id"] == "abc-123", "Data must not be empty"


class TestWebhookInvalidSignature:
    """POST /webhook/github — wrong HMAC → 401."""

    def test_returns_401(self, db_path, monkeypatch):
        client = _make_client(db_path, monkeypatch, WEBHOOK_SECRET=_SAMPLE_SECRET)
        body = json.dumps(_SAMPLE_PAYLOAD).encode()
        with client:
            resp = client.post(
                "/webhook/github",
                content=body,
                headers={
                    "Content-Type": "application/json",
                    "X-Hub-Signature-256": "sha256=bad0000000000000000000000000000000000000000000000000000000000000",
                    "X-GitHub-Event": "pull_request",
                },
            )
        assert resp.status_code == 401, "status_code is not valid"
        assert "Invalid signature" in resp.json()["error"], "Error should be raised or set"


class TestWebhookMissingSecret:
    """POST /webhook/github — no WEBHOOK_SECRET set → 401 (fail closed)."""

    def test_returns_401_when_secret_not_configured(self, db_path, monkeypatch):
        client = _make_client(db_path, monkeypatch)
        body = json.dumps(_SAMPLE_PAYLOAD).encode()
        with client:
            resp = client.post(
                "/webhook/github",
                content=body,
                headers={
                    "Content-Type": "application/json",
                    "X-Hub-Signature-256": _sign("any-secret", body),
                    "X-GitHub-Event": "push",
                },
            )
        assert resp.status_code == 401, "status_code is not valid"
        assert "not configured" in resp.json()["error"], "Error should be raised or set"


class TestWebhookInvalidJson:
    """POST /webhook/github — valid HMAC but non-JSON body → 400."""

    def test_returns_400_for_malformed_json(self, db_path, monkeypatch):
        client = _make_client(db_path, monkeypatch, WEBHOOK_SECRET=_SAMPLE_SECRET)
        body = b"not valid json {"
        with client:
            resp = client.post(
                "/webhook/github",
                content=body,
                headers={
                    "Content-Type": "application/json",
                    "X-Hub-Signature-256": _sign(_SAMPLE_SECRET, body),
                    "X-GitHub-Event": "push",
                },
            )
        assert resp.status_code == 400, "status_code is not valid"
        assert "Invalid JSON" in resp.json()["error"], "Error should be raised or set"


class TestWebhookRecentEvents:
    """GET /api/webhooks/recent — events appear after a valid POST."""

    def test_event_appears_in_recent(self, db_path, monkeypatch):
        client = _make_client(db_path, monkeypatch, WEBHOOK_SECRET=_SAMPLE_SECRET)
        body = json.dumps(_SAMPLE_PAYLOAD).encode()
        with client:
            post_resp = client.post(
                "/webhook/github",
                content=body,
                headers={
                    "Content-Type": "application/json",
                    "X-Hub-Signature-256": _sign(_SAMPLE_SECRET, body),
                    "X-GitHub-Event": "issues",
                    "X-GitHub-Delivery": "delivery-xyz",
                },
            )
            assert post_resp.status_code == 200, "status_code is not valid"

            get_resp = client.get("/api/webhooks/recent?limit=10")
        assert get_resp.status_code == 200, "status_code is not valid"
        data = get_resp.json()
        assert data["total"] >= 1, "Value must be greater than zero"
        event = data["events"][0]
        assert event["event_type"] == "issues", "Condition must be true"
        assert event["delivery_id"] == "delivery-xyz", "Condition must be true"
        assert event["payload"] == _SAMPLE_PAYLOAD, "Condition must be true"


class TestWebhookDevMode:
    """POST /webhook/github — CODEX_WEBHOOK_DEV_MODE=true skips HMAC check."""

    def test_dev_mode_accepts_without_secret(self, db_path, monkeypatch):
        client = _make_client(db_path, monkeypatch, CODEX_WEBHOOK_DEV_MODE="true")
        body = json.dumps(_SAMPLE_PAYLOAD).encode()
        with client:
            resp = client.post(
                "/webhook/github",
                content=body,
                headers={
                    "Content-Type": "application/json",
                    "X-GitHub-Event": "push",
                    "X-GitHub-Delivery": "dev-mode-delivery",
                },
            )
        assert resp.status_code == 200, "status_code is not valid"
        assert resp.json()["status"] == "accepted", "Condition must be true"
