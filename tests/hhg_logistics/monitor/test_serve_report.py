"""
Test Serve Report

Test module for serve report.
"""

import importlib

import pytest


def test_import_module():
    module = "hhg_logistics.monitor.serve_report"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
