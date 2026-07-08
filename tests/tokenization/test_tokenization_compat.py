"""
Test Tokenization Compat

Test module for tokenization compat.
"""

from __future__ import annotations

import importlib
import types
import warnings

import pytest


def test_tokenization_compat_emits_deprecation_and_forwards_attributes(monkeypatch):
    try:
        compat = importlib.import_module("codex_ml.tokenization.compat")
    except (ImportError, AttributeError) as exc:  # pragma: no cover - optional deps missing
        pytest.skip(f"compat module unavailable: {exc}")
    else:
        captured: dict[str, object] = {}

        def fake_load_tokenizer(*args, **kwargs):
            captured["args"] = args
            captured["kwargs"] = kwargs
            return "tokenizer"

        monkeypatch.setattr(
            compat,
            "_get_api",
            lambda: types.SimpleNamespace(load_tokenizer=fake_load_tokenizer),
        )

        with warnings.catch_warnings(record=True) as rec:
            warnings.simplefilter("always", DeprecationWarning)
            result = compat.load_tokenizer("demo-model", allow_remote=False)

        assert result == "tokenizer", "Result must not be empty"
        assert captured["args"] == ("demo-model",)
        assert captured["kwargs"] == {"allow_remote": False}, "Condition must be true"
        assert any(w.category is DeprecationWarning for w in rec), "no DeprecationWarning emitted"
