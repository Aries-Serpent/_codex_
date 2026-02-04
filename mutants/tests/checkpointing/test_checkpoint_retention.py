"""
Test Checkpoint Retention

Test module for checkpoint retention.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from codex_ml.utils.checkpoint_retention import RetainSpec, retain


def _touch_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def test_retain_ignores_auxiliary_dirs_when_keeping_latest(tmp_path):
    epoch_one = tmp_path / "epoch-1"
    epoch_two = tmp_path / "epoch-2"
    auxiliary = tmp_path / "best"

    for directory in (epoch_one, epoch_two, auxiliary):
        _touch_dir(directory)

    retain(tmp_path, RetainSpec(keep_last=1, best_k=0))

    remaining = {path.name for path in tmp_path.iterdir() if path.is_dir()}
    assert remaining == {"epoch-2", "best"}


def test_retain_best_k_min_and_max(tmp_path):
    metrics = {"epoch-1": 0.9, "epoch-2": 0.5, "epoch-3": 0.7}
    for name, value in metrics.items():
        directory = tmp_path / name
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "metadata.json").write_text(
            json.dumps({"val_loss": value, "val_reward": 1 - value}), encoding="utf-8"
        )

    retain(tmp_path, RetainSpec(keep_last=0, best_k=1, best_metric="val_loss", mode="min"))
    remaining = {path.name for path in tmp_path.iterdir() if path.is_dir()}
    assert remaining == {"epoch-2", "epoch-3"}  # latest plus best

    # Now keep the highest reward instead
    retain(tmp_path, RetainSpec(keep_last=0, best_k=1, best_metric="val_reward", mode="max"))
    remaining = {path.name for path in tmp_path.iterdir() if path.is_dir()}
    assert remaining == {"epoch-2", "epoch-3"}


def test_retain_invalid_mode(tmp_path):
    (tmp_path / "epoch-1").mkdir(parents=True, exist_ok=True)
    with pytest.raises(ValueError):
        retain(tmp_path, RetainSpec(best_k=1, mode="median"))
