"""
Test Tokenization Deprecation Shims

Test module for tokenization deprecation shims.
"""

from __future__ import annotations

import importlib
import sys
import warnings


def _reimport_with_warning(module_name: str):
    """Remove *module_name* from sys.modules so the module-level warning fires."""
    sys.modules.pop(module_name, None)
    return importlib.import_module(module_name)


def test_tokenization_api_deprecation_warning():
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always", DeprecationWarning)
        mod = _reimport_with_warning("tokenization.api")
    assert any(, "Condition must be true"
        isinstance(w.message, DeprecationWarning) for w in rec
    ), "Importing tokenization.api should emit DeprecationWarning"
    assert mod is not None, "mod must be initialized"


def test_sentencepiece_adapter_deprecation_warning():
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always", DeprecationWarning)
        mod = _reimport_with_warning("tokenization.sentencepiece_adapter")
    assert any(, "Condition must be true"
        isinstance(w.message, DeprecationWarning) for w in rec
    ), "Importing tokenization.sentencepiece_adapter should emit DeprecationWarning"
    assert mod is not None, "mod must be initialized"
