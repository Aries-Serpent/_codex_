"""
Test Entry Point Loader Function

Test module for entry point loader function.
"""

from __future__ import annotations

from codex_ml import plugins


def test_load_entry_point_plugins_disabled_returns_zero():
    result = plugins.load_entry_point_plugins(enable=False)
    assert isinstance(result, dict)
    assert all(count == 0 for count in result.values()), "Result must not be empty"


def test_load_entry_point_plugins_custom_group(monkeypatch):
    monkeypatch.setattr(plugins, "load_plugins", lambda group: 7)
    result = plugins.load_entry_point_plugins(enable=True, groups={"custom": "codex.custom"})
    assert result["custom"] == 7, "Result must not be empty"
