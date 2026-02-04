"""
Registry Module

This module provides functionality for registry.

Usage:
    from common.registry import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

from collections.abc import Callable, Iterable
from typing import Any

try:  # pragma: no cover - optional import path when codex_ml unavailable
    from codex_ml.metrics.metric_implementations import (
        BLEUScore,
        F1Score,
        RecallScore,
        TokenAccuracy,
    )
except Exception:  # pragma: no cover - allow registry to exist without metrics module
    BLEUScore = F1Score = RecallScore = TokenAccuracy = None  # type: ignore[assignment]
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


class Registry:
    """Simple string-to-callable registry with decorator support."""

    def xǁRegistryǁ__init____mutmut_orig(self, name: str) -> None:
        self.name = name
        self._store: dict[str, Callable[..., Any]] = {}

    def xǁRegistryǁ__init____mutmut_1(self, name: str) -> None:
        self.name = None
        self._store: dict[str, Callable[..., Any]] = {}

    def xǁRegistryǁ__init____mutmut_2(self, name: str) -> None:
        self.name = name
        self._store: dict[str, Callable[..., Any]] = None
    
    xǁRegistryǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRegistryǁ__init____mutmut_1': xǁRegistryǁ__init____mutmut_1, 
        'xǁRegistryǁ__init____mutmut_2': xǁRegistryǁ__init____mutmut_2
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRegistryǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁRegistryǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁRegistryǁ__init____mutmut_orig)
    xǁRegistryǁ__init____mutmut_orig.__name__ = 'xǁRegistryǁ__init__'

    def xǁRegistryǁregister__mutmut_orig(
        self, key: str | None = None
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            registry_key = key or fn.__name__
            if registry_key in self._store:
                raise KeyError(f"{self.name}: key already registered: {registry_key}")
            self._store[registry_key] = fn
            return fn

        return decorator

    def xǁRegistryǁregister__mutmut_1(
        self, key: str | None = None
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            registry_key = None
            if registry_key in self._store:
                raise KeyError(f"{self.name}: key already registered: {registry_key}")
            self._store[registry_key] = fn
            return fn

        return decorator

    def xǁRegistryǁregister__mutmut_2(
        self, key: str | None = None
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            registry_key = key and fn.__name__
            if registry_key in self._store:
                raise KeyError(f"{self.name}: key already registered: {registry_key}")
            self._store[registry_key] = fn
            return fn

        return decorator

    def xǁRegistryǁregister__mutmut_3(
        self, key: str | None = None
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            registry_key = key or fn.__name__
            if registry_key not in self._store:
                raise KeyError(f"{self.name}: key already registered: {registry_key}")
            self._store[registry_key] = fn
            return fn

        return decorator

    def xǁRegistryǁregister__mutmut_4(
        self, key: str | None = None
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            registry_key = key or fn.__name__
            if registry_key in self._store:
                raise KeyError(None)
            self._store[registry_key] = fn
            return fn

        return decorator

    def xǁRegistryǁregister__mutmut_5(
        self, key: str | None = None
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            registry_key = key or fn.__name__
            if registry_key in self._store:
                raise KeyError(f"{self.name}: key already registered: {registry_key}")
            self._store[registry_key] = None
            return fn

        return decorator
    
    xǁRegistryǁregister__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRegistryǁregister__mutmut_1': xǁRegistryǁregister__mutmut_1, 
        'xǁRegistryǁregister__mutmut_2': xǁRegistryǁregister__mutmut_2, 
        'xǁRegistryǁregister__mutmut_3': xǁRegistryǁregister__mutmut_3, 
        'xǁRegistryǁregister__mutmut_4': xǁRegistryǁregister__mutmut_4, 
        'xǁRegistryǁregister__mutmut_5': xǁRegistryǁregister__mutmut_5
    }
    
    def register(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRegistryǁregister__mutmut_orig"), object.__getattribute__(self, "xǁRegistryǁregister__mutmut_mutants"), args, kwargs, self)
        return result 
    
    register.__signature__ = _mutmut_signature(xǁRegistryǁregister__mutmut_orig)
    xǁRegistryǁregister__mutmut_orig.__name__ = 'xǁRegistryǁregister'

    def xǁRegistryǁadd__mutmut_orig(self, key: str, fn: Callable[..., Any]) -> None:
        if key in self._store:
            raise KeyError(f"{self.name}: key already registered: {key}")
        self._store[key] = fn

    def xǁRegistryǁadd__mutmut_1(self, key: str, fn: Callable[..., Any]) -> None:
        if key not in self._store:
            raise KeyError(f"{self.name}: key already registered: {key}")
        self._store[key] = fn

    def xǁRegistryǁadd__mutmut_2(self, key: str, fn: Callable[..., Any]) -> None:
        if key in self._store:
            raise KeyError(None)
        self._store[key] = fn

    def xǁRegistryǁadd__mutmut_3(self, key: str, fn: Callable[..., Any]) -> None:
        if key in self._store:
            raise KeyError(f"{self.name}: key already registered: {key}")
        self._store[key] = None
    
    xǁRegistryǁadd__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRegistryǁadd__mutmut_1': xǁRegistryǁadd__mutmut_1, 
        'xǁRegistryǁadd__mutmut_2': xǁRegistryǁadd__mutmut_2, 
        'xǁRegistryǁadd__mutmut_3': xǁRegistryǁadd__mutmut_3
    }
    
    def add(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRegistryǁadd__mutmut_orig"), object.__getattribute__(self, "xǁRegistryǁadd__mutmut_mutants"), args, kwargs, self)
        return result 
    
    add.__signature__ = _mutmut_signature(xǁRegistryǁadd__mutmut_orig)
    xǁRegistryǁadd__mutmut_orig.__name__ = 'xǁRegistryǁadd'

    def xǁRegistryǁget__mutmut_orig(self, key: str) -> Callable[..., Any]:
        if key not in self._store:
            raise KeyError(f"{self.name}: not found: {key}")
        return self._store[key]

    def xǁRegistryǁget__mutmut_1(self, key: str) -> Callable[..., Any]:
        if key in self._store:
            raise KeyError(f"{self.name}: not found: {key}")
        return self._store[key]

    def xǁRegistryǁget__mutmut_2(self, key: str) -> Callable[..., Any]:
        if key not in self._store:
            raise KeyError(None)
        return self._store[key]
    
    xǁRegistryǁget__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRegistryǁget__mutmut_1': xǁRegistryǁget__mutmut_1, 
        'xǁRegistryǁget__mutmut_2': xǁRegistryǁget__mutmut_2
    }
    
    def get(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRegistryǁget__mutmut_orig"), object.__getattribute__(self, "xǁRegistryǁget__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get.__signature__ = _mutmut_signature(xǁRegistryǁget__mutmut_orig)
    xǁRegistryǁget__mutmut_orig.__name__ = 'xǁRegistryǁget'

    def xǁRegistryǁkeys__mutmut_orig(self) -> list[str]:
        return list(self._store.keys())

    def xǁRegistryǁkeys__mutmut_1(self) -> list[str]:
        return list(None)
    
    xǁRegistryǁkeys__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRegistryǁkeys__mutmut_1': xǁRegistryǁkeys__mutmut_1
    }
    
    def keys(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRegistryǁkeys__mutmut_orig"), object.__getattribute__(self, "xǁRegistryǁkeys__mutmut_mutants"), args, kwargs, self)
        return result 
    
    keys.__signature__ = _mutmut_signature(xǁRegistryǁkeys__mutmut_orig)
    xǁRegistryǁkeys__mutmut_orig.__name__ = 'xǁRegistryǁkeys'

    def xǁRegistryǁ__contains____mutmut_orig(self, key: str) -> bool:  # pragma: no cover - trivial
        return key in self._store

    def xǁRegistryǁ__contains____mutmut_1(self, key: str) -> bool:  # pragma: no cover - trivial
        return key not in self._store
    
    xǁRegistryǁ__contains____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRegistryǁ__contains____mutmut_1': xǁRegistryǁ__contains____mutmut_1
    }
    
    def __contains__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRegistryǁ__contains____mutmut_orig"), object.__getattribute__(self, "xǁRegistryǁ__contains____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __contains__.__signature__ = _mutmut_signature(xǁRegistryǁ__contains____mutmut_orig)
    xǁRegistryǁ__contains____mutmut_orig.__name__ = 'xǁRegistryǁ__contains__'

    def items(self) -> Iterable[tuple[str, Callable[..., Any]]]:  # pragma: no cover - convenience
        return self._store.items()


MODELS = Registry("models")
DATASETS = Registry("datasets")
METRICS = Registry("metrics")

if F1Score is not None:  # pragma: no branch - guard optional dependency
    METRICS.add("f1_score", F1Score)
    METRICS.add("recall_score", RecallScore)
    METRICS.add("token_accuracy", TokenAccuracy)
    METRICS.add("bleu_score", BLEUScore)
