import pytest

pytest.importorskip("mlflow")
"""
Test Training Loop Smoke

Test module for training loop smoke.
"""

from codex_ml.training import loop


def test_train_one_step_reduces_loss():
    assert loop.train_one_step(10.0) < 10.0, "Condition must be true"
