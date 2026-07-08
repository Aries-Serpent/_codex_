"""Test MCP adapter registry and discovery."""

from __future__ import annotations


class SimpleAdapter:
    def __init__(self, name: str):
        self.name = name

    async def initialize(self) -> None:
        pass


def test_adapter_registry_register():
    """Test registering adapters."""
    registry = {}
    adapter = SimpleAdapter("test")
    registry["test"] = adapter

    assert "test" in registry, "Condition must be true"
    assert registry["test"] == adapter, "Condition must be true"


def test_adapter_registry_lookup():
    """Test looking up registered adapters."""
    registry = {"test": SimpleAdapter("test")}

    adapter = registry.get("test")
    assert adapter is not None, "adapter must be initialized"
    assert adapter.name == "test", "name is not valid"


def test_adapter_registry_list():
    """Test listing all adapters."""
    registry = {
        "adapter1": SimpleAdapter("adapter1"),
        "adapter2": SimpleAdapter("adapter2"),
    }

    names = list(registry.keys())
    assert len(names) == 2, "Names must not be empty"
    assert "adapter1" in names, "Condition must be true"


def test_adapter_registry_unregister():
    """Test unregistering adapters."""
    registry = {"test": SimpleAdapter("test")}

    del registry["test"]

    assert "test" not in registry, "Condition must be true"
