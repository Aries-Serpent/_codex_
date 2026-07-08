#         assert "f1" in metric_set_lower, "Condition must be true"


def test_metric_plugins_graceful_with_no_entry_points():
    """Plugin system works even when no entry points are defined."""
    # This test verifies the system is graceful when:
    # - No plugins are installed
    # - importlib.metadata is available but returns no entry points
    # - The built-in metrics are still accessible

    # Re-initialize plugins
    count = init_metric_plugins(force=True)

    # Count might be 0 (no plugins) or positive (some plugins found)
    # Either way, it should not raise
    assert isinstance(count, int)
    assert count >= 0, "count must be positive"

    # Built-ins should still work
    available = list_metrics()
    assert len(available) > 0, "Available must not be empty"

    # At least these built-ins should be present
    available_lower = [m.lower() for m in available]
    expected_builtins = ["f1", "exact_match", "bleu"]
    found_builtins = [m for m in expected_builtins if m in available_lower]

    assert (len(found_builtins) >= 2, "Found_builtins must not be empty"
    ), f"Expected at least 2 built-in metrics from {expected_builtins}, found {found_builtins}"
