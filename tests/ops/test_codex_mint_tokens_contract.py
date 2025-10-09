from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _import_script():
    root = Path(__file__).resolve().parents[2]
    script_path = root / "scripts" / "ops" / "codex_mint_tokens_per_run.py"
    spec = importlib.util.spec_from_file_location("codex_mint_tokens_per_run", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)  # type: ignore[assignment]
    return module


def test_script_main_dry_run_parsing(monkeypatch, capsys):
    m = _import_script()
    rc = m.main(["--dry-run", "--owner", "octo", "--repo", "codex", "runner-token"])
    assert rc == 0
    captured = capsys.readouterr()
    assert '"scoping_parsed": true' in captured.out.lower()


def test_allowlist_alias_accepts_hosts(monkeypatch):
    m = _import_script()
    monkeypatch.setenv("CODEX_NET_MODE", "online_allowlist")
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
        def post(self, path, timeout=15):  # noqa: ARG002 - contract interface
            assert path.endswith("/actions/runners/registration-token")
            return DummyResp(
                201,
                {"token": "ABCD1234EFGH5678", "expires_at": "2099-01-01T00:00:00Z"},
            )

    m.action_runner_registration_token(DummySession(), owner="o", repo="r", org=None)
    out = capsys.readouterr().out
    assert "token_masked" in out
    assert "ABCD1234EFGH5678" not in out
    assert "…" in out or "\\u2026" in out
