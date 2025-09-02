from codex_ml.tracking import mlflow_utils as MU


class DummyMLF:
    def __init__(self):
        self.logged = []

    def log_metric(self, k, v, step=None, timestamp=None):
        self.logged.append((k, v, step))


def test_log_metrics_enforces_step(monkeypatch):
    d = DummyMLF()
    monkeypatch.setattr(MU, "_mlf", d)
    MU._HAS_MLFLOW = True
    MU.log_metrics({"loss": 1.23}, step=5, enabled=True)
    assert d.logged == [("loss", 1.23, 5)]
