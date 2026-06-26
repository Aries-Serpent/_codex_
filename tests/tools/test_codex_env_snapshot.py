"""
Test Codex Env Snapshot

Test module for codex env snapshot.
"""

import json
from pathlib import Path

import tools.codex_env_snapshot as snap


def test_env_snapshot_writes_json(tmp_path: Path):
    out = tmp_path / "env.json"
    rc = snap.main(["--out", str(out)])
    assert rc == 0, "rc is not valid"
    assert out.exists(), "Condition must be true"
    data = json.loads(out.read_text(encoding="utf-8"))
    assert "python" in data, "Data must not be empty"
    assert "platform" in data, "Data must not be empty"
