"""
Adapter Loader Module

This module provides functionality for adapter loader.

Usage:
    from server.adapter_loader import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import asyncio
import importlib
import importlib.util
import logging
import os
from typing import Optional

from mcp.server.adapters.mock_adapter import MockAdapter

logger = logging.getLogger(__name__)

DEFAULT_ADAPTER = "src.mcp.server.adapters.mock_adapter.MockAdapter"
FALLBACK_ADAPTERS = [
    DEFAULT_ADAPTER,
    "src.mcp.backends.mock_backend.InMemoryMockBackend",
]


def _import_class(path: str):
    module_name, class_name = path.rsplit(".", 1)
    if importlib.util.find_spec(module_name) is None:
        return None
    mod = importlib.import_module(module_name)
    return getattr(mod, class_name, None)


def load_adapter(adapter_path: Optional[str] = None) -> tuple[object, str]:
    """
    Load adapter based on ADAPTER_CLASS environment variable or explicit param.
    Returns (adapter_instance, adapter_class_path).
    This function is import-safe and does not connect.
    """
    cls_path = adapter_path or os.environ.get("ADAPTER_CLASS", DEFAULT_ADAPTER)
    cls = _import_class(cls_path)
    if cls is None:
        for fallback in FALLBACK_ADAPTERS:
            cls_path = fallback
            cls = _import_class(cls_path)
            if cls is not None:
                break
    if cls is None:
        return MockAdapter(), DEFAULT_ADAPTER
    return cls(), cls_path


async def lazy_connect_all(timeout: float = 1.0) -> bool:
    """
    Attempt to connect to the configured adapter with a timeout.
    Returns True if connect succeeds, False otherwise.
    """
    adapter, _ = load_adapter()
    connect_fn = getattr(adapter, "connect", None)
    if connect_fn is None:
        return True

    async def _connect():
        await asyncio.to_thread(connect_fn)

    try:
        await asyncio.wait_for(_connect(), timeout=timeout)
        return True
    except (IOError, OSError):
        logger.warning("Exception occurred", exc_info=True)
        return False
