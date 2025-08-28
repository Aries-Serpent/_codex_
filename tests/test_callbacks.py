import pytest


def test_early_stopping_improves_and_plateaus():
    from codex_ml.training.callbacks import EarlyStopping

    es = EarlyStopping(patience=2, min_delta=0.1, mode="max")
    # improve twice
    assert es.step(0.5) is False
    assert es.step(0.7) is False
    # plateau below min_delta
    assert es.step(0.75) is False  # patience=1
    assert es.step(0.76) is False  # patience=2
    assert es.step(0.77) is True  # patience exceeded -> stop


def test_early_stopping_resets_on_real_improvement():
    from codex_ml.training.callbacks import EarlyStopping

    es = EarlyStopping(patience=2, min_delta=0.05, mode="min")
    # lower is better
    assert es.step(1.0) is False
    assert es.step(0.98) is False
    # plateau (not improved by min_delta)
    assert es.step(0.96) is False
    # clear improvement, should reset
    assert es.step(0.88) is False

