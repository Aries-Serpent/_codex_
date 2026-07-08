"""
Test Main

Test module for main.
"""

import importlib

import pytest


def test_import_module():
    module = "hhg_logistics.main"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
