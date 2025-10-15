from __future__ import annotations

import json
from pathlib import Path

import codex_ml.utils.checkpoint_core as checkpoint_core


def test_run_manifest_includes_provenance(tmp_path: Path) -> None:
    ckpt_dir = tmp_path / "artifacts"
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    state = {"weights": [1, 2, 3]}
    checkpoint_core.save_checkpoint(str(ckpt_dir), state)
    manifest_path = ckpt_dir / "run_manifest.json"
    assert manifest_path.exists()
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    provenance = payload.get("provenance")
    assert isinstance(provenance, dict)
    assert "python" in provenance
    assert "git" in provenance
    assert "lock_sha256" in provenance
