"""
Test Codeowners Validate

Test module for codeowners validate.
"""

import importlib

import pytest


def test_import_module():
    module = "tools.codeowners_validate"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
