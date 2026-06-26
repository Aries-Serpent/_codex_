"""
Test Env Snapshot

Test module for env snapshot.
"""

import json
import subprocess
import sys


def test_env_snapshot_writes_file(tmp_path, monkeypatch):
    # Write in temp dir
    cwd = tmp_path
    code = subprocess.call(
        [sys.executable, "-c", "import tools.env_snapshot as s; s.main()"], cwd=str(cwd)
    )
    assert code == 0, "code is not valid"
    p = cwd / "env_snapshot.json"
    assert p.exists(), "Condition must be true"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert "python" in data and isinstance(data["pip_freeze"], list)
