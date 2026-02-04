"""
Test Minimal Train Cli

Test module for minimal train cli.
"""

from codex_ml.cli import minimal_train


def test_run_minimal_produces_reasonable_metrics():
    result = minimal_train.run_minimal(experiment_name=None)

    assert result.loss_after < result.loss_before
    assert 0.0 <= result.score <= 1.0
