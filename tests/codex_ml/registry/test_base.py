"""
Test Base

Test module for base.
"""

import pytest

from codex_ml.registry.base import (
    Registry,
    RegistryConflictError,
    RegistryNotFoundError,
)


def test_register_and_lookup_roundtrip():
    registry = Registry("component")

    @registry.register("Example")
    class Example:
        pass

    assert registry.get("example") is Example, "Condition must be true"
    assert registry.list() == ["example"], "Condition must be true"


def test_register_conflict_raises():
    registry = Registry("component")

    registry.register("item", object)
    with pytest.raises(RegistryConflictError):
        registry.register("ITEM", object)


def test_temporarily_registered_restores_state():
    registry = Registry("component")
    registry.register("persisted", 1)

    with registry.temporarily_registered({"persisted": 2, "temporary": 3}):
        assert registry.get("persisted") == 2, "Condition must be true"
        assert registry.get("temporary") == 3, "Condition must be true"

    assert registry.get("persisted") == 1, "Condition must be true"
    with pytest.raises(RegistryNotFoundError):
        registry.get("temporary")
