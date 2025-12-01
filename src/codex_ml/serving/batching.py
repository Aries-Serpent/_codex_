"""Request batching middleware for lightweight inference tests."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from threading import Lock
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for batching and inference."""

    request_count: int = 0
    batch_count: int = 0
    total_latency: float = 0.0
    latencies: List[float] = field(default_factory=list)
    batch_sizes: List[int] = field(default_factory=list)
    throughput_window: float = 60.0
    window_requests: int = 0
    window_start: float = field(default_factory=time.time)

    def record_request(self, latency: float) -> None:
        self.request_count += 1
        self.total_latency += latency
        self.latencies.append(latency)

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
        return self.total_latency / self.request_count

    def get_throughput(self) -> float:
        elapsed = time.time() - self.window_start
        if elapsed == 0:
            return 0.0
        return self.window_requests / elapsed

    def get_average_batch_size(self) -> float:
        if not self.batch_sizes:
            return 0.0
        return sum(self.batch_sizes) / len(self.batch_sizes)

    def to_dict(self) -> Dict[str, Any]:
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


@dataclass
class BatchRequest:
    data: Any
    future: asyncio.Future
    timestamp: float = field(default_factory=time.time)


class BatchingMiddleware:
    def __init__(
        self,
        process_fn: Callable[[List[Any]], List[Any]],
        max_batch_size: int = 32,
        max_wait_time: float = 0.1,
    ) -> None:
        self.process_fn = process_fn
        self.max_batch_size = max_batch_size
        self.max_wait_time = max_wait_time
        self.batch_queue: List[BatchRequest] = []
        self.lock = Lock()
        self.metrics = PerformanceMetrics()
        self.flush_task: Optional[asyncio.Task] = None

    async def process(self, data: Any) -> Any:
        future = asyncio.get_event_loop().create_future()
        req = BatchRequest(data=data, future=future)
        should_flush = False
        with self.lock:
            self.batch_queue.append(req)
            if len(self.batch_queue) >= self.max_batch_size:
                should_flush = True
            elif len(self.batch_queue) == 1:
                self._schedule_flush()

        if should_flush:
            await self._flush_batch()

        return await future

    def _schedule_flush(self) -> None:
        if self.flush_task is not None and not self.flush_task.done():
            return

        async def delayed_flush() -> None:
            await asyncio.sleep(self.max_wait_time)
            await self._flush_batch()

        self.flush_task = asyncio.create_task(delayed_flush())

    async def _flush_batch(self) -> None:
        with self.lock:
            batch = self.batch_queue
            self.batch_queue = []
        if not batch:
            return

        batch_size = len(batch)
        self.metrics.record_batch(batch_size)
        try:
            inputs = [r.data for r in batch]
            start = time.time()
            outputs = self.process_fn(inputs)
            for req, output in zip(batch, outputs):
                latency = time.time() - req.timestamp
                self.metrics.record_request(latency)
                if not req.future.done():
                    req.future.set_result(output)
            logger.debug("Processed batch of %s in %.3fs", batch_size, time.time() - start)
        except Exception as exc:  # pragma: no cover - exercised via tests
            for req in batch:
                if not req.future.done():
                    req.future.set_exception(exc)
            raise

    def get_metrics(self) -> Dict[str, Any]:
        return self.metrics.to_dict()

    async def shutdown(self) -> None:
        if self.flush_task is not None and not self.flush_task.done():
            self.flush_task.cancel()
        await self._flush_batch()

