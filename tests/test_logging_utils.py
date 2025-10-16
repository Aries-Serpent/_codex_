from pathlib import Path

import pytest

from src.logging_utils import (
    init_tensorboard,
    log_metrics_mlflow,
    log_params_mlflow,
    log_scalar_tb,
    mlflow_run,
    system_metrics,
)


def test_tb_writer_creates_eventfiles(tmp_path: Path):
    tb = init_tensorboard(tmp_path / "tb")
    if tb is None:
        pytest.skip("tensorboard not available")
    log_scalar_tb(tb, "loss", 0.123, step=1)
    tb.flush()
    assert any((tmp_path / "tb").glob("events.*"))


def test_mlflow_offline_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    pytest.importorskip("mlflow", reason="mlflow not installed")
    uri = f"file:{tmp_path / 'mlruns'}"
    monkeypatch.setenv("MLFLOW_TRACKING_URI", uri)
    with mlflow_run(run_name="smoke", offline=True, tracking_dir=tmp_path / "mlruns"):
        log_params_mlflow({"p": 1})
        log_metrics_mlflow({"m": 0.123}, step=1)
    assert any((tmp_path / "mlruns").glob("**/meta.yaml"))


def test_system_metrics_has_keys():
    m = system_metrics()
    assert "ts" in m
    assert isinstance(m["ts"], float)
    if "cpu_percent" in m:
        assert 0.0 <= m["cpu_percent"] <= 100.0
