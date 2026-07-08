"""
Benchmark runner for RAG pipeline performance testing.

This module provides utilities for running, timing, and analyzing RAG pipeline benchmarks.
"""

import csv
import json
import logging
import statistics
import time
import tracemalloc
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run."""

    name: str
    duration_ms: float
    memory_mb: float
    success: bool
    error: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class BenchmarkRunner:
    """Runner for executing and timing benchmark functions."""

    def __init__(self, warmup_runs: int = 1):
        """
        Initialize benchmark runner.

        Args:
            warmup_runs: Number of warmup runs before timing
        """
        self.warmup_runs = warmup_runs
        self.results: list[BenchmarkResult] = []

    def run_benchmark(
        self, name: str, func: Callable, *args, runs: int = 5, **kwargs
    ) -> BenchmarkResult:
        """
        Run a benchmark function multiple times and collect metrics.

        Args:
            name: Benchmark name
            func: Function to benchmark
            *args: Positional arguments for func
            runs: Number of timing runs
            **kwargs: Keyword arguments for func

        Returns:
            Aggregated benchmark result
        """
        # Warmup runs
        for _ in range(self.warmup_runs):
            try:
                func(*args, **kwargs)
            except (ValueError, TypeError, RuntimeError):
                logger.debug("Suppressed exception in handler", exc_info=True)
        durations = []
        memory_usage = []
        last_error = None

        for _ in range(runs):
            # Start memory tracking
            tracemalloc.start()
            start_time = time.perf_counter()

            try:
                func(*args, **kwargs)
                success = True
                last_error = None
            except Exception as e:
                success = False
                last_error = str(e)

            end_time = time.perf_counter()
            _current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            duration_ms = (end_time - start_time) * 1000
            memory_mb = peak / (1024 * 1024)

            durations.append(duration_ms)
            memory_usage.append(memory_mb)

        # Calculate statistics
        avg_duration = statistics.mean(durations)
        avg_memory = statistics.mean(memory_usage)

        result = BenchmarkResult(
            name=name,
            duration_ms=avg_duration,
            memory_mb=avg_memory,
            success=success,
            error=last_error,
            metadata={
                "runs": runs,
                "min_duration_ms": min(durations),
                "max_duration_ms": max(durations),
                "p50_duration_ms": statistics.median(durations),
                "p95_duration_ms": self._percentile(durations, 0.95),
                "stddev_duration_ms": statistics.stdev(durations) if len(durations) > 1 else 0.0,
            },
        )

        self.results.append(result)
        return result

    def _percentile(self, data: list[float], percentile: float) -> float:
        """Calculate percentile of data."""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile)
        return sorted_data[min(index, len(sorted_data) - 1)]

    def get_summary(self) -> dict[str, Any]:
        """Get summary statistics of all benchmarks."""
        if not self.results:
            return {}

        return {
            "total_benchmarks": len(self.results),
            "successful": sum(1 for r in self.results if r.success),
            "failed": sum(1 for r in self.results if not r.success),
            "total_duration_ms": sum(r.duration_ms for r in self.results),
            "avg_duration_ms": statistics.mean([r.duration_ms for r in self.results]),
            "total_memory_mb": sum(r.memory_mb for r in self.results),
            "avg_memory_mb": statistics.mean([r.memory_mb for r in self.results]),
        }

    def export_json(self, filepath: str) -> None:
        """Export results to JSON file."""
        data = {
            "summary": self.get_summary(),
            "results": [r.to_dict() for r in self.results],
        }

        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def export_csv(self, filepath: str) -> None:
        """Export results to CSV file."""
        if not self.results:
            return

        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.results[0].to_dict().keys())
            writer.writeheader()
            for result in self.results:
                writer.writerow(result.to_dict())

    def compare_with_baseline(
        self, baseline_file: str, threshold_percent: float = 10.0
    ) -> dict[str, Any]:
        """
        Compare current results with baseline file.

        Args:
            baseline_file: Path to baseline JSON file
            threshold_percent: Acceptable regression threshold percentage

        Returns:
            Comparison results with regressions
        """
        with open(baseline_file) as f:
            baseline_data = json.load(f)

        baseline_results = {r["name"]: r for r in baseline_data.get("results", [])}

        comparisons = []
        regressions = []

        for current in self.results:
            if current.name not in baseline_results:
                continue

            baseline = baseline_results[current.name]
            duration_change = (
                (current.duration_ms - baseline["duration_ms"]) / baseline["duration_ms"] * 100
            )
            memory_change = (
                (current.memory_mb - baseline["memory_mb"]) / baseline["memory_mb"] * 100
            )

            comparison = {
                "name": current.name,
                "duration_change_percent": duration_change,
                "memory_change_percent": memory_change,
                "is_regression": duration_change > threshold_percent,
            }

            comparisons.append(comparison)

            if comparison["is_regression"]:
                regressions.append(comparison)

        return {
            "comparisons": comparisons,
            "regressions": regressions,
            "has_regressions": len(regressions) > 0,
        }
