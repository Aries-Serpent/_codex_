from __future__ import annotations

from common.registry import Registry


def test_registry_register_and_get() -> None:
    registry = Registry("example")

    @registry.register("foo")
    def foo() -> int:
        return 42

    assert registry.get("foo")() == 42
    assert "foo" in registry
