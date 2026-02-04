"""Performance metrics utilities."""

from __future__ import annotations

import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")
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


@dataclass
class TimingMetrics:
    """Simple timing container."""

    name: str
    started_ns: int
    finished_ns: int | None = None

    @property
    def duration_ms(self) -> float:
        end = time.perf_counter_ns() if self.finished_ns is None else self.finished_ns
        return (end - self.started_ns) / 1_000_000

    def stop(self) -> None:
        self.finished_ns = time.perf_counter_ns()

    def to_dict(self) -> dict[str, float | str]:
        return {
            "name": self.name,
            "duration_ms": round(self.duration_ms, 3),
        }


@contextmanager
def timer(name: str) -> Generator[TimingMetrics, None, None]:
    """Context manager that measures duration in milliseconds."""

    metrics = TimingMetrics(name=name, started_ns=time.perf_counter_ns())
    try:
        yield metrics
    finally:
        metrics.stop()


def x_measure_decompression__mutmut_orig(
    name: str | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator that records execution timing on the wrapped callable."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        metric_name = name or func.__name__

        def wrapper(*args, **kwargs):  # type: ignore[override]
            with timer(metric_name) as metrics:
                result = func(*args, **kwargs)
            wrapper.last_metrics = metrics  # type: ignore[attr-defined]
            return result

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = func.__module__
        wrapper.last_metrics = None  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator


def x_measure_decompression__mutmut_1(
    name: str | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator that records execution timing on the wrapped callable."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        metric_name = None

        def wrapper(*args, **kwargs):  # type: ignore[override]
            with timer(metric_name) as metrics:
                result = func(*args, **kwargs)
            wrapper.last_metrics = metrics  # type: ignore[attr-defined]
            return result

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = func.__module__
        wrapper.last_metrics = None  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator


def x_measure_decompression__mutmut_2(
    name: str | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator that records execution timing on the wrapped callable."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        metric_name = name and func.__name__

        def wrapper(*args, **kwargs):  # type: ignore[override]
            with timer(metric_name) as metrics:
                result = func(*args, **kwargs)
            wrapper.last_metrics = metrics  # type: ignore[attr-defined]
            return result

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = func.__module__
        wrapper.last_metrics = None  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator


def x_measure_decompression__mutmut_3(
    name: str | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator that records execution timing on the wrapped callable."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        metric_name = name or func.__name__

        def wrapper(*args, **kwargs):  # type: ignore[override]
            with timer(None) as metrics:
                result = func(*args, **kwargs)
            wrapper.last_metrics = metrics  # type: ignore[attr-defined]
            return result

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = func.__module__
        wrapper.last_metrics = None  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator


def x_measure_decompression__mutmut_4(
    name: str | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator that records execution timing on the wrapped callable."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        metric_name = name or func.__name__

        def wrapper(*args, **kwargs):  # type: ignore[override]
            with timer(metric_name) as metrics:
                result = None
            wrapper.last_metrics = metrics  # type: ignore[attr-defined]
            return result

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = func.__module__
        wrapper.last_metrics = None  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator


def x_measure_decompression__mutmut_5(
    name: str | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator that records execution timing on the wrapped callable."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        metric_name = name or func.__name__

        def wrapper(*args, **kwargs):  # type: ignore[override]
            with timer(metric_name) as metrics:
                result = func(**kwargs)
            wrapper.last_metrics = metrics  # type: ignore[attr-defined]
            return result

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = func.__module__
        wrapper.last_metrics = None  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator


def x_measure_decompression__mutmut_6(
    name: str | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator that records execution timing on the wrapped callable."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        metric_name = name or func.__name__

        def wrapper(*args, **kwargs):  # type: ignore[override]
            with timer(metric_name) as metrics:
                result = func(*args, )
            wrapper.last_metrics = metrics  # type: ignore[attr-defined]
            return result

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = func.__module__
        wrapper.last_metrics = None  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator


def x_measure_decompression__mutmut_7(
    name: str | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator that records execution timing on the wrapped callable."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        metric_name = name or func.__name__

        def wrapper(*args, **kwargs):  # type: ignore[override]
            with timer(metric_name) as metrics:
                result = func(*args, **kwargs)
            wrapper.last_metrics = None  # type: ignore[attr-defined]
            return result

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = func.__module__
        wrapper.last_metrics = None  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator


def x_measure_decompression__mutmut_8(
    name: str | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator that records execution timing on the wrapped callable."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        metric_name = name or func.__name__

        def wrapper(*args, **kwargs):  # type: ignore[override]
            with timer(metric_name) as metrics:
                result = func(*args, **kwargs)
            wrapper.last_metrics = metrics  # type: ignore[attr-defined]
            return result

        wrapper.__name__ = None
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = func.__module__
        wrapper.last_metrics = None  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator


def x_measure_decompression__mutmut_9(
    name: str | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator that records execution timing on the wrapped callable."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        metric_name = name or func.__name__

        def wrapper(*args, **kwargs):  # type: ignore[override]
            with timer(metric_name) as metrics:
                result = func(*args, **kwargs)
            wrapper.last_metrics = metrics  # type: ignore[attr-defined]
            return result

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = None
        wrapper.__module__ = func.__module__
        wrapper.last_metrics = None  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator


def x_measure_decompression__mutmut_10(
    name: str | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator that records execution timing on the wrapped callable."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        metric_name = name or func.__name__

        def wrapper(*args, **kwargs):  # type: ignore[override]
            with timer(metric_name) as metrics:
                result = func(*args, **kwargs)
            wrapper.last_metrics = metrics  # type: ignore[attr-defined]
            return result

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = None
        wrapper.last_metrics = None  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator


def x_measure_decompression__mutmut_11(
    name: str | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator that records execution timing on the wrapped callable."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        metric_name = name or func.__name__

        def wrapper(*args, **kwargs):  # type: ignore[override]
            with timer(metric_name) as metrics:
                result = func(*args, **kwargs)
            wrapper.last_metrics = metrics  # type: ignore[attr-defined]
            return result

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = func.__module__
        wrapper.last_metrics = ""  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator

x_measure_decompression__mutmut_mutants : ClassVar[MutantDict] = {
'x_measure_decompression__mutmut_1': x_measure_decompression__mutmut_1, 
    'x_measure_decompression__mutmut_2': x_measure_decompression__mutmut_2, 
    'x_measure_decompression__mutmut_3': x_measure_decompression__mutmut_3, 
    'x_measure_decompression__mutmut_4': x_measure_decompression__mutmut_4, 
    'x_measure_decompression__mutmut_5': x_measure_decompression__mutmut_5, 
    'x_measure_decompression__mutmut_6': x_measure_decompression__mutmut_6, 
    'x_measure_decompression__mutmut_7': x_measure_decompression__mutmut_7, 
    'x_measure_decompression__mutmut_8': x_measure_decompression__mutmut_8, 
    'x_measure_decompression__mutmut_9': x_measure_decompression__mutmut_9, 
    'x_measure_decompression__mutmut_10': x_measure_decompression__mutmut_10, 
    'x_measure_decompression__mutmut_11': x_measure_decompression__mutmut_11
}

def measure_decompression(*args, **kwargs):
    result = _mutmut_trampoline(x_measure_decompression__mutmut_orig, x_measure_decompression__mutmut_mutants, args, kwargs)
    return result 

measure_decompression.__signature__ = _mutmut_signature(x_measure_decompression__mutmut_orig)
x_measure_decompression__mutmut_orig.__name__ = 'x_measure_decompression'
