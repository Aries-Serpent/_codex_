import argparse
import types

from codex_ml.monitoring import codex_logging as cl


def test_logging_bootstrap_initialization(monkeypatch, tmp_path):
    calls = {}

    class DummyWriter:
        def __init__(self, logdir):
            calls["tb"] = logdir

        def add_scalar(self, *args, **kwargs):
            pass

    monkeypatch.setattr(cl, "SummaryWriter", DummyWriter)

    def fake_wandb_init(**kw):
        calls["wb"] = kw
        return object()

    monkeypatch.setattr(cl, "wandb", types.SimpleNamespace(init=fake_wandb_init))

    dummy_mlflow = types.SimpleNamespace(
        set_tracking_uri=lambda uri: calls.setdefault("ml_uri", uri),
        set_experiment=lambda exp: calls.setdefault("ml_exp", exp),
        start_run=lambda: calls.setdefault("ml_run", True),
    )
    monkeypatch.setattr(cl, "mlflow", dummy_mlflow)

    cfg = {
        "tensorboard": {"enable": True, "logdir": str(tmp_path)},
        "wandb": {"enable": True, "project": "proj"},
        "mlflow": {"enable": True, "tracking_uri": "uri", "experiment": "exp"},
    }

    loggers = cl._codex_logging_bootstrap(argparse.Namespace(hydra_cfg=cfg))

    assert isinstance(loggers.tb, DummyWriter)
    assert loggers.wb is not None
    assert calls["wb"]["mode"] == "offline" and calls["wb"]["project"] == "proj"
    assert loggers.mlflow_active and calls["ml_uri"] == "uri" and calls["ml_exp"] == "exp"
