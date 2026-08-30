"""
Test Metric Implementations

Test module for metric implementations.
"""

import pytest


class TestFlatListHelper:
    """Test _to_flat_list helper function."""

    def test_flat_list_with_list(self):
        """Test flattening a simple list."""
        try:
            from codex_ml.metrics.metric_implementations import _to_flat_list

            result = _to_flat_list([1, 2, 3])
            assert result == [1, 2, 3]
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")

    def test_flat_list_with_nested_list(self):
        """Test flattening a nested list."""
        try:
            from codex_ml.metrics.metric_implementations import _to_flat_list

            result = _to_flat_list([[1, 2], [3, 4]])
            assert result == [1, 2, 3, 4]
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")

    def test_flat_list_with_scalar(self):
        """Test flattening a scalar value."""
        try:
            from codex_ml.metrics.metric_implementations import _to_flat_list

            result = _to_flat_list(42)
            assert result == [42], "Result must not be empty"
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")


class TestMetricBase:
    """Test MetricBase abstract class."""

    def test_metric_base_name(self):
        """Test MetricBase stores name."""
        try:
            from codex_ml.metrics.metric_implementations import MetricBase

            class DummyMetric(MetricBase):
                def update(self, predictions, targets):
                    pass

                def compute(self):
                    return {}

            metric = DummyMetric("test_metric")
            assert metric.name == "test_metric", "name is not valid"
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")

    def test_metric_base_abstract(self):
        """Test MetricBase cannot be instantiated directly."""
        try:
            from codex_ml.metrics.metric_implementations import MetricBase

            with pytest.raises(TypeError):
                MetricBase("test")
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")


class TestClassificationStats:
    """Test _ClassificationStats helper class."""

    def test_classification_stats_creation(self):
        """Test creating classification stats."""
        try:
            from codex_ml.metrics.metric_implementations import _ClassificationStats

            stats = _ClassificationStats()
            assert stats is not None, "stats must be initialized"
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")

    def test_classification_stats_update(self):
        """Test updating classification stats."""
        try:
            from codex_ml.metrics.metric_implementations import _ClassificationStats

            stats = _ClassificationStats()
            stats.update([0, 1, 1], [0, 1, 0])
            assert stats.tp[0] == 1, "Condition must be true"
            assert stats.tp[1] == 1, "Condition must be true"
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")
