"""
Test Data Registry

Test module for data registry.
"""

from importlib import metadata

import pytest

from codex_ml.data.registry import _DatasetRegistry


def test_dataset_registry_register_and_get() -> None:
    registry = _DatasetRegistry()

    @registry.register("Demo")
    def loader(value: int) -> int:
        return value * 2

    assert registry.get("demo")(3) == 6, "Condition must be true"
    assert "demo" in registry.list(), "Condition must be true"


def test_dataset_registry_duplicate_registration_raises() -> None:
    registry = _DatasetRegistry()

    @registry.register("demo")
    def loader(value: int) -> int:  # pragma: no cover - behaviour tested via exception
        return value

    with pytest.raises(ValueError):
        registry.register("demo")(loader)


class _DummyEntryPoint:
    def __init__(self, name: str, target: object):
        self.name = name
        self._target = target

    def load(self) -> object:
        return self._target


def test_dataset_registry_entry_points(monkeypatch) -> None:
    registry = _DatasetRegistry()

    def loader(value: str) -> str:
        return value.upper()

    def fake_entry_points(*, group: str):
        if group in registry._ENTRY_POINT_GROUPS:  # type: ignore[attr-defined]
            return (_DummyEntryPoint("entry_loader", loader),)
        return (_DummyEntryPoint("__unused__", loader),)

    monkeypatch.setattr(metadata, "entry_points", fake_entry_points)

    resolved = registry.get("entry_loader")
    assert callable(resolved), "Condition must be true"
    assert resolved("ok") == "OK", "Condition must be true"
    assert "entry_loader" in registry.available(), "Condition must be true"

    # Subsequent calls reuse cached entry point state
    assert registry.list() == ["entry_loader"], "Condition must be true"
