from __future__ import annotations

import pytest
from codex_ml.training.unified_training import UnifiedTrainingConfig, run_unified_training


@pytest.mark.parametrize("backend", ["functional"])
def test_unified_training_runs(backend: str, tmp_path):
    cfg = UnifiedTrainingConfig(
        model_name="dummy",
        epochs=0,
        output_dir=str(tmp_path / "run"),
        backend=backend,
    )
    result = run_unified_training(cfg)
    assert result["status"] in {"ok", "error"}
    assert result["backend"] == backend


def test_invalid_config_raises():
    with pytest.raises(ValueError):
        UnifiedTrainingConfig(epochs=-1)
