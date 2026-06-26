"""
Test Base Metric Interface

Unit tests for the BaseMetric abstract base class.
"""

from __future__ import annotations

from typing import Any

import pytest

from codex_ml.metrics.base import BaseMetric


class ConcreteMetric(BaseMetric):
    """Concrete implementation of BaseMetric for testing."""

    def __init__(self) -> None:
        self._value = 0.0
        self._count = 0

    def update(self, preds: Any, labels: Any, **kwargs) -> None:
        """Accumulate sum of predictions."""
        if hasattr(preds, "__iter__"):
            self._value += sum(float(p) for p in preds)
            self._count += len(preds)
        else:
            self._value += float(preds)
            self._count += 1

    def compute(self) -> float:
        """Return average."""
        if self._count == 0:
            return 0.0
        return self._value / self._count

    def reset(self) -> None:
        """Reset state."""
        self._value = 0.0
        self._count = 0


class TestBaseMetric:
    """Tests for BaseMetric abstract class."""

    def test_cannot_instantiate_abstract(self) -> None:
        """BaseMetric should not be directly instantiable."""
        with pytest.raises(TypeError):
            BaseMetric()  # type: ignore[abstract]

    def test_concrete_implementation_works(self) -> None:
        """Concrete subclass should work correctly."""
        metric = ConcreteMetric()

        metric.update([1.0, 2.0, 3.0], None)
        assert metric.compute() == 2.0, "Condition must be true"

    def test_reset_clears_state(self) -> None:
        """Reset should clear accumulated state."""
        metric = ConcreteMetric()
        metric.update([1.0, 2.0], None)
        metric.reset()
        assert metric.compute() == 0.0, "Condition must be true"

    def test_meta_returns_class_name(self) -> None:
        """Meta should return dictionary with class name."""
        metric = ConcreteMetric()
        meta = metric.meta()
        assert isinstance(meta, dict)
        assert meta["name"] == "ConcreteMetric", "Condition must be true"

    def test_multiple_updates(self) -> None:
        """Multiple updates should accumulate correctly."""
        metric = ConcreteMetric()

        metric.update([1.0, 2.0], None)  # sum=3, count=2
        metric.update([3.0, 4.0], None)  # sum=10, count=4

        assert metric.compute() == 2.5, "Condition must be true"

    def test_single_value_update(self) -> None:
        """Single scalar value update should work."""
        metric = ConcreteMetric()
        metric.update(5.0, None)
        assert metric.compute() == 5.0, "Condition must be true"

    def test_kwargs_are_passed(self) -> None:
        """Update should accept arbitrary kwargs."""

        class KwargsMetric(BaseMetric):
            def __init__(self) -> None:
                self.received_kwargs: dict = {}

            def update(self, preds: Any, labels: Any, **kwargs) -> None:
                self.received_kwargs = kwargs

            def compute(self) -> Any:
                return self.received_kwargs

            def reset(self) -> None:
                self.received_kwargs = {}

        metric = KwargsMetric()
        metric.update(None, None, loss=1.0, step=5)
        result = metric.compute()
        assert result["loss"] == 1.0, "Result must not be empty"
        assert result["step"] == 5, "Result must not be empty"


class TestMetricInterface:
    """Tests to ensure proper interface compliance."""

    def test_required_methods_exist(self) -> None:
        """Verify BaseMetric requires update, compute, reset."""
        required_methods = ["update", "compute", "reset"]
        for method in required_methods:
            assert hasattr(BaseMetric, method)

    def test_meta_method_exists(self) -> None:
        """Verify meta method has default implementation."""
        metric = ConcreteMetric()
        assert hasattr(metric, "meta")
        assert callable(metric.meta), "Condition must be true"

    def test_incomplete_subclass_raises(self) -> None:
        """Subclass missing required methods should raise TypeError."""

        class IncompleteMetric(BaseMetric):
            def update(self, preds: Any, labels: Any, **kwargs) -> None:
                pass

            # Missing compute and reset

        with pytest.raises(TypeError):
            IncompleteMetric()  # type: ignore[abstract]
