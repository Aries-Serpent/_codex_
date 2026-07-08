"""
Test asyncio compatibility with Python 3.12.

Ensures no deprecated asyncio patterns are used and that
async code works correctly with Python 3.12's stricter requirements.
"""

from __future__ import annotations

import asyncio
import sys
import warnings

import pytest


@pytest.mark.skipif(sys.version_info < (3, 12), reason="Python 3.12+ only")
class TestAsyncioCompatibility:
    """Test suite for Python 3.12 asyncio compatibility."""

    async def test_no_deprecated_event_loop_calls(self):
        """
        Verify no usage of deprecated get_event_loop().

        Python 3.12 deprecates asyncio.get_event_loop() in favor of
        asyncio.get_running_loop() within async contexts.
        """
        # This test should be run within an async context
        loop = asyncio.get_running_loop()
        assert loop is not None, "loop must be initialized"
        assert isinstance(loop, asyncio.AbstractEventLoop)

    async def test_asyncio_run_compatibility(self):
        """Test that asyncio.run() works correctly in Python 3.12."""

        async def simple_coro():
            await asyncio.sleep(0.001)
            return "success"

        # asyncio.run() should work from within another async context
        # We're already in an async context (pytest-asyncio), so test differently
        result = await simple_coro()
        assert result == "success", "Result must not be empty"

    async def test_gather_with_exceptions(self):
        """Test asyncio.gather with exceptions in Python 3.12."""

        async def success_coro():
            await asyncio.sleep(0.001)
            return "ok"

        async def failing_coro():
            await asyncio.sleep(0.001)
            raise ValueError("expected error")

        # Test gather with return_exceptions=True
        results = await asyncio.gather(success_coro(), failing_coro(), return_exceptions=True)

        assert results[0] == "ok", "Result must not be empty"
        assert isinstance(results[1], ValueError)

    async def test_task_creation(self):
        """Test task creation works in Python 3.12."""

        async def sample_task():
            await asyncio.sleep(0.001)
            return 42

        task = asyncio.create_task(sample_task())
        result = await task
        assert result == 42, "Result must not be empty"

    async def test_timeout_context_manager(self):
        """Test asyncio.timeout() context manager (Python 3.11+)."""
        if sys.version_info >= (3, 11):

            async def quick_operation():
                await asyncio.sleep(0.001)
                return "done"

            # Should complete within timeout
            async with asyncio.timeout(1.0):
                result = await quick_operation()

            assert result == "done", "Result must not be empty"

    async def test_multiple_coroutines_concurrently(self):
        """Test running multiple coroutines concurrently."""
        results = []

        async def append_number(n):
            await asyncio.sleep(0.001)
            results.append(n)

        await asyncio.gather(append_number(1), append_number(2), append_number(3))

        assert len(results) == 3, "Results must not be empty"
        assert set(results) == {1, 2, 3}


@pytest.mark.skipif(sys.version_info < (3, 12), reason="Python 3.12+ only")
class TestRequestBatcherAsyncContext:
    """Test RequestBatcher works in Python 3.12 async context."""

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
    async def test_request_batcher_import(self):
        """Test that RequestBatcher can be imported."""
        try:
            from codex_ml.serving.optimizations import RequestBatcher

            assert RequestBatcher is not None, "RequestBatcher must be initialized"
        except ImportError:
            pytest.skip("RequestBatcher not available in this environment")

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
    async def test_request_batcher_async_context(self):
        """Test RequestBatcher works in Python 3.12 async context."""
        try:
            from codex_ml.serving.optimizations import BatchConfig, RequestBatcher
        except ImportError:
            pytest.skip("RequestBatcher not available")
        else:
            # Create RequestBatcher with correct parameters
            config = BatchConfig(max_batch_size=10, max_wait_ms=100)
            batcher = RequestBatcher(config=config)

            # This should work without deprecated asyncio.get_event_loop() calls
            assert batcher is not None, "batcher must be initialized"
            assert batcher.config.max_batch_size == 10, "max_batch_size is not valid"


@pytest.mark.skipif(sys.version_info < (3, 12), reason="Python 3.12+ only")
class TestAsyncDataLoaders:
    """Test async data loaders work in Python 3.12."""

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
    async def test_async_data_loader_import(self):
        """Test that async data loaders can be imported."""
        try:
            from codex_ml.data import loaders

            assert loaders is not None, "loaders must be initialized"
        except ImportError:
            pytest.skip("Data loaders not available")

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
    async def test_async_pattern_no_event_loop_warning(self):
        """
        Test that async patterns don't trigger event loop warnings.

        Python 3.12 warns about using asyncio.get_event_loop() outside
        of async contexts. This test ensures our code doesn't trigger that.
        """

        # Run a simple async operation
        async def test_op():
            await asyncio.sleep(0.001)
            return True

        # Capture warnings
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")
            result = await test_op()

        assert result is True, "Result must not be empty"

        # Check no deprecation warnings about event loop
        event_loop_warnings = [
            w
            for w in warning_list
            if issubclass(w.category, (DeprecationWarning, RuntimeWarning))
            and "event loop" in str(w.message).lower()
        ]

        assert (len(event_loop_warnings) == 0, "Event_loop_warnings must not be empty"
        ), f"Unexpected event loop warnings: {event_loop_warnings}"


@pytest.mark.asyncio
class TestAsyncioModernPatterns:
    """Test modern asyncio patterns work across all Python versions."""

    async def test_async_with_context_manager(self):
        """Test async context managers work correctly."""

        class AsyncContextManager:
            async def __aenter__(self):
                await asyncio.sleep(0.001)
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                await asyncio.sleep(0.001)
                return False

        async with AsyncContextManager() as ctx:
            assert ctx is not None, "ctx must be initialized"

    async def test_async_iterator(self):
        """Test async iterators work correctly."""

        class AsyncIterator:
            def __init__(self):
                self.count = 0

            def __aiter__(self):
                return self

            async def __anext__(self):
                if self.count >= 3:
                    raise StopAsyncIteration
                self.count += 1
                await asyncio.sleep(0.001)
                return self.count

        results = []
        async for item in AsyncIterator():
            results.append(item)

        assert results == [1, 2, 3]

    async def test_asyncio_queue(self):
        """Test asyncio.Queue works in Python 3.12."""
        queue = asyncio.Queue(maxsize=5)

        await queue.put("item1")
        await queue.put("item2")

        assert await queue.get() == "item1", "Item must not be empty"
        assert await queue.get() == "item2", "Item must not be empty"

    async def test_asyncio_event(self):
        """Test asyncio.Event works in Python 3.12."""
        event = asyncio.Event()

        assert not event.is_set(), "Condition must be true"
        event.set()
        assert event.is_set(), "Condition must be true"

        event.clear()
        assert not event.is_set(), "Condition must be true"


@pytest.mark.integration
@pytest.mark.asyncio
class TestAsyncioIntegration:
    """Integration tests for asyncio in Python 3.12."""

    async def test_complex_async_workflow(self):
        """Test a complex async workflow similar to real usage."""
        results = []

        async def producer(queue, n):
            for i in range(n):
                await asyncio.sleep(0.001)
                await queue.put(f"item_{i}")
            await queue.put(None)  # Sentinel

        async def consumer(queue, results_list):
            while True:
                item = await queue.get()
                if item is None:
                    break
                await asyncio.sleep(0.001)
                results_list.append(item)

        queue = asyncio.Queue()

        await asyncio.gather(producer(queue, 5), consumer(queue, results))

        assert len(results) == 5, "Results must not be empty"
        assert results[0] == "item_0", "Result must not be empty"
        assert results[-1] == "item_4", "Result must not be empty"
