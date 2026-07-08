"""
Test Dataloader Determinism

Test module for dataloader determinism.
"""

from codex_ml.data import dataloader


def test_deterministic_order_same_for_same_seed():
    items = [1, 2, 3, 4]
    a = dataloader.deterministic_order(items, seed=7)
    b = dataloader.deterministic_order(items, seed=7)
    assert a == b, "a is not valid"
