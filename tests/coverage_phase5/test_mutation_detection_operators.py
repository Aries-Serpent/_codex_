"""Tests for mutation detection - operator replacement."""

from __future__ import annotations

import pytest


def add(a: int, b: int) -> int:
    return a + b


def subtract(a: int, b: int) -> int:
    return a - b


def multiply(a: int, b: int) -> int:
    return a * b


def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Division by zero")
    return a / b


class TestArithmeticOperations:
    """Test arithmetic operations for mutation detection."""

    def test_add_positive_numbers(self):
        assert add(2, 3) == 5

    def test_add_with_zero(self):
        assert add(5, 0) == 5

    def test_add_negative_numbers(self):
        assert add(-2, -3) == -5

    def test_subtract_positive(self):
        assert subtract(5, 3) == 2

    def test_subtract_with_zero(self):
        assert subtract(5, 0) == 5

    def test_subtract_negative(self):
        assert subtract(-5, -3) == -2

    def test_multiply_positive(self):
        assert multiply(3, 4) == 12

    def test_multiply_by_zero(self):
        assert multiply(5, 0) == 0

    def test_multiply_negative(self):
        assert multiply(-3, 4) == -12

    def test_divide_positive(self):
        assert divide(10.0, 2.0) == 5.0

    def test_divide_by_one(self):
        assert divide(7.0, 1.0) == 7.0

    def test_divide_by_zero_raises(self):
        with pytest.raises(ValueError):
            divide(10.0, 0.0)

    def test_division_precision(self):
        result = divide(1.0, 3.0)
        assert 0.33 < result < 0.34, "Result must not be empty"
