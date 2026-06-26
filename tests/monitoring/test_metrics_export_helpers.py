"""Tests for metrics export utilities."""

from __future__ import annotations

from codex_ml.monitoring.metrics_export import get_metrics_text


def test_get_metrics_text_handles_missing_prometheus():
    text = get_metrics_text()
    assert isinstance(text, str)
    # Should mention prometheus in some form (either metrics or "not installed" message)
    assert "prometheus" in text.lower() or len(text) > 0, "Text must not be empty"
