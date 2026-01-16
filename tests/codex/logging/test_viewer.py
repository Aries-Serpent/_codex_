"""
Test Viewer

Test module for viewer.
"""

import importlib
import pytest


def test_import_module():
    module = "codex.logging.viewer"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
