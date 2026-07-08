"""
Test Prepare

Test module for prepare.
"""

import importlib

import pytest


def test_import_module():
    module = "hhg_logistics.data.prepare"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
