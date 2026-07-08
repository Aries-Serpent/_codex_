"""
Test Resume And Retention

Test module for resume and retention.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from codex_ml.training.rng_checkpoint import RNGState
from codex_ml.training.unified_training import (
    UnifiedTrainingConfig,
    _emit_checkpoint_epoch,
    run_unified_training,
)
from codex_ml.utils.checkpoint_core import CheckpointMeta


def test_emit_checkpoint_respects_retention(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_save_checkpoint(
        path: str,
        *,
        state,
        metric_value,
        metric_key,
        config,
        metadata=None,
        mode="min",
        top_k=3,
        prefix="ckpt",
    ) -> tuple[Path, CheckpointMeta]:
        captured.update(
            {
                "state": state,
                "metric_value": metric_value,
                "metric_key": metric_key,
                "config": config,
                "mode": mode,
                "top_k": top_k,
                "path": path,
            }
        )
        meta = CheckpointMeta(
            schema_version="2",
            created_at=123,
            git_sha="deadbeef",
            config_hash=None,
            rng={},
            env={},
            metric_key=metric_key,
            metric_value=metric_value,
            sha256="cafebabe",
        )
        return Path(path) / "ckpt-test.bin", meta

    monkeypatch.setattr("codex_ml.training.unified_training.save_checkpoint", fake_save_checkpoint)

    cfg = UnifiedTrainingConfig(output_dir=str(tmp_path), keep_last=2, best_k=1, best_metric="acc")
    emitted = _emit_checkpoint_epoch(
        cfg,
        epoch=0,
        state={"backend_name": "dummy", "global_step": 10},
        metrics={"acc": 0.42},
        rng_state=RNGState(),
    )

    assert Path(emitted).name == "epoch-0", "name is not valid"
    assert captured["metric_key"] == "acc", "Condition must be true"
    assert captured["metric_value"] == 0.42, "Value must be initialized"
    assert captured["config"]["keep_last"] == 2, "Condition must be true"
    assert captured["config"]["best_k"] == 1, "Condition must be true"
    metadata = json.loads((Path(emitted) / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["metrics"]["acc"] == 0.42, "Data must not be empty"


class _DummyResult:
    status = "ok"
    backend = "dummy"
    final_epoch = 1
    output_dir = "runs/dummy"


class _DummyStrategy:
    def run(self, cfg, callbacks, resume_from=None):
        for cb in callbacks:
            try:
                cb.on_epoch_end(0, {}, {})
            except (AttributeError, OSError, RuntimeError):
                _ = None  # intentional: dummy strategy ignores callback failures; test validates resume flow
        return _DummyResult()


def test_run_unified_training_resume_flow(monkeypatch, tmp_path: Path) -> None:
    seen: dict[str, object] = {}

    def fake_load_checkpoint(path: str, *, restore_rng: bool = False):
        seen["resume_path"] = path
        return {"model_state": {}}, CheckpointMeta(
            schema_version="2",
            created_at=123,
            git_sha=None,
            config_hash=None,
            rng={},
            env={},
            metric_key=None,
            metric_value=None,
            sha256="cafebabe",
        )

    def fake_save_checkpoint(*args, **kwargs):
        meta = CheckpointMeta(
            schema_version="2",
            created_at=0,
            git_sha=None,
            config_hash=None,
            rng={},
            env={},
            metric_key=None,
            metric_value=None,
            sha256="cafebabe",
        )
        return Path(kwargs.get("path", args[0])) / "ckpt.bin", meta

    monkeypatch.setattr("codex_ml.training.unified_training.load_checkpoint", fake_load_checkpoint)
    monkeypatch.setattr("codex_ml.training.unified_training.save_checkpoint", fake_save_checkpoint)
    monkeypatch.setattr(
        "codex_ml.training.unified_training.resolve_strategy", lambda _: _DummyStrategy()
    )

    cfg = UnifiedTrainingConfig(
        output_dir=str(tmp_path), epochs=1, resume_from=os.path.join(tempfile.gettempdir(), "ckpt"), keep_last=1
    )
    result = run_unified_training(cfg, callbacks=[])

    assert seen["resume_path"] == os.path.join(tempfile.gettempdir(), "ckpt"), "Condition must be true"
    assert result["status"] == "ok", "Result must not be empty"
    assert result["resume_from"] == os.path.join(tempfile.gettempdir(), "ckpt"), "Result must not be empty"
