"""
Test Prompting

Test module for prompting.
"""

import importlib

import pytest


def test_import_module():
    module = "codex_audit.prompting"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
