import importlib
import os
from pathlib import Path
from urllib.parse import urlparse


def test_ensure_file_backend_sets_local_uri(tmp_path, monkeypatch):
    monkeypatch.setenv("CODEX_MLFLOW_LOCAL_DIR", str(tmp_path / "mlruns"))
    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)
    monkeypatch.delenv("CODEX_MLFLOW_URI", raising=False)

    guard = importlib.import_module("codex_ml.tracking.mlflow_guard")
    importlib.reload(guard)

    uri = guard.ensure_file_backend()
    assert uri.startswith("file:")
    path = Path(urlparse(uri).path)
    assert path.exists()
    assert os.environ.get("MLFLOW_TRACKING_URI") == uri
    assert os.environ.get("CODEX_MLFLOW_URI") == uri


def test_plain_paths_are_normalised_to_file_uri(tmp_path, monkeypatch):
    monkeypatch.delenv("CODEX_MLFLOW_LOCAL_DIR", raising=False)
    monkeypatch.setenv("MLFLOW_TRACKING_URI", str(tmp_path / "plain_runs"))
    monkeypatch.delenv("CODEX_MLFLOW_URI", raising=False)

    guard = importlib.import_module("codex_ml.tracking.mlflow_guard")
    importlib.reload(guard)

    uri = guard.ensure_file_backend()
    assert uri.startswith("file:")
    # Normalisation should update both environment variables.
    assert os.environ["MLFLOW_TRACKING_URI"] == uri
    assert os.environ["CODEX_MLFLOW_URI"] == uri
    # The converted directory should exist on disk.
    path = Path(urlparse(uri).path)
    assert path.exists()


def test_bootstrap_blocks_remote_by_default(tmp_path, monkeypatch):
    monkeypatch.delenv("CODEX_MLFLOW_LOCAL_DIR", raising=False)
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "https://example.com/mlflow")
    monkeypatch.delenv("CODEX_MLFLOW_URI", raising=False)
    monkeypatch.delenv("MLFLOW_ALLOW_REMOTE", raising=False)

    guard = importlib.import_module("codex_ml.tracking.mlflow_guard")
    importlib.reload(guard)

    uri = guard.bootstrap_offline_tracking()
    assert uri.startswith("file:")
    assert os.environ["MLFLOW_TRACKING_URI"].startswith("file:")
    assert os.environ["CODEX_MLFLOW_URI"].startswith("file:")


def test_bootstrap_respects_allow_remote(monkeypatch):
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "https://remote.example/mlflow")
    monkeypatch.setenv("MLFLOW_ALLOW_REMOTE", "1")
    monkeypatch.delenv("CODEX_MLFLOW_URI", raising=False)

    guard = importlib.import_module("codex_ml.tracking.mlflow_guard")
    importlib.reload(guard)

    uri = guard.bootstrap_offline_tracking()
    assert uri == "https://remote.example/mlflow"
    assert os.environ["MLFLOW_TRACKING_URI"] == uri
