"""Smoke coverage for JSONL loader and dataset registry."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest


def test_load_jsonl_splits(tmp_path: Path) -> None:
    from codex_ml.data.jsonl_loader import load_jsonl

    path = tmp_path / "data.jsonl"
    path.write_text("\n".join(['{"text": "a"}', '{"text": "b"}']))

    train, val = load_jsonl(path, seed=0, val_fraction=0.5)
    assert train or val, "train is not valid"
    assert set(train + val) <= {"a", "b"}


class _EntryPoint:
    def __init__(self, name: str, value: Any) -> None:
        self.name = name
        self._value = value

    def load(self) -> Any:  # pragma: no cover - trivial
        return self._value


def test_dataset_registry_entrypoints(monkeypatch: pytest.MonkeyPatch) -> None:
    from codex_ml.data import registry

    # Reset singleton so monkeypatched entry_points are discovered
    monkeypatch.setattr(registry.data_loader_registry, "_entry_points_loaded", False)

    monkeypatch.setattr(
        registry.metadata,
        "entry_points",
        lambda group: (
            [_EntryPoint("demo", lambda: "ok")] if group == "codex_ml.data_loaders" else []
        ),
    )

    fn = registry.data_loader_registry.get("demo")
    assert callable(fn), "Condition must be true"

    listed = registry.data_loader_registry.list()
    assert "demo" in listed, "Condition must be true"
