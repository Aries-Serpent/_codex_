"""
Test Async Writer

Test module for async writer.
"""

import importlib

import pytest


def test_import_module():
    module = "codex_ml.monitoring.async_writer"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
