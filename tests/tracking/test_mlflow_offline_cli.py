import pytest

from examples.mlflow_offline import run_smoke

mlflow = pytest.importorskip("mlflow")


def test_mlflow_offline_smoke_enforces_file_uri(tmp_path, monkeypatch):
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "http://example.com")
    uri = run_smoke(tmp_path)
    assert uri.startswith("file:"), uri
    assert mlflow.get_tracking_uri().startswith("file:")
