"""MCP Adapters for connecting to external services."""

from __future__ import annotations

from .base_adapter import BaseAdapter
from .mock_backend import MockBackend
from .pinecone_adapter import PineconeAdapter

__all__ = ["BaseAdapter", "MockBackend", "PineconeAdapter"]
