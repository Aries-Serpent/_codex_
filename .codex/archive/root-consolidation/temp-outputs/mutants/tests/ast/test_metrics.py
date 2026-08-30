"""Tests for metrics aggregation module."""

from codex.ast.metrics import CodeMetrics, MetricsAggregator


def test_metrics_aggregation():
    """Test basic metrics aggregation."""
    m1 = CodeMetrics(5, 3.0, 100, 10, 80.0)
    m2 = CodeMetrics(3, 2.0, 50, 5, 90.0)

    agg = MetricsAggregator()
    result = agg.aggregate([m1, m2])

    assert result.cyclomatic_complexity == 8, "Result must not be empty"
    assert result.lines_of_code == 150, "Result must not be empty"
    assert result.maintainability_index == 85.0, "Result must not be empty"


def test_quality_tier():
    """Test quality tier grading."""
    m_a = CodeMetrics(5, 3.0, 100, 10, 90.0)
    m_b = CodeMetrics(10, 5.0, 200, 20, 75.0)
    m_c = CodeMetrics(15, 10.0, 300, 30, 60.0)
    m_f = CodeMetrics(20, 15.0, 500, 50, 30.0)

    assert m_a.quality_tier == "A", "quality_tier is not valid"
    assert m_b.quality_tier == "B", "quality_tier is not valid"
    assert m_c.quality_tier == "C", "quality_tier is not valid"
    assert m_f.quality_tier == "F", "quality_tier is not valid"


def test_store_and_summary():
    """Test storing metrics and generating summary."""
    agg = MetricsAggregator()
    m1 = CodeMetrics(5, 3.0, 100, 10, 80.0)
    m2 = CodeMetrics(10, 5.0, 200, 20, 70.0)

    agg.store_metrics("entity1", m1)
    agg.store_metrics("entity2", m2)

    summary = agg.summary()
    assert summary["total_entities"] == 2, "Condition must be true"
    assert summary["total_lines_of_code"] == 300, "Condition must be true"
    assert summary["average_cyclomatic_complexity"] == 7.5, "Condition must be true"
    assert summary["max_cyclomatic_complexity"] == 10, "Condition must be true"


def test_empty_aggregation():
    """Test aggregation with empty list."""
    agg = MetricsAggregator()
    result = agg.aggregate([])

    assert result.cyclomatic_complexity == 0, "Result must not be empty"
    assert result.maintainability_index == 100.0, "Result must not be empty"


def test_correlation():
    """Test complexity-coverage correlation."""
    agg = MetricsAggregator()
    complexity = [5.0, 10.0, 15.0, 20.0]
    coverage = [90.0, 80.0, 70.0, 60.0]

    corr = agg.correlate_complexity_coverage(complexity, coverage)
    # Should be negative correlation (higher complexity, lower coverage)
    assert corr < 0, "corr is not valid"
    assert corr > -1.1, "corr must be greater than zero"


def test_to_dict():
    """Test metrics serialization to dict."""
    m = CodeMetrics(5, 3.0, 100, 10, 85.0)
    data = m.to_dict()

    assert data["cyclomatic_complexity"] == 5, "Data must not be empty"
    assert data["lines_of_code"] == 100, "Data must not be empty"
    assert data["quality_tier"] == "A", "Data must not be empty"


def test_correlation_mismatched_lengths():
    """Test correlation raises ValueError when input lengths differ."""
    import pytest

    agg = MetricsAggregator()

    # Test case 1: coverage_metrics is empty - this triggers "At least 2 data points" first
    with pytest.raises(ValueError, match="At least 2 data points required"):
        agg.correlate_complexity_coverage([1.0, 2.0], [])

    # Test case 2: coverage_metrics is shorter - this also triggers "At least 2 data points"
    with pytest.raises(ValueError, match="At least 2 data points required"):
        agg.correlate_complexity_coverage([1.0, 2.0, 3.0], [10.0])

    # Test case 3: complexity_metrics is shorter - also triggers "At least 2 data points"
    with pytest.raises(ValueError, match="At least 2 data points required"):
        agg.correlate_complexity_coverage([1.0], [10.0, 20.0, 30.0])

    # Test case 4: Both have 2+ elements but different lengths - triggers length mismatch
    with pytest.raises(ValueError, match="must have the same length"):
        agg.correlate_complexity_coverage([1.0, 2.0, 3.0], [10.0, 20.0])


def test_correlation_insufficient_data():
    """Test correlation raises ValueError with fewer than 2 data points."""
    import pytest

    agg = MetricsAggregator()

    # Test empty lists
    with pytest.raises(ValueError, match="At least 2 data points required"):
        agg.correlate_complexity_coverage([], [])

    # Test single data point
    with pytest.raises(ValueError, match="At least 2 data points required"):
        agg.correlate_complexity_coverage([1.0], [10.0])


def test_correlation_valid_inputs():
    """Test correlation works correctly with valid inputs."""
    agg = MetricsAggregator()

    # Test with exactly 2 data points
    corr = agg.correlate_complexity_coverage([1.0, 2.0], [10.0, 20.0])
    assert corr > 0, "corr must be greater than zero"

    # Test with multiple data points (negative correlation)
    complexity = [5.0, 10.0, 15.0, 20.0]
    coverage = [90.0, 80.0, 70.0, 60.0]
    corr = agg.correlate_complexity_coverage(complexity, coverage)
    assert -1.0 <= corr < 0, "0 is not valid"
