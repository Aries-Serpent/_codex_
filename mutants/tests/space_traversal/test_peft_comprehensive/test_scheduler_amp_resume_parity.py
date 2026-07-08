import pytest

pytest.importorskip("mlflow")
"""
Test Scheduler Amp Resume Parity

Test module for scheduler amp resume parity.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

from codex_ml.training import strategies, unified_training
from codex_ml.training.strategies import TrainingCallback, TrainingResult


class _NoOpCallback:
    def on_epoch_start(self, epoch: int, state):  # pragma: no cover - not used
        pass

    def on_epoch_end(self, epoch: int, metrics, state):  # pragma: no cover - not used
        pass

    def on_step(
        self, batch_index: int, global_step: int, loss: float, state
    ):  # pragma: no cover - not used
        pass

    def on_checkpoint(self, epoch: int, path: str, metrics, state):
        self.metrics = metrics


class _FailingStrategy:
    backend_name = "functional"

    def run(
        self, config: Any, callbacks: Iterable[TrainingCallback], *, resume_from: str | None = None
    ) -> TrainingResult:
        return TrainingResult(
            status="error",
            backend=self.backend_name,
            final_epoch=config.epochs,
            output_dir=config.output_dir,
            extra={},
        )


def test_final_status_reflects_strategy_result(monkeypatch, tmp_path) -> None:
    recorded = {}

    def fake_save(out_dir: str | Path, *, state=None, metadata=None, **kwargs):
        if metadata is not None:
            recorded["metadata"] = dict(metadata)
        if state is not None:
            recorded["payload"] = dict(state)
        path = Path(out_dir) / "state.pt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
        return path, {}

    # Patch the module-level binding in unified_training (not checkpoint_core)
    # because unified_training imports `save_checkpoint` by name at module level.
    # See comment in unified_training.py: "tests can monkeypatch
    # `codex_ml.training.unified_training.save_checkpoint`"
    monkeypatch.setattr(unified_training, "save_checkpoint", fake_save)
    monkeypatch.setattr(strategies, "resolve_strategy", lambda name: _FailingStrategy())

    callback = _NoOpCallback()
    cfg = unified_training.UnifiedTrainingConfig(output_dir=str(tmp_path / "run"), epochs=1)
    result = unified_training.run_unified_training(cfg, callbacks=[callback])
    assert result["status"] == "error", "Result must not be empty"
    assert recorded["metadata"]["metrics"] == {"final_status": 0.0}, "Data must not be empty"
