from __future__ import annotations

from pathlib import Path

from codex_ml.training.unified_training import (
    UnifiedTrainingConfig,
    _emit_checkpoint_epoch,
    run_unified_training,
)


def test_emit_checkpoint_respects_retention(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_save_checkpoint(
        path: str,
        *,
        payload,
        metadata,
        include_rng,
        keep_last,
        best_k,
        best_metric,
    ) -> None:
        captured.update({
            "keep_last": keep_last,
            "best_k": best_k,
            "best_metric": best_metric,
            "path": path,
        })

    monkeypatch.setattr("codex_ml.training.unified_training.save_checkpoint", fake_save_checkpoint)
    monkeypatch.setattr("codex_ml.training.unified_training.capture_environment_summary", lambda: {})

    cfg = UnifiedTrainingConfig(output_dir=str(tmp_path), keep_last=2, best_k=1, best_metric="acc")
    emitted = _emit_checkpoint_epoch(cfg, epoch=0, state={}, metrics={})

    assert Path(emitted).name == "epoch-0"
    assert captured["keep_last"] == 2
    assert captured["best_k"] == 1
    assert captured["best_metric"] == "acc"


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
        return {"model_state": {}}

    def fake_save_checkpoint(*args, **kwargs):
        return None

    monkeypatch.setattr("codex_ml.training.unified_training.load_checkpoint", fake_load_checkpoint)
    monkeypatch.setattr("codex_ml.training.unified_training.save_checkpoint", fake_save_checkpoint)
    monkeypatch.setattr("codex_ml.training.unified_training.resolve_strategy", lambda _: _DummyStrategy())
    monkeypatch.setattr("codex_ml.training.unified_training.capture_environment_summary", lambda: {})

    cfg = UnifiedTrainingConfig(output_dir=str(tmp_path), epochs=1, resume_from="/tmp/ckpt", keep_last=1)
    result = run_unified_training(cfg, callbacks=[])

    assert seen["resume_path"] == "/tmp/ckpt"
    assert result["status"] == "ok"
    assert result["resume_from"] == "/tmp/ckpt"
