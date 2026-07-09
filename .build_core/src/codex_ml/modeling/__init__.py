"""
  Init   Module

This module provides functionality for   init  .

Usage:
    from modeling.__init__ import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Optional

from .codex_model import CodexModel, LoraOptions
from .factory import ENV_ENABLE_PEFT, ModelFactoryConfig, PeftAdapterConfig, build_model


@dataclass
class LoraSettings:
    """Lightweight settings container for test-time LoRA toggles."""

    adapter_path: str
    rank: int = 8
    alpha: float = 16.0


def _apply_lora(model: Any, settings: LoraSettings) -> Any:
    model._lora_applied = True
    model._lora_settings = settings
    return model


def _load_base_model(name_or_path: str, *, dtype: str, device: str) -> Any:
    class _DummyModel:
        def __init__(self, name: str, dtype: str, device: str) -> None:
            self.name = name
            self.dtype = dtype
            self.device = device

    return _DummyModel(name_or_path, dtype, device)


def load_model_and_tokenizer(
    model_name_or_path: str,
    _tokenizer_name_or_path: Optional[str] = None,
    *,
    lora_settings: Optional[LoraSettings] = None,
    enable_lora: bool = False,
    lora_rank: Optional[int] = None,
    dtype: str = "float32",
    device: str = "cpu",
) -> tuple[Any, Optional[Any]]:
    """Load a minimal model/tokenizer pair with optional LoRA toggles."""

    model = _load_base_model(model_name_or_path, dtype=dtype, device=device)

    if enable_lora and lora_settings is not None:
        rank = lora_rank if lora_rank is not None else lora_settings.rank
        if int(rank) <= 0:
            raise ValueError("lora_rank must be a positive integer")
        applied = replace(lora_settings, rank=int(rank))
        model = _apply_lora(model, applied)

    tokenizer = None
    return model, tokenizer


__all__ = [
    "ENV_ENABLE_PEFT",
    "CodexModel",
    "LoraOptions",
    "LoraSettings",
    "ModelFactoryConfig",
    "PeftAdapterConfig",
    "build_model",
    "load_model_and_tokenizer",
]
