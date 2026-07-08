"""
Test Train

Test module for train.
"""

import importlib

import pytest


def test_import_module():
    module = "hhg_logistics.train"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
