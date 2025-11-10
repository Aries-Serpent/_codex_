"""Tests for metrics aggregation module."""

from codex.ast.metrics import CodeMetrics, MetricsAggregator


def test_metrics_aggregation():
    """Test basic metrics aggregation."""
    m1 = CodeMetrics(5, 3.0, 100, 10, 80.0)
    m2 = CodeMetrics(3, 2.0, 50, 5, 90.0)
    
    agg = MetricsAggregator()
    result = agg.aggregate([m1, m2])
    
    assert result.cyclomatic_complexity == 8
    assert result.lines_of_code == 150
    assert result.maintainability_index == 85.0


def test_quality_tier():
    """Test quality tier grading."""
    m_a = CodeMetrics(5, 3.0, 100, 10, 90.0)
    m_b = CodeMetrics(10, 5.0, 200, 20, 75.0)
    m_c = CodeMetrics(15, 10.0, 300, 30, 60.0)
    m_f = CodeMetrics(20, 15.0, 500, 50, 30.0)
    
    assert m_a.quality_tier == "A"
    assert m_b.quality_tier == "B"
    assert m_c.quality_tier == "C"
    assert m_f.quality_tier == "F"


def test_store_and_summary():
    """Test storing metrics and generating summary."""
    agg = MetricsAggregator()
    m1 = CodeMetrics(5, 3.0, 100, 10, 80.0)
    m2 = CodeMetrics(10, 5.0, 200, 20, 70.0)
    
    agg.store_metrics("entity1", m1)
    agg.store_metrics("entity2", m2)
    
    summary = agg.summary()
    assert summary["total_entities"] == 2
    assert summary["total_lines_of_code"] == 300
    assert summary["average_cyclomatic_complexity"] == 7.5
    assert summary["max_cyclomatic_complexity"] == 10


def test_empty_aggregation():
    """Test aggregation with empty list."""
    agg = MetricsAggregator()
    result = agg.aggregate([])
    
    assert result.cyclomatic_complexity == 0
    assert result.maintainability_index == 100.0


def test_correlation():
    """Test complexity-coverage correlation."""
    agg = MetricsAggregator()
    complexity = [5.0, 10.0, 15.0, 20.0]
    coverage = [90.0, 80.0, 70.0, 60.0]
    
    corr = agg.correlate_complexity_coverage(complexity, coverage)
    # Should be negative correlation (higher complexity, lower coverage)
    assert corr < 0
    assert corr > -1.1  # Should be within valid range


def test_to_dict():
    """Test metrics serialization to dict."""
    m = CodeMetrics(5, 3.0, 100, 10, 85.0)
    data = m.to_dict()
    
    assert data["cyclomatic_complexity"] == 5
    assert data["lines_of_code"] == 100
    assert data["quality_tier"] == "A"
