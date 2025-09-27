from __future__ import annotations

import threading
import time

from codex_ml.monitoring.system_metrics import (
    sample_system_metrics,
    start_metrics_logger,
    system_metrics_scalars,
)


def test_sample_system_metrics_basic():
    payload = sample_system_metrics()
    assert isinstance(payload, dict)
    assert "cpu_percent" in payload
    cpu_value = payload.get("cpu_percent")
    assert cpu_value is None or isinstance(cpu_value, (int, float))

    scalars = system_metrics_scalars(payload)
    assert "cpu_percent" in scalars
    assert isinstance(scalars["cpu_percent"], float)
    if "mem_percent" in scalars:
        assert isinstance(scalars["mem_percent"], float)


def test_start_metrics_logger_collects_records():
    records: list[dict[str, object]] = []
    stop_event = threading.Event()

    thread = start_metrics_logger(
        interval_s=0.1,
        write_fn=records.append,
        stop_event=stop_event,
    )

    time.sleep(0.35)
    stop_event.set()
    thread.join(timeout=1.0)

    assert records, "expected at least one metrics sample"
    for entry in records:
        assert isinstance(entry, dict)
        assert "cpu_percent" in entry
