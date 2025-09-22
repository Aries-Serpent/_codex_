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
