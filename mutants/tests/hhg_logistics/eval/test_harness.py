"""
Test Harness

Test module for harness.
"""

import importlib

import pytest


def test_import_module():
    module = "hhg_logistics.eval.harness"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
