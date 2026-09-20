"""
Legacy compatibility layer for models package.

DEPRECATED: Use src.models instead.
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "Importing from 'models' is deprecated. Use 'src.models' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from src.models.chat_model import ChatModel, ChatModelConfig
from src.models.peft_utils import summarize_peft

__all__ = ["ChatModel", "ChatModelConfig", "summarize_peft"]
