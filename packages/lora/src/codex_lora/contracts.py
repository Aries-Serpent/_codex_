"""Stable contracts for applying and loading LoRA adapters."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class LoraConfig:
    """Backend-neutral LoRA configuration."""

    rank: int = 8
    alpha: int = 16
    dropout: float = 0.05
    bias: str = "none"
    task_type: str = "CAUSAL_LM"
    target_modules: Sequence[str] | None = None
    extra: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.rank <= 0:
            raise ValueError("rank must be positive")
        if self.alpha <= 0:
            raise ValueError("alpha must be positive")
        if not 0.0 <= self.dropout < 1.0:
            raise ValueError("dropout must be in the range [0, 1)")
        if not self.task_type.strip():
            raise ValueError("task_type must not be empty")
        targets = None if self.target_modules is None else tuple(self.target_modules)
        if targets is not None and (not targets or any(not item.strip() for item in targets)):
            raise ValueError("target_modules must contain non-empty names")
        reserved = {"r", "lora_alpha", "lora_dropout", "bias", "task_type", "target_modules"}
        overlap = reserved.intersection(self.extra)
        if overlap:
            names = ", ".join(sorted(overlap))
            raise ValueError(f"extra contains reserved keys: {names}")
        object.__setattr__(self, "target_modules", targets)
        object.__setattr__(self, "extra", MappingProxyType(dict(self.extra)))

    def as_backend_kwargs(self) -> dict[str, object]:
        """Return keyword arguments compatible with ``peft.LoraConfig``."""

        values: dict[str, object] = {
            "r": self.rank,
            "lora_alpha": self.alpha,
            "lora_dropout": self.dropout,
            "bias": self.bias,
            "task_type": self.task_type,
        }
        if self.target_modules is not None:
            values["target_modules"] = list(self.target_modules)
        values.update(self.extra)
        return values


@runtime_checkable
class LoraBackend(Protocol):
    """Structural adapter boundary for a concrete LoRA implementation."""

    def apply(
        self,
        model: object,
        config: LoraConfig,
        *,
        adapter_name: str | None = None,
    ) -> object:
        """Apply a trainable adapter and return the resulting model."""

    def load(self, model: object, path: str, *, adapter_name: str | None = None) -> object:
        """Load a persisted adapter for inference."""


__all__ = ["LoraBackend", "LoraConfig"]
