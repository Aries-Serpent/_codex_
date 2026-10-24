"""Exponential backoff retry logic for the Codex platform.

Provides a configurable decorator for synchronous callables, with capped
exponential delays plus additive uniform jitter. This is not full jitter
(which would randomize the entire delay). Calls block the current thread
during ``time.sleep``; coroutine failures are not awaited or retried.

Public API
----------
* :func:`retry_with_backoff` — decorator **and** direct-call wrapper.
* :exc:`RetryExhausted` — raised when all retry attempts are exhausted;
  the last exception is chained as ``__cause__``.

No-network example with zero-delay retries::

    from aries_serpent_core.resilience.retry import RetryExhausted, retry_with_backoff

    @retry_with_backoff(max_retries=2, base_delay=0, jitter=0, exceptions=(OSError,))
    def unavailable():
        raise OSError("service unavailable")

    try:
        unavailable()
    except RetryExhausted as exc:
        assert exc.attempts == 3  # initial call plus two retries
        assert isinstance(exc.__cause__, OSError)
"""

from __future__ import annotations

import functools
import random
import time
from collections.abc import Callable
from typing import ParamSpec, TypeVar

__all__ = ["RetryExhausted", "retry_with_backoff"]

from aries_serpent_core.logging.structured_logger import logger

P = ParamSpec("P")
R = TypeVar("R")


class RetryExhausted(Exception):
    """Raised when all retry attempts have been exhausted.

    The last exception that caused the final retry failure is chained as
    ``__cause__``, so callers can inspect the root error via
    ``exc.__cause__``.

    Example::

        try:
            flaky()
        except RetryExhausted as exc:
            logger.info(f"Gave up after {exc.attempts} attempts; last error: {exc.__cause__}")
    """

    def __init__(self, message: str, attempts: int) -> None:
        super().__init__(message)
        self.attempts: int = attempts


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: float = 0.1,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator factory that wraps a callable with exponential backoff retry.

    The delay after failed attempt *n* (0-indexed), if a retry remains, is::

        delay = min(base_delay * 2**n + random.uniform(0, jitter), max_delay)

    Args:
        max_retries: Total number of *extra* attempts after the first call
            fails.  A value of ``3`` means up to 4 total calls (1 initial +
            3 retries).
        base_delay: Initial delay in seconds before the first retry.
        max_delay: Upper bound on the computed delay (seconds).
        jitter: Maximum random jitter added to each delay (seconds).
        exceptions: Tuple of exception types that trigger a retry.  Any
            exception NOT in this tuple propagates immediately.

    Returns:
        A decorator that forwards arguments and returns the first successful
        result, preserving the wrapped function's metadata.

    Timing:
        With ``max_retries=0``, the callable is still invoked once and a
        matching failure becomes ``RetryExhausted`` without sleeping.
        There is no sleep after the final failure. Supply nonnegative retry
        counts and delays; the factory does not validate these values.
        This synchronous wrapper does not catch failures during later
        iteration of a generator or execution of a returned coroutine.

    Raises:
        RetryExhausted: After all retries are exhausted.  The last raised
            exception is chained via ``raise … from last_exc``.
        Exception: Any exception type not listed in *exceptions* propagates
            without retrying.

    Direct wrapping also uses the returned decorator::

        parse = retry_with_backoff(max_retries=0, exceptions=(OSError,))(int)
        assert parse("42") == 42
        # parse("invalid") raises ValueError immediately, without retrying.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_exc: BaseException | None = None
            total_attempts = max_retries + 1  # initial call + retries
            func_name = getattr(func, "__qualname__", None) or repr(func)

            for attempt in range(total_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    if attempt < total_attempts - 1:
                        delay = min(
                            base_delay * (2**attempt) + random.uniform(0, jitter),
                            max_delay,
                        )
                        logger.warning(
                            "retry_with_backoff: %s failed on attempt %d/%d "
                            "(retrying in %.2fs) — %s: %s",
                            func_name,
                            attempt + 1,
                            total_attempts,
                            delay,
                            type(exc).__name__,
                            exc,
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            "retry_with_backoff: %s exhausted all %d attempts — %s: %s",
                            func_name,
                            total_attempts,
                            type(exc).__name__,
                            exc,
                        )

            raise RetryExhausted(
                f"{func_name!r} failed after {total_attempts} attempt(s): {last_exc!r}",
                attempts=total_attempts,
            ) from last_exc

        return wrapper

    return decorator
