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
    monkeypatch.setenv("CODEX_ENABLE_MLFLOW", "1")
    with mock.patch.object(mlflow_utils, "mlflow") as m:
        run = object()
        m.start_run.return_value = run
        assert mlflow_utils.maybe_start_run("r1") is run
        m.set_tracking_uri.assert_called_once_with("file:/tmp/mlruns")
