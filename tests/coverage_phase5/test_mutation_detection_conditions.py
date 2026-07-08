"""Tests for mutation detection - conditional replacement."""

from __future__ import annotations


def is_even(n: int) -> bool:
    return n % 2 == 0


def is_positive(n: int) -> bool:
    return n > 0


def is_in_range(n: int, min_val: int, max_val: int) -> bool:
    return min_val <= n <= max_val


def compare_values(a: int, b: int) -> str:
    if a > b:
        return "greater"
    elif a < b:
        return "less"
    else:
        return "equal"


class TestConditionalMutations:
    """Test conditionals for mutation detection."""

    def test_is_even_true(self):
        assert is_even(2) is True, "Condition must be true"
        assert is_even(0) is True, "Condition must be true"
        assert is_even(100) is True, "Condition must be true"

    def test_is_even_false(self):
        assert is_even(1) is False, "Condition must be true"
        assert is_even(3) is False, "Condition must be true"
        assert is_even(-1) is False, "Condition must be true"

    def test_is_positive_true(self):
        assert is_positive(1) is True, "Condition must be true"
        assert is_positive(100) is True, "Condition must be true"

    def test_is_positive_false(self):
        assert is_positive(0) is False, "Condition must be true"
        assert is_positive(-1) is False, "Condition must be true"

    def test_is_positive_boundary(self):
        assert is_positive(1) is True, "Condition must be true"
        assert is_positive(0) is False, "Condition must be true"

    def test_in_range_lower_bound(self):
        assert is_in_range(5, 5, 10) is True

    def test_in_range_upper_bound(self):
        assert is_in_range(10, 5, 10) is True

    def test_in_range_below_min(self):
        assert is_in_range(4, 5, 10) is False

    def test_in_range_above_max(self):
        assert is_in_range(11, 5, 10) is False

    def test_compare_greater(self):
        assert compare_values(10, 5) == "greater"

    def test_compare_less(self):
        assert compare_values(3, 7) == "less"

    def test_compare_equal(self):
        assert compare_values(5, 5) == "equal"
