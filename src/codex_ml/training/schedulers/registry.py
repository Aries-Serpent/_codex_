from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Any

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    # Create placeholder types
    class _DummyOptimizer:
        pass
    class _DummyScheduler:
        pass
    torch = type('torch', (), {
        'optim': type('optim', (), {'Optimizer': _DummyOptimizer})(),
        'optim.lr_scheduler': type('lr_scheduler', (), {'_LRScheduler': _DummyScheduler})()
    })()


@dataclass
class SchedulerSpec:
    """Specification for a scheduler factory."""
    factory: Callable[..., Any]
    description: str


class SchedulerRegistry:
    """Lightweight LR scheduler registry with a few safe built-ins."""

    def __init__(self) -> None:
        self._specs: Dict[str, SchedulerSpec] = {}
        if TORCH_AVAILABLE:
            self._register_builtins()

    def _register_builtins(self) -> None:
        if not TORCH_AVAILABLE:
            return
        from torch.optim.lr_scheduler import StepLR, CosineAnnealingLR

        self.register(
            "step_lr",
            lambda optimizer, step_size=10, gamma=0.1: StepLR(optimizer, step_size=int(step_size), gamma=float(gamma)),
            "StepLR(optimizer, step_size=10, gamma=0.1)",
        )
        self.register(
            "cosine_annealing",
            lambda optimizer, T_max=50, eta_min=0.0: CosineAnnealingLR(optimizer, T_max=int(T_max), eta_min=float(eta_min)),
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
