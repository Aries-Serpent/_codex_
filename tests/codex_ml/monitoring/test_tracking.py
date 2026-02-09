"""
Test Tracking

Test module for tracking.
"""

import importlib

import pytest


def test_import_module():
    module = "codex_ml.monitoring.tracking"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
