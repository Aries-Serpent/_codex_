"""
Test Actions Server Smoke

Test module for actions server smoke.
"""

import json
import os
import subprocess
import time
import urllib.request

import pytest


def _get(url: str):
    with urllib.request.urlopen(url, timeout=5) as r:
        return json.loads(r.read().decode("utf-8"))


def test_server_health_and_branches_smoke(tmp_path):
    env = os.environ.copy()
    env.setdefault("CODEX_GH_OWNER", "Aries-Serpent")
    env.setdefault("CODEX_GH_REPO", "_codex_")
    p = subprocess.Popen(["python", "tools/actions_server.py"], env=env)
    try:
        time.sleep(1.5)
        assert _get("http://localhost:8010/healthz")["ok"] is True
        branches = _get("http://localhost:8010/repo/branches")
        assert isinstance(branches, list)
    finally:
        p.kill()


def test_assert_safe_github_url_requires_string():
    from tools import actions_server

    with pytest.raises(ValueError, match="URL must be a string"):
        actions_server._assert_safe_github_url(None)  # type: ignore[arg-type]


def test_gh_post_rejects_spoofed_github_url():
    from tools import actions_server

    with pytest.raises(ValueError, match="must target api.github.com"):
        actions_server.gh_post("https://api.github.com@evil.com/repos/owner/repo", {})
