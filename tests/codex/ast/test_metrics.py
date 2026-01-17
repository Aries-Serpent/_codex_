"""
Tests for codex.ast.metrics module.

This module contains tests for code metrics aggregation and analysis.
"""

import pytest


class TestCodeMetrics:
    """Tests for CodeMetrics dataclass."""

    def test_basic_creation(self):
        """Test CodeMetrics basic creation."""
        from codex.ast.metrics import CodeMetrics
        
        metrics = CodeMetrics(
            cyclomatic_complexity=10,
            cognitive_complexity=5.0,
            lines_of_code=100,
            comment_lines=20,
            maintainability_index=75.0
        )
        
        assert metrics.cyclomatic_complexity == 10
        assert metrics.cognitive_complexity == 5.0
        assert metrics.lines_of_code == 100
        assert metrics.comment_lines == 20
        assert metrics.maintainability_index == 75.0

    def test_quality_tier_a(self):
        """Test quality tier A (>= 85)."""
        from codex.ast.metrics import CodeMetrics
        
        metrics = CodeMetrics(0, 0.0, 0, 0, 90.0)
        assert metrics.quality_tier == "A"
        
        metrics_edge = CodeMetrics(0, 0.0, 0, 0, 85.0)
        assert metrics_edge.quality_tier == "A"

    def test_quality_tier_b(self):
        """Test quality tier B (70-84)."""
        from codex.ast.metrics import CodeMetrics
        
        metrics = CodeMetrics(0, 0.0, 0, 0, 75.0)
        assert metrics.quality_tier == "B"
        
        metrics_edge = CodeMetrics(0, 0.0, 0, 0, 70.0)
        assert metrics_edge.quality_tier == "B"

    def test_quality_tier_c(self):
        """Test quality tier C (55-69)."""
        from codex.ast.metrics import CodeMetrics
        
        metrics = CodeMetrics(0, 0.0, 0, 0, 60.0)
        assert metrics.quality_tier == "C"
        
        metrics_edge = CodeMetrics(0, 0.0, 0, 0, 55.0)
        assert metrics_edge.quality_tier == "C"

    def test_quality_tier_d(self):
        """Test quality tier D (40-54)."""
        from codex.ast.metrics import CodeMetrics
        
        metrics = CodeMetrics(0, 0.0, 0, 0, 45.0)
        assert metrics.quality_tier == "D"
        
        metrics_edge = CodeMetrics(0, 0.0, 0, 0, 40.0)
        assert metrics_edge.quality_tier == "D"

    def test_quality_tier_f(self):
        """Test quality tier F (< 40)."""
        from codex.ast.metrics import CodeMetrics
        
        metrics = CodeMetrics(0, 0.0, 0, 0, 30.0)
        assert metrics.quality_tier == "F"
        
        metrics_zero = CodeMetrics(0, 0.0, 0, 0, 0.0)
        assert metrics_zero.quality_tier == "F"

    def test_to_dict(self):
        """Test CodeMetrics serialization."""
        from codex.ast.metrics import CodeMetrics
        
        metrics = CodeMetrics(
            cyclomatic_complexity=5,
            cognitive_complexity=3.5,
            lines_of_code=50,
            comment_lines=10,
            maintainability_index=80.0
        )
        
        result = metrics.to_dict()
        
        assert result["cyclomatic_complexity"] == 5
        assert result["cognitive_complexity"] == 3.5
        assert result["lines_of_code"] == 50
        assert result["comment_lines"] == 10
        assert result["maintainability_index"] == 80.0
        assert result["quality_tier"] == "B"


class TestMetricsAggregator:
    """Tests for MetricsAggregator class."""

    def test_init(self):
        """Test MetricsAggregator initialization."""
        from codex.ast.metrics import MetricsAggregator
        
        aggregator = MetricsAggregator()
        
        assert aggregator.metrics == {}

    def test_store_metrics(self):
        """Test storing metrics for an entity."""
        from codex.ast.metrics import MetricsAggregator, CodeMetrics
        
        aggregator = MetricsAggregator()
        metrics = CodeMetrics(5, 3.0, 100, 20, 75.0)
        
        aggregator.store_metrics("entity_1", metrics)
        
        assert "entity_1" in aggregator.metrics
        assert aggregator.metrics["entity_1"] == metrics

    def test_aggregate_empty(self):
        """Test aggregation with empty list."""
        from codex.ast.metrics import MetricsAggregator
        
        aggregator = MetricsAggregator()
        result = aggregator.aggregate([])
        
        assert result.cyclomatic_complexity == 0
        assert result.cognitive_complexity == 0.0
        assert result.lines_of_code == 0
        assert result.comment_lines == 0
        assert result.maintainability_index == 100.0

    def test_aggregate_single(self):
        """Test aggregation with single metric."""
        from codex.ast.metrics import MetricsAggregator, CodeMetrics
        
        aggregator = MetricsAggregator()
        metrics = CodeMetrics(10, 5.0, 100, 20, 80.0)
        
        result = aggregator.aggregate([metrics])
        
        assert result.cyclomatic_complexity == 10
        assert result.cognitive_complexity == 5.0
        assert result.lines_of_code == 100
        assert result.comment_lines == 20
        assert result.maintainability_index == 80.0

    def test_aggregate_multiple(self):
        """Test aggregation with multiple metrics."""
        from codex.ast.metrics import MetricsAggregator, CodeMetrics
        
        aggregator = MetricsAggregator()
        metrics1 = CodeMetrics(10, 5.0, 100, 20, 80.0)
        metrics2 = CodeMetrics(20, 10.0, 200, 40, 60.0)
        
        result = aggregator.aggregate([metrics1, metrics2])
        
        # Sums for most fields
        assert result.cyclomatic_complexity == 30
        assert result.cognitive_complexity == 15.0
        assert result.lines_of_code == 300
        assert result.comment_lines == 60
        # Mean for maintainability
        assert result.maintainability_index == 70.0
