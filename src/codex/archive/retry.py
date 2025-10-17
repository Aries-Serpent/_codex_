"""Retry logic with exponential backoff for archive operations."""

from __future__ import annotations

import random
import time
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        *,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 32.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
        seed: int | None = None,
    ) -> None:
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self._seed = seed

    def delay_for_attempt(self, attempt: int) -> float:
        """Return the delay for *attempt* (0-indexed)."""

        delay = min(self.initial_delay * (self.backoff_factor**attempt), self.max_delay)
        if not self.jitter:
            return delay
        rng = random.Random(  # noqa: S311 - deterministic jitter for retry backoff
            None if self._seed is None else self._seed + attempt
        )
        return delay * (1.0 + rng.uniform(-0.1, 0.1))


def retry_with_backoff(
    config: RetryConfig,
    transient_errors: tuple[type[Exception], ...] = (
        ConnectionError,
        TimeoutError,
        OSError,
    ),
) -> Callable[[F], F]:
    """Decorator for retry logic with exponential backoff."""

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except transient_errors:
                    if attempt >= config.max_attempts - 1:
                        raise
                    delay = config.delay_for_attempt(attempt)
                    time.sleep(delay)
                    attempt += 1

        return wrapper  # type: ignore[misc]

    return decorator


def calculate_backoff(
    attempt: int,
    *,
    initial_delay: float = 1.0,
    max_delay: float = 32.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    seed: int | None = None,
) -> float:
    """Calculate backoff delay for a given attempt."""

    rng = random.Random(  # noqa: S311 - deterministic jitter for retry backoff
        None if seed is None else seed + attempt
    )
    delay = min(initial_delay * (backoff_factor**attempt), max_delay)
    if jitter:
        delay *= 1.0 + rng.uniform(-0.1, 0.1)
    return delay
