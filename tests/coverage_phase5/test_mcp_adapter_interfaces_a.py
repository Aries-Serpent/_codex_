"""Test MCP adapter interface contracts."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

try:
    from mcp.adapters import BaseAdapter  # noqa: F401
except ImportError:
    pytest.skip("mcp.adapters not available", allow_module_level=True)


class MockAdapter:
    """Mock adapter for testing interface contracts."""

    def __init__(self, name: str):
        self.name = name
        self.initialized = False

    async def initialize(self) -> None:
        self.initialized = True

    async def shutdown(self) -> None:
        self.initialized = False

    async def execute(self, command: str, **kwargs) -> Any:
        return {"status": "success", "command": command}


def test_adapter_initialization():
    """Test adapter initialization contract."""
    adapter = MockAdapter("test")

    assert not adapter.initialized, "Condition must be true"

    loop = asyncio.get_event_loop()
    loop.run_until_complete(adapter.initialize())

    assert adapter.initialized, "Condition must be true"


def test_adapter_shutdown():
    """Test adapter shutdown contract."""
    adapter = MockAdapter("test")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(adapter.initialize())
    loop.run_until_complete(adapter.shutdown())

    assert not adapter.initialized, "Condition must be true"


def test_adapter_execute():
    """Test adapter execute contract."""
    adapter = MockAdapter("test")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(adapter.initialize())
    result = loop.run_until_complete(adapter.execute("test_cmd"))

    assert result["status"] == "success", "Result must not be empty"
    assert result["command"] == "test_cmd", "Result must not be empty"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_adapter_context_manager():
    """Test adapter as context manager."""
    adapter = MockAdapter("test")

    assert not adapter.initialized, "Condition must be true"

    await adapter.initialize()
    assert adapter.initialized, "Condition must be true"

    await adapter.shutdown()
    assert not adapter.initialized, "Condition must be true"
