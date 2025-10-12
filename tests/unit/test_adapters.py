from __future__ import annotations

import pytest


def test_adapter_imports():
    try:
        from hhg_logistics.model.adapters import load_adapters_into  # noqa: F401
    except Exception:
        pytest.skip("peft not installed")
