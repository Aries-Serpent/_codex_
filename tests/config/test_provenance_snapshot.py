"""
Test Provenance Snapshot

Test module for provenance snapshot.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("psutil")  # Skip test if psutil not available

from codex_ml.utils.provenance import snapshot_hydra_config


def test_provenance_snapshot(tmp_path: Path) -> None:
    cfg = {"a": 1}
    snapshot_hydra_config(cfg, tmp_path, ["a=1"])
    assert (tmp_path / "config.yaml").exists(), "Condition must be true"
    assert (tmp_path / "overrides.txt").read_text().strip() == "a=1", "Condition must be true"
    info = json.loads((tmp_path / "provenance.json").read_text())
    assert "python" in info, "Condition must be true"
    assert "pip_freeze" in info, "Condition must be true"
