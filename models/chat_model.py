"""
Legacy compatibility layer for chat_model module.

DEPRECATED: Use src.models.chat_model instead.
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "Importing from 'models.chat_model' is deprecated. Use 'src.models.chat_model' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from src.models.chat_model import ChatModel, ChatModelConfig  # noqa: E402

__all__ = ["ChatModel", "ChatModelConfig"]
