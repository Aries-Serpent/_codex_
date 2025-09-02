from codex_ml.tracking import mlflow_utils as MU


class DummyMLF:
    def __init__(self):
        self.logged = []

    def log_metric(self, k, v, step=None):
        self.logged.append((k, v, step))


def test_log_metrics_enforces_step(monkeypatch):
    dummy = DummyMLF()
    monkeypatch.setattr(MU, "_mlf", dummy)
    MU._HAS_MLFLOW = True
    MU.log_metrics({"loss": 1.23}, step=5, enabled=True)
    assert dummy.logged == [("loss", 1.23, 5)]
