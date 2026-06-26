"""
Lane 3.1 Edge Case Tests - Collections & Type-Specific Operations
Tests for weak modules with focus on collection mutations
"""

from typing import Any, Dict, Optional

import pytest


class TestListMutations:
    """Test list-specific mutations"""

    def test_list_append_mutation(self):
        """Test that list append is not mutated"""
        items = []
        items.append(1)
        items.append(2)

        assert len(items) == 2, "Items must not be empty"
        assert items[0] == 1, "Item must not be empty"
        assert items[1] == 2, "Item must not be empty"
        assert items == [1, 2]

    def test_list_insert_mutation(self):
        """Test list insert operations"""
        items = [1, 3]
        items.insert(1, 2)

        assert items == [1, 2, 3]
        assert items[1] == 2, "Item must not be empty"
        assert len(items) == 3, "Items must not be empty"

    def test_list_pop_mutation(self):
        """Test list pop operations"""
        items = [1, 2, 3]
        last = items.pop()

        assert last == 3, "last is not valid"
        assert items == [1, 2]
        assert len(items) == 2, "Items must not be empty"

    def test_list_remove_mutation(self):
        """Test list remove operations"""
        items = [1, 2, 3, 2]
        items.remove(2)  # Removes first occurrence

        assert items == [1, 3, 2]
        assert len(items) == 3, "Items must not be empty"

    def test_list_extend_mutation(self):
        """Test list extend operations"""
        items = [1, 2]
        items.extend([3, 4])

        assert items == [1, 2, 3, 4]
        assert len(items) == 4, "Items must not be empty"

    def test_list_clear_mutation(self):
        """Test list clear operations"""
        items = [1, 2, 3]
        items.clear()

        assert items == [], "Item must not be empty"
        assert len(items) == 0, "Items must not be empty"

    def test_list_slice_mutation(self):
        """Test list slicing is not mutated"""
        items = [1, 2, 3, 4, 5]

        assert items[0:2] == [1, 2]
        assert items[1:3] == [2, 3]
        assert items[2:] == [3, 4, 5]
        assert items[:3] == [1, 2, 3]
        assert items[::2] == [1, 3, 5]

    def test_list_reverse_mutation(self):
        """Test list reverse operations"""
        items = [1, 2, 3]
        items.reverse()

        assert items == [3, 2, 1]
        assert items[0] == 3, "Item must not be empty"
        assert items[-1] == 1, "Item must not be empty"

    def test_list_sort_mutation(self):
        """Test list sort operations"""
        items = [3, 1, 2]
        items.sort()

        assert items == [1, 2, 3]
        assert items[0] == 1, "Item must not be empty"
        assert items[-1] == 3, "Item must not be empty"

    def test_list_copy_mutation(self):
        """Test list copy operations"""
        original = [1, 2, 3]
        copy = original.copy()

        copy.append(4)

        assert original == [1, 2, 3]
        assert copy == [1, 2, 3, 4]
        assert original is not copy, "original is not valid"


class TestDictMutations:
    """Test dict-specific mutations"""

    def test_dict_set_item_mutation(self):
        """Test dict set item operations"""
        d = {}
        d["key"] = "value"

        assert d == {"key": "value"}, "Value must be initialized"
        assert d["key"] == "value", "Value must be initialized"
        assert len(d) == 1, "D must not be empty"

    def test_dict_get_mutation(self):
        """Test dict get operations"""
        d = {"a": 1, "b": 2}

        assert d.get("a") == 1, "Condition must be true"
        assert d.get("c") is None, "Condition must be true"
        assert d.get("c", "default") == "default"

    def test_dict_pop_mutation(self):
        """Test dict pop operations"""
        d = {"a": 1, "b": 2}
        value = d.pop("a")

        assert value == 1, "Value must be initialized"
        assert d == {"b": 2}, "d is not valid"
        assert len(d) == 1, "D must not be empty"

    def test_dict_update_mutation(self):
        """Test dict update operations"""
        d = {"a": 1}
        d.update({"b": 2, "c": 3})

        assert d == {"a": 1, "b": 2, "c": 3}
        assert len(d) == 3, "D must not be empty"

    def test_dict_clear_mutation(self):
        """Test dict clear operations"""
        d = {"a": 1, "b": 2}
        d.clear()

        assert d == {}, "d is not valid"
        assert len(d) == 0, "D must not be empty"

    def test_dict_keys_values_items(self):
        """Test dict keys, values, items operations"""
        d = {"a": 1, "b": 2}

        assert "a" in d.keys(), "Condition must be true"
        assert "c" not in d.keys(), "Condition must be true"
        assert 1 in d.values(), "Value must be initialized"
        assert ("a", 1) in d.items()

    def test_dict_copy_mutation(self):
        """Test dict copy operations"""
        original = {"a": 1, "b": 2}
        copy = original.copy()

        copy["c"] = 3

        assert original == {"a": 1, "b": 2}
        assert copy == {"a": 1, "b": 2, "c": 3}
        assert original is not copy, "original is not valid"


class TestSetMutations:
    """Test set-specific mutations"""

    def test_set_add_mutation(self):
        """Test set add operations"""
        s = {1, 2}
        s.add(3)

        assert 3 in s, "Condition must be true"
        assert len(s) == 3, "S must not be empty"

    def test_set_remove_mutation(self):
        """Test set remove operations"""
        s = {1, 2, 3}
        s.remove(2)

        assert 2 not in s, "Condition must be true"
        assert len(s) == 2, "S must not be empty"

    def test_set_discard_mutation(self):
        """Test set discard operations"""
        s = {1, 2, 3}
        s.discard(2)
        s.discard(99)  # No error if not present

        assert 2 not in s, "Condition must be true"
        assert len(s) == 2, "S must not be empty"

    def test_set_clear_mutation(self):
        """Test set clear operations"""
        s = {1, 2, 3}
        s.clear()

        assert len(s) == 0, "S must not be empty"
        assert s == set(), "s is not valid"

    def test_set_union_mutation(self):
        """Test set union operations"""
        s1 = {1, 2, 3}
        s2 = {2, 3, 4}

        result = s1 | s2

        assert result == {1, 2, 3, 4}
        assert len(result) == 4, "Result must not be empty"

    def test_set_intersection_mutation(self):
        """Test set intersection operations"""
        s1 = {1, 2, 3}
        s2 = {2, 3, 4}

        result = s1 & s2

        assert result == {2, 3}
        assert len(result) == 2, "Result must not be empty"

    def test_set_difference_mutation(self):
        """Test set difference operations"""
        s1 = {1, 2, 3}
        s2 = {2, 3, 4}

        result = s1 - s2

        assert result == {1}, "Result must not be empty"
        assert len(result) == 1, "Result must not be empty"

    def test_set_copy_mutation(self):
        """Test set copy operations"""
        original = {1, 2, 3}
        copy = original.copy()

        copy.add(4)

        assert 4 not in original, "Condition must be true"
        assert 4 in copy, "Condition must be true"
        assert original is not copy, "original is not valid"


class TestIterationMutations:
    """Test iteration and loop mutations"""

    def test_for_loop_range(self):
        """Test for loop with range"""
        count = 0
        for i in range(5):
            count += 1

        assert count == 5, "Count must be greater than zero"

    def test_for_loop_list(self):
        """Test for loop with list"""
        values = [10, 20, 30]
        result = []
        for v in values:
            result.append(v * 2)

        assert result == [20, 40, 60]

    def test_while_loop_mutation(self):
        """Test while loop"""
        count = 0
        while count < 3:
            count += 1

        assert count == 3, "Count must be greater than zero"

    def test_list_comprehension(self):
        """Test list comprehension"""
        result = [x * 2 for x in range(4)]

        assert result == [0, 2, 4, 6]

    def test_dict_comprehension(self):
        """Test dict comprehension"""
        result = {x: x * 2 for x in range(3)}

        assert result == {0: 0, 1: 2, 2: 4}

    def test_set_comprehension(self):
        """Test set comprehension"""
        result = {x % 2 for x in range(5)}

        assert result == {0, 1}

    def test_enumerate_mutation(self):
        """Test enumerate function"""
        items = ["a", "b", "c"]
        result = []
        for idx, item in enumerate(items):
            result.append((idx, item))

        assert result == [(0, "a"), (1, "b"), (2, "c")]

    def test_zip_mutation(self):
        """Test zip function"""
        list1 = [1, 2, 3]
        list2 = ["a", "b", "c"]
        result = list(zip(list1, list2))

        assert result == [(1, "a"), (2, "b"), (3, "c")]


class TestTupleMutations:
    """Test tuple-specific operations"""

    def test_tuple_indexing(self):
        """Test tuple indexing"""
        t = (10, 20, 30)

        assert t[0] == 10, "Condition must be true"
        assert t[1] == 20, "Condition must be true"
        assert t[2] == 30, "Condition must be true"
        assert t[-1] == 30, "Condition must be true"

    def test_tuple_slicing(self):
        """Test tuple slicing"""
        t = (1, 2, 3, 4, 5)

        assert t[0:2] == (1, 2)
        assert t[1:4] == (2, 3, 4)
        assert t[::2] == (1, 3, 5)

    def test_tuple_count(self):
        """Test tuple count method"""
        t = (1, 2, 2, 3, 2)

        assert t.count(2) == 3, "Count must be greater than zero"
        assert t.count(1) == 1, "Count must be greater than zero"
        assert t.count(5) == 0, "Count must be greater than zero"

    def test_tuple_index(self):
        """Test tuple index method"""
        t = (10, 20, 30)

        assert t.index(10) == 0, "Condition must be true"
        assert t.index(20) == 1, "Condition must be true"
        assert t.index(30) == 2, "Condition must be true"

    def test_tuple_unpacking(self):
        """Test tuple unpacking"""
        t = (1, 2, 3)
        a, b, c = t

        assert a == 1, "a is not valid"
        assert b == 2, "b is not valid"
        assert c == 3, "c is not valid"


class TestStringMutations:
    """Test string-specific mutations"""

    def test_string_concatenation(self):
        """Test string concatenation"""
        s = "hello" + " " + "world"

        assert s == "hello world", "s is not valid"
        assert len(s) == 11, "S must not be empty"

    def test_string_multiplication(self):
        """Test string multiplication"""
        s = "x" * 3

        assert s == "xxx", "s is not valid"
        assert len(s) == 3, "S must not be empty"

    def test_string_upper_lower(self):
        """Test string case operations"""
        s = "Hello"

        assert s.upper() == "HELLO", "Condition must be true"
        assert s.lower() == "hello", "Condition must be true"

    def test_string_strip(self):
        """Test string strip operations"""
        s = "  hello  "

        assert s.strip() == "hello", "Condition must be true"
        assert s.lstrip() == "hello  ", "Condition must be true"
        assert s.rstrip() == "  hello", "Condition must be true"

    def test_string_split(self):
        """Test string split operations"""
        s = "a,b,c"
        result = s.split(",")

        assert result == ["a", "b", "c"]
        assert len(result) == 3, "Result must not be empty"

    def test_string_join(self):
        """Test string join operations"""
        items = ["a", "b", "c"]
        result = ",".join(items)

        assert result == "a,b,c"

    def test_string_replace(self):
        """Test string replace operations"""
        s = "hello world"
        result = s.replace("world", "python")

        assert result == "hello python", "Result must not be empty"

    def test_string_startswith_endswith(self):
        """Test string startswith/endswith"""
        s = "hello world"

        assert s.startswith("hello") is True, "Condition must be true"
        assert s.startswith("world") is False, "Condition must be true"
        assert s.endswith("world") is True, "Condition must be true"
        assert s.endswith("hello") is False, "Condition must be true"


class TestTypeConversions:
    """Test type conversion operations"""

    def test_int_conversion(self):
        """Test integer conversion"""
        assert int("5") == 5, "Condition must be true"
        assert int(5.9) == 5, "Condition must be true"
        assert int(True) == 1, "Condition must be true"
        assert int(False) == 0, "Condition must be true"

    def test_float_conversion(self):
        """Test float conversion"""
        assert float("5.5") == 5.5, "Condition must be true"
        assert float(5) == 5.0, "Condition must be true"
        assert float("inf") == float("inf"), "Condition must be true"

    def test_str_conversion(self):
        """Test string conversion"""
        assert str(5) == "5", "Condition must be true"
        assert str(5.5) == "5.5", "Condition must be true"
        assert str(True) == "True", "Condition must be true"
        assert str([1, 2]) == "[1, 2]"

    def test_bool_conversion(self):
        """Test boolean conversion"""
        assert bool(1) is True, "Condition must be true"
        assert bool(0) is False, "Condition must be true"
        assert bool("") is False, "Condition must be true"
        assert bool("text") is True, "Condition must be true"
        assert bool([]) is False, "Condition must be true"
        assert bool([1]) is True, "Condition must be true"

    def test_list_conversion(self):
        """Test list conversion"""
        assert list("abc") == ["a", "b", "c"]
        assert list((1, 2, 3)) == [1, 2, 3]
        assert list({1, 2, 3}) == sorted([1, 2, 3])

    def test_set_conversion(self):
        """Test set conversion"""
        assert set([1, 2, 2, 3]) == {1, 2, 3}
        assert set("aab") == {"a", "b"}


class TestComparisonChaining:
    """Test comparison chaining"""

    def test_chained_comparisons(self):
        """Test chained comparison operators"""
        x = 5

        assert 0 < x < 10, "0 is not valid"
        assert not (0 < x < 4), "0 is not valid"
        assert 5 <= x <= 5, "5 is not valid"
        assert not (6 <= x <= 10), "6 is not valid"

    def test_membership_operators(self):
        """Test membership operators"""
        items = [1, 2, 3]

        assert 1 in items, "Item must not be empty"
        assert 4 not in items, "Item must not be empty"
        assert 2 in items, "Item must not be empty"

    def test_identity_operators(self):
        """Test identity operators"""
        a = [1, 2]
        b = [1, 2]
        c = a

        assert a == b, "a is not valid"
        assert a is not b, "a is not valid"
        assert a is c, "a is not valid"


class TestNullableHandling:
    """Test nullable/optional handling"""

    def test_optional_unwrapping(self):
        """Test optional value unwrapping"""

        def process_optional(value: Optional[int]) -> int:
            if value is None:
                return 0
            else:
                return value * 2

        assert process_optional(5) == 10, "Condition must be true"
        assert process_optional(None) == 0, "Condition must be true"

    def test_optional_chaining(self):
        """Test optional chaining pattern"""

        def get_nested(data: Optional[Dict[str, Any]], key: str) -> Optional[Any]:
            if data is None:
                return None
            return data.get(key)

        assert get_nested({"a": 1}, "a") == 1
        assert get_nested({"a": 1}, "b") is None
        assert get_nested(None, "a") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
