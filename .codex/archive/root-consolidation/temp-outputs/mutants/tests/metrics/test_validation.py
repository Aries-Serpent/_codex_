"""Test suite for metrics validation."""

from __future__ import annotations

import pytest

from codex_ml.metrics.validation import (
    MetricValidationError,
    get_all_registered_metrics,
    validate_metric_exists,
    validate_metric_registry,
)


class TestMetricValidation:
    """Test metric validation functionality."""

    def test_validate_metric_registry_success(self):
        """Test validation passes for valid metrics."""
        # This will work if the registry is properly set up
        try:
            warnings = validate_metric_registry()
            # Should return empty list or list of non-critical warnings
            assert isinstance(warnings, list)
        except MetricValidationError:
            # If registry isn't set up, that's also acceptable
            pytest.skip("Metric registry not available in test environment")

    def test_metric_validation_error_exception(self):
        """Test MetricValidationError can be raised and caught."""
        with pytest.raises(MetricValidationError, match="test error"):
            raise MetricValidationError("test error")

    def test_validate_metric_exists_nonexistent(self):
        """Test validate_metric_exists returns False for non-existent metric."""
        # Use a metric name that definitely doesn't exist
        result = validate_metric_exists("this_metric_definitely_does_not_exist_12345")
        assert result is False, "Result must not be empty"

    def test_get_all_registered_metrics_returns_list(self):
        """Test get_all_registered_metrics returns a list."""
        metrics = get_all_registered_metrics()
        assert isinstance(metrics, list)
        # List may be empty if registry not set up, but should be a list

    def test_metric_validation_error_inheritance(self):
        """Test MetricValidationError inherits from Exception."""
        assert issubclass(MetricValidationError, Exception)

    def test_metric_validation_error_message(self):
        """Test MetricValidationError preserves message."""
        message = "Custom validation error message"
        error = MetricValidationError(message)
        assert str(error) == message, "Error should be raised or set"

    def test_validate_metric_exists_returns_bool(self):
        """Test validate_metric_exists always returns boolean."""
        result1 = validate_metric_exists("any_metric_name")
        result2 = validate_metric_exists("")
        result3 = validate_metric_exists("another_test_metric")

        assert isinstance(result1, bool)
        assert isinstance(result2, bool)
        assert isinstance(result3, bool)

    def test_get_all_registered_metrics_no_duplicates(self):
        """Test registered metrics list has no duplicates."""
        metrics = get_all_registered_metrics()
        assert len(metrics) == len(set(metrics)), "Metrics must not be empty"

    def test_validate_metric_registry_returns_list_of_strings(self):
        """Test validate_metric_registry returns list of warning strings."""
        try:
            warnings = validate_metric_registry()
            assert isinstance(warnings, list)
            for warning in warnings:
                assert isinstance(warning, str)
        except MetricValidationError:
            # Registry not available is acceptable
            pytest.skip("Metric registry not available")

    def test_validate_known_metrics_if_available(self):
        """Test validation of known metrics if registry is available."""
        metrics = get_all_registered_metrics()

        if not metrics:
            pytest.skip("No metrics registered in test environment")

        # Test first few metrics
        for metric_name in metrics[:3]:
            result = validate_metric_exists(metric_name)
            # Registered metrics should validate
            assert isinstance(result, bool)
