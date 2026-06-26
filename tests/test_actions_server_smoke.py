"""
Test Actions Server Smoke

Test module for actions server smoke.
"""

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

import pytest


def _get(url: str):
    parts = urlsplit(url)
    if parts.scheme != "http" or parts.hostname != "localhost" or parts.port != 8010:
        raise ValueError(f"unexpected smoke-test URL: {url!r}")
    with urllib.request.urlopen(  # nosec B310 -- test-only controlled URL; scheme/host/port constrained to http://localhost:8010 above  # nosemgrep: python.lang.security.audit.dynamic-urllib-use-detected.dynamic-urllib-use-detected -- URL is constrained to localhost:8010 above
        url, timeout=5
    ) as r:
        return json.loads(r.read().decode("utf-8"))


def test_server_health_and_branches_smoke(tmp_path):
    env = os.environ.copy()
    env.setdefault("CODEX_GH_OWNER", "Aries-Serpent")
    env.setdefault("CODEX_GH_REPO", "_codex_")
    server_script = (Path.cwd() / "tools" / "actions_server.py").resolve()
    p = subprocess.Popen(  # nosemgrep: python.lang.security.audit.dangerous-subprocess-use-tainted-env-args.dangerous-subprocess-use-tainted-env-args -- executable and script path are explicit and shell=False is used
        [sys.executable, str(server_script)], env=env, shell=False
    )
    try:
        time.sleep(1.5)
        assert _get("http://localhost:8010/healthz")["ok"] is True, "Condition must be true"
        branches = _get("http://localhost:8010/repo/branches")
        assert isinstance(branches, list)
    finally:
        p.kill()


def test_assert_safe_github_url_requires_string():
    from tools import actions_server

    with pytest.raises(ValueError, match="must be a string"):
        actions_server._assert_safe_github_url(None)  # type: ignore[arg-type]


def test_gh_post_rejects_spoofed_github_url():
    from tools import actions_server

    with pytest.raises(ValueError, match="must target api.github.com"):
        actions_server.gh_post("https://api.github.com@evil.com/repos/owner/repo", {})
