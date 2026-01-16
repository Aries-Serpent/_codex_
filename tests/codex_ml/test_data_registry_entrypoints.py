"""
Test Data Registry Entrypoints

Test module for data registry entrypoints.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib import metadata
from uuid import uuid4

import pytest

from codex_ml.data import registry


@dataclass
class _DummyEntryPoint:
    name: str
    value: object

    def load(self) -> object:  # pragma: no cover - simple passthrough
        return self.value


def test_entry_points_loaded_from_multiple_groups(monkeypatch):
    dataset_name = f"alias-{uuid4().hex}"
    calls: list[str] = []

    def fake_entry_points(group: str):
        calls.append(group)
        if group == registry._DatasetRegistry._ENTRY_POINT_GROUPS[1]:
            return (_DummyEntryPoint(dataset_name, lambda: "ok"),)
        return ()

    reg = registry._DatasetRegistry()
    monkeypatch.setattr(metadata, "entry_points", fake_entry_points)

    reg._ensure_entry_points_loaded()

    assert dataset_name in reg.list()
    assert reg.get(dataset_name)() == "ok"
    assert set(calls) >= set(registry._DatasetRegistry._ENTRY_POINT_GROUPS)


def test_available_datasets_includes_registered_loader():
    dataset_name = f"ephemeral-{uuid4().hex}"

    @registry.register_dataset(dataset_name)
    def _loader():
        return {"name": dataset_name}

    available = registry.available_datasets()
    assert dataset_name in available
    assert available[dataset_name]() == {"name": dataset_name}
