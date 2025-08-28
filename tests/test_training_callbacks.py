# BEGIN: CODEX_TEST_TRAINING_CALLBACKS
from codex_ml.training.callbacks import EarlyStopping


def test_early_stopping_triggers_after_patience():
    es = EarlyStopping(patience=1)
    assert es.step(1.0) is False
    assert es.step(1.0) is False
    assert es.step(1.0) is True


def test_early_stopping_resets_on_improvement():
    es = EarlyStopping(patience=2)
    es.step(1.0)
    es.step(1.1)
    es.step(0.9)  # improvement resets counter
    assert es.step(1.0) is False  # bad=1
    assert es.step(1.0) is False  # bad=2
    assert es.step(1.0) is True   # bad=3 > patience


def test_early_stopping_respects_min_delta():
    es = EarlyStopping(patience=0, min_delta=0.5)
    es.step(1.0)
    assert es.step(0.6) is True  # improvement < min_delta -> treated as no progress
# END: CODEX_TEST_TRAINING_CALLBACKS
