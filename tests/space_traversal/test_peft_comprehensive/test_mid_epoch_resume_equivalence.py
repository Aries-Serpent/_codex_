from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List

from codex_ml.training import unified_training
from codex_ml.training.strategies import TrainingCallback, TrainingResult
from codex_ml.utils import checkpoint_core


@dataclass
class _CaptureCallback:
    checkpoints: List[Dict[str, Any]]

    def on_epoch_start(
        self, epoch: int, state: Dict[str, Any]
    ) -> None:  # pragma: no cover - unused
        pass

    def on_epoch_end(
        self, epoch: int, metrics: Dict[str, float], state: Dict[str, Any]
    ) -> None:  # pragma: no cover - unused
        pass

    def on_step(
        self, batch_index: int, global_step: int, loss: float, state: Dict[str, Any]
    ) -> None:  # pragma: no cover
        pass

    def on_checkpoint(
        self, epoch: int, path: str, metrics: Dict[str, float], state: Dict[str, Any]
    ) -> None:
        self.checkpoints.append({"metrics": dict(metrics), "state": dict(state)})


class _ResumingStrategy:
    backend_name = "functional"

    def run(
        self, config: Any, callbacks: Iterable[TrainingCallback], *, resume_from: str | None = None
    ) -> TrainingResult:
        for cb in callbacks:
            cb.on_epoch_start(0, {"resume_from": resume_from})
        return TrainingResult(
            status="ok",
            backend=self.backend_name,
            final_epoch=config.epochs,
            output_dir=config.output_dir,
            extra={"resume_from": resume_from},
        )


def test_resume_error_is_recorded(monkeypatch, tmp_path) -> None:
    def fake_save(out_dir: str | Path, *, payload, metadata, **kwargs):
        return Path(out_dir) / "state.pt"

    def fake_load(path: str | Path):
        raise RuntimeError("boom")

    monkeypatch.setattr(checkpoint_core, "save_checkpoint", fake_save)
    monkeypatch.setattr(checkpoint_core, "load_checkpoint", fake_load)
    monkeypatch.setattr(
        unified_training.strategies, "resolve_strategy", lambda name: _ResumingStrategy()
    )

    callback = _CaptureCallback(checkpoints=[])
    cfg = unified_training.UnifiedTrainingConfig(
        output_dir=str(tmp_path / "run"),
        epochs=1,
        resume_from="/tmp/missing",
    )
    result = unified_training.run_unified_training(cfg, callbacks=[callback])
    assert result["status"] == "ok"
    assert callback.checkpoints
    recorded_state = callback.checkpoints[0]["state"]
    assert recorded_state.get("resume_error")
    assert recorded_state.get("resume_from") == "/tmp/missing"
