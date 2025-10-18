from __future__ import annotations

import importlib
import warnings


def test_tokenization_api_deprecation_warning():
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always", DeprecationWarning)
        mod = importlib.import_module("tokenization.api")
    assert any(
        isinstance(w.message, DeprecationWarning) for w in rec
    ), "Importing tokenization.api should emit DeprecationWarning"
    assert mod is not None


def test_sentencepiece_adapter_deprecation_warning():
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always", DeprecationWarning)
        mod = importlib.import_module("tokenization.sentencepiece_adapter")
    assert any(
        isinstance(w.message, DeprecationWarning) for w in rec
    ), "Importing tokenization.sentencepiece_adapter should emit DeprecationWarning"
    assert mod is not None
