from __future__ import annotations

import json
from pathlib import Path

from codex_ml.utils.provenance import snapshot_hydra_config


def test_provenance_snapshot(tmp_path: Path) -> None:
    cfg = {"a": 1}
    snapshot_hydra_config(cfg, tmp_path, ["a=1"])
    assert (tmp_path / "config.yaml").exists()
    assert (tmp_path / "overrides.txt").read_text().strip() == "a=1"
    info = json.loads((tmp_path / "provenance.json").read_text())
    assert "python" in info
    assert "pip_freeze" in info
