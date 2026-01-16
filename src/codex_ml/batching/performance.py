"""
Performance Module

This module provides functionality for performance.

Usage:
    from batching.performance import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Optional

_LATENCY_QUANTUM = Decimal("0.0000001")


@dataclass
class PerformanceMetrics:
    """Track batching performance with deterministic accumulation."""

    request_count: int = 0
    batch_count: int = 0
    total_latency: float = 0.0
    latencies: list[float] = field(default_factory=list)
    batch_sizes: list[int] = field(default_factory=list)
    throughput_window: float = 60.0
    window_requests: int = 0
    window_start: float = field(default_factory=time.time)
    _latency_accumulator: Decimal = field(default_factory=lambda: Decimal("0.0"), repr=False)

    def _quantize(self, value: Decimal) -> float:
        return float(value.quantize(_LATENCY_QUANTUM, rounding=ROUND_HALF_UP))

    def record_request(self, latency: float) -> None:
        latency_decimal = Decimal(str(latency))
        self.request_count += 1
        self.latencies.append(float(latency_decimal))
        self._latency_accumulator += latency_decimal
        self.total_latency = self._quantize(self._latency_accumulator)

        now = time.time()
        if now - self.window_start > self.throughput_window:
            self.window_start = now
            self.window_requests = 1
        else:
            self.window_requests += 1

        if len(self.latencies) > 10000:
            self.latencies = self.latencies[-10000:]

    def record_batch(self, batch_size: int) -> None:
        self.batch_count += 1
        self.batch_sizes.append(batch_size)
        if len(self.batch_sizes) > 1000:
            self.batch_sizes = self.batch_sizes[-1000:]

    def get_latency_percentile(self, percentile: float) -> Optional[float]:
        if not self.latencies:
            return None
        sorted_latencies = sorted(self.latencies)
        index = min(int(percentile * len(sorted_latencies)), len(sorted_latencies) - 1)
        return sorted_latencies[index]

    def get_average_latency(self) -> float:
        if self.request_count == 0:
            return 0.0
        avg = self._latency_accumulator / Decimal(str(self.request_count))
        return self._quantize(avg)

    def get_throughput(self) -> float:
        elapsed = time.time() - self.window_start
        if elapsed <= 0:
            return 0.0
        return self.window_requests / elapsed

    def get_average_batch_size(self) -> float:
        if not self.batch_sizes:
            return 0.0
        return sum(self.batch_sizes) / len(self.batch_sizes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_count": self.request_count,
            "batch_count": self.batch_count,
            "average_latency": self.get_average_latency(),
            "latency_p50": self.get_latency_percentile(0.5),
            "latency_p95": self.get_latency_percentile(0.95),
            "latency_p99": self.get_latency_percentile(0.99),
            "throughput_rps": self.get_throughput(),
            "average_batch_size": self.get_average_batch_size(),
        }


__all__ = ["PerformanceMetrics"]
