"""Test MCP worker lifecycle management."""

from __future__ import annotations

from enum import Enum

import pytest


class WorkerState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


class Worker:
    def __init__(self, name: str):
        self.name = name
        self.state = WorkerState.IDLE

    async def start(self) -> None:
        self.state = WorkerState.RUNNING

    async def pause(self) -> None:
        if self.state == WorkerState.RUNNING:
            self.state = WorkerState.PAUSED

    async def resume(self) -> None:
        if self.state == WorkerState.PAUSED:
            self.state = WorkerState.RUNNING

    async def stop(self) -> None:
        self.state = WorkerState.STOPPED


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_worker_lifecycle_start():
    """Test worker start transition."""
    worker = Worker("test")
    assert worker.state == WorkerState.IDLE, "state is not valid"

    await worker.start()

    assert worker.state == WorkerState.RUNNING, "state is not valid"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_worker_lifecycle_pause():
    """Test worker pause transition."""
    worker = Worker("test")

    await worker.start()
    await worker.pause()

    assert worker.state == WorkerState.PAUSED, "state is not valid"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_worker_lifecycle_resume():
    """Test worker resume transition."""
    worker = Worker("test")

    await worker.start()
    await worker.pause()
    await worker.resume()

    assert worker.state == WorkerState.RUNNING, "state is not valid"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_worker_lifecycle_stop():
    """Test worker stop transition."""
    worker = Worker("test")

    await worker.start()
    await worker.stop()

    assert worker.state == WorkerState.STOPPED, "state is not valid"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_worker_invalid_transition():
    """Test invalid state transitions."""
    worker = Worker("test")

    # Cannot pause from idle
    await worker.pause()
    assert worker.state == WorkerState.IDLE, "state is not valid"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_worker_multiple_starts():
    """Test starting an already running worker."""
    worker = Worker("test")

    await worker.start()
    await worker.start()  # Should be idempotent or handle gracefully

    assert worker.state == WorkerState.RUNNING, "state is not valid"
