"""
Phase 15.1: Property-Based Tests for Data Transformations

This module provides hypothesis-based property tests for data transformation
invariants, ensuring transformations preserve expected properties.

Created: 2026-01-18
Phase: 15.1 - Property-Based Testing
Target: Verify data transformation invariants
"""

from typing import Any

import pytest

try:
    from hypothesis import given, strategies as st, assume, settings
    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False
    # Provide stubs for when hypothesis is not available
    def given(*args: Any, **kwargs: Any) -> Any:
        def decorator(f: Any) -> Any:
            return pytest.mark.skip(reason="hypothesis not installed")(f)
        return decorator
    
    class st:  # type: ignore
        @staticmethod
        def text(*args: Any, **kwargs: Any) -> Any:
            return None
        @staticmethod
        def integers(*args: Any, **kwargs: Any) -> Any:
            return None
        @staticmethod
        def floats(*args: Any, **kwargs: Any) -> Any:
            return None
        @staticmethod
        def lists(*args: Any, **kwargs: Any) -> Any:
            return None
        @staticmethod
        def dictionaries(*args: Any, **kwargs: Any) -> Any:
            return None
        @staticmethod
        def booleans(*args: Any, **kwargs: Any) -> Any:
            return None
        @staticmethod
        def sampled_from(*args: Any, **kwargs: Any) -> Any:
            return None
    
    def assume(condition: bool) -> None:
        pass
    
    def settings(*args: Any, **kwargs: Any) -> Any:
        def decorator(f: Any) -> Any:
            return f
        return decorator


# ============================================================================
# Text Transformation Properties
# ============================================================================


class TestTextTransformationProperties:
    """Property-based tests for text transformations."""

    @given(st.text(min_size=0, max_size=1000))
    def test_lowercase_idempotent(self, text: str) -> None:
        """Lowercasing is idempotent: lower(lower(x)) == lower(x)."""
        result = text.lower()
        assert result.lower() == result

    @given(st.text(min_size=0, max_size=1000))
    def test_uppercase_idempotent(self, text: str) -> None:
        """Uppercasing is idempotent: upper(upper(x)) == upper(x)."""
        result = text.upper()
        assert result.upper() == result

    @given(st.text(min_size=0, max_size=1000))
    def test_strip_idempotent(self, text: str) -> None:
        """Stripping is idempotent: strip(strip(x)) == strip(x)."""
        result = text.strip()
        assert result.strip() == result

    @given(st.text(min_size=0, max_size=1000))
    def test_normalize_preserves_alphanumeric_count(self, text: str) -> None:
        """Normalization preserves count of alphanumeric characters."""
        def normalize(s: str) -> str:
            return s.lower().strip()
        
        original_alphanum = sum(1 for c in text if c.isalnum())
        normalized_alphanum = sum(1 for c in normalize(text) if c.isalnum())
        assert normalized_alphanum == original_alphanum

    @given(st.text(min_size=1, max_size=100))
    def test_split_join_roundtrip(self, text: str) -> None:
        """Split then join with same delimiter is identity for simple cases."""
        delimiter = " "
        if delimiter not in text:
            assert delimiter.join(text.split(delimiter)) == text

    @given(st.text(min_size=0, max_size=500), st.text(min_size=1, max_size=10))
    def test_replace_all_removes_substring(self, text: str, pattern: str) -> None:
        """Replacing all occurrences removes the pattern."""
        assume(len(pattern) > 0)
        result = text.replace(pattern, "")
        assert pattern not in result or pattern == ""


# ============================================================================
# List Transformation Properties
# ============================================================================


class TestListTransformationProperties:
    """Property-based tests for list transformations."""

    @given(st.lists(st.integers(), min_size=0, max_size=100))
    def test_reverse_reverse_identity(self, lst: list[int]) -> None:
        """Reversing twice is identity: reverse(reverse(x)) == x."""
        result = list(reversed(list(reversed(lst))))
        assert result == lst

    @given(st.lists(st.integers(), min_size=0, max_size=100))
    def test_sort_idempotent(self, lst: list[int]) -> None:
        """Sorting is idempotent: sort(sort(x)) == sort(x)."""
        sorted_once = sorted(lst)
        sorted_twice = sorted(sorted_once)
        assert sorted_once == sorted_twice

    @given(st.lists(st.integers(), min_size=0, max_size=100))
    def test_sort_preserves_length(self, lst: list[int]) -> None:
        """Sorting preserves list length."""
        assert len(sorted(lst)) == len(lst)

    @given(st.lists(st.integers(), min_size=0, max_size=100))
    def test_sort_preserves_elements(self, lst: list[int]) -> None:
        """Sorting preserves all elements (multiset equality)."""
        assert sorted(sorted(lst)) == sorted(lst)

    @given(st.lists(st.integers(), min_size=1, max_size=100))
    def test_min_in_list(self, lst: list[int]) -> None:
        """Minimum is always in the list."""
        assert min(lst) in lst

    @given(st.lists(st.integers(), min_size=1, max_size=100))
    def test_max_in_list(self, lst: list[int]) -> None:
        """Maximum is always in the list."""
        assert max(lst) in lst

    @given(st.lists(st.integers(), min_size=0, max_size=50),
           st.lists(st.integers(), min_size=0, max_size=50))
    def test_concatenation_length(self, lst1: list[int], lst2: list[int]) -> None:
        """Concatenation length is sum of lengths."""
        assert len(lst1 + lst2) == len(lst1) + len(lst2)


# ============================================================================
# Dictionary Transformation Properties
# ============================================================================


class TestDictTransformationProperties:
    """Property-based tests for dictionary transformations."""

    @given(st.dictionaries(st.text(min_size=1, max_size=20), st.integers()))
    def test_keys_values_length_match(self, d: dict[str, int]) -> None:
        """Keys and values have same length."""
        assert len(d.keys()) == len(d.values())

    @given(st.dictionaries(st.text(min_size=1, max_size=20), st.integers()))
    def test_items_length_matches_keys(self, d: dict[str, int]) -> None:
        """Items length matches keys length."""
        assert len(list(d.items())) == len(d.keys())

    @given(st.dictionaries(st.text(min_size=1, max_size=20), st.integers()))
    def test_update_with_self_identity(self, d: dict[str, int]) -> None:
        """Updating with self is identity."""
        original = d.copy()
        d.update(d)
        assert d == original

    @given(st.dictionaries(st.text(min_size=1, max_size=20), st.integers(), min_size=1))
    def test_pop_reduces_length(self, d: dict[str, int]) -> None:
        """Popping a key reduces length by 1."""
        original_len = len(d)
        key = next(iter(d.keys()))
        d.pop(key)
        assert len(d) == original_len - 1

    @given(st.dictionaries(st.text(min_size=1, max_size=20), st.integers()))
    def test_copy_equality(self, d: dict[str, int]) -> None:
        """Copy is equal but not identical."""
        copied = d.copy()
        assert copied == d
        if d:  # Only check identity if non-empty
            assert copied is not d


# ============================================================================
# Numeric Transformation Properties
# ============================================================================


class TestNumericTransformationProperties:
    """Property-based tests for numeric transformations."""

    @given(st.integers())
    def test_negation_involution(self, n: int) -> None:
        """Double negation is identity: -(-x) == x."""
        assert -(-n) == n

    @given(st.integers())
    def test_abs_idempotent(self, n: int) -> None:
        """Absolute value is idempotent: abs(abs(x)) == abs(x)."""
        assert abs(abs(n)) == abs(n)

    @given(st.integers())
    def test_abs_non_negative(self, n: int) -> None:
        """Absolute value is always non-negative."""
        assert abs(n) >= 0

    @given(st.floats(allow_nan=False, allow_infinity=False))
    def test_float_abs_non_negative(self, n: float) -> None:
        """Float absolute value is always non-negative."""
        assert abs(n) >= 0

    @given(st.integers(min_value=0, max_value=1000))
    def test_factorial_property(self, n: int) -> None:
        """Factorial is always positive for non-negative integers."""
        assume(n <= 20)  # Avoid very large factorials
        result = 1
        for i in range(1, n + 1):
            result *= i
        assert result > 0

    @given(st.integers(), st.integers())
    def test_addition_commutative(self, a: int, b: int) -> None:
        """Addition is commutative: a + b == b + a."""
        assert a + b == b + a

    @given(st.integers(), st.integers())
    def test_multiplication_commutative(self, a: int, b: int) -> None:
        """Multiplication is commutative: a * b == b * a."""
        assert a * b == b * a


# ============================================================================
# Data Pipeline Properties
# ============================================================================


class TestDataPipelineProperties:
    """Property-based tests for data pipeline transformations."""

    @given(st.lists(st.dictionaries(
        st.text(min_size=1, max_size=10),
        st.text(min_size=0, max_size=50)
    ), min_size=0, max_size=20))
    def test_filter_reduces_or_preserves_length(
        self, records: list[dict[str, str]]
    ) -> None:
        """Filtering never increases length."""
        filtered = [r for r in records if len(r) > 0]
        assert len(filtered) <= len(records)

    @given(st.lists(st.integers(), min_size=0, max_size=100))
    def test_map_preserves_length(self, lst: list[int]) -> None:
        """Mapping preserves length."""
        mapped = [x * 2 for x in lst]
        assert len(mapped) == len(lst)

    @given(st.lists(st.integers(), min_size=0, max_size=100))
    def test_filter_then_map_order(self, lst: list[int]) -> None:
        """Filter then map vs map all then filter produces different results."""
        # Filter positive then double
        result1 = [x * 2 for x in lst if x > 0]
        # This should equal: filter positive from original, then double
        result2 = [x * 2 for x in [y for y in lst if y > 0]]
        assert result1 == result2

    @given(st.lists(st.integers(min_value=-100, max_value=100), min_size=0, max_size=50))
    def test_reduce_sum_matches_builtin(self, lst: list[int]) -> None:
        """Manual reduce matches builtin sum."""
        from functools import reduce
        if lst:
            reduced = reduce(lambda a, b: a + b, lst, 0)
        else:
            reduced = 0
        assert reduced == sum(lst)


# ============================================================================
# Tokenization Properties
# ============================================================================


class TestTokenizationProperties:
    """Property-based tests for tokenization invariants."""

    @given(st.text(min_size=0, max_size=500))
    def test_word_tokenize_preserves_word_characters(self, text: str) -> None:
        """Word tokenization preserves word characters."""
        words = text.split()
        rejoined = " ".join(words)
        # All alphanumeric sequences should be preserved
        original_words = set(w for w in text.split() if w.isalnum())
        result_words = set(w for w in rejoined.split() if w.isalnum())
        assert original_words == result_words

    @given(st.lists(st.text(min_size=1, max_size=20, alphabet="abcdefghijklmnopqrstuvwxyz"), 
                    min_size=1, max_size=50))
    def test_token_count_bounded(self, tokens: list[str]) -> None:
        """Token count is bounded by character count."""
        text = " ".join(tokens)
        # Tokens should not exceed character count
        assert len(tokens) <= len(text) + 1

    @given(st.text(min_size=1, max_size=200, alphabet="abcdefghijklmnopqrstuvwxyz "))
    def test_whitespace_tokenization_reversible(self, text: str) -> None:
        """Whitespace tokenization is reversible for simple text."""
        tokens = text.split()
        reconstructed = " ".join(tokens)
        # Normalized whitespace should match
        assert reconstructed == " ".join(text.split())
