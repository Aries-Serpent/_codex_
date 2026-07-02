"""
pytest.importorskip("mlflow")
Test Checkpoint Checksum And Retention

Test module for checkpoint checksum and retention.
"""

import json

import pytest

torch = pytest.importorskip("torch", reason="Requires torch for checkpoint hashing test")

from codex_ml.train_loop import run_training


def test_checkpoint_sha256_and_retention(tmp_path):
    ckpt_dir = tmp_path / "ckpts"
    ckpt_dir.mkdir()

    # Run first with 3 epochs; retention keep_last=2
    res = run_training(
        epochs=3,
        steps_per_epoch=2,
        grad_accum=2,
        checkpoint_dir=str(ckpt_dir),
        retention_policy={"keep_last": 2},
    )
    latest = json.loads((ckpt_dir / "latest.json").read_text())
    assert "checkpoint_sha256" in latest, "Condition must be true"
    assert latest["checkpoint_sha256"] == res["checkpoint_sha256_last"], "Condition must be true"
    # After retention: only last 2 epochs should remain
    remaining = sorted(
        [p.name for p in ckpt_dir.iterdir() if p.is_dir() and p.name.startswith("epoch-")]
    )
    assert remaining == ["epoch-0002", "epoch-0003"]

    # Resume to epoch 5; retention keep_last=2 should keep 0004,0005
    res2 = run_training(
        epochs=5,
        steps_per_epoch=1,
        grad_accum=1,
        checkpoint_dir=str(ckpt_dir),
        resume=True,
        retention_policy={"keep_last": 2},
    )
    latest2 = json.loads((ckpt_dir / "latest.json").read_text())
    assert latest2["epoch"] == 5, "Condition must be true"
    rem2 = sorted(
        [p.name for p in ckpt_dir.iterdir() if p.is_dir() and p.name.startswith("epoch-")]
    )
    assert rem2 == ["epoch-0004", "epoch-0005"]
    assert "checkpoint_sha256_last" in res2, "Condition must be true"
    assert latest2["checkpoint_sha256"] == res2["checkpoint_sha256_last"], "Condition must be true"


def test_config_snapshot(tmp_path):
    ckpt_dir = tmp_path / "snap"
    ckpt_dir.mkdir()
    cfg = {"epochs": 1, "foo": {"bar": 42}}
    run_training(
        epochs=1,
        checkpoint_dir=str(ckpt_dir),
        run_config=cfg,
    )
    snap = ckpt_dir / "config.snapshot.json"
    assert snap.exists(), "Condition must be true"
    data = json.loads(snap.read_text())
    assert data["foo"]["bar"] == 42, "Data must not be empty"
