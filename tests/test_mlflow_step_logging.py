from codex_ml.tracking import mlflow_utils as MU


def test_log_metrics_enforces_step(monkeypatch):
    class Dummy:
        def __init__(self):
            self.logged = []

        def log_metric(self, k, v, step=None):
            self.logged.append((k, v, step))

    dummy = Dummy()
    monkeypatch.setattr(MU, "_mlf", dummy)
    monkeypatch.setattr(MU, "_mlflow_noop_or_raise", lambda enabled: dummy)
    MU.log_metrics({"loss": 1.2}, step=5, enabled=True)
    assert dummy.logged == [("loss", 1.2, 5)]
