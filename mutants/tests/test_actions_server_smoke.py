"""
Test Actions Server Smoke

Test module for actions server smoke.
"""

import json
import os
import subprocess
import time
import urllib.request


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
