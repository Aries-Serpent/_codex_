"""Model registry for codex_ml using the plugin framework."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Optional, Type

from codex_ml.plugins.registries import (
    load_model_entry_points,
)
from codex_ml.plugins.registries import (
    models as _models_registry,
)

__all__ = [
    "MiniLM",
    "MiniLMConfig",
    "DecoderOnlyLM",
    "ModelConfig",
    "register_model",
    "get_model",
]


def register_model(name: str):
    """Register a model class under ``name``."""

    return _models_registry.register(name)


_EP_LOADED = False


def get_model(name: str) -> Optional[Type[object]]:
    """Return a model class from the registry, loading entry points if enabled."""

    global _EP_LOADED
    if not _EP_LOADED and os.getenv("CODEX_PLUGINS_ENTRYPOINTS") == "1":
        load_model_entry_points(True)
        _EP_LOADED = True
    item = _models_registry.get(name)
    return item.obj if item else None


# Pre-register built-in models ---------------------------------------------
try:  # pragma: no cover - optional dependency
    from .minilm import MiniLM, MiniLMConfig

    register_model("minilm")(MiniLM)
except Exception:  # pragma: no cover - dependency not installed
    MiniLM = None  # type: ignore[assignment]
    MiniLMConfig = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency
    from .decoder_only import DecoderOnlyLM, ModelConfig

    register_model("decoder_only")(DecoderOnlyLM)
except Exception:  # pragma: no cover - dependency not installed
    DecoderOnlyLM = None  # type: ignore[assignment]
    ModelConfig = None  # type: ignore[assignment]

if TYPE_CHECKING:  # retain type information for type checkers
    from .decoder_only import DecoderOnlyLM, ModelConfig
    from .minilm import MiniLM, MiniLMConfig
