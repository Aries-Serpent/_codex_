"""
Latency Metric Adapter

Measures inference latency (time per sample/batch).
"""

import os
import sys
from typing import Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from codex_ml.evaluation.runner import MetricAdapter


class LatencyMetric(MetricAdapter):
    """
    Latency metric adapter.

    Measures inference time per sample or batch.

    Args:
        name: Metric name (default: 'latency_ms')
        per_sample: If True, report per-sample latency; else per-batch

    Example:
        metric = LatencyMetric(per_sample=True)

        start = time.time()
        predictions = model(batch)
        elapsed = time.time() - start

        metric.add_batch_with_time(predictions, targets, elapsed, batch_size=32)
        results = metric.compute()  # {'latency_ms': 15.2, 'throughput': 65.8}
    """

    def __init__(self, name: str = "latency_ms", per_sample: bool = False):
        super().__init__(name)
        self.per_sample = per_sample
        self._total_time = 0.0
        self._total_samples = 0
        self._batch_count = 0

    def add_batch(self, predictions: Any, references: Any) -> None:
        """
        Standard add_batch (no timing info).
        This adapter requires add_batch_with_time() for meaningful results.
        """
        # No-op for standard interface
        # Users should call add_batch_with_time()

    def add_batch_with_time(
        self,
        predictions: Any,
        references: Any,
        elapsed_time: float,
        batch_size: int = 1,
    ) -> None:
        """
        Add batch with timing information.

        Args:
            predictions: Model predictions
            references: Target references
            elapsed_time: Time taken for this batch (seconds)
            batch_size: Number of samples in batch
        """
        self._total_time += elapsed_time
        self._total_samples += batch_size
        self._batch_count += 1

        super().add_batch(predictions, references)

    def compute(self) -> dict[str, float]:
        """Compute latency metrics."""
        if self._batch_count == 0 or self._total_time == 0:
            return {
                self.name: 0.0,
                "throughput_samples_per_sec": 0.0,
            }

        if self.per_sample:
            # Per-sample latency
            avg_latency_sec = self._total_time / self._total_samples
        else:
            # Per-batch latency
            avg_latency_sec = self._total_time / self._batch_count

        avg_latency_ms = avg_latency_sec * 1000
        throughput = self._total_samples / self._total_time

        return {
            self.name: avg_latency_ms,
            "throughput_samples_per_sec": throughput,
            "total_time_sec": self._total_time,
            "total_samples": self._total_samples,
        }

    def reset(self) -> None:
        """Reset accumulated results."""
        super().reset()
        self._total_time = 0.0
        self._total_samples = 0
        self._batch_count = 0
