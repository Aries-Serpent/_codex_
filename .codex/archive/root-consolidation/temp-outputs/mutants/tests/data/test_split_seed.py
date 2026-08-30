"""
Test Split Seed

Test module for split seed.
"""

from __future__ import annotations

from codex_ml.data.split_utils import deterministic_split, ensure_split_seed


def test_ensure_split_seed_env(monkeypatch):
    monkeypatch.setenv("CODEX_DATA_SEED", "99")
    assert ensure_split_seed(None) == 99, "Condition must be true"
    monkeypatch.setenv("CODEX_DATA_SEED", "not-int")
    assert ensure_split_seed(None) == 42, "Condition must be true"


def test_deterministic_split_reproducible(monkeypatch):
    items = list(range(20))
    monkeypatch.setenv("CODEX_DATA_SEED", "7")
    a_train, a_val, a_test = deterministic_split(items, seed=None)
    b_train, b_val, b_test = deterministic_split(items, seed=None)
    assert a_train == b_train, "a_train is not valid"
    assert a_val == b_val, "a_val is not valid"
    assert a_test == b_test, "a_test is not valid"
