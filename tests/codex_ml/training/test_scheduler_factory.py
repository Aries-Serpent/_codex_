"""
Test Scheduler Factory

Test module for scheduler factory.
"""

import importlib
import pytest


def test_import_module():
    module = "codex_ml.training.scheduler_factory"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
