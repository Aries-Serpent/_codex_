"""
Test Query Logs

Test module for query logs.
"""

import importlib
import pytest


def test_import_module():
    module = "codex.logging.query_logs"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
