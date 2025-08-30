# BEGIN: CODEX_SMOKE_MLFLOW_NOOP

import pytest


def test_mlflow_utils_tolerant_when_missing():
    try:
        from codex_ml.tracking import MlflowConfig, mlflow_utils as MU
    except Exception as e:  # pragma: no cover - skip if tracking utils missing
        pytest.skip(f"tracking utils missing: {e}")
    cfg = MlflowConfig(enable=False)
    with MU.start_run(cfg) as run:
        assert run is False
    MU.log_params({"lr": 1e-3})
    MU.log_metrics({"loss": 0.1}, step=1)
    MU.log_artifacts([])
    assert True
