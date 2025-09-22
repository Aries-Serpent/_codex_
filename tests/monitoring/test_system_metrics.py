"""Tests for the psutil-backed system metrics logger."""

from __future__ import annotations

import json
import time

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


def test_system_metrics_logger_warns_and_noops(
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
    monkeypatch.setattr(system_metrics, "_LOGGER_WARNING_CONTEXTS", set())
    monkeypatch.setattr(system_metrics, "SYSTEM_METRICS_DEGRADED", False)

    caplog.set_level("WARNING")
    path = tmp_path / "logger-metrics.jsonl"

    logger = system_metrics.SystemMetricsLogger(path, interval=0.05)
    assert system_metrics.SYSTEM_METRICS_DEGRADED is True

    logger.start()
    logger.stop()

    assert getattr(logger, "_noop", False) is True
    assert not path.exists(), "no-op logger should not emit files"

    missing_psutil = [
        rec
        for rec in caplog.records
        if getattr(rec, "event", None) == "system_metrics.psutil_missing"
    ]
    assert missing_psutil, "expected psutil fallback warning"
    first_warning = missing_psutil[0]
    assert getattr(first_warning, "component", None) == "SystemMetricsLogger"
    assert getattr(first_warning, "sampler", None) == "minimal"

    noop_records = [
        rec
        for rec in caplog.records
        if getattr(rec, "event", None) == "system_metrics.logger_disabled"
    ]
    assert noop_records, "expected no-op logger warning"
    first_noop = noop_records[0]
    assert getattr(first_noop, "component", None) == "SystemMetricsLogger"
    assert "psutil" in getattr(first_noop, "missing", [])


def test_log_system_metrics_warns_and_noops(
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
    monkeypatch.setattr(system_metrics, "_LOGGER_WARNING_CONTEXTS", set())
    monkeypatch.setattr(system_metrics, "SYSTEM_METRICS_DEGRADED", False)

    caplog.set_level("WARNING")
    path = tmp_path / "loop-metrics.jsonl"

    system_metrics.log_system_metrics(path, interval=0.01)

    missing_psutil = [
        rec
        for rec in caplog.records
        if getattr(rec, "event", None) == "system_metrics.psutil_missing"
    ]
    assert any(
        getattr(record, "component", None) == "log_system_metrics" for record in missing_psutil
    ), "expected warning from log_system_metrics fallback"

    noop_records = [
        rec
        for rec in caplog.records
        if getattr(rec, "event", None) == "system_metrics.logger_disabled"
    ]
    assert noop_records, "expected log_system_metrics to issue no-op warning"
    noop = noop_records[0]
    assert getattr(noop, "component", None) == "log_system_metrics"
    assert "psutil" in getattr(noop, "missing", [])
    assert system_metrics.SYSTEM_METRICS_DEGRADED is True
    assert not path.exists(), "no-op log_system_metrics should not write output"
