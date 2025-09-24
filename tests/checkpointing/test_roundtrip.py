from __future__ import annotations

from pathlib import Path

import pytest

from codex_ml.utils.checkpointing import (
    CheckpointLoadError,
    load_training_checkpoint,
    save_checkpoint,
)


class _DummyModel:
    def __init__(self) -> None:
        self._weights: dict[str, int] = {"w": 1}

    def state_dict(self) -> dict[str, int]:
        return dict(self._weights)

    def load_state_dict(self, state_dict: dict[str, int], strict: bool = True) -> None:
        self._weights.update(state_dict)


def test_pickle_roundtrip(tmp_path: Path) -> None:
    model = _DummyModel()
    optimizer_state = {"lr": 0.5}
    scheduler_state = {"step": 10}
    extra = {"epoch": 3}
    ckpt_path = tmp_path / "basic.ckpt"

    save_checkpoint(
        ckpt_path,
        model,
        optimizer_state,
        scheduler_state,
        epoch=4,
        extra=extra,
        format="pickle",
    )

    fresh_model = _DummyModel()
    state = load_training_checkpoint(ckpt_path, fresh_model, None, None, format="pickle")

    assert state["epoch"] == 4
    assert state["extra"]["epoch"] == 3
    assert state["optimizer_state_dict"]["lr"] == 0.5
    assert fresh_model._weights["w"] == 1


def test_corrupt_pickle_checkpoint(tmp_path: Path) -> None:
    bad = tmp_path / "bad.ckpt"
    bad.write_bytes(b"not-a-checkpoint")

    with pytest.raises(CheckpointLoadError):
        load_training_checkpoint(bad, format="pickle")
