"""Trainer registry built on the shared registry infrastructure."""

from __future__ import annotations

import inspect
from typing import Any, Callable

from codex_ml.registry.base import Registry

trainer_registry = Registry("trainer", entry_point_group="codex_ml.trainers")


@trainer_registry.register("functional")
def _load_functional_trainer() -> Callable[..., Any]:
    from training.functional_training import run_custom_trainer

    return run_custom_trainer


def register_trainer(name: str, obj: Callable[..., Any] | None = None, *, override: bool = False):
    return trainer_registry.register(name, obj, override=override)


def get_trainer(name: str) -> Callable[..., Any]:
    trainer = trainer_registry.get(name)
    if callable(trainer):
        try:
            signature = inspect.signature(trainer)
        except (TypeError, ValueError):
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


__all__ = ["trainer_registry", "register_trainer", "get_trainer", "list_trainers"]
