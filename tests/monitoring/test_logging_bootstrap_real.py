from argparse import Namespace

import pytest

from codex_ml.monitoring import codex_logging as cl

mlflow = pytest.importorskip("mlflow")


def test_logging_bootstrap_creates_loggers(tmp_path, monkeypatch):
    cfg = {
        "tensorboard": {"enable": True, "logdir": str(tmp_path / "tb")},
        "wandb": {"enable": True, "project": "codex-test"},
        "mlflow": {
            "enable": True,
            "tracking_uri": str(tmp_path / "mlruns"),
            "experiment": "exp",
        },
    }
    monkeypatch.setenv("WANDB_MODE", "offline")
    loggers = cl._codex_logging_bootstrap(Namespace(hydra_cfg=cfg))
    assert loggers.tb is not None
    assert loggers.wb is not None
    assert loggers.mlflow_active
    loggers.tb.close()
    loggers.wb.finish()
    mlflow.end_run()
