"""Tests for plugin metric conflict resolution policies."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add src to path
_REPO_ROOT = Path(__file__).parent.parent
_SRC_DIR = _REPO_ROOT / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))


def _dummy_metric(preds, refs):
    """Simple dummy metric for testing."""
    return 0.5


@pytest.mark.parametrize("policy", ["prefer_local", "prefer_plugin", "alias_plugin", "shadow_warn"])
def test_plugin_conflict_resolution(monkeypatch, policy):
    """Test that each policy resolves conflicts correctly."""
    from codex_ml.metrics import registry

    # Register a local metric
    test_metric_name = f"test_metric_{policy}"
    registry.register_metric(test_metric_name, _dummy_metric)

    # Simulate plugin attempting duplicate registration
    monkeypatch.setenv("CODEX_METRIC_PLUGIN_POLICY", policy)

    # Inject plugin registration manually
    registry._register_metric_from_plugin(test_metric_name, _dummy_metric)

    names = registry.list_metrics()

    if policy in {"prefer_local", "shadow_warn"}:
        # Original metric should be present
        assert test_metric_name in names or test_metric_name.lower() in names, "Condition must be true"
        # No alias should be created
        assert not any(n.startswith(f"plugin:{test_metric_name}") for n in names), "Condition must be true"
    elif policy == "prefer_plugin":
        # Metric should still be present (overridden)
        assert test_metric_name in names or test_metric_name.lower() in names, "Condition must be true"
    elif policy == "alias_plugin":
        # Both original and alias should be present
        normalized_name = test_metric_name.lower()
        assert normalized_name in names, "n is not valid"
        # Check for alias (registry normalizes to lowercase)
        plugin_alias = f"plugin:{test_metric_name}".lower()
        assert plugin_alias in names, "Condition must be true"


def test_policy_error(monkeypatch):
    """Test that error policy raises RegistryConflictError."""
    from codex_ml.metrics import registry
    from codex_ml.registry.base import RegistryConflictError

    test_metric_name = "test_metric_error"
    registry.register_metric(test_metric_name, _dummy_metric)
    monkeypatch.setenv("CODEX_METRIC_PLUGIN_POLICY", "error")

    with pytest.raises(RegistryConflictError):
        registry._register_metric_from_plugin(test_metric_name, _dummy_metric)


def test_invalid_policy_defaults_prefer_local(monkeypatch):
    """Test that invalid policy defaults to prefer_local."""
    from codex_ml.metrics import registry

    test_metric_name = "test_metric_invalid_policy"
    registry.register_metric(test_metric_name, _dummy_metric)
    monkeypatch.setenv("CODEX_METRIC_PLUGIN_POLICY", "not_a_valid_policy")

    # Should not raise, should use prefer_local
    registry._register_metric_from_plugin(test_metric_name, _dummy_metric)

    names = registry.list_metrics()
    assert test_metric_name in names or test_metric_name.lower() in names, "Condition must be true"


def test_idempotent_plugin_loading(monkeypatch):
    """Test that plugin loading is idempotent."""
    from codex_ml.metrics import registry

    # Set a safe policy
    monkeypatch.setenv("CODEX_METRIC_PLUGIN_POLICY", "prefer_local")

    # First load
    count1 = registry.init_metric_plugins()
    assert count1 >= 0, "count1 must be positive"

    # Second load should return 0 (already loaded)
    count2 = registry.init_metric_plugins()
    assert count2 == 0, "Count must be greater than zero"

    # Force reload
    count3 = registry.init_metric_plugins(force=True)
    # May return a count or 0 depending on whether plugins exist
    assert count3 >= 0, "count3 must be positive"


def test_alias_plugin_creates_separate_entry(monkeypatch):
    """Test that alias_plugin policy creates a separate registry entry."""
    from codex_ml.metrics import registry

    def local_impl(preds, refs):
        return 0.3

    def plugin_impl(preds, refs):
        return 0.7

    test_metric_name = "test_metric_alias"
    registry.register_metric(test_metric_name, local_impl)
    monkeypatch.setenv("CODEX_METRIC_PLUGIN_POLICY", "alias_plugin")

    # Register plugin version
    registry._register_metric_from_plugin(test_metric_name, plugin_impl)

    # Get both implementations
    local = registry.get_metric(test_metric_name)
    plugin_name = f"plugin:{test_metric_name}"
    plugin = registry.get_metric(plugin_name)

    # They should return different values
    result_local = local([], [])
    result_plugin = plugin([], [])

    assert result_local == 0.3, "Result must not be empty"
    assert result_plugin == 0.7, "Result must not be empty"


def test_conflict_logging_dedup(monkeypatch, tmp_path):
    """Test that duplicate conflicts are only logged once per metric."""
    from codex_ml.metrics import registry

    # Set up a temporary error log directory
    monkeypatch.setenv("CODEX_ERROR_REPORTS_DIR", str(tmp_path))
    monkeypatch.setenv("CODEX_METRIC_PLUGIN_POLICY", "prefer_local")

    test_metric_name = "test_metric_dedup"
    registry.register_metric(test_metric_name, _dummy_metric)

    # Register the same plugin metric multiple times
    registry._register_metric_from_plugin(test_metric_name, _dummy_metric)
    registry._register_metric_from_plugin(test_metric_name, _dummy_metric)
    registry._register_metric_from_plugin(test_metric_name, _dummy_metric)

    # Check error log
    from datetime import datetime, timezone

    date_str = datetime.now(timezone.utc).date().isoformat()
    log_file = tmp_path / f"errors_{date_str}.md"

    if log_file.exists():
        content = log_file.read_text()
        # Count how many times this metric appears in conflict-resolution entries
        conflict_entries = content.count("### metric-plugin.conflict-resolution")
        metric_mentions = content.count(f"name={test_metric_name}")

        # Should only be logged once despite 3 registration attempts
        assert (conflict_entries == 1), f"Expected 1 conflict-resolution entry, got {conflict_entries}"
        assert metric_mentions == 1, f"Expected 1 metric mention, got {metric_mentions}"
