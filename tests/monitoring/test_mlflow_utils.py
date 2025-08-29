import os
from unittest import mock

from codex_ml.monitoring import mlflow_utils


def test_maybe_start_run_none_without_uri(monkeypatch):
    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)
    assert mlflow_utils.maybe_start_run() is None


def test_maybe_start_run_starts_with_uri(monkeypatch):
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "file:/tmp/mlruns")
    with mock.patch.object(mlflow_utils, "mlflow") as m:
        run = object()
        m.start_run.return_value = run
        assert mlflow_utils.maybe_start_run("r1") is run
        m.set_tracking_uri.assert_called_once_with("file:/tmp/mlruns")
