"""
Test Guards Codex Utils

Test module for guards codex utils.
"""

import importlib

import pytest


def test_import_module():
    module = "codex_utils.tracking.guards"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
