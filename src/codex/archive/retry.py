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
        self.seed = seed


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
            delay = config.initial_delay
            rng = random.Random(config.seed)  # noqa: S311 - jitter is non-cryptographic
            while attempt < config.max_attempts:
                try:
                    return func(*args, **kwargs)
                except transient_errors:
                    attempt += 1
                    if attempt >= config.max_attempts:
                        raise
                    jitter_factor = 1.0
                    if config.jitter:
                        jitter_factor += rng.uniform(-0.1, 0.1)
                    actual_delay = min(delay * jitter_factor, config.max_delay)
                    time.sleep(actual_delay)
                    delay = min(delay * config.backoff_factor, config.max_delay)
            return func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


def calculate_backoff(
    attempt: int,
    initial_delay: float = 1.0,
    max_delay: float = 32.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    seed: int | None = None,
) -> float:
    """Calculate backoff delay for a given attempt."""

    rng = random.Random()  # noqa: S311 - jitter is non-cryptographic
    if seed is not None:
        rng.seed(seed + attempt)
    delay = initial_delay * (backoff_factor**attempt)
    delay = min(delay, max_delay)
    if jitter:
        delay *= 1.0 + rng.uniform(-0.1, 0.1)
    return delay
