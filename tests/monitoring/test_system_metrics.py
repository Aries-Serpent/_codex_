"""
Test System Metrics

Test module for system metrics.
"""

from __future__ import annotations

import types

from codex_ml.monitoring import system_metrics as sm


class _Writer:
    def __init__(self) -> None:
        self.values: list[tuple[str, float, int]] = []

    def add_scalar(self, tag: str, value: float, global_step: int) -> None:
        self.values.append((tag, value, global_step))


def test_system_metrics_logger_with_writer(monkeypatch) -> None:
    class _Psutil:
        @staticmethod
        def cpu_percent() -> float:
            return 12.5

        @staticmethod
        def virtual_memory() -> types.SimpleNamespace:
            return types.SimpleNamespace(percent=64.0)

    monkeypatch.setattr(sm, "_PSUTIL", _Psutil)
    logger = sm.SystemMetricsLogger(log_interval=0.0)
    writer = _Writer()
    logger.log(step=5, writer=writer)
    assert writer.values
    assert writer.values[0][0].startswith("system/")


def test_system_metrics_logger_without_psutil(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sm, "_PSUTIL", None)
    logger = sm.SystemMetricsLogger(log_interval=0.0)
    logger.log(step=1)
    captured = capsys.readouterr()
    assert captured.out == ""
