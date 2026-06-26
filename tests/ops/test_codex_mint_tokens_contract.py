"""
Test Codex Mint Tokens Contract

Test module for codex mint tokens contract.
"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_MOD = "scripts.ops.codex_mint_tokens_per_run"


def _import_script():
    root = Path(__file__).resolve().parents[2]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return __import__(SCRIPT_MOD, fromlist=["*"])


def test_build_install_token_body_parsing():
    m = _import_script()
    body = m._build_install_token_body("o/r1,o/r2", "contents=read,actions=write")
    assert body["repositories"] == ["o/r1", "o/r2"]
    assert body["permissions"] == {"contents": "read", "actions": "write"}


def test_exchange_and_revoke_offline(monkeypatch):
    m = _import_script()

    class DummyResp:
        def __init__(self, status, data=None, text=""):
            self.status_code = status
            self._data = data or {}
            self.text = text

        def json(self):
            return self._data

    class MockSession:
        """Mock requests.Session to handle GitHubSession calls."""

        def request(
            self, method, url, params=None, json=None, data=None, headers=None, timeout=None
        ):
            if method == "POST" and "/access_tokens" in url:
                assert json == {"repositories": ["o/r1"], "permissions": {"contents": "read"}}
                return DummyResp(201, {"token": "inst.token", "expires_at": "2099-01-01T00:00:00Z"})
            if method == "DELETE" and url.endswith("/installation/token"):
                assert headers and "token inst.token" in headers.get("Authorization", "")
                return DummyResp(204)
            if method == "GET" and url.endswith("/rate_limit"):
                return DummyResp(200, {"resources": {"core": {"remaining": 5000}}})
            return DummyResp(404)

        def post(self, url, headers=None, json=None, timeout=None, **kwargs):
            return self.request("POST", url, headers=headers, json=json, timeout=timeout)

        def delete(self, url, headers=None, timeout=None, **kwargs):
            return self.request("DELETE", url, headers=headers, timeout=timeout)

        def get(self, url, headers=None, params=None, timeout=None, **kwargs):
            return self.request("GET", url, headers=headers, params=params, timeout=timeout)

        def close(self):
            pass

    # Create mock functions that use MockSession
    mock_session = MockSession()

    def fake_post(url, headers=None, json=None, timeout=None, **kwargs):
        return mock_session.post(url, headers=headers, json=json, timeout=timeout)

    def fake_delete(url, headers=None, timeout=None, **kwargs):
        return mock_session.delete(url, headers=headers, timeout=timeout)

    def fake_get(url, headers=None, params=None, timeout=None, **kwargs):
        return mock_session.get(url, headers=headers, params=params, timeout=timeout)

    # Patch all requests methods and Session
    monkeypatch.setattr(m.requests, "post", fake_post)
    monkeypatch.setattr(m.requests, "delete", fake_delete)
    monkeypatch.setattr(m.requests, "get", fake_get)
    monkeypatch.setattr(m.requests, "Session", MockSession)
    monkeypatch.setattr(m, "_assert_online_allowed", lambda: None)
    monkeypatch.setattr(m, "_mint_app_jwt", lambda app_id, ttl=540: "app.jwt")

    body = m._build_install_token_body("o/r1", "contents=read")
    token, exp = m._exchange_installation_token("app.jwt", "42", body=body)
    assert token == "inst.token", "token is not valid"
    assert exp == "2099-01-01T00:00:00Z", "exp is not valid"
    m._revoke_installation_token(token)


def test_script_main_dry_run_parsing(monkeypatch, capsys):
    m = _import_script()
    monkeypatch.setenv("GITHUB_APP_ID", "1")
    monkeypatch.setenv("GITHUB_APP_INSTALLATION_ID", "2")
    rc = m.main(
        [
            "--action",
            "print-rate-limit",
            "--dry-run",
            "--repos",
            "o/r1",
            "--permissions",
            "contents=read",
        ]
    )
    captured = capsys.readouterr()
    assert rc == 0, "rc is not valid"
    assert '"scoping_parsed": true' in captured.out.lower(), "Condition must be true"
