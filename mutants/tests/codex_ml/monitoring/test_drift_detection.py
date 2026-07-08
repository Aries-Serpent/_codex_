"""
Test Drift Detection

Test module for drift detection.
"""

import importlib

import pytest


def test_import_module():
    module = "codex_ml.monitoring.drift_detection"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
