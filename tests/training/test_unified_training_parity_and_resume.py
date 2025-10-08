from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List

from codex_ml.training import unified_training
from codex_ml.training.strategies import TrainingCallback, TrainingResult
from codex_ml.utils import checkpoint_core


@dataclass
class _RecordingCallback:
    checkpoints: List[Dict[str, Any]]

    def on_epoch_start(self, epoch: int, state: Dict[str, Any]) -> None:
        pass

    def on_epoch_end(self, epoch: int, metrics: Dict[str, float], state: Dict[str, Any]) -> None:
        pass

    def on_step(
        self, batch_index: int, global_step: int, loss: float, state: Dict[str, Any]
    ) -> None:
        pass

    def on_checkpoint(
        self,
        epoch: int,
        path: str,
        metrics: Dict[str, float],
        state: Dict[str, Any],
    ) -> None:
        payload = {
            "epoch": epoch,
            "path": path,
            "metrics": dict(metrics),
            "state": dict(state),
        }
        self.checkpoints.append(payload)


class _StubStrategy:
    backend_name = "functional"

    def run(
        self,
        config: Any,
        callbacks: Iterable[TrainingCallback],
        *,
        resume_from: str | None = None,
    ) -> TrainingResult:
        for cb in callbacks:
            cb.on_epoch_start(0, {"resume_from": resume_from})
        for cb in callbacks:
            cb.on_epoch_end(
                config.epochs,
                {"status": 1.0},
                {"resume_from": resume_from},
            )
        return TrainingResult(
            status="ok",
            backend=self.backend_name,
            final_epoch=config.epochs,
            output_dir=config.output_dir,
            extra={"resume_from": resume_from},
        )


def test_unified_training_resume_flow(monkeypatch, tmp_path) -> None:
    saved: Dict[str, Any] = {}

    def fake_save(out_dir: str | Path, *, payload, metadata, **kwargs):
        saved["out_dir"] = Path(out_dir)
        saved["payload"] = dict(payload)
        saved["metadata"] = dict(metadata)
        return Path(out_dir) / "state.pt"

    def fake_load(path: str | Path):
        saved["loaded"] = str(path)
        return {"model_state": {"w": 1}, "optimizer_state": {"lr": 0.01}}

    monkeypatch.setattr(checkpoint_core, "save_checkpoint", fake_save)
    monkeypatch.setattr(checkpoint_core, "load_checkpoint", fake_load)
    monkeypatch.setattr(
        checkpoint_core, "capture_environment_summary", lambda: {"platform": "test"}
    )
    monkeypatch.setattr(
        unified_training.strategies, "resolve_strategy", lambda name: _StubStrategy()
    )

    callback = _RecordingCallback(checkpoints=[])
    cfg = unified_training.UnifiedTrainingConfig(
        output_dir=str(tmp_path / "run"),
        epochs=2,
        resume_from="/tmp/resume",
    )
    result = unified_training.run_unified_training(cfg, callbacks=[callback])

    assert result["status"] == "ok"
    assert saved["loaded"] == "/tmp/resume"
    assert saved["out_dir"].name == "epoch-2"
    assert saved["metadata"]["metrics"] == {"final_status": 1.0}
    assert callback.checkpoints
    resumed_state = callback.checkpoints[0]["state"]
    assert resumed_state.get("resume_loaded") is True
    assert resumed_state.get("resume_payload_keys") == ["model_state", "optimizer_state"]
