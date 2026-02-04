"""Retry helpers with exponential backoff."""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

import random
import time
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import Any, TypeVar

T = TypeVar("T")
Func = Callable[..., T]
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


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
        return random.Random(self.seed)  # nosec B311 - deterministic non-crypto RNG


def x_calculate_backoff__mutmut_orig(
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


def x_calculate_backoff__mutmut_1(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = None
    capped = min(base_delay, config.max_delay)
    if config.jitter <= 0:
        return capped
    generator = rng or config.create_rng()
    delta = capped * config.jitter
    return max(0.0, generator.uniform(capped - delta, capped + delta))


def x_calculate_backoff__mutmut_2(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay / (config.multiplier ** max(0, attempt - 1))
    capped = min(base_delay, config.max_delay)
    if config.jitter <= 0:
        return capped
    generator = rng or config.create_rng()
    delta = capped * config.jitter
    return max(0.0, generator.uniform(capped - delta, capped + delta))


def x_calculate_backoff__mutmut_3(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier * max(0, attempt - 1))
    capped = min(base_delay, config.max_delay)
    if config.jitter <= 0:
        return capped
    generator = rng or config.create_rng()
    delta = capped * config.jitter
    return max(0.0, generator.uniform(capped - delta, capped + delta))


def x_calculate_backoff__mutmut_4(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(None, attempt - 1))
    capped = min(base_delay, config.max_delay)
    if config.jitter <= 0:
        return capped
    generator = rng or config.create_rng()
    delta = capped * config.jitter
    return max(0.0, generator.uniform(capped - delta, capped + delta))


def x_calculate_backoff__mutmut_5(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(0, None))
    capped = min(base_delay, config.max_delay)
    if config.jitter <= 0:
        return capped
    generator = rng or config.create_rng()
    delta = capped * config.jitter
    return max(0.0, generator.uniform(capped - delta, capped + delta))


def x_calculate_backoff__mutmut_6(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(attempt - 1))
    capped = min(base_delay, config.max_delay)
    if config.jitter <= 0:
        return capped
    generator = rng or config.create_rng()
    delta = capped * config.jitter
    return max(0.0, generator.uniform(capped - delta, capped + delta))


def x_calculate_backoff__mutmut_7(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(0, ))
    capped = min(base_delay, config.max_delay)
    if config.jitter <= 0:
        return capped
    generator = rng or config.create_rng()
    delta = capped * config.jitter
    return max(0.0, generator.uniform(capped - delta, capped + delta))


def x_calculate_backoff__mutmut_8(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(1, attempt - 1))
    capped = min(base_delay, config.max_delay)
    if config.jitter <= 0:
        return capped
    generator = rng or config.create_rng()
    delta = capped * config.jitter
    return max(0.0, generator.uniform(capped - delta, capped + delta))


def x_calculate_backoff__mutmut_9(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(0, attempt + 1))
    capped = min(base_delay, config.max_delay)
    if config.jitter <= 0:
        return capped
    generator = rng or config.create_rng()
    delta = capped * config.jitter
    return max(0.0, generator.uniform(capped - delta, capped + delta))


def x_calculate_backoff__mutmut_10(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(0, attempt - 2))
    capped = min(base_delay, config.max_delay)
    if config.jitter <= 0:
        return capped
    generator = rng or config.create_rng()
    delta = capped * config.jitter
    return max(0.0, generator.uniform(capped - delta, capped + delta))


def x_calculate_backoff__mutmut_11(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(0, attempt - 1))
    capped = None
    if config.jitter <= 0:
        return capped
    generator = rng or config.create_rng()
    delta = capped * config.jitter
    return max(0.0, generator.uniform(capped - delta, capped + delta))


def x_calculate_backoff__mutmut_12(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(0, attempt - 1))
    capped = min(None, config.max_delay)
    if config.jitter <= 0:
        return capped
    generator = rng or config.create_rng()
    delta = capped * config.jitter
    return max(0.0, generator.uniform(capped - delta, capped + delta))


def x_calculate_backoff__mutmut_13(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(0, attempt - 1))
    capped = min(base_delay, None)
    if config.jitter <= 0:
        return capped
    generator = rng or config.create_rng()
    delta = capped * config.jitter
    return max(0.0, generator.uniform(capped - delta, capped + delta))


def x_calculate_backoff__mutmut_14(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(0, attempt - 1))
    capped = min(config.max_delay)
    if config.jitter <= 0:
        return capped
    generator = rng or config.create_rng()
    delta = capped * config.jitter
    return max(0.0, generator.uniform(capped - delta, capped + delta))


def x_calculate_backoff__mutmut_15(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(0, attempt - 1))
    capped = min(base_delay, )
    if config.jitter <= 0:
        return capped
    generator = rng or config.create_rng()
    delta = capped * config.jitter
    return max(0.0, generator.uniform(capped - delta, capped + delta))


def x_calculate_backoff__mutmut_16(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(0, attempt - 1))
    capped = min(base_delay, config.max_delay)
    if config.jitter < 0:
        return capped
    generator = rng or config.create_rng()
    delta = capped * config.jitter
    return max(0.0, generator.uniform(capped - delta, capped + delta))


def x_calculate_backoff__mutmut_17(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(0, attempt - 1))
    capped = min(base_delay, config.max_delay)
    if config.jitter <= 1:
        return capped
    generator = rng or config.create_rng()
    delta = capped * config.jitter
    return max(0.0, generator.uniform(capped - delta, capped + delta))


def x_calculate_backoff__mutmut_18(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(0, attempt - 1))
    capped = min(base_delay, config.max_delay)
    if config.jitter <= 0:
        return capped
    generator = None
    delta = capped * config.jitter
    return max(0.0, generator.uniform(capped - delta, capped + delta))


def x_calculate_backoff__mutmut_19(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(0, attempt - 1))
    capped = min(base_delay, config.max_delay)
    if config.jitter <= 0:
        return capped
    generator = rng and config.create_rng()
    delta = capped * config.jitter
    return max(0.0, generator.uniform(capped - delta, capped + delta))


def x_calculate_backoff__mutmut_20(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(0, attempt - 1))
    capped = min(base_delay, config.max_delay)
    if config.jitter <= 0:
        return capped
    generator = rng or config.create_rng()
    delta = None
    return max(0.0, generator.uniform(capped - delta, capped + delta))


def x_calculate_backoff__mutmut_21(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(0, attempt - 1))
    capped = min(base_delay, config.max_delay)
    if config.jitter <= 0:
        return capped
    generator = rng or config.create_rng()
    delta = capped / config.jitter
    return max(0.0, generator.uniform(capped - delta, capped + delta))


def x_calculate_backoff__mutmut_22(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(0, attempt - 1))
    capped = min(base_delay, config.max_delay)
    if config.jitter <= 0:
        return capped
    generator = rng or config.create_rng()
    delta = capped * config.jitter
    return max(None, generator.uniform(capped - delta, capped + delta))


def x_calculate_backoff__mutmut_23(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(0, attempt - 1))
    capped = min(base_delay, config.max_delay)
    if config.jitter <= 0:
        return capped
    generator = rng or config.create_rng()
    delta = capped * config.jitter
    return max(0.0, None)


def x_calculate_backoff__mutmut_24(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(0, attempt - 1))
    capped = min(base_delay, config.max_delay)
    if config.jitter <= 0:
        return capped
    generator = rng or config.create_rng()
    delta = capped * config.jitter
    return max(generator.uniform(capped - delta, capped + delta))


def x_calculate_backoff__mutmut_25(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(0, attempt - 1))
    capped = min(base_delay, config.max_delay)
    if config.jitter <= 0:
        return capped
    generator = rng or config.create_rng()
    delta = capped * config.jitter
    return max(0.0, )


def x_calculate_backoff__mutmut_26(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(0, attempt - 1))
    capped = min(base_delay, config.max_delay)
    if config.jitter <= 0:
        return capped
    generator = rng or config.create_rng()
    delta = capped * config.jitter
    return max(1.0, generator.uniform(capped - delta, capped + delta))


def x_calculate_backoff__mutmut_27(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(0, attempt - 1))
    capped = min(base_delay, config.max_delay)
    if config.jitter <= 0:
        return capped
    generator = rng or config.create_rng()
    delta = capped * config.jitter
    return max(0.0, generator.uniform(None, capped + delta))


def x_calculate_backoff__mutmut_28(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(0, attempt - 1))
    capped = min(base_delay, config.max_delay)
    if config.jitter <= 0:
        return capped
    generator = rng or config.create_rng()
    delta = capped * config.jitter
    return max(0.0, generator.uniform(capped - delta, None))


def x_calculate_backoff__mutmut_29(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(0, attempt - 1))
    capped = min(base_delay, config.max_delay)
    if config.jitter <= 0:
        return capped
    generator = rng or config.create_rng()
    delta = capped * config.jitter
    return max(0.0, generator.uniform(capped + delta))


def x_calculate_backoff__mutmut_30(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(0, attempt - 1))
    capped = min(base_delay, config.max_delay)
    if config.jitter <= 0:
        return capped
    generator = rng or config.create_rng()
    delta = capped * config.jitter
    return max(0.0, generator.uniform(capped - delta, ))


def x_calculate_backoff__mutmut_31(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(0, attempt - 1))
    capped = min(base_delay, config.max_delay)
    if config.jitter <= 0:
        return capped
    generator = rng or config.create_rng()
    delta = capped * config.jitter
    return max(0.0, generator.uniform(capped + delta, capped + delta))


def x_calculate_backoff__mutmut_32(
    attempt: int, *, config: RetryConfig, rng: random.Random | None = None
) -> float:
    """Return the delay for *attempt* using exponential backoff."""

    base_delay = config.initial_delay * (config.multiplier ** max(0, attempt - 1))
    capped = min(base_delay, config.max_delay)
    if config.jitter <= 0:
        return capped
    generator = rng or config.create_rng()
    delta = capped * config.jitter
    return max(0.0, generator.uniform(capped - delta, capped - delta))

x_calculate_backoff__mutmut_mutants : ClassVar[MutantDict] = {
'x_calculate_backoff__mutmut_1': x_calculate_backoff__mutmut_1, 
    'x_calculate_backoff__mutmut_2': x_calculate_backoff__mutmut_2, 
    'x_calculate_backoff__mutmut_3': x_calculate_backoff__mutmut_3, 
    'x_calculate_backoff__mutmut_4': x_calculate_backoff__mutmut_4, 
    'x_calculate_backoff__mutmut_5': x_calculate_backoff__mutmut_5, 
    'x_calculate_backoff__mutmut_6': x_calculate_backoff__mutmut_6, 
    'x_calculate_backoff__mutmut_7': x_calculate_backoff__mutmut_7, 
    'x_calculate_backoff__mutmut_8': x_calculate_backoff__mutmut_8, 
    'x_calculate_backoff__mutmut_9': x_calculate_backoff__mutmut_9, 
    'x_calculate_backoff__mutmut_10': x_calculate_backoff__mutmut_10, 
    'x_calculate_backoff__mutmut_11': x_calculate_backoff__mutmut_11, 
    'x_calculate_backoff__mutmut_12': x_calculate_backoff__mutmut_12, 
    'x_calculate_backoff__mutmut_13': x_calculate_backoff__mutmut_13, 
    'x_calculate_backoff__mutmut_14': x_calculate_backoff__mutmut_14, 
    'x_calculate_backoff__mutmut_15': x_calculate_backoff__mutmut_15, 
    'x_calculate_backoff__mutmut_16': x_calculate_backoff__mutmut_16, 
    'x_calculate_backoff__mutmut_17': x_calculate_backoff__mutmut_17, 
    'x_calculate_backoff__mutmut_18': x_calculate_backoff__mutmut_18, 
    'x_calculate_backoff__mutmut_19': x_calculate_backoff__mutmut_19, 
    'x_calculate_backoff__mutmut_20': x_calculate_backoff__mutmut_20, 
    'x_calculate_backoff__mutmut_21': x_calculate_backoff__mutmut_21, 
    'x_calculate_backoff__mutmut_22': x_calculate_backoff__mutmut_22, 
    'x_calculate_backoff__mutmut_23': x_calculate_backoff__mutmut_23, 
    'x_calculate_backoff__mutmut_24': x_calculate_backoff__mutmut_24, 
    'x_calculate_backoff__mutmut_25': x_calculate_backoff__mutmut_25, 
    'x_calculate_backoff__mutmut_26': x_calculate_backoff__mutmut_26, 
    'x_calculate_backoff__mutmut_27': x_calculate_backoff__mutmut_27, 
    'x_calculate_backoff__mutmut_28': x_calculate_backoff__mutmut_28, 
    'x_calculate_backoff__mutmut_29': x_calculate_backoff__mutmut_29, 
    'x_calculate_backoff__mutmut_30': x_calculate_backoff__mutmut_30, 
    'x_calculate_backoff__mutmut_31': x_calculate_backoff__mutmut_31, 
    'x_calculate_backoff__mutmut_32': x_calculate_backoff__mutmut_32
}

def calculate_backoff(*args, **kwargs):
    result = _mutmut_trampoline(x_calculate_backoff__mutmut_orig, x_calculate_backoff__mutmut_mutants, args, kwargs)
    return result 

calculate_backoff.__signature__ = _mutmut_signature(x_calculate_backoff__mutmut_orig)
x_calculate_backoff__mutmut_orig.__name__ = 'x_calculate_backoff'


def x_retry_with_backoff__mutmut_orig(config: RetryConfig | None = None) -> Callable[[Func], Func]:
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
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("Exception occurred", exc_info=True)
                    raise
            if last_error is not None:  # pragma: no cover - defensive
                raise last_error
            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def x_retry_with_backoff__mutmut_1(config: RetryConfig | None = None) -> Callable[[Func], Func]:
    """Return a decorator that retries transient errors."""

    retry_config = None

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
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("Exception occurred", exc_info=True)
                    raise
            if last_error is not None:  # pragma: no cover - defensive
                raise last_error
            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def x_retry_with_backoff__mutmut_2(config: RetryConfig | None = None) -> Callable[[Func], Func]:
    """Return a decorator that retries transient errors."""

    retry_config = config and RetryConfig()

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
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("Exception occurred", exc_info=True)
                    raise
            if last_error is not None:  # pragma: no cover - defensive
                raise last_error
            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def x_retry_with_backoff__mutmut_3(config: RetryConfig | None = None) -> Callable[[Func], Func]:
    """Return a decorator that retries transient errors."""

    retry_config = config or RetryConfig()

    def decorator(func: Func) -> Func:
        if retry_config.enabled:
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
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("Exception occurred", exc_info=True)
                    raise
            if last_error is not None:  # pragma: no cover - defensive
                raise last_error
            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator

x_retry_with_backoff__mutmut_mutants : ClassVar[MutantDict] = {
'x_retry_with_backoff__mutmut_1': x_retry_with_backoff__mutmut_1, 
    'x_retry_with_backoff__mutmut_2': x_retry_with_backoff__mutmut_2, 
    'x_retry_with_backoff__mutmut_3': x_retry_with_backoff__mutmut_3
}

def retry_with_backoff(*args, **kwargs):
    result = _mutmut_trampoline(x_retry_with_backoff__mutmut_orig, x_retry_with_backoff__mutmut_mutants, args, kwargs)
    return result 

retry_with_backoff.__signature__ = _mutmut_signature(x_retry_with_backoff__mutmut_orig)
x_retry_with_backoff__mutmut_orig.__name__ = 'x_retry_with_backoff'
