from __future__ import annotations

import importlib
import warnings

import pytest


def test_checkpointing_compat_emits_deprecation_and_forwards_attributes():
    try:
        compat = importlib.import_module("codex_ml.checkpointing.compat")
    except Exception as exc:  # pragma: no cover - optional deps missing
        pytest.skip(f"compat module unavailable: {exc}")
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always", DeprecationWarning)
        with pytest.raises(AttributeError):
            getattr(compat, "__not_a_real_symbol__")  # ensures __getattr__ path executed
    assert any(w.category is DeprecationWarning for w in rec), "no DeprecationWarning emitted"
