"""
Test  Logger Types

Test module for  logger types.
"""

import importlib

import pytest


def test_import_module():
    module = "codex_ml.monitoring._logger_types"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
