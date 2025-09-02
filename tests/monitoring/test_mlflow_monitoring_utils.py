from unittest import mock

from codex_ml.monitoring import mlflow_utils


def test_maybe_start_run_none_without_uri(monkeypatch):
    """No URI means no run even when enabled."""
    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)
    monkeypatch.setenv("CODEX_ENABLE_MLFLOW", "1")
    assert mlflow_utils.maybe_start_run() is None


def test_maybe_start_run_respects_env_disable(monkeypatch):
    """Tracking disabled when env flag is unset."""
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "file:/tmp/mlruns")
    monkeypatch.delenv("CODEX_ENABLE_MLFLOW", raising=False)
    assert mlflow_utils.maybe_start_run("r0") is None


def test_maybe_start_run_starts_with_uri_when_enabled(monkeypatch):
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "file:/tmp/mlruns")
    monkeypatch.setenv("CODEX_ENABLE_MLFLOW", "true")
    with mock.patch.object(mlflow_utils, "mlflow") as m:
        run = object()
        m.start_run.return_value = run
        assert mlflow_utils.maybe_start_run("r1") is run
        m.set_tracking_uri.assert_called_once_with("file:/tmp/mlruns")


def test_maybe_start_run_accepts_truthy_env(monkeypatch):
    """Test that truthy environment values are properly handled."""
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "file:/tmp/mlruns")
    monkeypatch.setenv("CODEX_ENABLE_MLFLOW", "true")
    with mock.patch.object(mlflow_utils, "mlflow") as m:
        run = object()
        m.start_run.return_value = run
        assert mlflow_utils.maybe_start_run("r2") is run


def test_maybe_start_run_arg_overrides_env(monkeypatch):
    """Explicit argument should override environment flag."""
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "file:/tmp/mlruns")
    monkeypatch.setenv("CODEX_ENABLE_MLFLOW", "0")
    with mock.patch.object(mlflow_utils, "mlflow") as m:
        run = object()
        m.start_run.return_value = run
        assert mlflow_utils.maybe_start_run("r2", enabled=True) is run
        m.set_tracking_uri.assert_called_once_with("file:/tmp/mlruns")


def test_maybe_start_run_enabled_flag(monkeypatch):
    """Test explicit enabled flag bypasses environment check."""
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "file:/tmp/mlruns")
    monkeypatch.delenv("CODEX_ENABLE_MLFLOW", raising=False)
    with mock.patch.object(mlflow_utils, "mlflow") as m:
        run = object()
        m.start_run.return_value = run
        assert mlflow_utils.maybe_start_run("r3", enabled=True) is run
