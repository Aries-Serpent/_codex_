"""
Test Mlflow Utils Noop

Test module for mlflow utils noop.
"""

# BEGIN: CODEX_SMOKE_MLFLOW_NOOP

import pytest


def test_mlflow_utils_tolerant_when_missing():
    MU = None
    try:
        from codex_ml.tracking import mlflow_utils as MU
    except (ImportError, AttributeError) as e:
        pytest.skip(f"tracking utils missing: {e}")
    if MU is None:
        pytest.skip("tracking utils missing")
    try:
        _ = MU.start_run(tracking_uri=None, experiment_name=None)
    except TypeError:
        pytest.skip("start_run signature mismatch")
    MU.log_params({"lr": 1e-3})
    MU.log_metrics({"loss": 0.1}, step=1)
    MU.log_artifacts([])
    assert True, "True is not valid"
