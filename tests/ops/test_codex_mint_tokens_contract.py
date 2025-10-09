from __future__ import annotations

import json
from importlib import import_module


def _import_script():
    return import_module("scripts.ops.codex_mint_tokens_per_run")


def test_script_main_dry_run_parsing(monkeypatch, capsys):
    m = _import_script()
    monkeypatch.setenv("GITHUB_APP_ID", "1234")
    monkeypatch.setenv("GITHUB_APP_INSTALLATION_ID", "5678")
    rc = m.main(
        [
            "--dry-run",
            "--repositories",
            "demo/repo",
            "--permissions",
            "contents=read",
        ]
    )
    captured = capsys.readouterr()
    assert rc == 0
    assert '"scoping_parsed": true' in captured.out.lower()
    data = json.loads(captured.out)
    assert data["scoping"]["repositories"] == ["demo/repo"]
    assert data["scoping"]["permissions"] == {"contents": "read"}


def test_allowlist_alias_accepts_hosts(monkeypatch):
    m = _import_script()
    monkeypatch.setenv("CODEX_NET_MODE", "online_allowlist")
    monkeypatch.delenv("CODEX_NET_ALLOWLIST", raising=False)
    monkeypatch.setenv("CODEX_ALLOWLIST_HOSTS", "api.github.com")
    m._assert_online_allowed()


def test_runner_token_is_masked_only(capsys):
    m = _import_script()

    class DummyResp:
        def __init__(self, status, data=None, text=""):
            self.status_code = status
            self._data = data or {}
            self.text = text

        def json(self):
            return self._data

    class DummySession:
        def post(self, path, timeout=15):
            assert path.endswith("/actions/runners/registration-token")
            return DummyResp(
                201, {"token": "ABCD1234EFGH5678", "expires_at": "2099-01-01T00:00:00Z"}
            )

    m.action_runner_registration_token(DummySession(), owner="o", repo="r", org=None)
    out = capsys.readouterr().out
    assert "token_masked" in out
    assert "ABCD1234EFGH5678" not in out
    assert "…" in out
