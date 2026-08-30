"""Boundary condition tests 1."""

from __future__ import annotations


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max."""
    return max(min_val, min(value, max_val))


def test_clamp_within_range_1():
    """Test clamping value within range."""
    result = clamp(5.0, 0.0, 10.0)
    assert result == 5.0, "Result must not be empty"


def test_clamp_below_min_1():
    """Test clamping value below minimum."""
    result = clamp(-5.0, 0.0, 10.0)
    assert result == 0.0, "Result must not be empty"


def test_clamp_above_max_1():
    """Test clamping value above maximum."""
    result = clamp(15.0, 0.0, 10.0)
    assert result == 10.0, "Result must not be empty"


def test_clamp_at_boundaries_1():
    """Test clamping at exact boundaries."""
    assert clamp(0.0, 0.0, 10.0) == 0.0
    assert clamp(10.0, 0.0, 10.0) == 10.0


def test_clamp_zero_range_1():
    """Test clamping with zero range."""
    result = clamp(5.0, 5.0, 5.0)
    assert result == 5.0, "Result must not be empty"


def test_clamp_negative_range_1():
    """Test clamping with negative range."""
    result = clamp(-5.0, -10.0, 0.0)
    assert result == -5.0, "Result must not be empty"


def test_clamp_float_precision_1():
    """Test clamping with float precision."""
    result = clamp(3.14159, 0.0, 3.5)
    assert 3.14 < result < 3.15, "Result must not be empty"
