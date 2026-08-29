"""
Test Monitoring Mlflow Utils

Test module for monitoring mlflow utils.
"""

import pytest

try:
    from codex_ml.monitoring import mlflow_utils
except ImportError:
    pytest.skip("codex_ml.monitoring module not available", allow_module_level=True)

from unittest import mock


def test_maybe_start_run_none_without_uri(monkeypatch):
    """No URI means no run even when enabled."""
    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)
    monkeypatch.setenv("CODEX_ENABLE_MLFLOW", "1")

    # Mock bootstrap_offline_tracking to return None (simulating no tracking URI available)
    with mock.patch(
        "codex_ml.monitoring.mlflow_utils.bootstrap_offline_tracking"
    ) as mock_bootstrap:
        mock_bootstrap.return_value = None

        # Mock mlflow to ensure start_run is not called
        with mock.patch.object(mlflow_utils, "mlflow") as mock_mlflow:
            result = mlflow_utils.maybe_start_run()

            # Verify behavior
            assert result is None, "Result must not be empty"
            mock_mlflow.start_run.assert_not_called()
            mock_mlflow.set_tracking_uri.assert_not_called()


def test_maybe_start_run_respects_env_disable(monkeypatch):
    """Tracking disabled when env flag is unset."""
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "file:/tmp/mlruns")
    monkeypatch.delenv("CODEX_ENABLE_MLFLOW", raising=False)
    assert mlflow_utils.maybe_start_run("r0") is None, "Condition must be true"


def test_maybe_start_run_starts_with_uri_when_enabled(monkeypatch):
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "file:/tmp/mlruns")
    monkeypatch.setenv("CODEX_ENABLE_MLFLOW", "true")
    with mock.patch.object(mlflow_utils, "mlflow") as m:
        run = object()
        m.start_run.return_value = run
        assert mlflow_utils.maybe_start_run("r1") is run, "Condition must be true"
        m.set_tracking_uri.assert_called_once()
    called_uri = m.set_tracking_uri.call_args[0][0]
    assert isinstance(called_uri, str) and called_uri.startswith("file:")


def test_maybe_start_run_accepts_truthy_env(monkeypatch):
    """Test that truthy environment values are properly handled."""
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "file:/tmp/mlruns")
    monkeypatch.setenv("CODEX_ENABLE_MLFLOW", "true")
    with mock.patch.object(mlflow_utils, "mlflow") as m:
        run = object()
        m.start_run.return_value = run
        assert mlflow_utils.maybe_start_run("r2") is run, "Condition must be true"


def test_maybe_start_run_arg_overrides_env(monkeypatch):
    """Explicit argument should override environment flag."""
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "file:/tmp/mlruns")
    monkeypatch.setenv("CODEX_ENABLE_MLFLOW", "0")
    with mock.patch.object(mlflow_utils, "mlflow") as m:
        run = object()
        m.start_run.return_value = run
        assert mlflow_utils.maybe_start_run("r2", enabled=True) is run
        m.set_tracking_uri.assert_called_once()
    called_uri = m.set_tracking_uri.call_args[0][0]
    assert isinstance(called_uri, str) and called_uri.startswith("file:")


def test_maybe_start_run_enabled_flag(monkeypatch):
    """Test explicit enabled flag bypasses environment check."""
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "file:/tmp/mlruns")
    monkeypatch.delenv("CODEX_ENABLE_MLFLOW", raising=False)
    with mock.patch.object(mlflow_utils, "mlflow") as m:
        run = object()
        m.start_run.return_value = run
        assert mlflow_utils.maybe_start_run("r3", enabled=True) is run
