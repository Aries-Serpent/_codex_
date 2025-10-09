from __future__ import annotations

import json
from importlib import import_module


def _m():
    return import_module("scripts.ops.codex_repo_admin_bootstrap")


def test_dry_run_shape_and_flags(capsys):
    m = _m()
    rc = m.main(["--owner", "o", "--repo", "r"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["dry_run"] is True
    plan = out["plan"]
    assert plan["target"]["owner"] == "o"
    assert plan["target"]["repo"] == "r"
    assert isinstance(plan["repo_settings"], dict)
    assert isinstance(plan["branch_protection"], dict)
    assert isinstance(plan["labels"], list)


def test_detect_default_branch_in_apply_mode(monkeypatch):
    m = _m()

    class FakeResp:
        def __init__(self, status, json_data=None):
            self.status_code = status
            self._json = json_data or {}
            self.text = json.dumps(self._json)

        def json(self):
            return self._json

    calls = {"get_repo": 0}

    def fake_request(self, method, path, **kwargs):
        if method == "GET" and path.startswith("/repos/") and path.count("/") == 2:
            calls["get_repo"] += 1
            return FakeResp(200, {"default_branch": "trunk"})
        return FakeResp(202, {})

    import scripts.ops.codex_repo_admin_bootstrap as mod

    monkeypatch.setenv("CODEX_NET_MODE", "online_allowlist")
    monkeypatch.setenv("CODEX_ALLOWLIST_HOSTS", "api.github.com")
    monkeypatch.setenv("GITHUB_TOKEN", "x" * 40)

    mod.GitHubSession._request = fake_request  # type: ignore[method-assign]

    rc = m.main(["--owner", "o", "--repo", "r", "--apply", "--detect-default-branch"])
    assert rc == 0
    assert calls["get_repo"] == 1
