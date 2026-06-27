"""Lightweight wall-clock profiler for Codex workflows."""

from __future__ import annotations

import json
import time
from collections.abc import Iterable
from contextlib import contextmanager
from statistics import mean, median


class PerformanceProfiler:
    """Collect execution timings for named sections."""

    def __init__(self) -> None:
        self.timings: dict[str, list[float]] = {}

    @contextmanager  # type: ignore[arg-type]
    def profile(self, name: str) -> Iterable[None]:
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            bucket = self.timings.setdefault(name, [])
            bucket.append(elapsed)

    def summary(self) -> dict[str, dict[str, float]]:
        report: dict[str, dict[str, float]] = {}
        for name, samples in self.timings.items():
            if not samples:
                continue
            report[name] = {
                "count": len(samples),
                "min_s": min(samples),
                "max_s": max(samples),
                "mean_s": mean(samples),
                "median_s": median(samples),
            }
        return report

    def export_jsonl(self, output_path: str) -> None:
        summary = self.summary()
        with open(output_path, "w", encoding="utf-8") as handle:
            for section, stats in summary.items():
                payload = {"profiler_section": section, **stats}
                handle.write(json.dumps(payload) + "\n")


__all__ = ["PerformanceProfiler"]
