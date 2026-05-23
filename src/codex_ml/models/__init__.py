"""
  Init   Module

This module provides functionality for   init  .

Usage:
    from models.__init__ import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import functools
import os
from typing import TYPE_CHECKING, Optional, Type

from codex_ml.plugins.registries import load_model_entry_points
from codex_ml.plugins.registries import models as _models_registry

__all__ = [
    "DecoderOnlyLM",
    "MiniLM",
    "MiniLMConfig",
    "ModelConfig",
    "ReasoningHarness",
    "ReasoningHead",
    "ToolUseAdapter",
    "attach_reasoning_adapters",
    "get_model",
    "register_model",
]


def register_model(name: str):
    """Register a model class under ``name``."""

    return _models_registry.register(name)


@functools.lru_cache(maxsize=1)
def _load_entry_points_once() -> None:
    if os.getenv("CODEX_PLUGINS_ENTRYPOINTS") == "1":
        load_model_entry_points(True)


def get_model(name: str) -> Optional[type[object]]:
    """Return a model class from the registry, loading entry points if enabled."""
    if os.getenv("CODEX_PLUGINS_ENTRYPOINTS") == "1":
        _load_entry_points_once()
    item = _models_registry.get(name)
    return item.obj if item else None


# Pre-register built-in models ---------------------------------------------
try:  # pragma: no cover - optional dependency
    from .minilm import MiniLM, MiniLMConfig

    register_model("minilm")(MiniLM)
except Exception:  # pragma: no cover - dependency not installed
    MiniLM = None  # type: ignore[assignment,misc]
    MiniLMConfig = None  # type: ignore[assignment,misc]

try:  # pragma: no cover - optional dependency
    from .decoder_only import DecoderOnlyLM, ModelConfig

    register_model("decoder_only")(DecoderOnlyLM)
except Exception:  # pragma: no cover - dependency not installed
    DecoderOnlyLM = None  # type: ignore[assignment,misc]
    ModelConfig = None  # type: ignore[assignment,misc]

try:  # pragma: no cover - optional dependency
    from .reasoning import (
        ReasoningHarness,
        ReasoningHead,
        ToolUseAdapter,
        attach_reasoning_adapters,
    )
except Exception:  # pragma: no cover - dependency not installed
    ReasoningHarness = None  # type: ignore[assignment,misc]
    ReasoningHead = None  # type: ignore[assignment,misc]
    ToolUseAdapter = None  # type: ignore[assignment,misc]
    attach_reasoning_adapters = None  # type: ignore[assignment]

if TYPE_CHECKING:  # retain type information for type checkers
    from .decoder_only import DecoderOnlyLM, ModelConfig
    from .minilm import MiniLM, MiniLMConfig
    from .reasoning import ReasoningHarness, ReasoningHead, ToolUseAdapter
