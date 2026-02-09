"""
Test Metrics Export

Test module for metrics export.
"""

import importlib

import pytest


def test_import_module():
    module = "codex_ml.monitoring.metrics_export"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
