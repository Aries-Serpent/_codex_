from pathlib import Path
import json

import tools.codex_env_snapshot as snap


def test_env_snapshot_writes_json(tmp_path: Path):
    out = tmp_path / "env.json"
    rc = snap.main(["--out", str(out)])
    assert rc == 0
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert "python" in data
    assert "platform" in data
