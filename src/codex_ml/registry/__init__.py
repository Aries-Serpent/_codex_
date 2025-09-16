"""Registry facade exposing component registries and helper APIs."""

from __future__ import annotations

from .base import (
    Registry,
    RegistryConflictError,
    RegistryError,
    RegistryLoadError,
    RegistryNotFoundError,
)
from .data_loaders import (
    data_loader_registry,
    get_data_loader,
    list_data_loaders,
    register_data_loader,
)
from .metrics import get_metric, list_metrics, metric_registry, register_metric
from .models import get_model, list_models, model_registry, register_model
from .tokenizers import (
    get_tokenizer,
    list_tokenizers,
    register_tokenizer,
    tokenizer_registry,
)
from .trainers import get_trainer, list_trainers, register_trainer, trainer_registry

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
