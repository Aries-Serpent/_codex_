"""Test MCP worker pool and concurrency."""

from __future__ import annotations

import asyncio
from typing import List

import pytest


class WorkerPool:
    def __init__(self, size: int):
        self.size = size
        self.workers: List[asyncio.Task] = []
        self.completed = 0

    async def submit(self, coro):
        """Submit a coroutine to the pool."""
        task = asyncio.create_task(coro)
        self.workers.append(task)
        return task

    async def wait_all(self):
        """Wait for all workers to complete."""
        if self.workers:
            await asyncio.gather(*self.workers)
            self.completed = len(self.workers)


async def dummy_task(duration: float = 0.01):
    """Dummy task for testing."""
    await asyncio.sleep(duration)
    return "done"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_worker_pool_creation():
    """Test creating a worker pool."""
    pool = WorkerPool(4)
    assert pool.size == 4, "size is not valid"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_worker_pool_submit():
    """Test submitting tasks to pool."""
    pool = WorkerPool(4)

    task = await pool.submit(dummy_task())
    assert task in pool.workers, "Condition must be true"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_worker_pool_wait_all():
    """Test waiting for all workers to complete."""
    pool = WorkerPool(4)

    for _ in range(3):
        await pool.submit(dummy_task())

    await pool.wait_all()

    assert pool.completed == 3, "completed is not valid"
