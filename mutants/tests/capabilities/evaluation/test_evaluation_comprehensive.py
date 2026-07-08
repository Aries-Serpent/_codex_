"""Comprehensive tests for evaluation and metrics capability.

Tests cover:
- Metric determinism enforcement
- NDJSON/CSV logging schema validation
- Regression suite coverage
- Offline eval data versioning
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

import pytest

pytest.importorskip("hypothesis")


pytest.importorskip("hypothesis", reason="hypothesis required for property tests")

from hypothesis import given, settings
from hypothesis import strategies as st

# --- Metric Determinism Tests ---


class DeterministicMetric:
    """Base class for deterministic metrics."""

    def __init__(self, seed: int = 42):
        self.seed = seed

    def compute(self, predictions: list[float], targets: list[float]) -> float:
        """Compute metric value."""
        raise NotImplementedError


class MeanSquaredError(DeterministicMetric):
    """MSE metric implementation."""

    def compute(self, predictions: list[float], targets: list[float]) -> float:
        if len(predictions) != len(targets):
            raise ValueError("Length mismatch")
        if len(predictions) == 0:
            return 0.0
        return sum((p - t) ** 2 for p, t in zip(predictions, targets)) / len(predictions)


class MeanAbsoluteError(DeterministicMetric):
    """MAE metric implementation."""

    def compute(self, predictions: list[float], targets: list[float]) -> float:
        if len(predictions) != len(targets):
            raise ValueError("Length mismatch")
        if len(predictions) == 0:
            return 0.0
        return sum(abs(p - t) for p, t in zip(predictions, targets)) / len(predictions)


class Accuracy(DeterministicMetric):
    """Accuracy metric for classification."""

    def compute(self, predictions: list[int], targets: list[int]) -> float:
        if len(predictions) != len(targets):
            raise ValueError("Length mismatch")
        if len(predictions) == 0:
            return 0.0
        correct = sum(1 for p, t in zip(predictions, targets) if p == t)
        return correct / len(predictions)


class TestMetricDeterminism:
    """Tests for metric determinism."""

    def test_mse_deterministic(self):
        """MSE should be deterministic."""
        preds = [1.0, 2.0, 3.0]
        targets = [1.5, 2.0, 2.5]
        mse = MeanSquaredError()
        result1 = mse.compute(preds, targets)
        result2 = mse.compute(preds, targets)
        assert result1 == result2, "Result must not be empty"

    def test_mae_deterministic(self):
        """MAE should be deterministic."""
        preds = [1.0, 2.0, 3.0]
        targets = [1.5, 2.0, 2.5]
        mae = MeanAbsoluteError()
        result1 = mae.compute(preds, targets)
        result2 = mae.compute(preds, targets)
        assert result1 == result2, "Result must not be empty"

    def test_accuracy_deterministic(self):
        """Accuracy should be deterministic."""
        preds = [0, 1, 1, 0, 1]
        targets = [0, 1, 0, 0, 1]
        acc = Accuracy()
        result1 = acc.compute(preds, targets)
        result2 = acc.compute(preds, targets)
        assert result1 == result2, "Result must not be empty"

    @given(
        st.lists(
            st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=50,
        ),
        st.lists(
            st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=50,
        ),
    )
    @settings(max_examples=30)
    def test_mse_deterministic_property(self, preds: list[float], targets: list[float]):
        """Property: MSE is deterministic for any input."""
        if len(preds) != len(targets):
            return  # Skip mismatched lengths
        mse = MeanSquaredError()
        result1 = mse.compute(preds, targets)
        result2 = mse.compute(preds, targets)
        assert result1 == result2, "Result must not be empty"

    def test_mse_edge_cases(self):
        """MSE should handle edge cases."""
        mse = MeanSquaredError()
        assert mse.compute([], []) == 0.0
        assert mse.compute([1.0], [1.0]) == 0.0
        assert mse.compute([0.0], [1.0]) == 1.0


# --- NDJSON Schema Validation Tests ---


NDJSON_SCHEMA = {
    "required_fields": ["metric", "value", "timestamp"],
    "optional_fields": ["step", "epoch", "run_id", "metadata"],
    "field_types": {
        "metric": str,
        "value": (int, float),
        "timestamp": str,
        "step": int,
        "epoch": int,
        "run_id": str,
        "metadata": dict,
    },
}


def validate_ndjson_record(record: dict[str, Any]) -> list[str]:
    """Validate NDJSON record against schema."""
    errors = []

    # Check required fields
    for field in NDJSON_SCHEMA["required_fields"]:
        if field not in record:
            errors.append(f"Missing required field: {field}")

    # Check field types
    for field, value in record.items():
        if field in NDJSON_SCHEMA["field_types"]:
            expected_type = NDJSON_SCHEMA["field_types"][field]
            if not isinstance(value, expected_type):
                errors.append(
                    f"Invalid type for {field}: expected {expected_type}, got {type(value)}"
                )

    return errors


class TestNdjsonSchemaValidation:
    """Tests for NDJSON schema validation."""

    def test_valid_record(self):
        """Valid record should pass validation."""
        record = {"metric": "loss", "value": 0.5, "timestamp": "2024-01-01T00:00:00Z"}
        errors = validate_ndjson_record(record)
        assert len(errors) == 0, "Errors must not be empty"

    def test_valid_record_with_optional(self):
        """Record with optional fields should pass."""
        record = {
            "metric": "accuracy",
            "value": 0.95,
            "timestamp": "2024-01-01T00:00:00Z",
            "step": 100,
            "epoch": 1,
        }
        errors = validate_ndjson_record(record)
        assert len(errors) == 0, "Errors must not be empty"

    def test_missing_required_field(self):
        """Missing required field should fail."""
        record = {"metric": "loss", "value": 0.5}
        errors = validate_ndjson_record(record)
        assert len(errors) == 1, "Errors must not be empty"
        assert "timestamp" in errors[0], "Error should be raised or set"

    def test_wrong_type(self):
        """Wrong field type should fail."""
        record = {"metric": 123, "value": 0.5, "timestamp": "2024-01-01T00:00:00Z"}
        errors = validate_ndjson_record(record)
        assert len(errors) == 1, "Errors must not be empty"
        assert "metric" in errors[0], "Error should be raised or set"

    def test_all_missing_required(self):
        """All missing required fields should be reported."""
        record = {}
        errors = validate_ndjson_record(record)
        assert len(errors) == 3, "Errors must not be empty"


# --- CSV Schema Validation Tests ---


CSV_SCHEMA = {
    "required_columns": ["metric_name", "metric_value", "timestamp"],
    "optional_columns": ["step", "epoch", "run_id"],
}


def validate_csv_header(header: list[str]) -> list[str]:
    """Validate CSV header against schema."""
    errors = []
    for col in CSV_SCHEMA["required_columns"]:
        if col not in header:
            errors.append(f"Missing required column: {col}")
    return errors


class TestCsvSchemaValidation:
    """Tests for CSV schema validation."""

    def test_valid_header(self):
        """Valid header should pass validation."""
        header = ["metric_name", "metric_value", "timestamp"]
        errors = validate_csv_header(header)
        assert len(errors) == 0, "Errors must not be empty"

    def test_valid_header_with_optional(self):
        """Header with optional columns should pass."""
        header = ["metric_name", "metric_value", "timestamp", "step", "epoch"]
        errors = validate_csv_header(header)
        assert len(errors) == 0, "Errors must not be empty"

    def test_missing_required_column(self):
        """Missing required column should fail."""
        header = ["metric_name", "metric_value"]
        errors = validate_csv_header(header)
        assert len(errors) == 1, "Errors must not be empty"


# --- Regression Suite Tests ---


class RegressionSuite:
    """Regression test suite for metrics."""

    def __init__(self):
        self.baselines: dict[str, dict[str, float]] = {}

    def register_baseline(self, test_name: str, metrics: dict[str, float]) -> None:
        """Register baseline metrics for a test."""
        self.baselines[test_name] = metrics

    def check_regression(
        self, test_name: str, current: dict[str, float], tolerance: float = 0.01
    ) -> dict[str, Any]:
        """Check for regressions against baseline."""
        if test_name not in self.baselines:
            return {"status": "no_baseline", "test": test_name}

        baseline = self.baselines[test_name]
        regressions = []
        improvements = []

        for metric, value in current.items():
            if metric in baseline:
                diff = value - baseline[metric]
                if diff < -tolerance:
                    regressions.append(
                        {
                            "metric": metric,
                            "baseline": baseline[metric],
                            "current": value,
                            "diff": diff,
                        }
                    )
                elif diff > tolerance:
                    improvements.append(
                        {
                            "metric": metric,
                            "baseline": baseline[metric],
                            "current": value,
                            "diff": diff,
                        }
                    )

        return {
            "status": "regression" if regressions else "ok",
            "regressions": regressions,
            "improvements": improvements,
        }


class TestRegressionSuite:
    """Tests for regression suite functionality."""

    def test_no_regression(self):
        """No regression when metrics match baseline."""
        suite = RegressionSuite()
        suite.register_baseline("test1", {"accuracy": 0.95, "f1": 0.92})
        result = suite.check_regression("test1", {"accuracy": 0.95, "f1": 0.92})
        assert result["status"] == "ok", "Result must not be empty"
        assert len(result["regressions"]) == 0, "Collection must not be empty"

    def test_detect_regression(self):
        """Detect regression when metric decreases."""
        suite = RegressionSuite()
        suite.register_baseline("test1", {"accuracy": 0.95})
        result = suite.check_regression("test1", {"accuracy": 0.90})
        assert result["status"] == "regression", "Result must not be empty"
        assert len(result["regressions"]) == 1, "Collection must not be empty"

    def test_detect_improvement(self):
        """Detect improvement when metric increases."""
        suite = RegressionSuite()
        suite.register_baseline("test1", {"accuracy": 0.90})
        result = suite.check_regression("test1", {"accuracy": 0.95})
        assert result["status"] == "ok", "Result must not be empty"
        assert len(result["improvements"]) == 1, "Collection must not be empty"

    def test_no_baseline(self):
        """Handle missing baseline gracefully."""
        suite = RegressionSuite()
        result = suite.check_regression("unknown", {"accuracy": 0.95})
        assert result["status"] == "no_baseline", "Result must not be empty"


# --- Eval Data Versioning Tests ---


class EvalDataVersion:
    """Version info for evaluation data."""

    def __init__(self, name: str, version: str, checksum: str, size: int):
        self.name = name
        self.version = version
        self.checksum = checksum
        self.size = size

    def matches(self, other: "EvalDataVersion") -> bool:
        return (
            self.name == other.name
            and self.version == other.version
            and self.checksum == other.checksum
        )


def compute_data_checksum(data: list[dict]) -> str:
    """Compute checksum of evaluation data."""
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class TestEvalDataVersioning:
    """Tests for evaluation data versioning."""

    def test_version_match(self):
        """Matching versions should be equal."""
        v1 = EvalDataVersion("test_set", "1.0.0", "abc123", 1000)
        v2 = EvalDataVersion("test_set", "1.0.0", "abc123", 1000)
        assert v1.matches(v2), "Condition must be true"

    def test_version_mismatch(self):
        """Different versions should not match."""
        v1 = EvalDataVersion("test_set", "1.0.0", "abc123", 1000)
        v2 = EvalDataVersion("test_set", "1.0.1", "abc123", 1000)
        assert not v1.matches(v2), "Condition must be true"

    def test_checksum_mismatch(self):
        """Different checksums should not match."""
        v1 = EvalDataVersion("test_set", "1.0.0", "abc123", 1000)
        v2 = EvalDataVersion("test_set", "1.0.0", "def456", 1000)
        assert not v1.matches(v2), "Condition must be true"

    def test_data_checksum_deterministic(self):
        """Data checksum should be deterministic."""
        data = [
            {"input": "test1", "expected": "output1"},
            {"input": "test2", "expected": "output2"},
        ]
        h1 = compute_data_checksum(data)
        h2 = compute_data_checksum(data)
        assert h1 == h2, "h1 is not valid"

    @given(
        st.lists(
            st.dictionaries(st.text(min_size=1, max_size=10), st.text(min_size=1, max_size=20)),
            min_size=1,
            max_size=10,
        )
    )
    @settings(max_examples=30)
    def test_checksum_deterministic_property(self, data: list[dict]):
        """Property: data checksum is deterministic."""
        h1 = compute_data_checksum(data)
        h2 = compute_data_checksum(data)
        assert h1 == h2, "h1 is not valid"


# --- Metric Registry Tests ---


class MetricRegistry:
    """Registry for metric implementations."""

    def __init__(self):
        self._metrics: dict[str, type] = {}

    def register(self, name: str, metric_cls: type) -> None:
        """Register a metric class."""
        self._metrics[name] = metric_cls

    def get(self, name: str) -> type | None:
        """Get a metric class by name."""
        return self._metrics.get(name)

    def list_metrics(self) -> list[str]:
        """List all registered metrics."""
        return list(self._metrics.keys())


class TestMetricRegistry:
    """Tests for metric registry."""

    def test_register_and_get(self):
        """Register and retrieve metric."""
        registry = MetricRegistry()
        registry.register("mse", MeanSquaredError)
        assert registry.get("mse") == MeanSquaredError, "Error should be raised or set"

    def test_get_unknown(self):
        """Get unknown metric returns None."""
        registry = MetricRegistry()
        assert registry.get("unknown") is None, "Condition must be true"

    def test_list_metrics(self):
        """List all registered metrics."""
        registry = MetricRegistry()
        registry.register("mse", MeanSquaredError)
        registry.register("mae", MeanAbsoluteError)
        assert set(registry.list_metrics()) == {"mse", "mae"}


# --- Metric Bounds Tests ---


class TestMetricBounds:
    """Tests for metric value bounds."""

    def test_accuracy_bounded_zero_one(self):
        """Accuracy should be in [0, 1]."""
        acc = Accuracy()
        result = acc.compute([0, 1, 0], [1, 1, 0])
        assert 0.0 <= result <= 1.0, "Result must not be empty"

    def test_mse_non_negative(self):
        """MSE should be non-negative."""
        mse = MeanSquaredError()
        result = mse.compute([1.0, 2.0], [3.0, 4.0])
        assert result >= 0.0, "result must be greater than zero"

    def test_mae_non_negative(self):
        """MAE should be non-negative."""
        mae = MeanAbsoluteError()
        result = mae.compute([1.0, 2.0], [3.0, 4.0])
        assert result >= 0.0, "result must be greater than zero"

    @given(
        st.lists(st.integers(min_value=0, max_value=1), min_size=1, max_size=50),
        st.lists(st.integers(min_value=0, max_value=1), min_size=1, max_size=50),
    )
    @settings(max_examples=30)
    def test_accuracy_bounds_property(self, preds: list[int], targets: list[int]):
        """Property: accuracy is always in [0, 1]."""
        if len(preds) != len(targets):
            return
        acc = Accuracy()
        result = acc.compute(preds, targets)
        assert 0.0 <= result <= 1.0, "Result must not be empty"


# --- Aggregation Tests ---


class TestMetricAggregation:
    """Tests for metric aggregation."""

    def test_mean_aggregation(self):
        """Mean aggregation should work correctly."""
        values = [0.8, 0.9, 0.85, 0.95]
        mean = sum(values) / len(values)
        assert abs(mean - 0.875) < 1e-9, "Condition must be true"

    def test_min_max_aggregation(self):
        """Min/max aggregation should work correctly."""
        values = [0.8, 0.9, 0.85, 0.95]
        assert min(values) == 0.8, "Value must be initialized"
        assert max(values) == 0.95, "Value must be initialized"

    def test_weighted_aggregation(self):
        """Weighted aggregation should work correctly."""
        values = [0.8, 0.9]
        weights = [1.0, 3.0]
        weighted_mean = sum(v * w for v, w in zip(values, weights)) / sum(weights)
        expected = (0.8 * 1.0 + 0.9 * 3.0) / 4.0
        assert abs(weighted_mean - expected) < 1e-9, "Condition must be true"
