"""Use-case functions over the backend-neutral LoRA boundary."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

from .adapters import PeftBackend
from .contracts import (
    LoraArtifact,
    LoraArtifactMetadata,
    LoraBackend,
    LoraConfig,
    LoraLifecycleBackend,
    LoraTrainingBackend,
)

_METADATA_FILENAME = "adapter_metadata.json"


def _artifact_path(path: str | Path) -> str:
    """Normalize a user-supplied artifact path through the public contract."""

    return LoraArtifact(str(path)).path


def _named_adapter(adapter_name: str) -> str:
    if not isinstance(adapter_name, str) or not (normalized := adapter_name.strip()):
        raise ValueError("adapter_name must be a non-empty string")
    return normalized


def _lifecycle_backend(backend: object) -> LoraLifecycleBackend:
    if not isinstance(backend, LoraLifecycleBackend):
        raise TypeError("backend does not implement the LoRA adapter lifecycle")
    return backend


def _training_backend(backend: object) -> LoraTrainingBackend:
    if not isinstance(backend, LoraTrainingBackend):
        raise TypeError("backend does not implement LoRA training preparation")
    return backend


def _read_artifact(path: str | Path) -> LoraArtifact:
    artifact_path = _artifact_path(path)
    manifest = Path(artifact_path) / _METADATA_FILENAME
    if not manifest.exists():
        return LoraArtifact(artifact_path)
    try:
        raw = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid LoRA artifact metadata at {manifest}") from exc
    if not isinstance(raw, Mapping):
        raise ValueError(f"invalid LoRA artifact metadata at {manifest}")
    return LoraArtifact(artifact_path, LoraArtifactMetadata.from_dict(raw))


def read_lora_artifact(path: str | Path) -> LoraArtifact:
    """Read the optional, bounded manifest persisted with an adapter."""

    return _read_artifact(path)


def apply_lora(
    model: object,
    config: LoraConfig | None = None,
    *,
    backend: LoraBackend | None = None,
    adapter_name: str | None = None,
) -> object:
    """Apply a LoRA adapter using an explicit or lazily created PEFT backend."""

    selected = backend or PeftBackend()
    return selected.apply(model, config or LoraConfig(), adapter_name=adapter_name)


def load_lora(
    model: object,
    path: str | Path | LoraArtifact,
    *,
    backend: LoraBackend | None = None,
    adapter_name: str | None = None,
) -> object:
    """Load a LoRA adapter, restoring its recorded adapter name when available."""

    artifact = path if isinstance(path, LoraArtifact) else _read_artifact(path)
    selected_name = adapter_name or artifact.metadata.adapter_name
    selected = backend or PeftBackend()
    return selected.load(model, artifact.path, adapter_name=selected_name)


def save_lora(
    model: object,
    path: str | Path,
    *,
    backend: LoraLifecycleBackend | None = None,
    adapter_name: str | None = None,
    metadata: Mapping[str, str] | None = None,
) -> LoraArtifact:
    """Persist an adapter and its strictly bounded, dependency-free manifest."""

    artifact = LoraArtifact(
        _artifact_path(path),
        LoraArtifactMetadata(adapter_name=adapter_name, metadata=metadata or {}),
    )
    selected = _lifecycle_backend(backend or PeftBackend())
    selected.save(model, artifact.path, adapter_name=artifact.metadata.adapter_name)
    manifest = Path(artifact.path) / _METADATA_FILENAME
    try:
        manifest.write_text(
            json.dumps(artifact.metadata.as_dict(), sort_keys=True, separators=(",", ":")),
            encoding="utf-8",
        )
    except OSError as exc:
        raise OSError(f"unable to write LoRA artifact metadata at {manifest}") from exc
    return artifact


def activate_lora(
    model: object,
    adapter_name: str,
    *,
    backend: LoraLifecycleBackend | None = None,
) -> object:
    """Activate one named adapter on a model with multiple adapters."""

    selected = _lifecycle_backend(backend or PeftBackend())
    return selected.activate(model, _named_adapter(adapter_name))


def disable_lora(
    model: object,
    *,
    backend: LoraLifecycleBackend | None = None,
) -> object:
    """Disable LoRA layers without removing their loaded weights."""

    return _lifecycle_backend(backend or PeftBackend()).disable(model)


def delete_lora(
    model: object,
    adapter_name: str,
    *,
    backend: LoraLifecycleBackend | None = None,
) -> object:
    """Delete a named adapter from a model."""

    return _lifecycle_backend(backend or PeftBackend()).delete(model, _named_adapter(adapter_name))


def prepare_lora_training(
    model: object,
    *,
    backend: LoraTrainingBackend | None = None,
    gradient_checkpointing: bool = False,
    gradient_checkpointing_kwargs: Mapping[str, object] | None = None,
) -> object:
    """Run the backend's optional pre-training preparation hook."""

    if not isinstance(gradient_checkpointing, bool):
        raise TypeError("gradient_checkpointing must be a bool")
    if gradient_checkpointing_kwargs is not None and not isinstance(
        gradient_checkpointing_kwargs, Mapping
    ):
        raise TypeError("gradient_checkpointing_kwargs must be a mapping or None")
    safe_kwargs = (
        None if gradient_checkpointing_kwargs is None else dict(gradient_checkpointing_kwargs)
    )
    return _training_backend(backend or PeftBackend()).prepare_for_training(
        model,
        gradient_checkpointing=gradient_checkpointing,
        gradient_checkpointing_kwargs=safe_kwargs,
    )


__all__ = [
    "activate_lora",
    "apply_lora",
    "delete_lora",
    "disable_lora",
    "load_lora",
    "prepare_lora_training",
    "read_lora_artifact",
    "save_lora",
]
