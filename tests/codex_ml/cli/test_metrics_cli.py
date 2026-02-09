"""
Test Metrics Cli

Test module for metrics cli.
"""

import importlib

import pytest


def test_import_module():
    module = "codex_ml.cli.metrics_cli"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
