import json
from pathlib import Path

import pytest

from ingestion.utils import write_manifest


@pytest.mark.xfail(reason="write_manifest depends on git repo", strict=False)
def test_write_manifest(tmp_path: Path):
    path = write_manifest("sample", ["src"], 42, {"train": 10}, tmp_path)
    data = json.loads(path.read_text())
    assert data["name"] == "sample" and data["seed"] == 42
    assert "commit" in data
