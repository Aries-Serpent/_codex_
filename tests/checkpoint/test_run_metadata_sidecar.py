"""
Test Run Metadata Sidecar

Test module for run metadata sidecar.
"""

from __future__ import annotations

import json
from pathlib import Path


def test_run_manifest_sidecar_written(tmp_path: Path) -> None:
    import codex_ml.utils.checkpoint_core as checkpoint_core

    ckpt_dir = tmp_path / "artifacts"
    state = {"weights": [1, 2, 3]}
    checkpoint_core.save_checkpoint(str(ckpt_dir), state)
    manifest = ckpt_dir / "run_manifest.json"
    assert manifest.exists(), "Condition must be true"
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert "python" in payload, "Condition must be true"
    assert "platform" in payload, "Condition must be true"
