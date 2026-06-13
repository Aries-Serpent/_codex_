"""Test async protocol handling and concurrency."""
from __future__ import annotations

import asyncio
from typing import List, Dict, Any
import pytest


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
            msg = await self.dequeue()
            self.processed += 1


@pytest.mark.asyncio
async def test_message_queue_enqueue():
    """Test enqueueing messages."""
    queue = AsyncMessageQueue()
    
    message = {"id": 1, "method": "test"}
    await queue.enqueue(message)
    
    retrieved = await queue.dequeue()
    assert retrieved == message


@pytest.mark.asyncio
async def test_message_queue_fifo():
    """Test FIFO ordering."""
    queue = AsyncMessageQueue()
    
    for i in range(5):
        await queue.enqueue({"id": i})
    
    for i in range(5):
        msg = await queue.dequeue()
        assert msg["id"] == i


@pytest.mark.asyncio
async def test_message_queue_concurrent_processing():
    """Test concurrent message processing."""
    queue = AsyncMessageQueue()
    
    # Enqueue messages
    for i in range(10):
        await queue.enqueue({"id": i})
    
    # Process all
    await queue.process_all()
    
    assert queue.processed == 10


@pytest.mark.asyncio
async def test_message_queue_timeout():
    """Test timeout on empty queue."""
    queue = AsyncMessageQueue()
    
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(queue.dequeue(), timeout=0.1)


@pytest.mark.asyncio
async def test_concurrent_enqueue_dequeue():
    """Test concurrent enqueue/dequeue operations."""
    queue = AsyncMessageQueue()
    
    async def producer():
        for i in range(5):
            await queue.enqueue({"id": i})
            await asyncio.sleep(0.01)
    
    async def consumer():
        count = 0
        while count < 5:
            await queue.dequeue()
            count += 1
        return count
    
    prod_task = asyncio.create_task(producer())
    cons_task = asyncio.create_task(consumer())
    
    await prod_task
    consumed = await cons_task
    
    assert consumed == 5
