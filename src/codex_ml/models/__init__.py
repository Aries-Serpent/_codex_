"""Model implementations for Codex ML.

This module exposes a tiny registry to resolve lightweight models without
pulling in heavy optional dependencies at import time.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Dict, Optional, Type

MODEL_REGISTRY: Dict[str, Type[object]] = {}


def register_model(name: str) -> Callable[[Type[object]], Type[object]]:
    def decorator(cls: Type[object]) -> Type[object]:
        MODEL_REGISTRY[name] = cls
        return cls

    return decorator


def get_model(name: str) -> Optional[Type[object]]:
    return MODEL_REGISTRY.get(name)


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

__all__ = [
    "MiniLM",
    "MiniLMConfig",
    "DecoderOnlyLM",
    "ModelConfig",
    "register_model",
    "get_model",
]
