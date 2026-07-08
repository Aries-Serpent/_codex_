"""Exponential backoff retry logic for the Codex platform.

Provides a configurable retry decorator / callable wrapper with full jitter
exponential backoff, suitable for wrapping unreliable external HTTP / service
calls.

Public API
----------
* :func:`retry_with_backoff` — decorator **and** direct-call wrapper.
* :exc:`RetryExhausted` — raised when all retry attempts are exhausted;
  the last exception is chained as ``__cause__``.

Quick start::

    from codex.resilience.retry import retry_with_backoff, RetryExhausted

    # --- Decorator usage ---
    @retry_with_backoff(max_retries=4, base_delay=0.5)
    def call_external_api() -> dict:
        return requests.get("https://api.example.com/data").json()

    # --- Direct wrapper ---
    result = retry_with_backoff(max_retries=3)(my_func)(arg1, arg2)

    # --- Catching exhaustion ---
    try:
        call_external_api()
    except RetryExhausted as exc:
        logger.error("All retries failed: %s", exc.__cause__)
"""

from __future__ import annotations

import functools
import random
import time
from collections.abc import Callable
from typing import Any, TypeVar

__all__ = ["RetryExhausted", "retry_with_backoff"]

from codex.logging.structured_logger import logger

F = TypeVar("F", bound=Callable[..., Any])


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
) -> Callable[[F], F]:
    """Decorator factory that wraps a callable with exponential backoff retry.

    The delay before attempt *n* (0-indexed) is::

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
        A decorator that wraps a callable with the retry logic.

    Raises:
        RetryExhausted: After all retries are exhausted.  The last raised
            exception is chained via ``raise … from last_exc``.
        Exception: Any exception type not listed in *exceptions* propagates
            without retrying.

    Examples::

        @retry_with_backoff(max_retries=3, base_delay=0.5)
        def fetch() -> str:
            return urllib.request.urlopen("https://example.com").read()

        # Use as a direct wrapper (no decoration):
        result = retry_with_backoff(max_retries=2)(some_func)(arg)
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
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

        return wrapper  # type: ignore[VarArg(Any),KwArg(Any),unused-ignore,VarArg(Any), KwArg(Any)]

    return decorator
