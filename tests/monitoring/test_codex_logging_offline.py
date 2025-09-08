import argparse
import types

from codex_ml.monitoring import codex_logging as cl


def test_logging_bootstrap_offline(monkeypatch, tmp_path):
    calls = {}

    class DummyWriter:
        def __init__(self, log_dir):
            calls["tb"] = log_dir

        def add_scalar(self, *args, **kwargs):
            pass

    monkeypatch.setattr(cl, "SummaryWriter", DummyWriter)

    dummy_wandb = types.SimpleNamespace(init=lambda **kw: calls.setdefault("wb", kw))
    monkeypatch.setattr(cl, "wandb", dummy_wandb)

    dummy_mlflow = types.SimpleNamespace(
        set_tracking_uri=lambda uri: calls.setdefault("ml", uri),
        set_experiment=lambda exp: calls.setdefault("ml_exp", exp),
        start_run=lambda: calls.setdefault("ml_run", True),
    )
    monkeypatch.setattr(cl, "mlflow", dummy_mlflow)

    cfg = {
        "tensorboard": {"enable": True, "logdir": str(tmp_path)},
        "wandb": {"enable": True, "project": "proj"},
        "mlflow": {"enable": True, "tracking_uri": "uri"},
    }
    loggers = cl._codex_logging_bootstrap(argparse.Namespace(hydra_cfg=cfg))
    assert calls["tb"] == str(tmp_path)
    assert calls["wb"]["mode"] == "offline"
    assert loggers.mlflow_active and calls["ml"] == "uri"
