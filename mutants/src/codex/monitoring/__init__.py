"""Minimal monitoring registry used by Zendesk integrations."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from statistics import mean
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
class _Metric:
    """Base representation for a metric instrument."""

    name: str
    description: str
    unit: str | None = None

    def snapshot(self) -> dict[str, object]:  # pragma: no cover - simple accessors
        return {
            "name": self.name,
            "description": self.description,
            "unit": self.unit,
        }


@dataclass
class Counter(_Metric):
    """Monotonic counter tracking increment operations."""

    value: int = 0

    def increment(self, amount: int = 1) -> None:
        self.value += amount

    def snapshot(self) -> dict[str, object]:  # pragma: no cover - simple accessors
        data = super().snapshot()
        data["value"] = self.value
        return data


@dataclass
class Histogram(_Metric):
    """Histogram collecting observed numeric values."""

    _observations: list[float] = field(default_factory=list)

    def observe(self, value: float) -> None:
        self._observations.append(float(value))

    def snapshot(self) -> dict[str, object]:  # pragma: no cover - simple accessors
        data = super().snapshot()
        if not self._observations:
            stats: dict[str, float] = {"count": 0, "sum": 0.0}
        else:
            stats = {
                "count": len(self._observations),
                "sum": float(sum(self._observations)),
                "avg": float(mean(self._observations)),
            }
        data.update(stats)
        return data


class _MetricRegistry:
    """In-memory registry for metric instruments."""

    def xǁ_MetricRegistryǁ__init____mutmut_orig(self) -> None:
        self._metrics: dict[str, _Metric] = {}

    def xǁ_MetricRegistryǁ__init____mutmut_1(self) -> None:
        self._metrics: dict[str, _Metric] = None
    
    xǁ_MetricRegistryǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_MetricRegistryǁ__init____mutmut_1': xǁ_MetricRegistryǁ__init____mutmut_1
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_MetricRegistryǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁ_MetricRegistryǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁ_MetricRegistryǁ__init____mutmut_orig)
    xǁ_MetricRegistryǁ__init____mutmut_orig.__name__ = 'xǁ_MetricRegistryǁ__init__'

    def xǁ_MetricRegistryǁregister__mutmut_orig(self, metric: _Metric) -> None:
        self._metrics[metric.name] = metric

    def xǁ_MetricRegistryǁregister__mutmut_1(self, metric: _Metric) -> None:
        self._metrics[metric.name] = None
    
    xǁ_MetricRegistryǁregister__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_MetricRegistryǁregister__mutmut_1': xǁ_MetricRegistryǁregister__mutmut_1
    }
    
    def register(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_MetricRegistryǁregister__mutmut_orig"), object.__getattribute__(self, "xǁ_MetricRegistryǁregister__mutmut_mutants"), args, kwargs, self)
        return result 
    
    register.__signature__ = _mutmut_signature(xǁ_MetricRegistryǁregister__mutmut_orig)
    xǁ_MetricRegistryǁregister__mutmut_orig.__name__ = 'xǁ_MetricRegistryǁregister'

    def xǁ_MetricRegistryǁget__mutmut_orig(self, name: str) -> _Metric | None:
        return self._metrics.get(name)

    def xǁ_MetricRegistryǁget__mutmut_1(self, name: str) -> _Metric | None:
        return self._metrics.get(None)
    
    xǁ_MetricRegistryǁget__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_MetricRegistryǁget__mutmut_1': xǁ_MetricRegistryǁget__mutmut_1
    }
    
    def get(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_MetricRegistryǁget__mutmut_orig"), object.__getattribute__(self, "xǁ_MetricRegistryǁget__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get.__signature__ = _mutmut_signature(xǁ_MetricRegistryǁget__mutmut_orig)
    xǁ_MetricRegistryǁget__mutmut_orig.__name__ = 'xǁ_MetricRegistryǁget'

    def registered(self) -> Iterable[_Metric]:  # pragma: no cover - simple iterator
        return self._metrics.values()

    def xǁ_MetricRegistryǁemit_counter__mutmut_orig(self, name: str, amount: int = 1) -> None:
        metric = self.get(name)
        if isinstance(metric, Counter):
            metric.increment(amount)
            return
        raise KeyError(name)

    def xǁ_MetricRegistryǁemit_counter__mutmut_1(self, name: str, amount: int = 2) -> None:
        metric = self.get(name)
        if isinstance(metric, Counter):
            metric.increment(amount)
            return
        raise KeyError(name)

    def xǁ_MetricRegistryǁemit_counter__mutmut_2(self, name: str, amount: int = 1) -> None:
        metric = None
        if isinstance(metric, Counter):
            metric.increment(amount)
            return
        raise KeyError(name)

    def xǁ_MetricRegistryǁemit_counter__mutmut_3(self, name: str, amount: int = 1) -> None:
        metric = self.get(None)
        if isinstance(metric, Counter):
            metric.increment(amount)
            return
        raise KeyError(name)

    def xǁ_MetricRegistryǁemit_counter__mutmut_4(self, name: str, amount: int = 1) -> None:
        metric = self.get(name)
        if isinstance(metric, Counter):
            metric.increment(None)
            return
        raise KeyError(name)

    def xǁ_MetricRegistryǁemit_counter__mutmut_5(self, name: str, amount: int = 1) -> None:
        metric = self.get(name)
        if isinstance(metric, Counter):
            metric.increment(amount)
            return
        raise KeyError(None)
    
    xǁ_MetricRegistryǁemit_counter__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_MetricRegistryǁemit_counter__mutmut_1': xǁ_MetricRegistryǁemit_counter__mutmut_1, 
        'xǁ_MetricRegistryǁemit_counter__mutmut_2': xǁ_MetricRegistryǁemit_counter__mutmut_2, 
        'xǁ_MetricRegistryǁemit_counter__mutmut_3': xǁ_MetricRegistryǁemit_counter__mutmut_3, 
        'xǁ_MetricRegistryǁemit_counter__mutmut_4': xǁ_MetricRegistryǁemit_counter__mutmut_4, 
        'xǁ_MetricRegistryǁemit_counter__mutmut_5': xǁ_MetricRegistryǁemit_counter__mutmut_5
    }
    
    def emit_counter(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_MetricRegistryǁemit_counter__mutmut_orig"), object.__getattribute__(self, "xǁ_MetricRegistryǁemit_counter__mutmut_mutants"), args, kwargs, self)
        return result 
    
    emit_counter.__signature__ = _mutmut_signature(xǁ_MetricRegistryǁemit_counter__mutmut_orig)
    xǁ_MetricRegistryǁemit_counter__mutmut_orig.__name__ = 'xǁ_MetricRegistryǁemit_counter'


metrics = _MetricRegistry()

__all__ = ["Counter", "Histogram", "metrics"]
