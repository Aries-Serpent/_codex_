"""Tests for MLflow step-based logging functionality with comprehensive mock validation."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from unittest.mock import MagicMock

import pytest

from codex_ml.tracking import mlflow_utils as MU


class DummyMLFlowBackend:
    """Comprehensive mock MLflow backend for testing."""

    def __init__(self):
        self.logged_metrics: List[Tuple[str, float, Optional[int]]] = []
        self.logged_params: List[Dict[str, Any]] = []
        self.logged_artifacts: List[str] = []
        self.run_started = False
        self.tracking_uri: Optional[str] = None
        self.experiment: Optional[str] = None

    def log_metric(
        self, key: str, value: float, step: Optional[int] = None, timestamp: Optional[int] = None
    ):
        """Mock log_metric that records calls for verification."""
        self.logged_metrics.append((key, value, step))

    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        """Mock log_metrics for batch logging."""
        for key, value in metrics.items():
            self.log_metric(key, value, step)

    def log_params(self, params: Dict[str, Any]):
        """Mock log_params for parameter logging."""
        self.logged_params.append(dict(params))

    def log_artifacts(self, path: str):
        """Mock log_artifacts for artifact logging."""
        self.logged_artifacts.append(path)

    def set_tracking_uri(self, uri: str):
        """Mock set_tracking_uri."""
        self.tracking_uri = uri

    def set_experiment(self, experiment: str):
        """Mock set_experiment."""
        self.experiment = experiment

    def start_run(self, **kwargs):
        """Mock start_run."""
        self.run_started = True
        return MagicMock()

    def reset(self):
        """Reset all logged data for fresh test state."""
        self.logged_metrics.clear()
        self.logged_params.clear()
        self.logged_artifacts.clear()
        self.run_started = False
        self.tracking_uri = None
        self.experiment = None


@pytest.fixture
def dummy_mlflow():
    """Fixture providing a fresh DummyMLFlowBackend instance."""
    return DummyMLFlowBackend()


@pytest.fixture
def patched_mlflow(monkeypatch, dummy_mlflow):
    """Fixture that patches MLflow with our dummy backend."""
    monkeypatch.setattr(MU, "_mlf", dummy_mlflow, raising=False)
    monkeypatch.setattr(MU, "_HAS_MLFLOW", True, raising=False)

    # Some implementations may use this helper; ensure it returns our dummy when enabled.
    def mock_noop_or_raise(enabled):
        return dummy_mlflow if enabled else None

    monkeypatch.setattr(MU, "_mlflow_noop_or_raise", mock_noop_or_raise, raising=False)
    return dummy_mlflow


def test_log_metrics_enforces_step(patched_mlflow):
    """Test that log_metrics requires and uses the step parameter."""
    dummy = patched_mlflow

    MU.log_metrics({"loss": 1.2}, step=5, enabled=True)

    assert len(dummy.logged_metrics) == 1
    assert dummy.logged_metrics[0] == ("loss", 1.2, 5)


def test_log_metrics_multiple_values(patched_mlflow):
    """Test logging multiple metrics with the same step."""
    dummy = patched_mlflow

    metrics = {"loss": 1.23, "accuracy": 0.95, "f1_score": 0.87}
    MU.log_metrics(metrics, step=10, enabled=True)

    assert len(dummy.logged_metrics) == 3
    expected = [("loss", 1.23, 10), ("accuracy", 0.95, 10), ("f1_score", 0.87, 10)]
    assert dummy.logged_metrics == expected


def test_log_metrics_disabled_noop(patched_mlflow):
    """Test that disabled logging is a no-op."""
    dummy = patched_mlflow

    MU.log_metrics({"loss": 1.0}, step=1, enabled=False)

    assert len(dummy.logged_metrics) == 0


def test_log_metrics_none_enabled_noop(patched_mlflow):
    """Test that enabled=None defaults to disabled behavior."""
    dummy = patched_mlflow

    MU.log_metrics({"loss": 1.0}, step=1, enabled=None)

    assert len(dummy.logged_metrics) == 0


def test_log_metrics_step_extraction(patched_mlflow):
    """Test backwards compatibility with _step key in metrics."""
    dummy = patched_mlflow

    # Test explicit step parameter takes precedence
    MU.log_metrics({"loss": 1.0, "_step": 100}, step=5, enabled=True)
    assert dummy.logged_metrics[0] == ("loss", 1.0, 5)

    # Reset for next test
    dummy.reset()

    # Test _step extraction when no explicit step
    MU.log_metrics({"loss": 2.0, "_step": 15}, step=None, enabled=True)
    assert dummy.logged_metrics[0] == ("loss", 2.0, 15)


def test_log_metrics_empty_dict(patched_mlflow):
    """Test logging empty metrics dictionary."""
    dummy = patched_mlflow

    MU.log_metrics({}, step=1, enabled=True)

    assert len(dummy.logged_metrics) == 0


def test_log_metrics_type_conversion(patched_mlflow):
    """Test that metric values are properly converted to float."""
    dummy = patched_mlflow

    MU.log_metrics({"int_val": 42, "float_val": 3.14}, step=1, enabled=True)

    assert len(dummy.logged_metrics) == 2
    assert dummy.logged_metrics[0][1] == 42
    assert dummy.logged_metrics[1][1] == 3.14


def test_log_metrics_step_zero(patched_mlflow):
    """Test logging with step=0."""
    dummy = patched_mlflow

    MU.log_metrics({"initial_loss": 10.0}, step=0, enabled=True)

    assert dummy.logged_metrics[0] == ("initial_loss", 10.0, 0)


def test_log_metrics_negative_step(patched_mlflow):
    """Test logging with negative step values."""
    dummy = patched_mlflow

    MU.log_metrics({"metric": 1.0}, step=-1, enabled=True)

    assert dummy.logged_metrics[0] == ("metric", 1.0, -1)


def test_log_metrics_large_step(patched_mlflow):
    """Test logging with large step values."""
    dummy = patched_mlflow

    MU.log_metrics({"metric": 1.0}, step=10_000, enabled=True)

    assert dummy.logged_metrics[0] == ("metric", 1.0, 10_000)
