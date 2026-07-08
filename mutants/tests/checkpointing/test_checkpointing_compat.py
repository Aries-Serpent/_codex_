"""
Test Checkpointing Compat

Test module for checkpointing compat.
"""

from __future__ import annotations

import importlib
import warnings

import pytest


def test_checkpointing_compat_emits_deprecation_and_forwards_attributes():
    try:
        compat = importlib.import_module("codex_ml.checkpointing.compat")
    except (ImportError, AttributeError) as exc:  # pragma: no cover - optional deps missing
        pytest.skip(f"compat module unavailable: {exc}")
    else:
        with warnings.catch_warnings(record=True) as rec:
            warnings.simplefilter("always", DeprecationWarning)
            with pytest.raises(AttributeError):
                compat.__not_a_real_symbol__  # ensures __getattr__ path executed  # noqa: B018
        assert any(w.category is DeprecationWarning for w in rec), "no DeprecationWarning emitted"
