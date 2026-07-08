"""
Test Plugin Loader

Test module for plugin loader.
"""

from __future__ import annotations

import pytest


def test_plugin_loader_imports() -> None:
    load_plugins = pytest.importorskip("hhg_logistics.plugins").load_plugins

    load_plugins(["hhg_logistics.plugins.example_plugin", "nonexistent.module.maybe"])
