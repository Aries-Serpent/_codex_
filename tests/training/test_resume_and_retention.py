from __future__ import annotations

import json
from pathlib import Path

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
    )

    assert Path(emitted).name == "epoch-0"
    assert captured["metric_key"] == "acc"
    assert captured["metric_value"] == 0.42
    assert captured["config"]["keep_last"] == 2
    assert captured["config"]["best_k"] == 1
    metadata = json.loads((Path(emitted) / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["metrics"]["acc"] == 0.42


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
            except Exception:
                pass
        return _DummyResult()


def test_run_unified_training_resume_flow(monkeypatch, tmp_path: Path) -> None:
    seen: dict[str, object] = {}

    def fake_load_checkpoint(path: str):
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
        output_dir=str(tmp_path), epochs=1, resume_from="/tmp/ckpt", keep_last=1
    )
    result = run_unified_training(cfg, callbacks=[])

    assert seen["resume_path"] == "/tmp/ckpt"
    assert result["status"] == "ok"
    assert result["resume_from"] == "/tmp/ckpt"
