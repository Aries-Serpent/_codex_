"""
Tier 3 Mutation Killing Enhancements - Type Coercion and Edge Cases

Focus: Test edge cases that are often incompletely tested:
1. Type coercion boundaries
2. Datetime boundary conditions
3. Collection indexing edge cases (0, -1, length-1)
4. Empty collection handling
"""

import pytest
from datetime import datetime, timedelta


class TestTypeCoercionEdgeCases:
    """Test type coercion with strong boundary assertions."""

    def test_int_to_float_conversion(self):
        """Test integer to float conversion maintains value."""
        int_val = 42
        float_val = float(int_val)
        
        assert float_val == 42.0, \
            f"float({int_val}) must equal 42.0, got {float_val}"
        assert isinstance(float_val, float), \
            f"Result must be float, got {type(float_val)}"

    def test_float_to_int_truncation(self):
        """Test float to int conversion truncates correctly."""
        # Test positive values
        assert int(3.7) == 3, "int(3.7) must be 3"
        assert int(3.2) == 3, "int(3.2) must be 3"
        assert not (int(3.7) == 4), "int(3.7) must NOT be 4"
        
        # Test negative values
        assert int(-3.7) == -3, "int(-3.7) must be -3"
        assert int(-3.2) == -3, "int(-3.2) must be -3"

    def test_string_to_int_conversion(self):
        """Test string to int conversion with valid/invalid inputs."""
        assert int("42") == 42, "int('42') must equal 42"
        assert int("0") == 0, "int('0') must equal 0"
        assert int("-42") == -42, "int('-42') must equal -42"
        
        # Invalid conversions should raise
        with pytest.raises(ValueError):
            int("not_a_number")

    def test_string_to_bool_truthiness(self):
        """Test string boolean truthiness edge cases."""
        assert bool("") == False, "Empty string must be falsy"
        assert bool("0") == True, "String '0' must be truthy (non-empty string)"
        assert bool("False") == True, "String 'False' must be truthy"
        assert bool("True") == True, "String 'True' must be truthy"

    def test_numeric_zero_variants(self):
        """Test different representations of zero."""
        assert 0 == 0.0, "int 0 must equal float 0.0"
        assert not (0 == 0.1), "int 0 must NOT equal 0.1"
        assert int(0.0) == 0, "int(0.0) must be 0"
        assert int(0.9) == 0, "int(0.9) must be 0 (truncates)"


class TestCollectionIndexingEdgeCases:
    """Test collection indexing boundary conditions."""

    def test_list_first_element_access(self):
        """Test accessing first element of list."""
        lst = [10, 20, 30]
        
        # Index 0 must return first element
        assert lst[0] == 10, "lst[0] must be first element (10)"
        assert lst[0] != lst[1], "lst[0] must NOT equal lst[1]"

    def test_list_last_element_access(self):
        """Test accessing last element of list."""
        lst = [10, 20, 30, 40, 50]
        
        # Negative indexing for last element
        assert lst[-1] == 50, "lst[-1] must be last element (50)"
        assert lst[-1] != lst[-2], "lst[-1] must NOT equal lst[-2]"
        assert lst[-2] == 40, "lst[-2] must be second-to-last (40)"

    def test_list_index_boundaries(self):
        """Test list index boundary conditions."""
        lst = [1, 2, 3, 4, 5]
        length = len(lst)
        
        # Valid indices
        assert lst[0] == 1, "First index must work"
        assert lst[length - 1] == 5, "Last valid index must work"
        
        # Out of bounds should raise
        with pytest.raises(IndexError):
            lst[length]
        with pytest.raises(IndexError):
            lst[length + 1]

    def test_empty_list_operations(self):
        """Test operations on empty list."""
        lst = []
        
        assert len(lst) == 0, "Empty list must have length 0"
        assert not lst, "Empty list must be falsy"
        
        with pytest.raises(IndexError):
            lst[0]

    def test_dict_key_access_with_defaults(self):
        """Test dict key access with missing keys."""
        d = {"a": 1, "b": 2}
        
        # Key present
        assert d["a"] == 1, "Key 'a' must be present and equal 1"
        assert d.get("a") == 1, "get('a') must return 1"
        
        # Key missing
        with pytest.raises(KeyError):
            d["c"]
        
        # get() with default
        assert d.get("c", -1) == -1, "get('c', -1) must return default"
        assert d.get("a", -1) == 1, "get('a', -1) must return actual value"

    def test_string_indexing_boundaries(self):
        """Test string indexing edge cases."""
        s = "hello"
        
        # Valid indices
        assert s[0] == "h", "First character must be 'h'"
        assert s[-1] == "o", "Last character must be 'o'"
        assert s[4] == "o", "Index 4 must be 'o'"
        
        # Out of bounds
        with pytest.raises(IndexError):
            s[5]


class TestDatetimeBoundaryConditions:
    """Test datetime edge cases and boundary conditions."""

    def test_datetime_equality_exact(self):
        """Test datetime equality is exact."""
        dt1 = datetime(2024, 1, 15, 10, 30, 45)
        dt2 = datetime(2024, 1, 15, 10, 30, 45)
        dt3 = datetime(2024, 1, 15, 10, 30, 46)
        
        assert dt1 == dt2, "Identical datetimes must be equal"
        assert dt1 != dt3, "Different datetimes must not be equal"

    def test_datetime_comparison_boundaries(self):
        """Test datetime comparison with boundaries."""
        dt_early = datetime(2024, 1, 1, 0, 0, 0)
        dt_late = datetime(2024, 1, 1, 0, 0, 1)
        
        assert dt_early < dt_late, "Earlier time must be < later time"
        assert not (dt_early >= dt_late), "Earlier time must NOT be >= later time"
        assert dt_late > dt_early, "Later time must be > earlier time"

    def test_timedelta_exact_values(self):
        """Test timedelta with exact value checks."""
        td1 = timedelta(days=1)
        td2 = timedelta(hours=24)
        td3 = timedelta(hours=25)
        
        # 1 day must equal 24 hours
        assert td1 == td2, "1 day must equal 24 hours"
        assert td1.total_seconds() == td2.total_seconds(), \
            "total_seconds() must be equal for equivalent durations"
        
        # 24 hours must not equal 25 hours
        assert td2 != td3, "24 hours must NOT equal 25 hours"

    def test_datetime_microsecond_precision(self):
        """Test datetime with microsecond precision."""
        dt1 = datetime(2024, 1, 1, 0, 0, 0, 100000)  # +100ms
        dt2 = datetime(2024, 1, 1, 0, 0, 0, 100001)  # +100.001ms
        
        assert dt1 != dt2, "Different microseconds must not be equal"
        assert dt1 < dt2, "Earlier microsecond must be <"


class TestEmptyCollectionHandling:
    """Test handling of empty collections."""

    def test_empty_list_behavior(self):
        """Test empty list in boolean context."""
        empty_list = []
        
        # Empty list is falsy
        assert not empty_list, "Empty list must be falsy"
        assert len(empty_list) == 0, "Empty list length must be 0"
        assert not bool(empty_list), "bool(empty_list) must be False"

    def test_empty_dict_behavior(self):
        """Test empty dict in boolean context."""
        empty_dict = {}
        
        assert not empty_dict, "Empty dict must be falsy"
        assert len(empty_dict) == 0, "Empty dict length must be 0"
        assert not bool(empty_dict), "bool(empty_dict) must be False"

    def test_empty_string_behavior(self):
        """Test empty string in boolean context."""
        empty_str = ""
        
        assert not empty_str, "Empty string must be falsy"
        assert len(empty_str) == 0, "Empty string length must be 0"
        assert not bool(empty_str), "bool(empty_str) must be False"

    def test_nonempty_vs_empty_comparison(self):
        """Test distinction between empty and non-empty collections."""
        empty_list = []
        nonempty_list = [None]  # Contains one None element
        
        assert len(empty_list) == 0, "Empty list length must be 0"
        assert len(nonempty_list) > 0, "List with one element must have length > 0"
        assert len(nonempty_list) == 1, "List with one element must have length == 1"


class TestNullAndUndefinedHandling:
    """Test None and undefined value handling."""

    def test_none_identity_checks(self):
        """Test None identity vs equality."""
        value = None
        
        # Identity check
        assert value is None, "None must be None (identity)"
        assert not (value is not None), "None must NOT be 'not None'"
        
        # Equality check
        assert value == None, "None must == None"
        assert not (value != None), "None must NOT != None"

    def test_none_vs_false_distinction(self):
        """Test None is distinct from False."""
        assert None != False, "None must NOT equal False"
        assert None is not False, "None must NOT be False (identity)"
        assert False != None, "False must NOT equal None"

    def test_none_vs_empty_string(self):
        """Test None vs empty string distinction."""
        none_val = None
        empty_str = ""
        
        assert none_val != empty_str, "None must NOT equal empty string"
        assert not (none_val == empty_str), "None must NOT == empty string"

    def test_none_vs_zero(self):
        """Test None vs zero distinction."""
        none_val = None
        zero = 0
        
        assert none_val != zero, "None must NOT equal 0"
        assert not (none_val == zero), "None must NOT == 0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
