import json
from pathlib import Path

from ingestion.utils import write_manifest


def test_write_manifest(tmp_path: Path):
    path = write_manifest("sample", ["src"], 42, {"train": 10}, tmp_path)
    data = json.loads(path.read_text())
    assert data["name"] == "sample" and data["seed"] == 42
    assert "commit" in data
