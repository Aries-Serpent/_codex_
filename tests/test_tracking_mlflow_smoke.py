from pathlib import Path

import pytest

mlflow = pytest.importorskip("mlflow", reason="mlflow not installed")

pytestmark = [pytest.mark.smoke]


def test_mlflow_local_file_backend(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    uri = f"file:{tmp_path / 'mlruns'}"
    monkeypatch.setenv("MLFLOW_TRACKING_URI", uri)

    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("m", 0.123)

    assert any((tmp_path / "mlruns").glob("**/meta.yaml"))
