from __future__ import annotations

import time

from codex.archive.perf import TimingMetrics, measure_decompression, timer


def test_timer_measures_elapsed_time() -> None:
    with timer("example") as metrics:
        time.sleep(0.001)

    assert metrics.duration_ms > 0
    payload = metrics.to_dict()
    assert payload["name"] == "example"
    assert payload["duration_ms"] >= metrics.duration_ms - 0.001


def test_measure_decompression_records_metrics() -> None:
    @measure_decompression("work")
    def work(x: int) -> int:
        return x * 2

    result = work(3)
    metrics: TimingMetrics = work.last_metrics  # type: ignore[assignment]

    assert result == 6
    assert isinstance(metrics, TimingMetrics)
    assert metrics.name == "work"
