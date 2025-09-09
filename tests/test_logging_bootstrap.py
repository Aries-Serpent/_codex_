from types import SimpleNamespace

from codex_ml.monitoring import codex_logging


def test_codex_logging_bootstrap(monkeypatch):
    class DummyTB:
        def __init__(self, logdir):
            self.logdir = logdir

    class DummyWandb:
        def init(self, project, mode):
            return "wb"

    class DummyMlflow:
        def set_tracking_uri(self, uri):
            self.uri = uri

        def set_experiment(self, exp):
            self.exp = exp

        def start_run(self):
            pass

    monkeypatch.setattr(codex_logging, "SummaryWriter", DummyTB)
    monkeypatch.setattr(codex_logging, "wandb", DummyWandb())
    monkeypatch.setattr(codex_logging, "mlflow", DummyMlflow())

    args = SimpleNamespace(
        hydra_cfg={
            "tensorboard": {"enable": True, "logdir": "./tb"},
            "wandb": {"enable": True, "project": "proj"},
            "mlflow": {"enable": True, "tracking_uri": "./mlruns"},
        }
    )

    loggers = codex_logging._codex_logging_bootstrap(args)
    assert isinstance(loggers.tb, DummyTB)
    assert loggers.wb == "wb"
    assert loggers.mlflow_active is True
