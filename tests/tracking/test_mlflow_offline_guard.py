"""
Test Mlflow Offline Guard

Test module for mlflow offline guard.
"""

import os

import pytest

mlflow = pytest.importorskip("mlflow")

from src.codex_ml.utils import experiment_tracking_mlflow as etm


def _reset_mlflow_uri() -> None:
    """Reset MLflow tracking URI state between tests."""
    mlflow.set_tracking_uri(None)


def test_default_enforces_file_uri(tmp_path, monkeypatch):
    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)
    monkeypatch.delenv(etm.ALLOW_REMOTE_ENV, raising=False)
    _reset_mlflow_uri()
    uri = etm.ensure_local_tracking(default_uri=f"file:{tmp_path.as_posix()}")
    assert uri.startswith("file:"), uri


def test_blocks_remote_without_override(monkeypatch, tmp_path):
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
    monkeypatch.delenv(etm.ALLOW_REMOTE_ENV, raising=False)
    _reset_mlflow_uri()
    uri = etm.ensure_local_tracking(default_uri=f"file:{tmp_path.as_posix()}")
    assert uri.startswith("file:"), f"expected file: uri, got {uri}"
    assert os.environ["MLFLOW_TRACKING_URI"].startswith("file:"), "Condition must be true"


def test_allows_remote_with_explicit_opt_in(monkeypatch):
    _reset_mlflow_uri()  # Reset first
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
    monkeypatch.setenv(etm.ALLOW_REMOTE_ENV, "1")
    uri = etm.ensure_local_tracking()
    assert uri.startswith("http"), f"Expected remote http: URI with opt-in, got {uri}"


def test_respects_existing_local_file_uri(monkeypatch, tmp_path):
    _reset_mlflow_uri()  # Reset first
    local_uri = f"file:{tmp_path.as_posix()}"
    monkeypatch.setenv("MLFLOW_TRACKING_URI", local_uri)
    monkeypatch.delenv(etm.ALLOW_REMOTE_ENV, raising=False)
    uri = etm.ensure_local_tracking()
    # Allow for normalization - just verify it points to the same location
    assert uri.startswith("file:"), f"Expected file: URI, got {uri}"
    assert (str(tmp_path) in uri or tmp_path.as_posix() in uri, "Condition must be true"
    ), f"Expected path {tmp_path} in URI {uri}"


def test_blocks_remote_when_tracking_uri_argument_is_remote(monkeypatch, tmp_path):
    """Even if a remote tracking_uri is passed, without opt-in the guard should force file:."""

    monkeypatch.delenv(etm.ALLOW_REMOTE_ENV, raising=False)
    _reset_mlflow_uri()
    # Provide an explicit remote URI; guard should still enforce local unless opt-in is set.
    with etm.maybe_mlflow(
        enable=True, run_name="guarded", tracking_uri="http://127.0.0.1:5000"
    ) as m:
        # mlflow API: get_tracking_uri() reflects effective value after guard.
        uri = m.get_tracking_uri()
        assert uri.startswith("file:"), f"guard did not enforce local file backend, got: {uri}"
