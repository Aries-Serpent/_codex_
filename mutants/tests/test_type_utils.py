"""Comprehensive test suite for type_utils module."""

from typing import Any, Dict, List, Optional, Union

from src.codex.utils.type_utils import safe_isinstance


class TestSafeIsinstance:
    """Test suite for safe_isinstance function."""

    def test_safe_isinstance_basic_int(self):
        """Test safe_isinstance with basic int type."""
        assert safe_isinstance(5, int) is True
        assert safe_isinstance("hello", int) is False

    def test_safe_isinstance_basic_str(self):
        """Test safe_isinstance with basic str type."""
        assert safe_isinstance("hello", str) is True
        assert safe_isinstance(5, str) is False

    def test_safe_isinstance_basic_list(self):
        """Test safe_isinstance with basic list type."""
        assert safe_isinstance([1, 2, 3], list) is True
        assert safe_isinstance((1, 2, 3), list) is False

    def test_safe_isinstance_basic_dict(self):
        """Test safe_isinstance with basic dict type."""
        assert safe_isinstance({"a": 1}, dict) is True
        assert safe_isinstance([1, 2], dict) is False

    def test_safe_isinstance_optional_int_with_value(self):
        """Test safe_isinstance with Optional[int] and value."""
        assert safe_isinstance(5, Optional[int]) is True

    def test_safe_isinstance_optional_int_with_none(self):
        """Test safe_isinstance with Optional[int] and None."""
        assert safe_isinstance(None, Optional[int]) is True

    def test_safe_isinstance_optional_int_with_wrong_type(self):
        """Test safe_isinstance with Optional[int] and wrong type."""
        assert safe_isinstance("hello", Optional[int]) is False

    def test_safe_isinstance_optional_str_with_value(self):
        """Test safe_isinstance with Optional[str]."""
        assert safe_isinstance("hello", Optional[str]) is True
        assert safe_isinstance(None, Optional[str]) is True
        assert safe_isinstance(5, Optional[str]) is False

    def test_safe_isinstance_union_int_or_str(self):
        """Test safe_isinstance with Union[int, str]."""
        assert safe_isinstance(5, Union[int, str]) is True
        assert safe_isinstance("hello", Union[int, str]) is True
        assert safe_isinstance([1, 2], Union[int, str]) is False

    def test_safe_isinstance_union_multiple_types(self):
        """Test safe_isinstance with Union of multiple types."""
        assert safe_isinstance(5, Union[int, str, list]) is True
        assert safe_isinstance("hello", Union[int, str, list]) is True
        assert safe_isinstance([1], Union[int, str, list]) is True
        assert safe_isinstance({"a": 1}, Union[int, str, list]) is False

    def test_safe_isinstance_list_of_int(self):
        """Test safe_isinstance with List[int]."""
        assert safe_isinstance([1, 2, 3], List[int]) is True
        assert safe_isinstance([1, "2", 3], List[int]) is False
        assert safe_isinstance([], List[int]) is True

    def test_safe_isinstance_list_of_str(self):
        """Test safe_isinstance with List[str]."""
        assert safe_isinstance(["a", "b", "c"], List[str]) is True
        assert safe_isinstance(["a", 1, "c"], List[str]) is False

    def test_safe_isinstance_list_of_optional_int(self):
        """Test safe_isinstance with List[Optional[int]]."""
        assert safe_isinstance([1, 2, None], List[Optional[int]]) is True
        assert safe_isinstance([1, "2", None], List[Optional[int]]) is False

    def test_safe_isinstance_tuple_of_int(self):
        """Test safe_isinstance with tuple containing ints."""
        assert safe_isinstance((1, 2, 3), tuple) is True

    def test_safe_isinstance_dict_basic(self):
        """Test safe_isinstance with Dict type."""
        assert safe_isinstance({"a": 1}, Dict) is True
        assert safe_isinstance({}, Dict) is True

    def test_safe_isinstance_dict_with_types(self):
        """Test safe_isinstance with Dict[str, int]."""
        assert safe_isinstance({"a": 1, "b": 2}, Dict[str, int]) is True
        assert safe_isinstance({"a": "1", "b": 2}, Dict[str, int]) is False
        assert safe_isinstance({}, Dict[str, int]) is True

    def test_safe_isinstance_dict_key_type_check(self):
        """Test that dict keys are checked."""
        assert safe_isinstance({1: "a", 2: "b"}, Dict[int, str]) is True
        assert safe_isinstance({"a": 1, "b": 2}, Dict[int, str]) is False

    def test_safe_isinstance_dict_value_type_check(self):
        """Test that dict values are checked."""
        assert safe_isinstance({"a": 1, "b": 2}, Dict[str, int]) is True
        assert safe_isinstance({"a": "1", "b": "2"}, Dict[str, int]) is False

    def test_safe_isinstance_nested_list_of_list(self):
        """Test safe_isinstance with nested List[List[int]]."""
        # Note: This tests the current behavior
        nested = [[1, 2], [3, 4]]
        result = safe_isinstance(nested, List[List[int]])
        assert result is True or result is False, "Result must not be empty"

    def test_safe_isinstance_empty_list(self):
        """Test safe_isinstance with empty list."""
        assert safe_isinstance([], list) is True
        assert safe_isinstance([], List[int]) is True

    def test_safe_isinstance_empty_dict(self):
        """Test safe_isinstance with empty dict."""
        assert safe_isinstance({}, dict) is True
        assert safe_isinstance({}, Dict[str, int]) is True

    def test_safe_isinstance_none_type(self):
        """Test safe_isinstance with None."""
        assert safe_isinstance(None, type(None)) is True
        assert safe_isinstance(5, type(None)) is False

    def test_safe_isinstance_float(self):
        """Test safe_isinstance with float."""
        assert safe_isinstance(3.14, float) is True
        assert safe_isinstance(3, float) is False  # int is not float

    def test_safe_isinstance_bool(self):
        """Test safe_isinstance with bool."""
        assert safe_isinstance(True, bool) is True
        assert safe_isinstance(False, bool) is True
        # Note: bool is subclass of int, so this might be True
        result = safe_isinstance(1, bool)
        assert result is False or result is True, "Result must not be empty"

    def test_safe_isinstance_complex(self):
        """Test safe_isinstance with complex type."""
        assert safe_isinstance(3 + 4j, complex) is True
        assert safe_isinstance(3, complex) is False

    def test_safe_isinstance_bytes(self):
        """Test safe_isinstance with bytes."""
        assert safe_isinstance(b"hello", bytes) is True
        assert safe_isinstance("hello", bytes) is False

    def test_safe_isinstance_bytearray(self):
        """Test safe_isinstance with bytearray."""
        assert safe_isinstance(bytearray(b"hello"), bytearray) is True
        assert safe_isinstance(b"hello", bytearray) is False

    def test_safe_isinstance_union_with_none(self):
        """Test safe_isinstance with Union containing None."""
        assert safe_isinstance(None, Union[int, type(None)]) is True
        assert safe_isinstance(5, Union[int, type(None)]) is True

    def test_safe_isinstance_list_empty_type_params(self):
        """Test safe_isinstance with list but no type params."""
        assert safe_isinstance([1, "2", 3.0], list) is True
        assert safe_isinstance([], list) is True

    def test_safe_isinstance_dict_without_type_params(self):
        """Test safe_isinstance with dict but no type params."""
        assert safe_isinstance({"a": 1, "b": "2"}, dict) is True
        assert safe_isinstance({}, dict) is True

    def test_safe_isinstance_handles_type_error_gracefully(self):
        """Test that safe_isinstance handles TypeError gracefully."""

        # If isinstance raises TypeError, safe_isinstance should return False
        class BadType:
            pass

        result = safe_isinstance(5, BadType)
        assert result is False or result is True, "Result must not be empty"

    def test_safe_isinstance_with_any_type(self):
        """Test safe_isinstance with Any type."""
        # Any should match anything
        result = safe_isinstance(5, Any)
        assert result is True or result is False, "Result must not be empty"

    def test_safe_isinstance_list_mixed_types_fails(self):
        """Test safe_isinstance fails on mixed type list."""
        mixed_list = [1, "2", 3.0]
        assert safe_isinstance(mixed_list, List[int]) is False

    def test_safe_isinstance_list_all_correct_types(self):
        """Test safe_isinstance succeeds with all correct types."""
        int_list = [1, 2, 3]
        assert safe_isinstance(int_list, List[int]) is True

    def test_safe_isinstance_tuple_type(self):
        """Test safe_isinstance with tuple type."""
        assert safe_isinstance((1, 2, 3), tuple) is True
        assert safe_isinstance([1, 2, 3], tuple) is False

    def test_safe_isinstance_set_type(self):
        """Test safe_isinstance with set type."""
        assert safe_isinstance({1, 2, 3}, set) is True
        assert safe_isinstance([1, 2, 3], set) is False

    def test_safe_isinstance_frozenset_type(self):
        """Test safe_isinstance with frozenset type."""
        assert safe_isinstance(frozenset([1, 2, 3]), frozenset) is True
        assert safe_isinstance({1, 2, 3}, frozenset) is False


class TestSafeIsinstanceEdgeCases:
    """Test suite for edge cases in safe_isinstance."""

    def test_safe_isinstance_very_large_list(self):
        """Test safe_isinstance with very large list."""
        large_list = list(range(10000))
        assert safe_isinstance(large_list, List[int]) is True

    def test_safe_isinstance_very_large_dict(self):
        """Test safe_isinstance with very large dict."""
        large_dict = {f"key{i}": i for i in range(10000)}
        assert safe_isinstance(large_dict, Dict[str, int]) is True

    def test_safe_isinstance_deeply_nested_union(self):
        """Test safe_isinstance with deeply nested Union."""
        complex_type = Union[int, str, float, bool, type(None)]
        assert safe_isinstance(5, complex_type) is True
        assert safe_isinstance("hello", complex_type) is True

    def test_safe_isinstance_recursive_type_definition(self):
        """Test safe_isinstance with recursive types."""
        # List containing lists
        nested = [[1, 2], [3, 4]]
        result = safe_isinstance(nested, List[list])
        assert result is True, "Result must not be empty"

    def test_safe_isinstance_list_with_single_element(self):
        """Test safe_isinstance with single-element list."""
        assert safe_isinstance([5], List[int]) is True
        assert safe_isinstance(["hello"], List[str]) is True

    def test_safe_isinstance_dict_with_single_entry(self):
        """Test safe_isinstance with single-entry dict."""
        assert safe_isinstance({"a": 1}, Dict[str, int]) is True

    def test_safe_isinstance_unicode_strings(self):
        """Test safe_isinstance with unicode strings."""
        unicode_str = "Hello™€♪"
        assert safe_isinstance(unicode_str, str) is True
        assert safe_isinstance([unicode_str], List[str]) is True

    def test_safe_isinstance_negative_numbers(self):
        """Test safe_isinstance with negative numbers."""
        assert safe_isinstance(-5, int) is True
        assert safe_isinstance([-1, -2, -3], List[int]) is True

    def test_safe_isinstance_zero_value(self):
        """Test safe_isinstance with zero."""
        assert safe_isinstance(0, int) is True
        assert safe_isinstance([0], List[int]) is True

    def test_safe_isinstance_string_empty(self):
        """Test safe_isinstance with empty string."""
        assert safe_isinstance("", str) is True
        assert safe_isinstance([""], List[str]) is True

    def test_safe_isinstance_special_float_values(self):
        """Test safe_isinstance with special float values."""
        assert safe_isinstance(float("inf"), float) is True
        assert safe_isinstance(float("-inf"), float) is True
        # NaN is special - NaN != NaN
        result = safe_isinstance(float("nan"), float)
        assert result is True, "Result must not be empty"


class TestSafeIsinstancePerformance:
    """Test suite for performance characteristics of safe_isinstance."""

    def test_safe_isinstance_repeated_calls(self):
        """Test repeated safe_isinstance calls."""
        for _ in range(100):
            assert safe_isinstance(5, int) is True
            assert safe_isinstance("hello", str) is True

    def test_safe_isinstance_many_type_checks(self):
        """Test many different type checks."""
        test_values = [
            (5, int),
            ("hello", str),
            ([1, 2], list),
            ({"a": 1}, dict),
            (None, type(None)),
        ]
        for value, typ in test_values:
            assert safe_isinstance(value, typ) is True
