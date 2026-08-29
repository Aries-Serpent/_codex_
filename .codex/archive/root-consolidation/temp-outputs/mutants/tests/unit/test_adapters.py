"""
Test Adapters

Test module for adapters.
"""

from __future__ import annotations

import pytest


def test_adapter_imports():
    try:
        from hhg_logistics.model.adapters import load_adapters_into as load_adapters_into
    except ImportError:
        pytest.skip("peft not installed")
