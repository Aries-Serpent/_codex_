"""Test async protocol handling and concurrency."""

from __future__ import annotations

import asyncio
from typing import Any, Dict

import pytest


# STABILIZATION V3: Add fixture to reset event loop state between tests
# This prevents async state leaks where event loop handles persist across tests
@pytest.fixture(autouse=True)
def reset_event_loop():
    """Reset event loop state after each test to prevent state leaks."""
    yield
    # Cleanup: close any pending tasks and reset the event loop
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.stop()
        # Cancel all remaining tasks
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()
        # Wait for cancellation to propagate
        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
    except RuntimeError:
        # Event loop might already be closed in some environments
        pass


class AsyncMessageQueue:
    def __init__(self, max_size: int = 100):
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=max_size)
        self.processed = 0

    async def enqueue(self, message: Dict[str, Any]):
        await self.queue.put(message)

    async def dequeue(self) -> Dict[str, Any]:
        return await self.queue.get()

    async def process_all(self):
        while not self.queue.empty():
            await asyncio.wait_for(self.dequeue(), timeout=10)
            self.processed += 1


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_message_queue_enqueue():
    """Test enqueueing messages."""
    queue = AsyncMessageQueue()

    message = {"id": 1, "method": "test"}
    await asyncio.wait_for(queue.enqueue(message), timeout=10)

    retrieved = await asyncio.wait_for(queue.dequeue(), timeout=10)
    assert retrieved == message, "Assertion must pass"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_message_queue_fifo():
    """Test FIFO ordering."""
    queue = AsyncMessageQueue()

    for i in range(5):
        await asyncio.wait_for(queue.enqueue({"id": i}), timeout=10)

    for i in range(5):
        msg = await asyncio.wait_for(queue.dequeue(), timeout=10)
        assert msg["id"] == i, "Assertion must pass"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_message_queue_concurrent_processing():
    """Test concurrent message processing."""
    queue = AsyncMessageQueue()

    # Enqueue messages
    for i in range(10):
        await asyncio.wait_for(queue.enqueue({"id": i}), timeout=10)

    # Process all
    await asyncio.wait_for(queue.process_all(), timeout=30)

    assert queue.processed == 10, "Assertion must pass"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_message_queue_timeout():
    """Test timeout on empty queue."""
    queue = AsyncMessageQueue()

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(queue.dequeue(), timeout=0.1)


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_concurrent_enqueue_dequeue():
    """Test concurrent enqueue/dequeue operations."""
    queue = AsyncMessageQueue()

    async def producer():
        for i in range(5):
            await asyncio.wait_for(queue.enqueue({"id": i}), timeout=10)
            await asyncio.wait_for(asyncio.sleep(0.01), timeout=1.5)

    async def consumer():
        count = 0
        while count < 5:
            await asyncio.wait_for(queue.dequeue(), timeout=10)
            count += 1
        return count

    prod_task = asyncio.create_task(producer())
    cons_task = asyncio.create_task(consumer())

    await prod_task
    consumed = await cons_task

    assert consumed == 5, "Assertion must pass"
