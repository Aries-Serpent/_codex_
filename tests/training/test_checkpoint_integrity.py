from __future__ import annotations

import time
from pathlib import Path

import pytest

from src.codex_ml.utils.checkpoint_core import (
    save_checkpoint,
    load_checkpoint,
    verify_checkpoint,
    load_best,
    CheckpointIntegrityError,
)


def test_roundtrip_and_integrity(tmp_path: Path):
    state = {"weights": [1, 2, 3], "epoch": 1}
    ckpt_path, meta = save_checkpoint(
        tmp_path, state, metric_value=0.321, metric_key="val_loss", mode="min", top_k=3
    )
    assert ckpt_path.exists()
    # Verify checksum and metadata fields
    m2 = verify_checkpoint(ckpt_path)
    assert m2.sha256 and m2.metric_key == "val_loss"
    # Load and compare state
    s2, meta2 = load_checkpoint(ckpt_path)
    assert s2 == state
    assert meta2.sha256 == m2.sha256


def test_corruption_detection(tmp_path: Path):
    state = {"payload": "ok"}
    ckpt_path, _ = save_checkpoint(tmp_path, state, metric_value=1.0)
    # Corrupt: flip last byte
    raw = ckpt_path.read_bytes()
    corrupt = bytearray(raw)
    corrupt[-1] = (corrupt[-1] + 1) % 256
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
    # Only 3 files should remain (best / lowest metric)
    existing = sorted([p for p in tmp_path.glob("*.pt") if p.exists()])
    assert len(existing) == 3
    # Load best and ensure it's the smallest metric (here, the lowest retained metric is 1.0 - 0.4 = 0.6)
    state, meta, best_path = load_best(tmp_path)
    assert meta.metric_value is not None
    # The best should be the last saved (lowest metric): approximately 0.6
    assert pytest.approx(meta.metric_value, rel=0, abs=1e-9) == 0.6
    assert best_path.exists()
