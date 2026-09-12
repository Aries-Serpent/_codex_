"""Legacy LoRA/PEFT compatibility facade.

This facade is deprecated and is scheduled for removal in ``codex-ml 0.5.0``.
New code should import from ``codex_lora``. The existing ``apply_lora``
signature is retained for compatibility.
"""

from __future__ import annotations

from importlib import import_module

from codex_ml._compat import warn_deprecated_facade

from .peft_adapter import DEFAULT_CFG, apply_lora

warn_deprecated_facade("peft", "codex_ml.peft", "codex_lora", removal="0.5.0")

_STANDALONE_EXPORTS = {
    "CodexMlLoraAdapter",
    "LoraBackend",
    "LoraConfig",
    "OptionalDependencyError",
    "PeftBackend",
    "load_lora",
}


def __getattr__(name: str) -> object:
    """Resolve standalone LoRA names lazily, avoiding a reverse import cycle."""

    if name not in _STANDALONE_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    try:
        value = getattr(import_module("codex_lora"), name)
    except ImportError as exc:
        raise AttributeError(
            f"{name} requires the optional codex-ml-lora distribution"
        ) from exc
    globals()[name] = value
    return value

__all__ = [
    "CodexMlLoraAdapter",
    "DEFAULT_CFG",
    "LoraBackend",
    "LoraConfig",
    "OptionalDependencyError",
    "PeftBackend",
    "apply_lora",
    "load_lora",
]
