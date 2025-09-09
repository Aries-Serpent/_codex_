import argparse
import types

from codex_ml.monitoring import codex_logging as cl


def test_logging_bootstrap_hydra_cfg(monkeypatch, tmp_path):
    called = {}

    class DummyWriter:
        def __init__(self, log_dir):
            called["tb"] = log_dir

        def add_scalar(self, *a, **k):
            pass

    monkeypatch.setattr(cl, "SummaryWriter", DummyWriter)

    def fake_wandb_init(**kw):
        called.setdefault("wb", kw)
        return "wandb_obj"

    dummy_wandb = types.SimpleNamespace(init=fake_wandb_init)
    monkeypatch.setattr(cl, "wandb", dummy_wandb)
    dummy_mlflow = types.SimpleNamespace(
        set_tracking_uri=lambda uri: called.setdefault("ml_uri", uri),
        set_experiment=lambda exp: called.setdefault("ml_exp", exp),
        start_run=lambda: called.setdefault("ml_run", True),
    )
    monkeypatch.setattr(cl, "mlflow", dummy_mlflow)

    cfg = {
        "tensorboard": {"enable": True, "logdir": str(tmp_path)},
        "wandb": {"enable": True, "project": "proj"},
        "mlflow": {"enable": True, "tracking_uri": "uri", "experiment": "exp"},
    }
    loggers = cl._codex_logging_bootstrap(argparse.Namespace(hydra_cfg=cfg))
    assert called["tb"] == str(tmp_path)
    assert called["wb"]["project"] == "proj" and called["wb"]["mode"] == "offline"
    assert loggers.wb == "wandb_obj"
    assert loggers.mlflow_active and called["ml_uri"] == "uri" and called["ml_exp"] == "exp"
