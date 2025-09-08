from types import SimpleNamespace

import pytest

from codex_ml.monitoring.codex_logging import _codex_logging_bootstrap


def test_logging_bootstrap(tmp_path):
    pytest.importorskip("wandb")
    pytest.importorskip("mlflow")
    cfg = {
        "tensorboard": {"enable": True, "logdir": str(tmp_path / "tb")},
        "wandb": {"enable": True, "project": "test"},
        "mlflow": {"enable": True, "tracking_uri": str(tmp_path / "mlruns"), "experiment": "test"},
    }
    args = SimpleNamespace(hydra_cfg=cfg)
    loggers = _codex_logging_bootstrap(args)
    assert loggers.tb is not None
    assert loggers.wb is not None
    assert loggers.mlflow_active
    loggers.wb.finish()
    import mlflow

    mlflow.end_run()
