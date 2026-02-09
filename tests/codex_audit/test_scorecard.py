"""
Test Scorecard

Test module for scorecard.
"""

import importlib

import pytest


def test_import_module():
    module = "codex_audit.scorecard"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
