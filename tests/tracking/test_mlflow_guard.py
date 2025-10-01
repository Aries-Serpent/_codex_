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
