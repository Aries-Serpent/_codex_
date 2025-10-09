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

    def fake_post(url, headers=None, json=None, timeout=None):
        assert "/access_tokens" in url
        assert json == {"repositories": ["o/r1"], "permissions": {"contents": "read"}}
        return DummyResp(201, {"token": "inst.token", "expires_at": "2099-01-01T00:00:00Z"})

    def fake_delete(url, headers=None, timeout=None):
        assert url.endswith("/installation/token")
        assert headers and "token inst.token" in headers.get("Authorization", "")
        return DummyResp(204)

    def fake_get(url, headers=None, params=None, timeout=None):
        assert url.endswith("/rate_limit")
        return DummyResp(200, {"resources": {"core": {"remaining": 5000}}})

    monkeypatch.setattr(m.requests, "post", fake_post)
    monkeypatch.setattr(m.requests, "delete", fake_delete)
    monkeypatch.setattr(m.requests, "get", fake_get)
    monkeypatch.setattr(m, "_assert_online_allowed", lambda: None)
    monkeypatch.setattr(m, "_mint_app_jwt", lambda app_id, ttl=540: "app.jwt")

    body = m._build_install_token_body("o/r1", "contents=read")
    token, exp = m._exchange_installation_token("app.jwt", "42", body=body)
    assert token == "inst.token"
    assert exp == "2099-01-01T00:00:00Z"
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
    assert rc == 0
    assert '"scoping_parsed": true' in captured.out.lower()
