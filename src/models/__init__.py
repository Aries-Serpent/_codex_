"""Shims for model utilities."""

from .chat_model import ChatModel, ChatModelConfig
from .peft_utils import summarize_peft

__all__ = ["ChatModel", "ChatModelConfig", "summarize_peft"]
