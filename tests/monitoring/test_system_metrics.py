"""
Test System Metrics

Test module for system metrics.
"""

from __future__ import annotations

import time
import types

from codex_ml.monitoring import system_metrics as sm


class _Writer:
    def __init__(self) -> None:
        self.values: list[tuple[str, float, int]] = []

    def add_scalar(self, tag: str, value: float, global_step: int) -> None:
        self.values.append((tag, value, global_step))


def test_system_metrics_logger_with_writer(monkeypatch) -> None:
    captured: list[tuple[object, dict[str, object]]] = []

    monkeypatch.setattr(
        sm,
        "_ensure_sampler_dependencies",
        lambda *args, **kwargs: sm.SamplerStatus(
            cpu_enabled=True,
            degraded=False,
            gpu_enabled=False,
        ),
    )
    monkeypatch.setattr(
        sm,
        "sample_system_metrics",
        lambda: {"cpu_percent": 12.5, "memory": types.SimpleNamespace(percent=64.0)},
    )
    monkeypatch.setattr(sm, "_write_record", lambda path, record: captured.append((path, record)))

    logger = sm.SystemMetricsLogger(path="metrics.jsonl", interval=0.1)
    logger.start()
    try:
        deadline = time.monotonic() + 1.0
        while not captured and time.monotonic() < deadline:
            time.sleep(0.01)
    finally:
        logger.stop()

    assert captured, "captured is not valid"
    assert captured[0][0] == logger._path, "Condition must be true"
    assert captured[0][1]["cpu_percent"] == 12.5, "Condition must be true"


def test_system_metrics_logger_without_psutil(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        sm,
        "_ensure_sampler_dependencies",
        lambda *args, **kwargs: sm.SamplerStatus(
            cpu_enabled=False,
            degraded=True,
            gpu_enabled=False,
            missing_dependencies=("psutil",),
        ),
    )
    logger = sm.SystemMetricsLogger(path="metrics.jsonl", interval=0.1)
    logger.start()
    captured = capsys.readouterr()
    assert logger._thread is None, "_thread is not valid"
    assert captured.out == "", "out is not valid"
