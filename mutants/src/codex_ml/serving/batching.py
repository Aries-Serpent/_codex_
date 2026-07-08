"""Request batching middleware for lightweight inference tests."""

from __future__ import annotations

import asyncio
import inspect
import logging
import time
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, Optional

from codex_ml.batching.performance import PerformanceMetrics

logger = logging.getLogger(__name__)


@dataclass
class BatchRequest:
    data: Any
    future: asyncio.Future
    timestamp: float = field(default_factory=time.time)


class BatchingMiddleware:
    """Async-friendly batching helper used by inference endpoints."""

    def __init__(
        self,
        process_fn: Callable[[list[Any]], Sequence[Any] | Awaitable[Sequence[Any]]],
        max_batch_size: int = 32,
        max_wait_time: float = 0.1,
    ) -> None:
        self.process_fn = process_fn
        self.max_batch_size = max_batch_size
        self.max_wait_time = max_wait_time
        self.batch_queue: list[BatchRequest] = []
        self.lock = asyncio.Lock()
        self.metrics = PerformanceMetrics()
        self.flush_task: Optional[asyncio.Task] = None

    async def process(self, data: Any) -> Any:
        """Enqueue a request and await the processed result."""

        loop = asyncio.get_running_loop()
        future: asyncio.Future = loop.create_future()
        req = BatchRequest(data=data, future=future)

        async with self.lock:
            self.batch_queue.append(req)
            should_flush_now = len(self.batch_queue) >= self.max_batch_size
            if should_flush_now:
                batch = self._pop_batch_locked()
            else:
                batch = None
                self._schedule_flush_locked()

        if batch:
            await self._execute_batch(batch)

        return await future

    def _schedule_flush_locked(self) -> None:
        """Schedule a flush if one is not already pending."""

        if self.flush_task is not None and not self.flush_task.done():
            return

        task: Optional[asyncio.Task] = None

        async def delayed_flush() -> None:
            try:
                await asyncio.sleep(self.max_wait_time)
                await self._flush_batch()
            finally:
                # Ensure the handle is cleared when the task completes.
                self.flush_task = None

        task = asyncio.create_task(delayed_flush())
        self.flush_task = task

    def _pop_batch_locked(self) -> list[BatchRequest]:
        batch = list(self.batch_queue)
        self.batch_queue.clear()
        return batch

    async def _flush_batch(self) -> None:
        async with self.lock:
            if not self.batch_queue:
                return
            batch = self._pop_batch_locked()
        await self._execute_batch(batch)

    async def _execute_batch(self, batch: list[BatchRequest]) -> None:
        batch_size = len(batch)
        self.metrics.record_batch(batch_size)
        inputs = [r.data for r in batch]

        start = time.time()
        try:
            outputs = self.process_fn(inputs)
            if inspect.isawaitable(outputs):
                outputs = await outputs
        except (ValueError, TypeError, RuntimeError) as exc:  # pragma: no cover - surfaced in tests
            logger.exception("Exception occurred during batch processing")
            for req in batch:
                if not req.future.done():
                    req.future.set_exception(exc)
            raise
        finally:
            logger.debug("Processed batch of %s in %.3fs", batch_size, time.time() - start)

        for req, output in zip(batch, outputs, strict=False):
            latency = time.time() - req.timestamp
            self.metrics.record_request(latency)
            if not req.future.done():
                req.future.set_result(output)

    def get_metrics(self) -> dict[str, Any]:
        return self.metrics.to_dict()

    async def shutdown(self) -> None:
        if self.flush_task is not None and not self.flush_task.done():
            self.flush_task.cancel()
        await self._flush_batch()
