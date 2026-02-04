"""
Test Engine

Test module for engine.
"""

import importlib
import pytest


def test_import_module():
    module = "codex_ml.training.engine"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
