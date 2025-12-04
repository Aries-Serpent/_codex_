from pathlib import Path
import json

import tools.codex_env_snapshot as envsnap


def test_env_snapshot_writes_json_and_markdown(tmp_path: Path, monkeypatch):
    json_out = tmp_path / "snap.json"
    md_out = tmp_path / "snap.md"

    rc = envsnap.main(
        [
            "--json-out",
            str(json_out),
            "--md-out",
            str(md_out),
        ]
    )
    assert rc == 0
    assert json_out.exists()
    assert md_out.exists()

    data = json.loads(json_out.read_text(encoding="utf-8"))
    assert "python" in data
    assert "platform" in data
