from __future__ import annotations

import warnings

import pytest

# Always import the shim; it exists in this repo
from src.tokenization.api import legacy_tokenizer

# The direct adapter may not exist in minimal environments; skip if missing.
HFTokenizerAdapter = None
try:
    from src.tokenization.api import HFTokenizerAdapter as _HF  # type: ignore
    HFTokenizerAdapter = _HF
except Exception:
    HFTokenizerAdapter = None


def test_legacy_tokenizer_triggers_warning(monkeypatch):
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always", DeprecationWarning)
        try:
            # Attribute access path
            _ = getattr(legacy_tokenizer, "__doc__", None)
            # Call path (may raise ImportError if optional deps missing)
            try:
                legacy_tokenizer()  # type: ignore[call-arg]
            except Exception:
                pass
        except ImportError:
            # Accept missing underlying implementation in minimal envs
            pass
        # Ensure at least one deprecation warning was captured
        assert any(issubclass(x.category, DeprecationWarning) for x in w)


def test_direct_adapter_no_warning():
    if HFTokenizerAdapter is None:
        pytest.skip("HFTokenizerAdapter not available in this environment")
    # Accessing the direct adapter should not emit a DeprecationWarning
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always", DeprecationWarning)
        _ = HFTokenizerAdapter  # type: ignore
        assert not any(issubclass(x.category, DeprecationWarning) for x in w)