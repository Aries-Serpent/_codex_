"""
Test Logger Fanout Smoke

Test module for logger fanout smoke.
"""

from __future__ import annotations

from typing import Any, Optional

from codex_ml.logging.unified_logger import LoggerBackend, LoggerRegistry


class DummyBackend(LoggerBackend):
    def __init__(self) -> None:
        self.events: list[str] = []
        self.metrics: list[dict[str, Any]] = []
        self.params: list[dict[str, Any]] = []

    def start_run(self, run_name: Optional[str] = None):
        self.events.append(f"start:{run_name}")

    def end_run(self):
        self.events.append("end")

    def log_metrics(self, metrics: dict[str, Any], step: Optional[int] = None):
        self.metrics.append({"metrics": dict(metrics), "step": step})

    def log_params(self, params: dict[str, Any]):
        self.params.append(dict(params))


def test_logger_fanout_two_backends():
    reg = LoggerRegistry()
    a = DummyBackend()
    b = DummyBackend()
    reg.register("dummy-a", a)
    reg.register("dummy-b", b)

    reg.start_run(run_name="smoke")
    reg.log_params({"lr": 0.001, "batch": 8})
    reg.log_metrics({"loss": 1.23, "acc": 0.45}, step=1)
    reg.end_run()

    # Both backends saw events and data
    for backend in (a, b):
        assert backend.events[0].startswith("start:"), "Condition must be true"
        assert backend.events[-1] == "end", "Condition must be true"
        assert backend.params and backend.params[0]["lr"] == 0.001, "Condition must be true"
        assert backend.metrics and backend.metrics[0]["metrics"]["loss"] == 1.23, "Condition must be true"
