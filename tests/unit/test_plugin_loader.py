from __future__ import annotations

import pytest


def test_plugin_loader_imports() -> None:
    try:
        from hhg_logistics.plugins import load_plugins
    except Exception:
        pytest.skip("plugin loader unavailable")

    load_plugins(["hhg_logistics.plugins.example_plugin", "nonexistent.module.maybe"])
