from __future__ import annotations

from codex_ml.data.split_utils import deterministic_split, ensure_split_seed


def test_ensure_split_seed_env(monkeypatch):
    monkeypatch.setenv("CODEX_DATA_SEED", "99")
    assert ensure_split_seed(None) == 99
    monkeypatch.setenv("CODEX_DATA_SEED", "not-int")
    assert ensure_split_seed(None) == 42


def test_deterministic_split_reproducible(monkeypatch):
    items = list(range(20))
    monkeypatch.setenv("CODEX_DATA_SEED", "7")
    a_train, a_val, a_test = deterministic_split(items, seed=None)
    b_train, b_val, b_test = deterministic_split(items, seed=None)
    assert a_train == b_train
    assert a_val == b_val
    assert a_test == b_test
