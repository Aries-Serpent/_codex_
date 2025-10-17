"""Retry helpers with exponential backoff."""

from __future__ import annotations

import random
import time
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import Any, TypeVar

T = TypeVar("T")
Func = Callable[..., T]


@dataclass(frozen=True)
class RetryConfig:
    """Configuration for :func:`retry_with_backoff`."""

    enabled: bool = True
    max_attempts: int = 5
    initial_delay: float = 1.0
    max_delay: float = 32.0
    multiplier: float = 2.0
    jitter: float = 0.1
    seed: int | None = None
    transient_exceptions: tuple[type[BaseException], ...] = (
        ConnectionError,
        TimeoutError,
        OSError,
    )

    def create_rng(self) -> random.Random:
        return random.Random(self.seed)  # noqa: S311 - deterministic non-crypto RNG


def calculate_backoff(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(0, attempt - 1))
    capped = min(base_delay, config.max_delay)
    if config.jitter <= 0:
        return capped
    generator = rng or config.create_rng()
    delta = capped * config.jitter
    return max(0.0, generator.uniform(capped - delta, capped + delta))


def retry_with_backoff(config: RetryConfig | None = None) -> Callable[[Func], Func]:
    """Return a decorator that retries transient errors."""

    retry_config = config or RetryConfig()

    def decorator(func: Func) -> Func:
        if not retry_config.enabled:
            return func

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            rng = retry_config.create_rng()
            last_error: BaseException | None = None
            for attempt in range(1, retry_config.max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except retry_config.transient_exceptions as exc:  # type: ignore[misc]
                    last_error = exc
                    if attempt >= retry_config.max_attempts:
                        raise
                    delay = calculate_backoff(attempt, config=retry_config, rng=rng)
                    time.sleep(delay)
                except Exception:
                    raise
            if last_error is not None:  # pragma: no cover - defensive
                raise last_error
            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
