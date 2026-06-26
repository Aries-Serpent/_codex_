"""
Test Unified Logger

Test module for unified logger.
"""

from codex_ml.logging.unified_logger import LoggerBackend, get_logger_registry


class DummyBackend(LoggerBackend):
    def __init__(self):
        self.started = None
        self.ended = False
        self.metrics = []
        self.params = []

    def start_run(self, run_name=None):
        self.started = run_name

    def end_run(self):
        self.ended = True

    def log_metrics(self, metrics, step=None):
        self.metrics.append((dict(metrics), step))

    def log_params(self, params):
        self.params.append(dict(params))


def test_registry_dispatches_to_backends(monkeypatch):
    registry = get_logger_registry()
    registry.backends.clear()

    backend = DummyBackend()
    registry.register("dummy", backend)

    registry.start_run("run-1")
    registry.log_params({"lr": 1e-3})
    registry.log_metrics({"acc": 0.9}, step=1)
    registry.end_run()

    assert backend.started == "run-1", "started is not valid"
    assert backend.ended is True, "ended is not valid"
    assert backend.params == [{"lr": 1e-3}], "params is not valid"
    assert backend.metrics == [({"acc": 0.9}, 1)]
