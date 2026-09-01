"""
Registry Module

This module provides functionality for registry.

Usage:
    from schedulers.registry import ...

Classes:
Functions:
Author: Codex Team
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from types import ModuleType
from typing import Any, cast

logger = logging.getLogger(__name__)

try:
    import torch

    # Verify torch is functional
    _ = torch.Tensor
    TORCH_AVAILABLE = True
except (ImportError, AttributeError) as e:
    error_type = type(e).__name__
    logger.debug("Failed to import or verify torch: <ERROR_TYPE>")
    logger.warning("Failed to import or verify torch: <ERROR_TYPE>", exc_info=True)
    TORCH_AVAILABLE = False

    # Create placeholder types so consumer code can import the registry
    # without torch installed. These stubs intentionally expose only the
    # attributes accessed by this module.
    class _DummyOptimizer:
        pass

    class _DummyScheduler:
        pass

    torch = cast(Any, ModuleType("torch"))
    torch.optim = ModuleType("optim")
    torch.optim.Optimizer = _DummyOptimizer
    torch.optim.lr_scheduler = ModuleType("lr_scheduler")
    torch.optim.lr_scheduler._LRScheduler = _DummyScheduler


@dataclass
class SchedulerSpec:
    """Specification for a scheduler factory."""

    factory: Callable[..., Any]
    description: str


class SchedulerRegistry:
    """Lightweight LR scheduler registry with a few safe built-ins."""

    def __init__(self) -> None:
        self._specs: dict[str, SchedulerSpec] = {}
        if TORCH_AVAILABLE:
            self._register_builtins()

    def _register_builtins(self) -> None:
        if not TORCH_AVAILABLE:
            return
        from torch.optim.lr_scheduler import CosineAnnealingLR, StepLR

        self.register(
            "step_lr",
            lambda optimizer, step_size=10, gamma=0.1: StepLR(
                optimizer, step_size=int(step_size), gamma=float(gamma)
            ),
            "StepLR(optimizer, step_size=10, gamma=0.1)",
        )
        self.register(
            "cosine_annealing",
            lambda optimizer, T_max=50, eta_min=0.0: CosineAnnealingLR(
                optimizer, T_max=int(T_max), eta_min=float(eta_min)
            ),
            "CosineAnnealingLR(optimizer, T_max=50, eta_min=0.0)",
        )

    def register(self, name: str, factory: Callable[..., Any], description: str = "") -> None:
        if not name or not isinstance(name, str):
            raise ValueError("Scheduler name must be a non-empty string.")
        self._specs[name] = SchedulerSpec(factory=factory, description=description)

    def list(self) -> list[str]:
        return sorted(self._specs.keys())

    def build(self, name: str, optimizer: Any, **kwargs: Any) -> Any:
        if name not in self._specs:
            raise KeyError(f"Unknown scheduler '{name}'. Available: {self.list()}")
        return self._specs[name].factory(optimizer=optimizer, **kwargs)

    def describe(self, name: str) -> str:
        if name not in self._specs:
            raise KeyError(f"Unknown scheduler '{name}'. Available: {self.list()}")
        return self._specs[name].description


# Global instance
_global_registry = SchedulerRegistry()


def get_scheduler_registry() -> SchedulerRegistry:
    return _global_registry
