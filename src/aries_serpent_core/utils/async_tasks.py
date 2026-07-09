"""
P010: Async Task Management Utilities

Consolidates async task coordination patterns.

Example:
    # Instead of: asyncio.create_task(...)
    task = create_managed_task(coro)
    result = await task.wait_with_timeout(timeout=10)
"""

import asyncio
from typing import Any, Coroutine, Optional

__all__ = [
    "run_async",
    "cancel_task",
]


async def run_async(coro: Coroutine, timeout: Optional[float] = None) -> Any:
    """
    Run a coroutine with optional timeout.

    Args:
        coro: Coroutine to run
        timeout: Timeout in seconds

    Returns:
        Coroutine result
    """
    try:
        if timeout:
            return await asyncio.wait_for(coro, timeout=timeout)
        return await coro
    except asyncio.TimeoutError:
        raise TimeoutError(f"Coroutine timed out after {timeout}s")


async def cancel_task(task: asyncio.Task) -> None:
    """
    Cancel a task safely.

    Args:
        task: Task to cancel
    """
    if not task.done():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
