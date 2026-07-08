"""
Test Checkpoint Integrity

Test module for checkpoint integrity.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from codex_ml.utils.checkpoint_core import (
    CheckpointIntegrityError,
    load_best,
    load_checkpoint,
    save_checkpoint,
    verify_checkpoint,
)


def test_roundtrip_and_integrity(tmp_path: Path):
    state = {"weights": [1, 2, 3], "epoch": 1}
    ckpt_path, _meta = save_checkpoint(
        tmp_path,
        state,
        metric_value=0.321,
        metric_key="val_loss",
        mode="min",
        top_k=3,
        include_rng=False,
    )
    assert ckpt_path.exists(), "Condition must be true"
    # Verify checksum and metadata fields
    m2 = verify_checkpoint(ckpt_path)
    assert m2.sha256 and m2.metric_key == "val_loss", "metric_key is not valid"
    # Load and compare state
    s2, meta2 = load_checkpoint(ckpt_path)
    assert s2 == state, "s2 is not valid"
    assert meta2.sha256 == m2.sha256, "sha256 is not valid"


def test_corruption_detection(tmp_path: Path):
    state = {"payload": "ok"}
    ckpt_path, _ = save_checkpoint(tmp_path, state, metric_value=1.0)
    # Corrupt: flip a byte in the middle of the file (last byte may be
    # trailing pickle padding that is silently ignored on deserialisation)
    raw = ckpt_path.read_bytes()
    corrupt = bytearray(raw)
    corrupt[len(corrupt) // 2] ^= 0xFF
    ckpt_path.write_bytes(bytes(corrupt))
    with pytest.raises(CheckpointIntegrityError):
        verify_checkpoint(ckpt_path)
    with pytest.raises(CheckpointIntegrityError):
        load_checkpoint(ckpt_path)


def test_best_k_retention(tmp_path: Path):
    # Save 5 checkpoints with decreasing loss; keep top_k=3 (mode=min)
    paths = []
    for i in range(5):
        p, _ = save_checkpoint(
            tmp_path, {"epoch": i}, metric_value=1.0 - (i * 0.1), top_k=3, prefix=f"ckpt{i}"
        )
        paths.append(p)
        time.sleep(0.01)  # ensure distinct names
    # Only 3 checkpoint files should remain (best / lowest metric).
    # state.pt is a compatibility alias for the latest checkpoint and is excluded.
    existing = sorted([p for p in tmp_path.glob("*.pt") if p.exists() and p.name != "state.pt"])
    assert len(existing) == 3, "Existing must not be empty"
    # Load best and ensure it's the smallest metric (here, the lowest retained metric is 1.0 - 0.4 = 0.6)
    _state, meta, best_path = load_best(tmp_path)
    assert meta.metric_value is not None, "metric_value must be initialized"
    # The best should be the last saved (lowest metric): approximately 0.6
    assert pytest.approx(meta.metric_value, rel=0, abs=1e-9) == 0.6
    assert best_path.exists(), "Condition must be true"
