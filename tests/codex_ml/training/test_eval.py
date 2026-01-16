"""
Test Eval

Test module for eval.
"""

import importlib
import pytest


def test_import_module():
    module = "codex_ml.training.eval"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
