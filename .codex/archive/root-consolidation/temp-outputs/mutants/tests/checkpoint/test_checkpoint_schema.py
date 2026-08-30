"""
Test Checkpoint Schema

Test module for checkpoint schema.
"""

from __future__ import annotations

import json
from pathlib import Path

from codex_ml.utils.checkpoint_core import SCHEMA_VERSION, save_checkpoint


def test_checkpoint_schema_v2(tmp_path: Path):
    out = tmp_path / "epoch-0"
    save_checkpoint(
        out, payload={"model_state": {}}, metadata={"epoch": 0, "metrics": {"val_loss": 1.23}}
    )
    meta = json.loads((out / "metadata.json").read_text(encoding="utf-8"))
    assert meta["schema_version"] == SCHEMA_VERSION, "Condition must be true"
    assert "digest_sha256" in meta, "Condition must be true"
    assert "environment" in meta, "Condition must be true"
