"""Deterministic shuffling ensures reproducible iterations for tests."""

from __future__ import annotations

from codex_ml.data.datamodule import DataModule


def test_datamodule_determinism():
    """Identical seeds produce identical batches; differing seeds do not."""

    dm1 = DataModule(train=list(range(10)), val=list(range(10)), test=list(range(10)), seed=7)
    dm2 = DataModule(train=list(range(10)), val=list(range(10)), test=list(range(10)), seed=7)
    assert list(dm1.iter_train(3)) == list(dm2.iter_train(3))

    dm3 = DataModule(train=list(range(10)), val=list(range(10)), test=list(range(10)), seed=8)
    assert list(dm1.iter_train(3)) != list(dm3.iter_train(3))
