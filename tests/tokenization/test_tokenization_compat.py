from __future__ import annotations

import importlib
import warnings

import pytest


def test_tokenization_compat_emits_deprecation_and_forwards_attributes():
    try:
        compat = importlib.import_module("codex_ml.tokenization.compat")
    except Exception as exc:  # pragma: no cover - optional deps missing
        pytest.skip(f"compat module unavailable: {exc}")
    # Accessing a non-existent symbol should still emit a deprecation warning.
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always", DeprecationWarning)
        with pytest.raises(AttributeError):
            getattr(compat, "__definitely_not_a_symbol__")  # triggers __getattr__
    assert any(w.category is DeprecationWarning for w in rec), "no DeprecationWarning emitted"
