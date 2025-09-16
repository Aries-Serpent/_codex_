"""Data loader registry facade."""

from __future__ import annotations

from codex_ml.data.registry import data_loader_registry
from codex_ml.data.registry import get_dataset as get_data_loader
from codex_ml.data.registry import list_datasets as list_data_loaders
from codex_ml.data.registry import register_dataset as register_data_loader

__all__ = [
    "data_loader_registry",
    "register_data_loader",
    "get_data_loader",
    "list_data_loaders",
]
