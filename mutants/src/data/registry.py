"""
Registry Module

This module provides functionality for registry.

Usage:
    from data.registry import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)
"""Dataset registry utilities for Codex data loaders."""


import importlib
from typing import Any, Callable

try:  # pragma: no cover - torch is optional
    from torch.utils.data import DataLoader, TensorDataset, random_split

    import torch
except Exception:  # pragma: no cover - fallback stubs when torch is absent
    torch = None  # type: ignore[assignment]
    DataLoader = None  # type: ignore[assignment]
    TensorDataset = None  # type: ignore[assignment]
    random_split = None  # type: ignore[assignment]

_REGISTRY: dict[str, Callable[..., Any]] = {}
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


class DatasetRegistryError(RuntimeError):
    """Raised when dataset registry operations fail."""


def x_register__mutmut_orig(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Register ``fn`` under ``name`` and return the original callable."""

    normalized = name.strip().lower()
    if not normalized:
        raise ValueError("dataset name must be a non-empty string")

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        if normalized in _REGISTRY:
            raise DatasetRegistryError(f"Dataset '{name}' already registered")
        _REGISTRY[normalized] = fn
        return fn

    return decorator


def x_register__mutmut_1(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Register ``fn`` under ``name`` and return the original callable."""

    normalized = None
    if not normalized:
        raise ValueError("dataset name must be a non-empty string")

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        if normalized in _REGISTRY:
            raise DatasetRegistryError(f"Dataset '{name}' already registered")
        _REGISTRY[normalized] = fn
        return fn

    return decorator


def x_register__mutmut_2(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Register ``fn`` under ``name`` and return the original callable."""

    normalized = name.strip().upper()
    if not normalized:
        raise ValueError("dataset name must be a non-empty string")

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        if normalized in _REGISTRY:
            raise DatasetRegistryError(f"Dataset '{name}' already registered")
        _REGISTRY[normalized] = fn
        return fn

    return decorator


def x_register__mutmut_3(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Register ``fn`` under ``name`` and return the original callable."""

    normalized = name.strip().lower()
    if normalized:
        raise ValueError("dataset name must be a non-empty string")

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        if normalized in _REGISTRY:
            raise DatasetRegistryError(f"Dataset '{name}' already registered")
        _REGISTRY[normalized] = fn
        return fn

    return decorator


def x_register__mutmut_4(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Register ``fn`` under ``name`` and return the original callable."""

    normalized = name.strip().lower()
    if not normalized:
        raise ValueError(None)

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        if normalized in _REGISTRY:
            raise DatasetRegistryError(f"Dataset '{name}' already registered")
        _REGISTRY[normalized] = fn
        return fn

    return decorator


def x_register__mutmut_5(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Register ``fn`` under ``name`` and return the original callable."""

    normalized = name.strip().lower()
    if not normalized:
        raise ValueError("XXdataset name must be a non-empty stringXX")

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        if normalized in _REGISTRY:
            raise DatasetRegistryError(f"Dataset '{name}' already registered")
        _REGISTRY[normalized] = fn
        return fn

    return decorator


def x_register__mutmut_6(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Register ``fn`` under ``name`` and return the original callable."""

    normalized = name.strip().lower()
    if not normalized:
        raise ValueError("DATASET NAME MUST BE A NON-EMPTY STRING")

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        if normalized in _REGISTRY:
            raise DatasetRegistryError(f"Dataset '{name}' already registered")
        _REGISTRY[normalized] = fn
        return fn

    return decorator


def x_register__mutmut_7(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Register ``fn`` under ``name`` and return the original callable."""

    normalized = name.strip().lower()
    if not normalized:
        raise ValueError("dataset name must be a non-empty string")

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        if normalized not in _REGISTRY:
            raise DatasetRegistryError(f"Dataset '{name}' already registered")
        _REGISTRY[normalized] = fn
        return fn

    return decorator


def x_register__mutmut_8(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Register ``fn`` under ``name`` and return the original callable."""

    normalized = name.strip().lower()
    if not normalized:
        raise ValueError("dataset name must be a non-empty string")

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        if normalized in _REGISTRY:
            raise DatasetRegistryError(None)
        _REGISTRY[normalized] = fn
        return fn

    return decorator


def x_register__mutmut_9(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Register ``fn`` under ``name`` and return the original callable."""

    normalized = name.strip().lower()
    if not normalized:
        raise ValueError("dataset name must be a non-empty string")

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        if normalized in _REGISTRY:
            raise DatasetRegistryError(f"Dataset '{name}' already registered")
        _REGISTRY[normalized] = None
        return fn

    return decorator

x_register__mutmut_mutants : ClassVar[MutantDict] = {
'x_register__mutmut_1': x_register__mutmut_1, 
    'x_register__mutmut_2': x_register__mutmut_2, 
    'x_register__mutmut_3': x_register__mutmut_3, 
    'x_register__mutmut_4': x_register__mutmut_4, 
    'x_register__mutmut_5': x_register__mutmut_5, 
    'x_register__mutmut_6': x_register__mutmut_6, 
    'x_register__mutmut_7': x_register__mutmut_7, 
    'x_register__mutmut_8': x_register__mutmut_8, 
    'x_register__mutmut_9': x_register__mutmut_9
}

def register(*args, **kwargs):
    result = _mutmut_trampoline(x_register__mutmut_orig, x_register__mutmut_mutants, args, kwargs)
    return result 

register.__signature__ = _mutmut_signature(x_register__mutmut_orig)
x_register__mutmut_orig.__name__ = 'x_register'


def x_register_dataset__mutmut_orig(name: str, fn: Callable[..., Any]) -> None:
    """Register ``fn`` explicitly without using the decorator helper."""

    if not callable(fn):
        raise TypeError("dataset builder must be callable")
    register(name)(fn)


def x_register_dataset__mutmut_1(name: str, fn: Callable[..., Any]) -> None:
    """Register ``fn`` explicitly without using the decorator helper."""

    if callable(fn):
        raise TypeError("dataset builder must be callable")
    register(name)(fn)


def x_register_dataset__mutmut_2(name: str, fn: Callable[..., Any]) -> None:
    """Register ``fn`` explicitly without using the decorator helper."""

    if not callable(None):
        raise TypeError("dataset builder must be callable")
    register(name)(fn)


def x_register_dataset__mutmut_3(name: str, fn: Callable[..., Any]) -> None:
    """Register ``fn`` explicitly without using the decorator helper."""

    if not callable(fn):
        raise TypeError(None)
    register(name)(fn)


def x_register_dataset__mutmut_4(name: str, fn: Callable[..., Any]) -> None:
    """Register ``fn`` explicitly without using the decorator helper."""

    if not callable(fn):
        raise TypeError("XXdataset builder must be callableXX")
    register(name)(fn)


def x_register_dataset__mutmut_5(name: str, fn: Callable[..., Any]) -> None:
    """Register ``fn`` explicitly without using the decorator helper."""

    if not callable(fn):
        raise TypeError("DATASET BUILDER MUST BE CALLABLE")
    register(name)(fn)


def x_register_dataset__mutmut_6(name: str, fn: Callable[..., Any]) -> None:
    """Register ``fn`` explicitly without using the decorator helper."""

    if not callable(fn):
        raise TypeError("dataset builder must be callable")
    register(name)(None)


def x_register_dataset__mutmut_7(name: str, fn: Callable[..., Any]) -> None:
    """Register ``fn`` explicitly without using the decorator helper."""

    if not callable(fn):
        raise TypeError("dataset builder must be callable")
    register(None)(fn)

x_register_dataset__mutmut_mutants : ClassVar[MutantDict] = {
'x_register_dataset__mutmut_1': x_register_dataset__mutmut_1, 
    'x_register_dataset__mutmut_2': x_register_dataset__mutmut_2, 
    'x_register_dataset__mutmut_3': x_register_dataset__mutmut_3, 
    'x_register_dataset__mutmut_4': x_register_dataset__mutmut_4, 
    'x_register_dataset__mutmut_5': x_register_dataset__mutmut_5, 
    'x_register_dataset__mutmut_6': x_register_dataset__mutmut_6, 
    'x_register_dataset__mutmut_7': x_register_dataset__mutmut_7
}

def register_dataset(*args, **kwargs):
    result = _mutmut_trampoline(x_register_dataset__mutmut_orig, x_register_dataset__mutmut_mutants, args, kwargs)
    return result 

register_dataset.__signature__ = _mutmut_signature(x_register_dataset__mutmut_orig)
x_register_dataset__mutmut_orig.__name__ = 'x_register_dataset'


def x_get__mutmut_orig(name: str) -> Callable[..., Any]:
    """Return the dataset builder registered under ``name``."""

    normalized = name.strip().lower()
    try:
        return _REGISTRY[normalized]
    except KeyError as exc:  # pragma: no cover - small helper
        raise DatasetRegistryError(
            f"Unknown dataset '{name}'. Available: {sorted(_REGISTRY)}"
        ) from exc


def x_get__mutmut_1(name: str) -> Callable[..., Any]:
    """Return the dataset builder registered under ``name``."""

    normalized = None
    try:
        return _REGISTRY[normalized]
    except KeyError as exc:  # pragma: no cover - small helper
        raise DatasetRegistryError(
            f"Unknown dataset '{name}'. Available: {sorted(_REGISTRY)}"
        ) from exc


def x_get__mutmut_2(name: str) -> Callable[..., Any]:
    """Return the dataset builder registered under ``name``."""

    normalized = name.strip().upper()
    try:
        return _REGISTRY[normalized]
    except KeyError as exc:  # pragma: no cover - small helper
        raise DatasetRegistryError(
            f"Unknown dataset '{name}'. Available: {sorted(_REGISTRY)}"
        ) from exc


def x_get__mutmut_3(name: str) -> Callable[..., Any]:
    """Return the dataset builder registered under ``name``."""

    normalized = name.strip().lower()
    try:
        return _REGISTRY[normalized]
    except KeyError as exc:  # pragma: no cover - small helper
        raise DatasetRegistryError(
            None
        ) from exc


def x_get__mutmut_4(name: str) -> Callable[..., Any]:
    """Return the dataset builder registered under ``name``."""

    normalized = name.strip().lower()
    try:
        return _REGISTRY[normalized]
    except KeyError as exc:  # pragma: no cover - small helper
        raise DatasetRegistryError(
            f"Unknown dataset '{name}'. Available: {sorted(None)}"
        ) from exc

x_get__mutmut_mutants : ClassVar[MutantDict] = {
'x_get__mutmut_1': x_get__mutmut_1, 
    'x_get__mutmut_2': x_get__mutmut_2, 
    'x_get__mutmut_3': x_get__mutmut_3, 
    'x_get__mutmut_4': x_get__mutmut_4
}

def get(*args, **kwargs):
    result = _mutmut_trampoline(x_get__mutmut_orig, x_get__mutmut_mutants, args, kwargs)
    return result 

get.__signature__ = _mutmut_signature(x_get__mutmut_orig)
x_get__mutmut_orig.__name__ = 'x_get'


def x_list_datasets__mutmut_orig() -> list[str]:
    """Return the list of registered dataset names."""

    return sorted(_REGISTRY)


def x_list_datasets__mutmut_1() -> list[str]:
    """Return the list of registered dataset names."""

    return sorted(None)

x_list_datasets__mutmut_mutants : ClassVar[MutantDict] = {
'x_list_datasets__mutmut_1': x_list_datasets__mutmut_1
}

def list_datasets(*args, **kwargs):
    result = _mutmut_trampoline(x_list_datasets__mutmut_orig, x_list_datasets__mutmut_mutants, args, kwargs)
    return result 

list_datasets.__signature__ = _mutmut_signature(x_list_datasets__mutmut_orig)
x_list_datasets__mutmut_orig.__name__ = 'x_list_datasets'


def x_build__mutmut_orig(name: str, *args: Any, **kwargs: Any) -> Any:
    """Convenience helper returning ``get(name)(*args, **kwargs)``."""

    builder = get(name)
    return builder(*args, **kwargs)


def x_build__mutmut_1(name: str, *args: Any, **kwargs: Any) -> Any:
    """Convenience helper returning ``get(name)(*args, **kwargs)``."""

    builder = None
    return builder(*args, **kwargs)


def x_build__mutmut_2(name: str, *args: Any, **kwargs: Any) -> Any:
    """Convenience helper returning ``get(name)(*args, **kwargs)``."""

    builder = get(None)
    return builder(*args, **kwargs)


def x_build__mutmut_3(name: str, *args: Any, **kwargs: Any) -> Any:
    """Convenience helper returning ``get(name)(*args, **kwargs)``."""

    builder = get(name)
    return builder(**kwargs)


def x_build__mutmut_4(name: str, *args: Any, **kwargs: Any) -> Any:
    """Convenience helper returning ``get(name)(*args, **kwargs)``."""

    builder = get(name)
    return builder(*args, )

x_build__mutmut_mutants : ClassVar[MutantDict] = {
'x_build__mutmut_1': x_build__mutmut_1, 
    'x_build__mutmut_2': x_build__mutmut_2, 
    'x_build__mutmut_3': x_build__mutmut_3, 
    'x_build__mutmut_4': x_build__mutmut_4
}

def build(*args, **kwargs):
    result = _mutmut_trampoline(x_build__mutmut_orig, x_build__mutmut_mutants, args, kwargs)
    return result 

build.__signature__ = _mutmut_signature(x_build__mutmut_orig)
x_build__mutmut_orig.__name__ = 'x_build'


@register("synthetic_classification")
def _synthetic_classification_dataset(
    *,
    num_samples: int = 32,
    input_dim: int = 8,
    num_classes: int = 2,
    batch_size: int = 8,
    seed: int = 0,
    val_split: float = 0.25,
) -> tuple[Any, Any | None]:
    """Return simple synthetic classification dataloaders for smoke tests."""

    global torch, DataLoader, TensorDataset, random_split
    if torch is None or DataLoader is None or TensorDataset is None:
        try:
            torch = importlib.import_module("torch")  # type: ignore[assignment]
        except Exception as exc:  # pragma: no cover - optional dependency guard
            raise DatasetRegistryError("torch is required for synthetic datasets") from exc
        torch_utils = getattr(torch, "utils", None)
        data_module = getattr(torch_utils, "data", None)
        if data_module is None:
            raise DatasetRegistryError("torch.utils.data not available")
        DataLoader = getattr(data_module, "DataLoader", None)
        TensorDataset = getattr(data_module, "TensorDataset", None)
        random_split = getattr(data_module, "random_split", None)
    if DataLoader is None or TensorDataset is None:
        raise DatasetRegistryError("torch.utils.data components unavailable")
    generator = torch.Generator().manual_seed(int(seed))
    features = torch.randn(num_samples, input_dim, generator=generator)
    labels = torch.randint(num_classes, (num_samples,), generator=generator)
    dataset = TensorDataset(features, labels)
    if val_split <= 0 or random_split is None:
        train_dataset = dataset
        val_dataset = None
    else:
        val_size = max(1, int(len(dataset) * float(val_split)))
        val_size = min(val_size, len(dataset) - 1) if len(dataset) > 1 else val_size
        if val_size <= 0:
            train_dataset = dataset
            val_dataset = None
        else:
            train_size = len(dataset) - val_size
            if train_size <= 0:
                train_size = len(dataset) - 1
                val_size = len(dataset) - train_size
            train_dataset, val_dataset = random_split(
                dataset,
                [train_size, val_size],
                generator=torch.Generator().manual_seed(int(seed) + 1),
            )
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = (
        DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        if val_dataset is not None
        else None
    )
    return train_loader, val_loader


__all__ = [
    "DatasetRegistryError",
    "build",
    "get",
    "list_datasets",
    "register",
    "register_dataset",
]
