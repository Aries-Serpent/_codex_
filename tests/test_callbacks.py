import pytest


def test_early_stopping_improves_and_plateaus():
    from codex_ml.training.callbacks import EarlyStopping

    es = EarlyStopping(patience=2, min_delta=0.1, mode="max")
    assert es.step(0.5) is False
    assert es.step(0.7) is False
    assert es.step(0.75) is False
    assert es.step(0.76) is True


def test_early_stopping_resets_on_real_improvement():
    from codex_ml.training.callbacks import EarlyStopping

    es = EarlyStopping(patience=2, min_delta=0.05, mode="min")
    assert es.step(1.0) is False
    # small improvement < min_delta counts as plateau
    assert es.step(0.99) is False
    # real improvement resets patience
    assert es.step(0.90) is False
    # after reset, a plateau does not trigger stop
    assert es.step(0.92) is False

