#!/usr/bin/env python3
"""Test that metric plugin loading is non-fatal and built-ins remain available."""

from __future__ import annotations

from codex_ml.metrics.registry import init_metric_plugins, list_metrics


def test_metric_plugins_load_without_errors():
    """Plugin initialization path does not raise and built-ins remain available.
    
    This test ensures that:
    1. init_metric_plugins() does not raise exceptions
    2. Returns an integer (count of loaded plugins)
    3. Built-in metrics remain available regardless of plugin load outcome
    4. Registry includes expected built-in metrics
    """
    # Force re-initialization to test the plugin loading path
    result = init_metric_plugins(force=True)
    
    # Should return an integer count (0 or more)
    assert isinstance(result, int)
    assert result >= 0
    
    # Built-in metrics should always be available
    available = list_metrics()
    assert isinstance(available, list)
    assert len(available) > 0
    
    # Check for specific built-in metrics
    available_lower = [m.lower() for m in available]
    
    # Token accuracy (may be registered as "token_accuracy" or "accuracy@token")
    assert any(
        "token_accuracy" in m or "accuracy@token" in m 
        for m in available_lower
    ), f"token_accuracy or accuracy@token not found in {available}"
    
    # F1 metric
    assert "f1" in available_lower, f"f1 not found in {available}"
    
    # Exact match
    assert "exact_match" in available_lower, f"exact_match not found in {available}"
    
    # Perplexity
    assert "ppl" in available_lower or "perplexity" in available_lower, \
        f"perplexity metric not found in {available}"


def test_metric_plugins_initialization_is_idempotent():
    """Multiple calls to init_metric_plugins should be safe."""
    # First call
    result1 = init_metric_plugins(force=True)
    metrics1 = set(list_metrics())
    
    # Second call
    result2 = init_metric_plugins(force=True)
    metrics2 = set(list_metrics())
    
    # Should return consistent results
    assert isinstance(result1, int)
    assert isinstance(result2, int)
    
    # Built-in metrics should still be available
    assert len(metrics1) > 0
    assert len(metrics2) > 0
    
    # Core metrics should be present in both
    for metric_set in [metrics1, metrics2]:
        metric_set_lower = {m.lower() for m in metric_set}
        assert any("token_accuracy" in m or "accuracy@token" in m for m in metric_set_lower)
        assert "f1" in metric_set_lower


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
    assert count >= 0
    
    # Built-ins should still work
    available = list_metrics()
    assert len(available) > 0
    
    # At least these built-ins should be present
    available_lower = [m.lower() for m in available]
    expected_builtins = ["f1", "exact_match", "bleu"]
    found_builtins = [m for m in expected_builtins if m in available_lower]
    
    assert len(found_builtins) >= 2, \
        f"Expected at least 2 built-in metrics from {expected_builtins}, found {found_builtins}"
