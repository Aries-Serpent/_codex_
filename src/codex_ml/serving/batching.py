"""
Request Batching Middleware for Inference Server

Provides automatic request batching to improve throughput:
- Accumulates requests up to batch_size or timeout
- Thread-safe batch queue with async processing
- Automatic batch flushing on timeout
- Performance metrics tracking
"""
import asyncio
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from threading import Lock

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for batching and inference
    
    Attributes:
        request_count: Total number of requests processed
        batch_count: Total number of batches processed
        total_latency: Sum of all request latencies (seconds)
        latencies: List of individual request latencies for percentile calculation
        batch_sizes: List of batch sizes for statistics
        throughput_window: Time window for throughput calculation (seconds)
        window_requests: Requests in current throughput window
        window_start: Start time of current window
    """
    request_count: int = 0
    batch_count: int = 0
    total_latency: float = 0.0
    latencies: List[float] = field(default_factory=list)
    batch_sizes: List[int] = field(default_factory=list)
    throughput_window: float = 60.0  # 1 minute window
    window_requests: int = 0
    window_start: float = field(default_factory=time.time)
    
    def record_request(self, latency: float) -> None:
        """Record a single request completion"""
        self.request_count += 1
        self.total_latency += latency
        self.latencies.append(latency)
        
        # Track throughput in rolling window
        current_time = time.time()
        if current_time - self.window_start > self.throughput_window:
            self.window_requests = 1
            self.window_start = current_time
        else:
            self.window_requests += 1
            
        # Keep only recent latencies for percentile calculation (last 10000)
        if len(self.latencies) > 10000:
            self.latencies = self.latencies[-10000:]
    
    def record_batch(self, batch_size: int) -> None:
        """Record a batch processing event"""
        self.batch_count += 1
        self.batch_sizes.append(batch_size)
        
        # Keep only recent batch sizes (last 1000)
        if len(self.batch_sizes) > 1000:
            self.batch_sizes = self.batch_sizes[-1000:]
    
    def get_latency_percentile(self, percentile: float) -> Optional[float]:
        """Calculate latency percentile (0.0 to 1.0)"""
        if not self.latencies:
            return None
        sorted_latencies = sorted(self.latencies)
        index = int(percentile * len(sorted_latencies))
        index = min(index, len(sorted_latencies) - 1)
        return sorted_latencies[index]
    
    def get_average_latency(self) -> float:
        """Calculate average latency"""
        if self.request_count == 0:
            return 0.0
        return self.total_latency / self.request_count
    
    def get_throughput(self) -> float:
        """Calculate requests per second in current window"""
        elapsed = time.time() - self.window_start
        if elapsed == 0:
            return 0.0
        return self.window_requests / elapsed
    
    def get_average_batch_size(self) -> float:
        """Calculate average batch size"""
        if not self.batch_sizes:
            return 0.0
        return sum(self.batch_sizes) / len(self.batch_sizes)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
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
    """Single request in a batch
    
    Attributes:
        data: Request data (typically text or features)
        future: asyncio.Future to set result when batch is processed
        timestamp: Time when request was added to batch
    """
    data: Any
    future: asyncio.Future
    timestamp: float = field(default_factory=time.time)


class BatchingMiddleware:
    """Middleware for automatic request batching
    
    Accumulates requests up to max_batch_size or max_wait_time,
    then processes them as a batch for improved throughput.
    
    Attributes:
        max_batch_size: Maximum number of requests per batch
        max_wait_time: Maximum time to wait before flushing batch (seconds)
        process_fn: Function to process a batch of requests
        metrics: Performance metrics tracker
    """
    
    def __init__(
        self,
        process_fn: Callable[[List[Any]], List[Any]],
        max_batch_size: int = 32,
        max_wait_time: float = 0.1,  # 100ms
    ):
        """Initialize batching middleware
        
        Args:
            process_fn: Function that takes a list of inputs and returns a list of outputs
            max_batch_size: Maximum requests per batch
            max_wait_time: Maximum wait time in seconds before flushing batch
        """
        self.process_fn = process_fn
        self.max_batch_size = max_batch_size
        self.max_wait_time = max_wait_time
        
        self.batch_queue: List[BatchRequest] = []
        self.lock = Lock()
        self.metrics = PerformanceMetrics()
        self.flush_task: Optional[asyncio.Task] = None
        
        logger.info(
            f"BatchingMiddleware initialized: max_batch_size={max_batch_size}, "
            f"max_wait_time={max_wait_time}s"
        )
    
    async def process(self, data: Any) -> Any:
        """Process a single request (may be batched with others)
        
        Args:
            data: Input data for processing
            
        Returns:
            Processed result
        """
        # Create a future for this request
        future = asyncio.get_event_loop().create_future()
        request = BatchRequest(data=data, future=future)
        
        # Add to batch queue
        should_flush = False
        with self.lock:
            self.batch_queue.append(request)
            if len(self.batch_queue) >= self.max_batch_size:
                should_flush = True
            elif len(self.batch_queue) == 1:
                # First request in batch, schedule timeout flush
                self._schedule_flush()
        
        # Flush immediately if batch is full
        if should_flush:
            await self._flush_batch()
        
        # Wait for result
        return await future
    
    def _schedule_flush(self) -> None:
        """Schedule automatic batch flush after max_wait_time"""
        if self.flush_task is not None and not self.flush_task.done():
            # Flush already scheduled
            return
            
        async def delayed_flush():
            await asyncio.sleep(self.max_wait_time)
            await self._flush_batch()
        
        self.flush_task = asyncio.create_task(delayed_flush())
    
    async def _flush_batch(self) -> None:
        """Flush current batch and process all requests"""
        # Get current batch
        batch_to_process: List[BatchRequest] = []
        with self.lock:
            if not self.batch_queue:
                return
            batch_to_process = self.batch_queue
            self.batch_queue = []
        
        if not batch_to_process:
            return
        
        # Record batch size
        batch_size = len(batch_to_process)
        self.metrics.record_batch(batch_size)
        
        logger.debug(f"Processing batch of {batch_size} requests")
        
        # Process batch
        try:
            batch_inputs = [req.data for req in batch_to_process]
            batch_start = time.time()
            batch_outputs = self.process_fn(batch_inputs)
            batch_time = time.time() - batch_start
            
            # Set results for all requests
            for req, output in zip(batch_to_process, batch_outputs):
                latency = time.time() - req.timestamp
                self.metrics.record_request(latency)
                if not req.future.done():
                    req.future.set_result(output)
            
            logger.debug(f"Batch processed in {batch_time:.3f}s")
            
        except Exception as e:
            logger.error(f"Batch processing error: {e}")
            # Set exception for all requests
            for req in batch_to_process:
                if not req.future.done():
                    req.future.set_exception(e)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return self.metrics.to_dict()
    
    async def shutdown(self) -> None:
        """Shutdown batching middleware and flush remaining requests"""
        # Cancel flush task
        if self.flush_task is not None and not self.flush_task.done():
            self.flush_task.cancel()
        
        # Flush any remaining requests
        await self._flush_batch()
        
        logger.info("BatchingMiddleware shutdown complete")
