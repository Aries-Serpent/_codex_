"""
Test Github Connector Check

Test module for github connector check.
"""

import subprocess
import sys


def test_connector_offline_ok(tmp_path, monkeypatch):
    cfg = {
        "endpoint": "https://api.github.com",
        "repo": "Aries-Serpent/_codex_",
        "auth": {"env_token_keys": ["GH_TOKEN", "GITHUB_TOKEN"], "required": False},
        "offline_ok": True,
        "timeouts": {"connect_seconds": 1, "read_seconds": 1},
    }
    p = tmp_path / "configs/connectors"
    p.mkdir(parents=True, exist_ok=True)
    (p / "github_connector.config.json").write_text(__import__("json").dumps(cfg), encoding="utf-8")
    code = subprocess.call(
        [sys.executable, "-c", "import tools.connectors.github_connector_check as c; c.main()"],
        cwd=str(tmp_path),
    )
    assert code == 0, "code is not valid"
