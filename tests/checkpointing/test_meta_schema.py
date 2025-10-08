from __future__ import annotations

import json

from codex_ml.utils import checkpoint_core


def test_metadata_structure(tmp_path) -> None:
    ckpt_dir = tmp_path / "epoch-7"
    checkpoint_core.save_checkpoint(
        ckpt_dir,
        payload={"model_state": {"w": 1}},
        metadata={"metrics": {"accuracy": 0.9}},
    )
    meta = json.loads((ckpt_dir / "metadata.json").read_text(encoding="utf-8"))
    assert meta["schema_version"] == checkpoint_core.SCHEMA_VERSION
    assert "environment" in meta and "python_version" in meta["environment"]
    assert meta["metrics"]["accuracy"] == 0.9

    sha = (ckpt_dir / "state.sha256").read_text(encoding="utf-8").strip()
    assert sha == meta["digest_sha256"]
