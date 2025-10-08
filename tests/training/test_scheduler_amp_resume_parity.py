from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from codex_ml.training import unified_training
from codex_ml.training.strategies import TrainingCallback, TrainingResult
from codex_ml.utils import checkpoint_core


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

    def fake_save(out_dir: str | Path, *, payload, metadata, **kwargs):
        recorded["metadata"] = dict(metadata)
        recorded["payload"] = dict(payload)
        return Path(out_dir) / "state.pt"

    monkeypatch.setattr(checkpoint_core, "save_checkpoint", fake_save)
    monkeypatch.setattr(
        unified_training.strategies, "resolve_strategy", lambda name: _FailingStrategy()
    )

    callback = _NoOpCallback()
    cfg = unified_training.UnifiedTrainingConfig(output_dir=str(tmp_path / "run"), epochs=1)
    result = unified_training.run_unified_training(cfg, callbacks=[callback])
    assert result["status"] == "error"
    assert recorded["metadata"]["metrics"] == {"final_status": 0.0}
