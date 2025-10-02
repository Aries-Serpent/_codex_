from __future__ import annotations

import importlib
import os
import sys

from codex_ml.utils.mlflow_entrypoints import configure_mlflow_uri


def test_configure_mlflow_blocks_remote_uri(monkeypatch):
    monkeypatch.delenv("CODEX_MLFLOW_ALLOW_REMOTE", raising=False)
    monkeypatch.delenv("CODEX_MLFLOW_LOCAL_DIR", raising=False)
    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)
    effective = configure_mlflow_uri("http://example.invalid")
    assert effective.startswith("file:"), effective
    assert os.environ["MLFLOW_TRACKING_URI"].startswith("file:")
    assert os.environ.get("CODEX_MLFLOW_URI", "").startswith("file:")


def test_sitecustomize_enforces_local_backend(monkeypatch):
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "http://example.invalid")
    monkeypatch.delenv("CODEX_MLFLOW_ALLOW_REMOTE", raising=False)
    monkeypatch.delenv("CODEX_MLFLOW_LOCAL_DIR", raising=False)
    if "sitecustomize" in sys.modules:
        del sys.modules["sitecustomize"]
    module = importlib.import_module("sitecustomize")
    importlib.reload(module)
    assert os.environ["MLFLOW_TRACKING_URI"].startswith("file:")
