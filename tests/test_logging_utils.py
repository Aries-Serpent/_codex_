from __future__ import annotations

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
    writer = init_tensorboard(tmp_path / "tb")
    if writer is None:
        pytest.skip("tensorboard not available")
    log_scalar_tb(writer, "loss", 0.123, step=1)
    writer.flush()
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
    metrics = system_metrics()
    assert "ts" in metrics
    assert isinstance(metrics["ts"], float)
    if "cpu_percent" in metrics:
        assert 0.0 <= metrics["cpu_percent"] <= 100.0
