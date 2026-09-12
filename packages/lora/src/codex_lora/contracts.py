"""Stable contracts for applying and loading LoRA adapters."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Protocol, runtime_checkable

MAX_ARTIFACT_METADATA_ENTRIES = 32
MAX_ARTIFACT_METADATA_KEY_LENGTH = 64
MAX_ARTIFACT_METADATA_VALUE_LENGTH = 256


@dataclass(frozen=True, slots=True)
class LoraArtifactMetadata:
    """Small, portable metadata recorded alongside a saved adapter.

    The limits deliberately keep artifact manifests suitable for source-control
    and prevent arbitrary caller metadata from turning adapter saves into an
    unbounded data channel.
    """

    adapter_name: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        name = self.adapter_name
        if name is not None:
            if not isinstance(name, str) or not (normalized := name.strip()):
                raise ValueError("adapter_name must be a non-empty string when provided")
            if len(normalized) > MAX_ARTIFACT_METADATA_VALUE_LENGTH:
                raise ValueError("adapter_name exceeds the metadata value limit")
            object.__setattr__(self, "adapter_name", normalized)

        values = dict(self.metadata)
        if len(values) > MAX_ARTIFACT_METADATA_ENTRIES:
            raise ValueError(
                f"metadata may contain at most {MAX_ARTIFACT_METADATA_ENTRIES} entries"
            )
        for key, value in values.items():
            if not isinstance(key, str) or not key or len(key) > MAX_ARTIFACT_METADATA_KEY_LENGTH:
                raise ValueError("metadata keys must be non-empty strings within the size limit")
            if not isinstance(value, str) or len(value) > MAX_ARTIFACT_METADATA_VALUE_LENGTH:
                raise ValueError("metadata values must be strings within the size limit")
        object.__setattr__(self, "metadata", MappingProxyType(values))

    def as_dict(self) -> dict[str, object]:
        """Return the stable JSON representation used in adapter artifacts."""

        return {
            "format_version": 1,
            "adapter_name": self.adapter_name,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, values: Mapping[str, object]) -> "LoraArtifactMetadata":
        """Validate and restore metadata loaded from an adapter artifact."""

        if values.get("format_version") != 1:
            raise ValueError("unsupported LoRA artifact metadata format")
        adapter_name = values.get("adapter_name")
        metadata = values.get("metadata", {})
        if adapter_name is not None and not isinstance(adapter_name, str):
            raise ValueError("artifact adapter_name must be a string or null")
        if not isinstance(metadata, Mapping):
            raise ValueError("artifact metadata must be an object")
        return cls(adapter_name=adapter_name, metadata=metadata)


@dataclass(frozen=True, slots=True)
class LoraArtifact:
    """Location and bounded metadata for a persisted LoRA adapter."""

    path: str
    metadata: LoraArtifactMetadata = field(default_factory=LoraArtifactMetadata)

    def __post_init__(self) -> None:
        if not isinstance(self.path, str) or not (normalized := self.path.strip()):
            raise ValueError("artifact path must be a non-empty string")
        object.__setattr__(self, "path", normalized)


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


@runtime_checkable
class LoraLifecycleBackend(Protocol):
    """Optional backend operations for a named adapter's lifecycle."""

    def save(self, model: object, path: str, *, adapter_name: str | None = None) -> object:
        """Persist an adapter."""

    def activate(self, model: object, adapter_name: str) -> object:
        """Make a named adapter active."""

    def disable(self, model: object) -> object:
        """Disable active adapter layers without deleting them."""

    def delete(self, model: object, adapter_name: str) -> object:
        """Remove a named adapter."""


@runtime_checkable
class LoraTrainingBackend(Protocol):
    """Optional backend hook for preparing a model for LoRA training."""

    def prepare_for_training(
        self,
        model: object,
        *,
        gradient_checkpointing: bool = False,
        gradient_checkpointing_kwargs: Mapping[str, object] | None = None,
    ) -> object:
        """Prepare a quantized model before a LoRA training run."""


__all__ = [
    "LoraArtifact",
    "LoraArtifactMetadata",
    "LoraBackend",
    "LoraConfig",
    "LoraLifecycleBackend",
    "LoraTrainingBackend",
    "MAX_ARTIFACT_METADATA_ENTRIES",
    "MAX_ARTIFACT_METADATA_KEY_LENGTH",
    "MAX_ARTIFACT_METADATA_VALUE_LENGTH",
]
