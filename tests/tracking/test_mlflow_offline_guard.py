import os

import pytest

pytest.importorskip("mlflow")
import mlflow

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
    assert os.environ["MLFLOW_TRACKING_URI"].startswith("file:")


def test_allows_remote_with_explicit_opt_in(monkeypatch):
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
    monkeypatch.setenv(etm.ALLOW_REMOTE_ENV, "1")
    _reset_mlflow_uri()
    uri = etm.ensure_local_tracking()
    assert uri.startswith("http")


def test_respects_existing_local_file_uri(monkeypatch, tmp_path):
    local_uri = f"file:{tmp_path.as_posix()}"
    monkeypatch.setenv("MLFLOW_TRACKING_URI", local_uri)
    monkeypatch.delenv(etm.ALLOW_REMOTE_ENV, raising=False)
    _reset_mlflow_uri()
    uri = etm.ensure_local_tracking()
    assert uri == local_uri
