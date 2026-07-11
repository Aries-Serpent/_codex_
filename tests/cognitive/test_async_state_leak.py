"""
Test async state leaks - Pattern 1: Context manager cleanup
Tests require proper async context managers to prevent state leaks.
"""
import asyncio
import pytest
from contextlib import asynccontextmanager


# Global state tracker to detect leaks
_global_state = {}
_state_lock = asyncio.Lock()


@asynccontextmanager
async def managed_async_context(context_id):
    """Properly managed async context with cleanup."""
    global _global_state
    
    # Acquire lock before modifying global state
    async with _state_lock:
        # Initialize context state
        _global_state[context_id] = {
            "active": True,
            "data": [],
        }
    
    try:
        yield _global_state[context_id]
    finally:
        # Ensure cleanup happens even on exception
        async with _state_lock:
            if context_id in _global_state:
                del _global_state[context_id]


class TestAsyncStateLeaks:
    """Test suite for async state leaks with context managers."""

    async def async_test_state_leak(self):
        """Test async state leak prevention with context managers."""
        
        async def async_worker(worker_id):
            """Async worker that uses managed context."""
            async with managed_async_context(worker_id) as ctx:
                # Simulate async work
                ctx["data"].append("item_1")
                await asyncio.sleep(0.01)
                
                ctx["data"].append("item_2")
                await asyncio.sleep(0.01)
                
                ctx["data"].append("item_3")
                
                # Context should be active
                assert ctx["active"] is True
                assert len(ctx["data"]) == 3
        
        # Run multiple concurrent workers
        tasks = [async_worker(i) for i in range(5)]
        await asyncio.gather(*tasks)
        
        # Verify no state leaks - global state should be empty
        async with _state_lock:
            assert len(_global_state) == 0, f"State leaked: {_global_state}"

    @pytest.mark.timeout(10)
    def test_state_leak(self):
        """Test wrapper for async state leak prevention."""
        # Clear global state before test
        global _global_state
        _global_state.clear()
        
        # Run async test
        asyncio.run(self.async_test_state_leak())
        
        # Verify cleanup
        assert len(_global_state) == 0


class TestAsyncStateLeaksWithExceptions:
    """Test suite for async state leaks with exception handling."""

    async def async_test_with_exceptions(self):
        """Test state leak prevention even with exceptions."""
        
        async def failing_worker(worker_id):
            """Async worker that may raise exceptions."""
            try:
                async with managed_async_context(worker_id) as ctx:
                    ctx["data"].append("item_1")
                    await asyncio.sleep(0.01)
                    
                    if worker_id == 2:
                        raise ValueError(f"Simulated error in worker {worker_id}")
                    
                    ctx["data"].append("item_2")
                    await asyncio.sleep(0.01)
            except ValueError:
                pass  # Expected for worker 2
        
        # Run multiple concurrent workers
        tasks = [failing_worker(i) for i in range(5)]
        await asyncio.gather(*tasks)
        
        # Verify no state leaks even after exceptions
        async with _state_lock:
            assert len(_global_state) == 0, f"State leaked: {_global_state}"

    @pytest.mark.timeout(10)
    def test_state_leak(self):
        """Test wrapper for async state leak prevention with exceptions."""
        # Clear global state before test
        global _global_state
        _global_state.clear()
        
        # Run async test
        asyncio.run(self.async_test_with_exceptions())
        
        # Verify cleanup
        assert len(_global_state) == 0
