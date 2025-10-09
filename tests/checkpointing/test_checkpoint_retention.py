from __future__ import annotations

from pathlib import Path

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
