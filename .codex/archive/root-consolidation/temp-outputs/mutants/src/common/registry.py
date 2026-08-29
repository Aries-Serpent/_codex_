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
from collections.abc import Callable, Iterable
from typing import Any

logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional import path when codex_ml unavailable
    from codex_ml.metrics.metric_implementations import (
        BLEUScore,
        F1Score,
        RecallScore,
        TokenAccuracy,
    )
except (
    ImportError,
    AttributeError,
):  # pragma: no cover - allow registry to exist without metrics module
    BLEUScore = F1Score = RecallScore = TokenAccuracy = None


class Registry:
    """Simple string-to-callable registry with decorator support."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._store: dict[str, Callable[..., Any]] = {}

    def register(
        self, key: str | None = None
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            registry_key = key or fn.__name__
            if registry_key in self._store:
                raise KeyError(f"{self.name}: key already registered: {registry_key}")
            self._store[registry_key] = fn
            return fn

        return decorator

    def add(self, key: str, fn: Callable[..., Any]) -> None:
        if key in self._store:
            raise KeyError(f"{self.name}: key already registered: {key}")
        self._store[key] = fn

    def get(self, key: str) -> Callable[..., Any]:
        if key not in self._store:
            raise KeyError(f"{self.name}: not found: {key}")
        return self._store[key]

    def keys(self) -> list[str]:
        return list(self._store.keys())

    def __contains__(self, key: str) -> bool:  # pragma: no cover - trivial
        return key in self._store

    def items(
        self,
    ) -> Iterable[tuple[str, Callable[..., Any]]]:  # pragma: no cover - convenience
        return self._store.items()


MODELS = Registry("models")
DATASETS = Registry("datasets")
METRICS = Registry("metrics")

if F1Score is not None:  # pragma: no branch - guard optional dependency
    METRICS.add("f1_score", F1Score)
    METRICS.add("recall_score", RecallScore)
    METRICS.add("token_accuracy", TokenAccuracy)
    METRICS.add("bleu_score", BLEUScore)
