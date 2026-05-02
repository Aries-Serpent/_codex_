"""
Test Seed Util

Test module for seed util.
"""

from __future__ import annotations

import pytest

pytest.importorskip("numpy", reason="numpy required")

import random

import pytest

from training.seed import ensure_global_seed


def test_ensure_global_seed_sets_random_state() -> None:
    ensure_global_seed(123)
    first = random.randint(0, 1000)
    ensure_global_seed(123)
    second = random.randint(0, 1000)
    assert first == second


def test_ensure_global_seed_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[int] = []

    def fake_set_seed(value: int, *, deterministic: bool = True) -> None:
        calls.append(value)
        assert deterministic is True

    # Patch _set_seed where it's imported in src.training.seed
    monkeypatch.setattr("src.training.seed._set_seed", fake_set_seed)
    resolved = ensure_global_seed()
    assert resolved == 42
    assert calls == [42]
