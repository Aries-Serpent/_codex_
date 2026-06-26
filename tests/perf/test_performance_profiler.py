"""Tests for the lightweight performance profiler."""

from __future__ import annotations

import json
import time

from codex_ml.perf.profiler import PerformanceProfiler


def test_performance_profiler_collects_timings(tmp_path):
    profiler = PerformanceProfiler()
    with profiler.profile("section"):
        time.sleep(0.001)

    summary = profiler.summary()
    assert "section" in summary, "Condition must be true"
    stats = summary["section"]
    assert stats["count"] == 1, "Count must be greater than zero"
    assert stats["max_s"] >= stats["min_s"], "Value must be greater than zero"

    output = tmp_path / "profiler.jsonl"
    profiler.export_jsonl(output.as_posix())
    payloads = [
        json.loads(line) for line in output.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    assert payloads, "payloads is not valid"
    assert payloads[0]["profiler_section"] == "section", "Condition must be true"
