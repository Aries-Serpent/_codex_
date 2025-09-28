from __future__ import annotations

import os

import pytest

mlflow = pytest.importorskip("mlflow")


def test_default_file_backend(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # Make sure user didn't predefine the URI
    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)
    # sitecustomize should set the default upon import
    import importlib
    import sitecustomize

    importlib.reload(sitecustomize)
    assert os.environ.get("MLFLOW_TRACKING_URI", "").startswith("file:")

    with mlflow.start_run():
        mlflow.log_param("p", 1)
    assert (tmp_path / "artifacts" / "mlruns").exists()

