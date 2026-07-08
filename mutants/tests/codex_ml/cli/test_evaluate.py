"""
Test Evaluate

Test module for evaluate.
"""

import importlib

import pytest


def test_import_module():
    module = "codex_ml.cli.evaluate"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
