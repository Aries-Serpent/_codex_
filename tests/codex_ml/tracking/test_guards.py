"""
Test Guards

Test module for guards.
"""

import importlib

import pytest


def test_import_module():
    module = "codex_ml.tracking.guards"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
