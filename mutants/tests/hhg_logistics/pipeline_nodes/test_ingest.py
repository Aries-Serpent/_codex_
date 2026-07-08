"""
Test Ingest

Test module for ingest.
"""

import importlib

import pytest


def test_import_module():
    module = "hhg_logistics.pipeline_nodes.ingest"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
