import json
from pathlib import Path

from codex_ml.io.atomic import atomic_write_json


def test_atomic_write_json_creates_file(tmp_path: Path) -> None:
    target = tmp_path / "meta" / "manifest.json"
    payload = {"x": 1, "nested": {"y": 2}}

    atomic_write_json(target, payload)

    assert target.exists()
    loaded = json.loads(target.read_text(encoding="utf-8"))
    assert loaded == payload
