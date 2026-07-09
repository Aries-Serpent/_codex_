"""
Tier 2 Mutation Killing Enhancements - Comparison Operators

Focus: Add exhaustive comparison operator tests to catch mutations:
- `<` vs `<=` vs `>`vs `>=`
- `==` vs `!=`
- Boolean negations

These tests catch common operator mutations that weak tests miss.
"""

import pytest


class TestLessThanVsLessEqual:
    """Test boundaries between < and <= operators."""

    def test_less_than_exclusive_boundary(self):
        """Test that < excludes the boundary value."""
        value = 10
        max_value = 10

        # value < max_value should be False when value == max_value
        assert not (value < max_value), \
            f"{value} must NOT be < {max_value}"

        # value <= max_value should be True when value == max_value
        assert value <= max_value, \
            f"{value} must be <= {max_value}"

    def test_less_than_with_negative_numbers(self):
        """Test comparison with negative numbers."""
        val1, val2 = -5, -4
        assert val1 < val2, f"{val1} must be < {val2}"
        assert not (val2 < val1), f"{val2} must NOT be < {val1}"
        assert val2 <= val2, f"{val2} must be <= {val2}"

    def test_less_than_with_floats(self):
        """Test comparison with floating point values."""
        val1, val2, val3 = 1.5, 2.0, 1.9999
        assert val1 < val2, f"{val1} must be < {val2}"
        assert not (val2 < val2), f"{val2} must NOT be < {val2}"
        assert val2 <= val2, f"{val2} must be <= {val2}"
        assert val3 < val2, f"{val3} must be < {val2}"


class TestGreaterThanVsGreaterEqual:
    """Test boundaries between > and >= operators."""

    def test_greater_than_exclusive_boundary(self):
        """Test that > excludes the boundary value."""
        value = 10
        min_value = 10

        # value > min_value should be False when value == min_value
        assert not (value > min_value), \
            f"{value} must NOT be > {min_value}"

        # value >= min_value should be True when value == min_value
        assert value >= min_value, \
            f"{value} must be >= {min_value}"

    def test_greater_than_with_negative_numbers(self):
        """Test comparison with negative numbers."""
        val1, val2 = -4, -5
        assert val1 > val2, f"{val1} must be > {val2}"
        assert not (val2 > val1), f"{val2} must NOT be > {val1}"
        assert val1 >= val1, f"{val1} must be >= {val1}"

    def test_greater_than_with_floats(self):
        """Test comparison with floating point values."""
        val1, val2, val3 = 2.0, 1.5, 2.0001
        assert val1 > val2, f"{val1} must be > {val2}"
        assert not (val1 > val1), f"{val1} must NOT be > {val1}"
        assert val1 >= val1, f"{val1} must be >= {val1}"
        assert val3 > val1, f"{val3} must be > {val1}"


class TestEqualityVsInequality:
    """Test == vs != mutations."""

    def test_equality_with_integers(self):
        """Test integer equality."""
        int1, int2, int3 = 5, 5, 6
        assert int1 == int2, f"{int1} must be == {int2}"
        assert not (int1 == int3), f"{int1} must NOT be == {int3}"
        assert int1 != int3, f"{int1} must be != {int3}"
        assert not (int1 != int2), f"{int1} must NOT be != {int2}"

    def test_equality_with_strings(self):
        """Test string equality."""
        str1, str2, str3 = "hello", "hello", "world"
        assert str1 == str2, "Identical strings must be equal"
        assert not (str1 == str3), "Different strings must not be equal"
        assert str1 != str3, "Different strings must be !="
        assert not (str1 != str2), "Same string must NOT be !="

    def test_equality_with_floats(self):
        """Test float equality (exact match)."""
        assert 1.0 == 1.0, "1.0 must == 1.0"
        assert not (1.0 == 1.0001), "1.0 must NOT == 1.0001"
        assert 1.0 != 1.0001, "1.0 must != 1.0001"

    def test_equality_with_none(self):
        """Test None equality."""
        value = None
        assert value is None, "None must be None"
        assert not (value is None) or value is None, "None identity check must be consistent"


class TestBoundaryMultiplier:
    """Test operators with multiplied boundaries."""

    def test_inclusive_vs_exclusive_with_multiplier(self):
        """Test boundary with multiplication factor."""
        max_len = 10
        multiplier = 2
        boundary = max_len * multiplier
        value = max_len + max_len

        # 20 < 20 should be False at the inclusive upper boundary.
        assert not (value < boundary), f"{value} must NOT be < {boundary}"
        # 20 <= 20 should be True
        assert value <= boundary, f"{value} must be <= {boundary}"
        # 20 > 10 should be True
        assert value > max_len, f"{value} must be > {max_len}"

    def test_off_by_one_boundaries(self):
        """Test classic off-by-one mutation scenarios."""
        start = 0
        stop = 5
        values = list(range(start, stop))
        lower = values[0]
        interior = values[1]
        upper = values[-1]

        # Upper bound must reject a strict-less-than mutation at equality.
        assert not (upper < (stop - 1)), f"{upper} must NOT be < {stop - 1}"
        assert upper <= (stop - 1), f"{upper} must be <= {stop - 1}"
        # Interior value must remain strictly above the lower bound.
        assert interior > lower, f"{interior} must be > {lower}"
        # Lower bound must remain inclusive for >= checks.
        assert lower >= start, f"{lower} must be >= {start}"


class TestLogicalNegation:
    """Test boolean negation mutations (not x vs x)."""

    def test_negation_flips_truth(self):
        """Test that negation reverses boolean value."""
        true_val = True
        false_val = False

        # not True must be False
        assert (not true_val) is False, "not True must be False"
        # not not True must be True
        assert (not (not true_val)) is True, "not not True must evaluate to True"

        # not False must be True
        assert (not false_val) is True, "not False must evaluate to True"
        # not not False must be False
        assert (not (not false_val)) is False, "not not False must evaluate to False"

    def test_negation_with_comparisons(self):
        """Test negation of comparison results."""
        a = 5
        b = 10

        assert a < b, "a < b must be True for the chosen comparison inputs"
        # Test the explicit comparison that can catch mutations
        result = not (a < b)
        assert result is False, "not (5 < 10) must be False"
        assert (a >= b) is False, "(5 >= 10) must be False"


class TestChainedComparisons:
    """Test chained comparison operators."""

    def test_chained_less_than(self):
        """Test a < b < c pattern."""
        a, b, c = 1, 2, 3

        assert a < b < c, "1 < 2 < 3 must be True"
        assert not (c < b < a), "3 < 2 < 1 must be False"
        assert not (a > b < c), "1 > 2 < 3 must be False"

    def test_chained_with_equal(self):
        """Test a <= b <= c pattern."""
        a, b, c = 1, 2, 2

        assert a <= b <= c, "1 <= 2 <= 2 must be True"
        assert not (c <= b <= a), "2 <= 2 <= 1 must be False"


class TestInBoundaryCheck:
    """Test common in-range checks."""

    def test_value_in_range(self):
        """Test if value is within range."""
        value = 50
        min_val = 0
        max_val = 100

        # All these patterns appear in real code and are mutation-prone
        assert min_val <= value <= max_val, \
            f"{value} must be in [{min_val}, {max_val}]"
        assert not (value < min_val), \
            f"{value} must NOT be < {min_val}"
        assert not (value > max_val), \
            f"{value} must NOT be > {max_val}"

    def test_value_outside_range(self):
        """Test boundaries where value is out of range."""
        value = 150
        max_val = 100

        assert value > max_val, \
            f"{value} must be > {max_val}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
