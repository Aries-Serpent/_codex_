import pytest

pytest.importorskip("mlflow")
"""
Test Unified Training Repro

Test module for unified training repro.
"""

from pathlib import Path

from codex_ml.training import unified_training
from codex_ml.training.strategies import TrainingResult


class _DummyStrategy:
    backend_name = "dummy"

    def run(self, config, callbacks, resume_from=None):  # type: ignore[override]
        return TrainingResult(
            status="ok",
            backend=self.backend_name,
            final_epoch=0,
            output_dir=config.output_dir,
            extra={},
        )


def test_unified_training_captures_environment(monkeypatch, tmp_path):
    env_calls = {}

    def _fake_capture(path):
        env_calls["path"] = Path(path)

    monkeypatch.setattr(unified_training, "capture_environment", _fake_capture)
    monkeypatch.setattr(
        unified_training, "resolve_strategy", lambda *_args, **_kwargs: _DummyStrategy()
    )

    cfg = unified_training.UnifiedTrainingConfig(output_dir=str(tmp_path / "run"), epochs=1)
    result = unified_training.run_unified_training(cfg, callbacks=[], ndjson_log_path=None)

    assert env_calls["path"].name == "environment", "name is not valid"
    assert result["config_version"] == cfg.config_version, "Result must not be empty"
    assert result["dataset_version"] == cfg.dataset_version, "Result must not be empty"
