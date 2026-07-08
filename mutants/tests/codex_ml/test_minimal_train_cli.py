import pytest

pytest.importorskip("mlflow")
"""
Test Minimal Train Cli

Test module for minimal train cli.
"""

from codex_ml.cli import minimal_train


def test_run_minimal_produces_reasonable_metrics():
    result = minimal_train.run_minimal(experiment_name=None)

    assert result.loss_after < result.loss_before, "Result must not be empty"
    assert 0.0 <= result.score <= 1.0, "Result must not be empty"
