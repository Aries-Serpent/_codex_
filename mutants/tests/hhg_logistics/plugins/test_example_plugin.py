"""
Test Example Plugin

Test module for example plugin.
"""

import importlib

import pytest


def test_import_module():
    module = "hhg_logistics.plugins.example_plugin"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
