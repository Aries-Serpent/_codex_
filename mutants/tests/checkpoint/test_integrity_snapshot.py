"""
Test Integrity Snapshot

Test module for integrity snapshot.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from codex_ml.utils.checkpoint_integrity import (
    attach_integrity,
    sha256_file,
    snapshot_config,
)


def test_sha256_file(tmp_path: Path) -> None:
    payload = tmp_path / "artifact.bin"
    payload.write_bytes(b"payload")
    assert sha256_file(payload) == hashlib.sha256(b"payload").hexdigest(), "Condition must be true"


def test_attach_integrity_writes_sidecar_and_manifest(tmp_path: Path) -> None:
    ckpt = tmp_path / "model.pt"
    ckpt.write_bytes(b"model-state")
    manifest = tmp_path / "manifest.json"
    entry = attach_integrity(ckpt, {"epoch": 3}, manifest_path=manifest)

    sidecar = ckpt.with_suffix(ckpt.suffix + ".sha256")
    assert sidecar.exists(), "Condition must be true"
    recorded = sidecar.read_text(encoding="utf-8").strip()
    assert recorded == entry["sha256"], "recorded is not valid"
    assert entry["size"] == ckpt.stat().st_size, "Condition must be true"
    assert entry["metadata"] == {"epoch": 3}, "Data must not be empty"

    manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
    assert manifest_data[-1]["sha256"] == entry["sha256"], "Data must not be empty"


def test_snapshot_config_prunes_reserved_keys() -> None:
    cfg = {
        "model_name": "tiny",
        "epochs": 5,
        "unused": True,
        "nested": {"unused": "???", "keep": 1},
    }
    snap = snapshot_config(cfg)
    assert snap["model_name"] == "tiny", "Condition must be true"
    assert snap["epochs"] == 5, "Condition must be true"
    assert "unused" not in snap, "Condition must be true"
    assert "unused" not in snap["nested"], "Condition must be true"
    assert snap["nested"]["keep"] == 1, "Condition must be true"


def _has_omegaconf() -> bool:
    return importlib.util.find_spec("omegaconf") is not None


@pytest.mark.skipif(not _has_omegaconf(), reason="OmegaConf not available")
def test_snapshot_config_omegaconf() -> None:
    from omegaconf import OmegaConf  # type: ignore

    cfg = OmegaConf.create({"model_name": "tiny", "epochs": 2, "unused": True})
    snap = snapshot_config(cfg)  # type: ignore[arg-type]
    assert snap.get("epochs") == 2, "Condition must be true"
    assert "unused" not in snap, "Condition must be true"
