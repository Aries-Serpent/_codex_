"""
Test Feature Freshness Drift

Test module for feature freshness drift.
"""

import importlib

import pytest


def test_import_module():
    module = "codex_ml.monitoring.feature_freshness_drift"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
