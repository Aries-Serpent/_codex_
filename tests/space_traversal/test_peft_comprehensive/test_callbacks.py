"""
Test Callbacks

Test module for callbacks.
"""

from __future__ import annotations

import importlib


def test_early_stopping_patience_and_plateau():
    mod = importlib.import_module("codex_ml.training.callbacks")
    es = mod.EarlyStopping(patience=2, min_delta=0.1)
    es.mode = "min"
    assert es.step(1.0) is False, "Condition must be true"
    assert es.step(0.8) is False, "Condition must be true"
    assert es.step(0.85) is False, "Condition must be true"
    stop = es.step(0.9)  # plateau count=2
    assert stop is True, "stop is not valid"
