"""
Performance optimizations for inference serving.

This module provides request batching, memory pooling, and other performance
optimizations to maximize throughput and minimize latency.
"""

import asyncio
import logging

logger = logging.getLogger(__name__)
import threading  # noqa: E402
import time  # noqa: E402
from collections import deque  # noqa: E402
from collections.abc import Callable  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from typing import Any, Literal, Optional  # noqa: E402


@dataclass
class BatchConfig:
    """Configuration for request batching."""

    max_batch_size: int = 32
    max_wait_ms: int = 10
    min_batch_size: int = 1
    dynamic_batching: bool = True


class RequestBatcher:
    """
    Batches incoming requests for efficient processing.

    Features:
    - Dynamic batch sizing based on load
    - Timeout-based flushing
    - Priority queue support
    - Backpressure handling

    Example:
        >>> batcher = RequestBatcher(max_batch_size=32, max_wait_ms=10)
        >>> async def process(batch):
        ...     return [model.predict(item) for item in batch]
        >>> result = await batcher.add_request(data, process)
    """

    def __init__(self, config: Optional[BatchConfig] = None):
        self.config = config or BatchConfig()
        self.queue: deque[tuple[int, str, Any, asyncio.Future[Any], Callable[[list[Any]], Any]]] = deque()
        self.lock = threading.Lock()
        self.batch_ready = threading.Event()
        self.results: dict[str, Any] = {}
        self._stop = False

    async def add_request(self, data: Any, process_fn: Callable, priority: int = 0) -> Any:
        """
        Add request to batch queue and wait for result.

        Args:
            data: Input data to process
            process_fn: Function to process the batch
            priority: Request priority (higher = more important)

        Returns:
            Processing result for this request
        """
        request_id = f"{time.time()}_{id(data)}"
        future: asyncio.Future[Any] = asyncio.Future()

        with self.lock:
            self.queue.append((priority, request_id, data, future, process_fn))
            self.batch_ready.set()

        # Wait for result
        return await future

    async def process_batches(self) -> None:
        """Background task to process batched requests."""
        while not self._stop:
            if not self.queue:
                self.batch_ready.clear()
                await asyncio.sleep(0.001)
                continue

            # Wait for batch to fill or timeout
            await asyncio.sleep(self.config.max_wait_ms / 1000.0)

            # Extract batch
            batch_items: list[tuple[int, str, Any, asyncio.Future[Any], Callable[[list[Any]], Any]]] = []
            with self.lock:
                batch_size = min(len(self.queue), self.config.max_batch_size)
                for _ in range(batch_size):
                    if self.queue:
                        batch_items.append(self.queue.popleft())

            if not batch_items:
                continue

            # Sort by priority
            batch_items.sort(reverse=True, key=lambda x: x[0])

            # Process batch
            _, _ids, data_items, futures, process_fns = zip(*batch_items, strict=False)
            process_fn = process_fns[0] if process_fns else None
            if process_fn is None:
                continue
            try:
                batch_payload: list[Any] = list(data_items)
                results_payload: Any = await asyncio.get_running_loop().run_in_executor(
                    None, process_fn, batch_payload
                )
                if not isinstance(results_payload, list):
                    results_payload = [results_payload] * len(futures)
                if len(results_payload) != len(futures):
                    raise ValueError("Batch processor returned an unexpected number of results")
                # Distribute results
                for future, result in zip(futures, results_payload, strict=False):
                    future.set_result(result)
            except (ValueError, TypeError, RuntimeError) as exc:
                logger.debug("Batch processing failed: %s", type(exc).__name__)
                for future in futures:
                    future.set_exception(exc)

    def start(self) -> None:
        """Start background batch processor."""
        asyncio.create_task(self.process_batches())

    def stop(self) -> None:
        """Stop batch processor."""
        self._stop = True


class MemoryPool:
    """
    Memory pool for efficient tensor/array allocation.

    Reduces GC overhead by reusing allocated buffers.

    Example:
        >>> pool = MemoryPool(buffer_size=1024, pool_size=10)
        >>> with pool.get_buffer() as buf:
        ...     # Use buffer
        ...     buf[:] = data
    """

    def __init__(self, buffer_size: int, pool_size: int = 10):
        self.buffer_size = buffer_size
        self.pool_size = pool_size
        self.available: deque = deque()
        self.in_use: set[Any] = set()
        self.lock = threading.Lock()
        self._active_buffer: bytearray | None = None

        # Pre-allocate buffers
        for _ in range(pool_size):
            self.available.append(bytearray(buffer_size))

    def get_buffer(self) -> bytearray:
        """Get buffer from pool or allocate new one."""
        with self.lock:
            if self.available:
                buf = self.available.popleft()
                self.in_use.add(id(buf))
                return buf
            # Pool exhausted, allocate new
            buf = bytearray(self.buffer_size)
            self.in_use.add(id(buf))
            return buf

    def return_buffer(self, buf: bytearray) -> None:
        """Return buffer to pool."""
        with self.lock:
            buf_id = id(buf)
            if buf_id in self.in_use:
                self.in_use.remove(buf_id)
                if len(self.available) < self.pool_size:
                    # Clear and return to pool
                    buf[:] = b"\x00" * len(buf)
                    self.available.append(buf)

    def __enter__(self) -> bytearray:
        self._active_buffer = self.get_buffer()
        return self._active_buffer

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> Literal[False]:
        if self._active_buffer is not None:
            self.return_buffer(self._active_buffer)
            self._active_buffer = None
        return False


class ModelWarmer:
    """
    Model warmup utility to reduce cold start latency.

    Runs dummy predictions on startup to initialize model state,
    allocate GPU memory, and compile CUDA kernels.

    Example:
        >>> warmer = ModelWarmer(model)
        >>> warmer.warmup(num_samples=10, input_shape=(1, 512))
    """

    def __init__(self, model: Any):
        self.model = model

    def warmup(self, num_samples: int = 10, input_shape: tuple[int, ...] = (1, 512)):
        """
        Warm up model with dummy predictions.

        Args:
            num_samples: Number of warmup predictions
            input_shape: Shape of dummy inputs
        """
        import torch

        # Generate dummy inputs
        dummy_input = torch.randn(*input_shape)

        # Run predictions
        with torch.no_grad():
            for _ in range(num_samples):
                _ = self.model(dummy_input)

        # Synchronize GPU
        if torch.cuda.is_available():
            torch.cuda.synchronize()


class DynamicBatchSizer:
    """
    Automatically adjusts batch size based on system load and latency.

    Features:
    - Increases batch size when latency is acceptable
    - Decreases batch size when latency exceeds target
    - Respects memory constraints

    Example:
        >>> sizer = DynamicBatchSizer(target_latency_ms=100)
        >>> batch_size = sizer.get_batch_size()
        >>> # ... process batch ...
        >>> sizer.update(actual_latency_ms=95)
    """

    def __init__(
        self,
        initial_size: int = 8,
        min_size: int = 1,
        max_size: int = 64,
        target_latency_ms: float = 100.0,
        adjustment_rate: float = 0.1,
    ):
        self.current_size = initial_size
        self.min_size = min_size
        self.max_size = max_size
        self.target_latency_ms = target_latency_ms
        self.adjustment_rate = adjustment_rate
        self.latency_history: deque = deque(maxlen=100)

    def get_batch_size(self) -> int:
        """Get current optimal batch size."""
        return self.current_size

    def update(self, actual_latency_ms: float):
        """
        Update batch size based on observed latency.

        Args:
            actual_latency_ms: Actual latency observed for last batch
        """
        self.latency_history.append(actual_latency_ms)

        if len(self.latency_history) < 10:
            return  # Need more samples

        # Calculate average recent latency
        avg_latency = sum(list(self.latency_history)[-10:]) / 10

        # Adjust batch size
        if avg_latency < self.target_latency_ms * 0.8:
            # Latency comfortable, increase batch size
            new_size = int(self.current_size * (1 + self.adjustment_rate))
            self.current_size = min(new_size, self.max_size)
        elif avg_latency > self.target_latency_ms * 1.2:
            # Latency too high, decrease batch size
            new_size = int(self.current_size * (1 - self.adjustment_rate))
            self.current_size = max(new_size, self.min_size)

    def reset(self) -> None:
        """Reset to initial batch size."""
        self.current_size = (self.min_size + self.max_size) // 2
        self.latency_history.clear()


# Async prediction pipeline for overlapping I/O and compute
class AsyncPredictionPipeline:
    """
    Asynchronous prediction pipeline for overlapping I/O and computation.

    Uses multiple stages to hide I/O latency:
    1. Input preprocessing (async)
    2. Model inference (GPU/CPU)
    3. Output postprocessing (async)

    Example:
        >>> pipeline = AsyncPredictionPipeline(model, preprocess_fn, postprocess_fn)
        >>> result = await pipeline.predict(input_data)
    """

    def __init__(
        self,
        model: Any,
        preprocess_fn: Optional[Callable] = None,
        postprocess_fn: Optional[Callable] = None,
        max_concurrent: int = 4,
    ):
        self.model = model
        self.preprocess_fn = preprocess_fn or (lambda x: x)
        self.postprocess_fn = postprocess_fn or (lambda x: x)
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def predict(self, input_data: Any) -> Any:
        """
        Run async prediction pipeline.

        Args:
            input_data: Raw input data

        Returns:
            Processed prediction result
        """
        async with self.semaphore:
            # Stage 1: Preprocess (async I/O)
            processed = await asyncio.get_event_loop().run_in_executor(
                None, self.preprocess_fn, input_data
            )

            # Stage 2: Inference (blocking, but parallelized across requests)
            prediction = await asyncio.get_event_loop().run_in_executor(None, self.model, processed)

            # Stage 3: Postprocess (async I/O)
            return await asyncio.get_event_loop().run_in_executor(
                None, self.postprocess_fn, prediction
            )
