"""Adapters for connecting to external AI providers."""

from __future__ import annotations

from .base_adapter import BaseAdapter
from .mock_adapter import MockAdapter

# OpenAIAdapter not yet implemented
__all__ = ["BaseAdapter", "MockAdapter"]
