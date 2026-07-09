"""
P017: Async/Await Utilities

Consolidates 443 occurrences of async patterns.

Example:
    # Instead of: asyncio.gather(task1, task2, ...)
    results = await gather_with_timeout(coro1, coro2, timeout=30)
"""

import asyncio
from typing import Any, Callable, Coroutine, List, TypeVar

__all__ = [
    "gather_with_timeout",
    "async_retry",
    "AsyncError",
]

T = TypeVar("T")


class AsyncError(Exception):
    """Raised when async operations fail."""

    pass


async def gather_with_timeout(
    *coros: Coroutine,
    timeout: float = 30,
    return_exceptions: bool = False,
) -> List[Any]:
    """
    Gather coroutines with timeout protection.

    Args:
        *coros: Coroutines to gather
        timeout: Timeout in seconds
        return_exceptions: If True, return exceptions instead of raising

    Returns:
        List of results

    Raises:
        asyncio.TimeoutError: If any coroutine times out

    Example:
        >>> results = await gather_with_timeout(coro1, coro2, timeout=10)
    """
    try:
        return await asyncio.wait_for(
            asyncio.gather(*coros, return_exceptions=return_exceptions),
            timeout=timeout,
        )
    except asyncio.TimeoutError as e:
        raise AsyncError(f"Async operation timed out after {timeout}s") from e


async def async_retry(
    coro_fn: Callable[..., Coroutine],
    *args,
    retries: int = 3,
    backoff: float = 1.0,
    **kwargs,
) -> Any:
    """
    Retry an async function with exponential backoff.

    Args:
        coro_fn: Async function to retry
        *args: Arguments to pass to function
        retries: Number of retries
        backoff: Backoff multiplier
        **kwargs: Keyword arguments to pass to function

    Returns:
        Result of the coroutine

    Raises:
        AsyncError: If all retries fail

    Example:
        >>> result = await async_retry(fetch_data, url, retries=3)
    """
    last_error = None

    for attempt in range(retries):
        try:
            return await coro_fn(*args, **kwargs)
        except Exception as e:
            last_error = e
            if attempt < retries - 1:
                wait_time = backoff**attempt
                await asyncio.sleep(wait_time)

    raise AsyncError(f"Failed after {retries} retries") from last_error
