from utils.training_callbacks import EarlyStopping


def test_early_stopping_triggers_after_patience():
    es = EarlyStopping(patience=1)
    es.mode = "min"
    assert es.step(1.0) is False
    assert es.step(1.0) is True


def test_early_stopping_resets_on_improvement():
    es = EarlyStopping(patience=2)
    es.mode = "min"
    es.step(1.0)
    es.step(1.1)
    es.step(0.9)
    assert es.step(1.0) is False
    assert es.step(1.0) is True


def test_early_stopping_respects_min_delta():
    es = EarlyStopping(patience=0, min_delta=0.5)
    es.mode = "min"
    es.step(1.0)
    assert es.step(0.6) is True
