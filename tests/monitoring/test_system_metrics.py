"""Tests for the psutil-backed system metrics logger."""

from __future__ import annotations

import json
import time
from typing import Optional

import pytest

from codex_ml.monitoring import system_metrics


@pytest.mark.skipif(not system_metrics.HAS_PSUTIL, reason="psutil not installed")
def test_system_metrics_logger_writes_samples(tmp_path) -> None:
    path = tmp_path / "metrics.jsonl"
    logger = system_metrics.SystemMetricsLogger(path, interval=0.05)
    logger.start()
    try:
        time.sleep(0.2)
    finally:
        logger.stop()

    data = path.read_text(encoding="utf-8").strip().splitlines()
    assert data, "expected at least one metrics record"
    first = json.loads(data[0])
    assert "cpu_percent" in first
    assert "memory" in first


def test_sample_system_metrics_without_psutil(monkeypatch) -> None:
    monkeypatch.setattr(system_metrics, "psutil", None)
    monkeypatch.setattr(system_metrics, "HAS_PSUTIL", False)
    monkeypatch.setattr(
        system_metrics,
        "_CONFIG",
        system_metrics.SystemMetricsConfig(use_psutil=False, poll_gpu=False, use_nvml=False),
    )
    monkeypatch.setattr(system_metrics, "_NVML_DISABLED", True)

    payload = system_metrics.sample_system_metrics()
    assert payload["memory"] is None
    assert "cpu_percent" in payload
    proc = payload.get("process")
    if proc is not None:
        assert "cpu_percent" in proc or "memory_info" in proc


def test_system_metrics_logger_warns_and_writes_stub(
    monkeypatch: pytest.MonkeyPatch, tmp_path, caplog
) -> None:
    monkeypatch.setattr(system_metrics, "psutil", None)
    monkeypatch.setattr(system_metrics, "HAS_PSUTIL", False)
    monkeypatch.setattr(
        system_metrics,
        "_CONFIG",
        system_metrics.SystemMetricsConfig(use_psutil=True, poll_gpu=False, use_nvml=False),
    )
    monkeypatch.setattr(system_metrics, "_NVML_DISABLED", True)
    monkeypatch.setattr(system_metrics, "_PSUTIL_WARNING_CONTEXTS", set())

    caplog.set_level("WARNING")
    path = tmp_path / "logger-metrics.jsonl"

    logger = system_metrics.SystemMetricsLogger(path, interval=0.05)

    warning_records = [
        rec
        for rec in caplog.records
        if getattr(rec, "event", None) == "system_metrics.psutil_missing"
    ]
    assert warning_records, "expected psutil fallback warning"
    first_warning = warning_records[0]
    assert getattr(first_warning, "component", None) == "SystemMetricsLogger"
    assert getattr(first_warning, "sampler", None) == "minimal"

    logger.start()
    try:
        time.sleep(0.2)
    finally:
        logger.stop()

    raw = path.read_text(encoding="utf-8").strip().splitlines()
    assert raw, "expected fallback sampler to write records"
    record = json.loads(raw[0])
    assert record.get("memory") is None
    assert "cpu_count" in record
    assert "ts" in record


def test_log_system_metrics_warns_and_writes_stub(
    monkeypatch: pytest.MonkeyPatch, tmp_path, caplog
) -> None:
    monkeypatch.setattr(system_metrics, "psutil", None)
    monkeypatch.setattr(system_metrics, "HAS_PSUTIL", False)
    monkeypatch.setattr(
        system_metrics,
        "_CONFIG",
        system_metrics.SystemMetricsConfig(use_psutil=True, poll_gpu=False, use_nvml=False),
    )
    monkeypatch.setattr(system_metrics, "_NVML_DISABLED", True)
    monkeypatch.setattr(system_metrics, "_PSUTIL_WARNING_CONTEXTS", set())

    caplog.set_level("WARNING")
    path = tmp_path / "loop-metrics.jsonl"

    class DummyEvent:
        def __init__(self) -> None:
            self._flag = False

        def set(self) -> None:
            self._flag = True

        def is_set(self) -> bool:
            return self._flag

        def wait(self, timeout: Optional[float] = None) -> bool:
            self._flag = True
            return True

    class DummyThread:
        def __init__(self, *args, **kwargs) -> None:
            self._target = kwargs.get("target") or (args[0] if args else None)
            self._alive = False

        def start(self) -> None:
            self._alive = True
            try:
                if self._target:
                    self._target()
            finally:
                self._alive = False

        def is_alive(self) -> bool:
            return self._alive

        def join(self, timeout: Optional[float] = None) -> None:
            self._alive = False

    monkeypatch.setattr(system_metrics.threading, "Event", DummyEvent)
    monkeypatch.setattr(system_metrics.threading, "Thread", DummyThread)

    system_metrics.log_system_metrics(path, interval=0.01)

    warning_records = [
        rec
        for rec in caplog.records
        if getattr(rec, "event", None) == "system_metrics.psutil_missing"
    ]
    assert any(
        getattr(record, "component", None) == "log_system_metrics" for record in warning_records
    ), "expected warning from log_system_metrics fallback"

    raw = path.read_text(encoding="utf-8").strip().splitlines()
    assert raw, "expected fallback sampler to write records"
    payload = json.loads(raw[0])
    assert payload.get("memory") is None
    assert "cpu_count" in payload
