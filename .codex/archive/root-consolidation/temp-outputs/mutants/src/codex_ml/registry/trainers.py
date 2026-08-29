"""
Trainers Module

This module provides functionality for trainers.

Usage:
    from registry.trainers import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


import inspect  # noqa: E402
from collections.abc import Callable  # noqa: E402
from typing import Any  # noqa: E402

from codex_ml.registry.base import Registry  # noqa: E402

trainer_registry = Registry("trainer", entry_point_group="codex_ml.trainers")


@trainer_registry.register("functional")
def _load_functional_trainer() -> Callable[..., Any]:
    from codex_ml.training.functional_training import train

    return train


def register_trainer(name: str, obj: Callable[..., Any] | None = None, *, override: bool = False):
    return trainer_registry.register(name, obj, override=override)


def get_trainer(name: str) -> Callable[..., Any]:
    trainer = trainer_registry.get(name)
    if callable(trainer):
        try:
            signature = inspect.signature(trainer)
        except (TypeError, ValueError):
            logger.debug("Exception caught, returning", exc_info=True)
            return trainer
        if len(signature.parameters) == 0:
            resolved = trainer()
            if not callable(resolved):
                raise TypeError(
                    f"Trainer loader for '{name}' did not return a callable: {resolved!r}"
                )
            return resolved
    return trainer


def list_trainers() -> list[str]:
    return trainer_registry.list()


# Public API wrapper for entry point
def load_functional_trainer() -> Callable[..., Any]:
    """Public API wrapper for functional trainer loader.

    This is the stable public entry point for loading the functional trainer.

    Returns:
        Callable that implements the functional trainer interface.
    """
    return _load_functional_trainer()


__all__ = [
    "get_trainer",
    "list_trainers",
    "load_functional_trainer",
    "register_trainer",
    "trainer_registry",
]
