"""
pytest.importorskip("tensorboard")
Test Logging Utils

Test module for logging utils.
"""

import json
from pathlib import Path

import pytest

import src.logging_utils as logging_utils_mod


def test_tb_writer_creates_eventfiles(tmp_path: Path):
    tb = logging_utils_mod.init_tensorboard(tmp_path / "tb")
    if tb is None:
        pytest.skip("tensorboard not available")
    logging_utils_mod.log_scalar_tb(tb, "loss", 0.123, step=1)
    tb.flush()
    assert any((tmp_path / "tb").glob("events.*")), "Condition must be true"


def test_mlflow_offline_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    pytest.importorskip("mlflow", reason="mlflow not installed")
    uri = f"file:{tmp_path / 'mlruns'}"
    monkeypatch.setenv("MLFLOW_TRACKING_URI", uri)
    monkeypatch.setenv("MLFLOW_ALLOW_FILE_STORE", "true")
    with logging_utils_mod.mlflow_run(
        run_name="smoke", offline=True, tracking_dir=tmp_path / "mlruns"
    ):
        logging_utils_mod.log_params_mlflow({"p": 1})
        logging_utils_mod.log_metrics_mlflow({"m": 0.123}, step=1)
    assert any((tmp_path / "mlruns").glob("**/meta.yaml")), "Condition must be true"


def test_system_metrics_has_keys():
    m = logging_utils_mod.system_metrics()
    assert "ts" in m, "Condition must be true"
    assert isinstance(m["ts"], float)
    if "cpu_percent" in m:
        assert 0.0 <= m["cpu_percent"] <= 100.0, "0 is not valid"


def test_fallback_metrics_writer_emits_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(logging_utils_mod, "psutil", None)
    monkeypatch.setattr(logging_utils_mod, "pynvml", None)

    cfg = logging_utils_mod.LoggingConfig(
        enable_tensorboard=False,
        enable_mlflow=False,
        enable_fallback_metrics=True,
        fallback_metrics_path=tmp_path / "fallback.ndjson",
    )
    session = logging_utils_mod.setup_logging(cfg)
    logging_utils_mod.log_metrics(session, {"loss": 0.42}, step=7)
    fallback_path = Path(cfg.fallback_metrics_path)
    assert fallback_path.exists(), "Condition must be true"
    rows = [
        json.loads(line) for line in fallback_path.read_text(encoding="utf-8").splitlines() if line
    ]
    assert rows and rows[0]["metrics"]["loss"] == pytest.approx(0.42), "rows is not valid"
    assert rows[0]["step"] == 7, "Condition must be true"
    logging_utils_mod.shutdown_logging(session)
