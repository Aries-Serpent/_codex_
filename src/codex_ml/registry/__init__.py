"""Registry facade exposing component registries and helper APIs.

This module intentionally performs *lazy* imports for component-specific
registries to avoid circular import issues.  ``codex_ml.models.registry`` depends
on :mod:`codex_ml.registry.base`, so eagerly importing the model facade from this
module previously caused an ``ImportError`` when both modules initialised at the
same time.  The helper :func:`__getattr__` resolves the concrete registry object
on first access and caches it in ``globals()`` so subsequent lookups are fast.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

from .base import (
    Registry,
    RegistryConflictError,
    RegistryError,
    RegistryLoadError,
    RegistryNotFoundError,
)

__all__ = [
    "Registry",
    "RegistryError",
    "RegistryConflictError",
    "RegistryLoadError",
    "RegistryNotFoundError",
    "tokenizer_registry",
    "register_tokenizer",
    "get_tokenizer",
    "list_tokenizers",
    "model_registry",
    "register_model",
    "get_model",
    "list_models",
    "metric_registry",
    "register_metric",
    "get_metric",
    "list_metrics",
    "data_loader_registry",
    "register_data_loader",
    "get_data_loader",
    "list_data_loaders",
    "trainer_registry",
    "register_trainer",
    "get_trainer",
    "list_trainers",
]

_LAZY_ATTRS = {
    "tokenizer_registry": (".tokenizers", "tokenizer_registry"),
    "register_tokenizer": (".tokenizers", "register_tokenizer"),
    "get_tokenizer": (".tokenizers", "get_tokenizer"),
    "list_tokenizers": (".tokenizers", "list_tokenizers"),
    "model_registry": (".models", "model_registry"),
    "register_model": (".models", "register_model"),
    "get_model": (".models", "get_model"),
    "list_models": (".models", "list_models"),
    "metric_registry": (".metrics", "metric_registry"),
    "register_metric": (".metrics", "register_metric"),
    "get_metric": (".metrics", "get_metric"),
    "list_metrics": (".metrics", "list_metrics"),
    "data_loader_registry": (".data_loaders", "data_loader_registry"),
    "register_data_loader": (".data_loaders", "register_data_loader"),
    "get_data_loader": (".data_loaders", "get_data_loader"),
    "list_data_loaders": (".data_loaders", "list_data_loaders"),
    "trainer_registry": (".trainers", "trainer_registry"),
    "register_trainer": (".trainers", "register_trainer"),
    "get_trainer": (".trainers", "get_trainer"),
    "list_trainers": (".trainers", "list_trainers"),
}


def __getattr__(name: str) -> Any:
    """Lazily import facade attributes when accessed.

    Parameters
    ----------
    name:
        Attribute requested from the :mod:`codex_ml.registry` package.

    Returns
    -------
    Any
        The resolved object from the appropriate submodule.

    Raises
    ------
    AttributeError
        If the attribute is not part of the registry facade.
    """

    try:
        module_name, attr = _LAZY_ATTRS[name]
    except KeyError as exc:  # pragma: no cover - defensive
        raise AttributeError(f"module 'codex_ml.registry' has no attribute {name!r}") from exc
    module = import_module(module_name, package=__name__)
    value = getattr(module, attr)
    globals()[name] = value
    return value
