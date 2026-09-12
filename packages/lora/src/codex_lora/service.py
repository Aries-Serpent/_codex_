"""Use-case functions over the backend-neutral LoRA boundary."""

from __future__ import annotations

from .adapters import PeftBackend
from .contracts import LoraBackend, LoraConfig


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
    path: str,
    *,
    backend: LoraBackend | None = None,
    adapter_name: str | None = None,
) -> object:
    """Load a LoRA adapter using an explicit or lazily created PEFT backend."""

    if not path.strip():
        raise ValueError("path must not be empty")
    selected = backend or PeftBackend()
    return selected.load(model, path, adapter_name=adapter_name)


__all__ = ["apply_lora", "load_lora"]
