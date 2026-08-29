import tempfile

import pytest

pytest.importorskip("mlflow")
"""
Test Unified Training Parity And Resume

Test module for unified training parity and resume.
"""

from __future__ import annotations

import types
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from codex_ml.training import unified_training
from codex_ml.training.strategies import TrainingCallback, TrainingResult
from codex_ml.utils import checkpoint_core


@dataclass
class _RecordingCallback:
    checkpoints: list[dict[str, Any]]

    def on_epoch_start(self, epoch: int, state: dict[str, Any]) -> None:
        pass

    def on_epoch_end(self, epoch: int, metrics: dict[str, float], state: dict[str, Any]) -> None:
        pass

    def on_step(
        self, batch_index: int, global_step: int, loss: float, state: dict[str, Any]
    ) -> None:
        pass

    def on_checkpoint(
        self,
        epoch: int,
        path: str,
        metrics: dict[str, float],
        state: dict[str, Any],
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
    saved: dict[str, Any] = {}

    def fake_save(out_dir: str | Path, *, state=None, payload=None, metadata, **kwargs):
        saved["out_dir"] = Path(out_dir)
        # Accept either 'state' (new) or 'payload' (legacy) kwarg; at least one must be provided.
        checkpoint_data = state if state is not None else payload
        assert checkpoint_data is not None, "fake_save requires either 'state' or 'payload'"
        saved["payload"] = dict(checkpoint_data)
        saved["metadata"] = dict(metadata)
        ckpt_path = Path(out_dir) / "state.pt"
        mock_meta = types.SimpleNamespace(
            sha256=None,
            created_at="2026-02-23T00:00:00Z",
            schema_version=2,
            env={},
            metric_key=None,
            metric_value=None,
            git_sha=None,
            config_hash=None,
            rng=None,
            config_version=None,
            dataset_version=None,
        )
        return ckpt_path, mock_meta

    def fake_load(path: str | Path, **_kwargs: Any):
        saved["loaded"] = str(path)
        state_dict = {"model_state": {"w": 1}, "optimizer_state": {"lr": 0.01}}
        fake_meta = types.SimpleNamespace(sha256=None, rng=None)
        return state_dict, fake_meta

    # Patch the module-level names in unified_training so _emit_checkpoint_epoch
    # and the resume path pick up the fakes regardless of which backend they call.
    monkeypatch.setattr(unified_training, "save_checkpoint", fake_save)
    monkeypatch.setattr(unified_training, "load_checkpoint", fake_load)
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
        resume_from=os.path.join(tempfile.gettempdir(), "resume"),
    )
    result = unified_training.run_unified_training(cfg, callbacks=[callback])

    assert result["status"] == "ok", "Result must not be empty"
    assert saved["loaded"] == os.path.join(tempfile.gettempdir(), "resume"), "Condition must be true"
    assert saved["out_dir"].name == "epoch-2", "name is not valid"
    assert saved["metadata"]["metrics"] == {"final_status": 1.0}, "Data must not be empty"
    assert callback.checkpoints, "Condition must be true"
    resumed_state = callback.checkpoints[0]["state"]
    assert resumed_state.get("resume_loaded") is True, "Condition must be true"
    assert resumed_state.get("resume_payload_keys") == ["model_state", "optimizer_state"]
