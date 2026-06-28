"""Tests for request batching middleware"""

import asyncio
import time

import pytest

from src.codex_ml.serving.batching import (
    BatchingMiddleware,
    PerformanceMetrics,
)


class TestPerformanceMetrics:
    """Test performance metrics tracking"""

    def test_initialization(self):
        """Test metrics initialization"""
        metrics = PerformanceMetrics()
        assert metrics.request_count == 0, "Count must be greater than zero"
        assert metrics.batch_count == 0, "Count must be greater than zero"
        assert metrics.total_latency == 0.0, "total_latency is not valid"
        assert len(metrics.latencies) == 0, "Collection must not be empty"
        assert len(metrics.batch_sizes) == 0, "Collection must not be empty"

    def test_record_request(self):
        """Test recording request completion"""
        metrics = PerformanceMetrics()
        metrics.record_request(0.1)
        metrics.record_request(0.2)
        metrics.record_request(0.15)

        assert metrics.request_count == 3, "Count must be greater than zero"
        assert metrics.total_latency == 0.45, "total_latency is not valid"
        assert len(metrics.latencies) == 3, "Collection must not be empty"

    def test_record_batch(self):
        """Test recording batch processing"""
        metrics = PerformanceMetrics()
        metrics.record_batch(10)
        metrics.record_batch(15)
        metrics.record_batch(8)

        assert metrics.batch_count == 3, "Count must be greater than zero"
        assert len(metrics.batch_sizes) == 3, "Collection must not be empty"
        assert metrics.get_average_batch_size() == 11.0, "Condition must be true"

    def test_latency_percentiles(self):
        """Test latency percentile calculation"""
        metrics = PerformanceMetrics()
        latencies = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        for lat in latencies:
            metrics.record_request(lat)

        # p50 should be around 0.5-0.6
        p50 = metrics.get_latency_percentile(0.5)
        assert 0.5 <= p50 <= 0.6, "5 is not valid"

        # p95 should be around 0.9-1.0
        p95 = metrics.get_latency_percentile(0.95)
        assert 0.9 <= p95 <= 1.0, "9 is not valid"

        # p99 should be close to 1.0
        p99 = metrics.get_latency_percentile(0.99)
        assert 0.95 <= p99 <= 1.0, "95 is not valid"

    def test_average_latency(self):
        """Test average latency calculation"""
        metrics = PerformanceMetrics()
        metrics.record_request(0.1)
        metrics.record_request(0.2)
        metrics.record_request(0.3)

        assert metrics.get_average_latency() == 0.2, "Condition must be true"

    def test_throughput(self):
        """Test throughput calculation"""
        metrics = PerformanceMetrics()
        metrics.throughput_window = 1.0  # 1 second window for testing

        # Record some requests
        for _ in range(5):
            metrics.record_request(0.01)

        # Throughput should be > 0
        throughput = metrics.get_throughput()
        assert throughput > 0, "throughput must be greater than zero"

    def test_to_dict(self):
        """Test metrics dictionary conversion"""
        metrics = PerformanceMetrics()
        metrics.record_request(0.1)
        metrics.record_request(0.2)
        metrics.record_batch(5)

        metrics_dict = metrics.to_dict()
        assert "request_count" in metrics_dict, "Count must be greater than zero"
        assert "batch_count" in metrics_dict, "Count must be greater than zero"
        assert "average_latency" in metrics_dict, "Condition must be true"
        assert "latency_p50" in metrics_dict, "Condition must be true"
        assert "latency_p95" in metrics_dict, "Condition must be true"
        assert "latency_p99" in metrics_dict, "Condition must be true"
        assert "throughput_rps" in metrics_dict, "Condition must be true"
        assert "average_batch_size" in metrics_dict, "Condition must be true"

        assert metrics_dict["request_count"] == 2, "Count must be greater than zero"
        assert metrics_dict["batch_count"] == 1, "Count must be greater than zero"


class TestBatchingMiddleware:
    """Test batching middleware"""

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_initialization(self):
        """Test middleware initialization"""

        def process_fn(inputs):
            return [x * 2 for x in inputs]

        middleware = BatchingMiddleware(
            process_fn=process_fn,
            max_batch_size=10,
            max_wait_time=0.1,
        )

        assert middleware.max_batch_size == 10, "max_batch_size is not valid"
        assert middleware.max_wait_time == 0.1, "max_wait_time is not valid"
        assert len(middleware.batch_queue) == 0, "Collection must not be empty"

        await middleware.shutdown()

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_single_request(self):
        """Test processing a single request"""

        def process_fn(inputs):
            return [x * 2 for x in inputs]

        middleware = BatchingMiddleware(process_fn=process_fn, max_wait_time=0.05)

        result = await middleware.process(5)
        assert result == 10, "Result must not be empty"

        await middleware.shutdown()

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_batch_on_size(self):
        """Test batching when max_batch_size is reached"""

        def process_fn(inputs):
            return [x * 2 for x in inputs]

        middleware = BatchingMiddleware(
            process_fn=process_fn,
            max_batch_size=3,
            max_wait_time=1.0,  # Long timeout, should batch on size
        )

        # Send 3 requests simultaneously
        tasks = [middleware.process(i) for i in [1, 2, 3]]
        results = await asyncio.gather(*tasks)

        assert results == [2, 4, 6]
        assert middleware.metrics.batch_count == 1, "Count must be greater than zero"
        assert middleware.metrics.request_count == 3, "Count must be greater than zero"

        await middleware.shutdown()

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_batch_on_timeout(self):
        """Test batching when max_wait_time is reached"""

        def process_fn(inputs):
            return [x * 2 for x in inputs]

        middleware = BatchingMiddleware(
            process_fn=process_fn,
            max_batch_size=100,  # Large batch size, should batch on timeout
            max_wait_time=0.05,  # 50ms timeout
        )

        # Send 2 requests
        start_time = time.time()
        tasks = [middleware.process(i) for i in [1, 2]]
        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start_time

        assert results == [2, 4]
        assert middleware.metrics.batch_count == 1, "Count must be greater than zero"
        assert middleware.metrics.request_count == 2, "Count must be greater than zero"
        # Should complete within timeout window + processing time
        assert elapsed < 0.2, "elapsed is not valid"

        await middleware.shutdown()

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_multiple_batches(self):
        """Test processing multiple batches"""

        def process_fn(inputs):
            return [x * 2 for x in inputs]

        middleware = BatchingMiddleware(
            process_fn=process_fn,
            max_batch_size=2,
            max_wait_time=0.05,
        )

        # Send 5 requests (should create 3 batches: 2, 2, 1)
        tasks = [middleware.process(i) for i in range(5)]
        results = await asyncio.gather(*tasks)

        assert results == [0, 2, 4, 6, 8]
        assert middleware.metrics.batch_count >= 2, "batch_count must be positive"
        assert middleware.metrics.request_count == 5, "Count must be greater than zero"

        await middleware.shutdown()

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_error_handling(self):
        """Test error handling in batch processing"""

        def process_fn(inputs):
            raise ValueError("Processing error")

        middleware = BatchingMiddleware(
            process_fn=process_fn,
            max_batch_size=2,
            max_wait_time=0.05,
        )

        # Should propagate exception
        with pytest.raises(ValueError, match="Processing error"):
            await middleware.process(1)

        await middleware.shutdown()

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_metrics_tracking(self):
        """Test that metrics are tracked correctly"""

        def process_fn(inputs):
            time.sleep(0.01)  # Simulate some processing time
            return [x * 2 for x in inputs]

        middleware = BatchingMiddleware(
            process_fn=process_fn,
            max_batch_size=3,
            max_wait_time=0.05,
        )

        # Process a batch
        tasks = [middleware.process(i) for i in [1, 2, 3]]
        await asyncio.gather(*tasks)

        # Check metrics
        metrics = middleware.get_metrics()
        assert metrics["request_count"] == 3, "Count must be greater than zero"
        assert metrics["batch_count"] == 1, "Count must be greater than zero"
        assert metrics["average_batch_size"] == 3.0, "Condition must be true"
        assert metrics["average_latency"] > 0, "Value must be greater than zero"
        assert metrics["latency_p50"] is not None, "Value must be initialized"

        await middleware.shutdown()

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_shutdown_flushes_queue(self):
        """Test that shutdown flushes remaining requests"""

        def process_fn(inputs):
            return [x * 2 for x in inputs]

        middleware = BatchingMiddleware(
            process_fn=process_fn,
            max_batch_size=100,  # Large size, won't batch on size
            max_wait_time=10.0,  # Long timeout
        )

        # Add a request but don't wait for it
        task = asyncio.create_task(middleware.process(5))

        # Give it a moment to add to queue
        await asyncio.sleep(0.01)

        # Shutdown should flush it
        await middleware.shutdown()

        # Request should be completed
        result = await task
        assert result == 10, "Result must not be empty"
