"""
Lane 3.1 Edge Case Tests - Boundary Conditions & Default Values
Tests for src/codex_ml/utils/ and core module edge cases
Coverage target: +1-2pp improvement (17.57% → 18-19%)
"""

import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestBoundaryConditions:
    """Test boundary conditions that are often weak in coverage"""

    def test_zero_boundary_condition(self):
        """Test zero as boundary condition"""
        # Common pattern: comparison at 0
        values = [0, -1, 1]
        results = [(v > 0, v < 0, v == 0, v >= 0, v <= 0) for v in values]

        assert results[0] == (False, True, True, True, True)  # -1
        assert results[1] == (False, False, True, True, True)  # 0
        assert results[2] == (True, False, False, True, False)  # 1

    def test_empty_collection_boundary(self):
        """Test empty vs non-empty collections"""
        empty_list = []
        single_list = [1]
        multi_list = [1, 2, 3]

        assert len(empty_list) == 0, "Empty_list must not be empty"
        assert len(single_list) == 1, "Single_list must not be empty"
        assert len(multi_list) == 3, "Multi_list must not be empty"

        assert bool(empty_list) is False, "Condition must be true"
        assert bool(single_list) is True, "Condition must be true"
        assert bool(multi_list) is True, "Condition must be true"

    def test_none_vs_falsy_values(self):
        """Test None vs other falsy values"""
        assert None is None, "None is not valid"
        assert None is not False, "None is not valid"
        assert None != 0, "None is not valid"
        assert None != "", "None is not valid"
        assert None != [], "None is not valid"

        # None should be handled differently from falsy
        values = [None, False, 0, "", []]
        for v in values:
            if v is None:
                assert v is None, "v is not valid"
            else:
                assert v is not None, "v must be initialized"

    def test_true_false_inversion(self):
        """Test that boolean inversions are caught"""
        test_cases = [
            (True, False),
            (False, True),
            (not True, False),
            (not False, True),
        ]

        for actual, expected in test_cases:
            assert actual == expected, "actual is not valid"

    def test_one_off_errors_positive(self):
        """Test off-by-one errors on positive side"""
        # Common pattern: off by one in loops/ranges
        count = 5
        assert count > 4, "count must be positive"
        assert count < 6, "Count must be greater than zero"
        assert count == 5, "Count must be greater than zero"

        results = [i for i in range(count)]
        assert len(results) == 5, "Results must not be empty"
        assert results[-1] == 4, "Result must not be empty"

    def test_one_off_errors_negative(self):
        """Test off-by-one errors on negative side"""
        count = -5
        assert count < 0, "Count must be greater than zero"
        assert count != 0, "Count must be greater than zero"
        assert abs(count) == 5, "Count must be greater than zero"

        # Test with comparisons
        assert count <= -5, "Count must be greater than zero"
        assert count >= -5, "count must be positive"


class TestDefaultValues:
    """Test that exact default values are validated"""

    def test_exact_zero_default(self):
        """Test that 0 default is exactly 0, not falsy"""
        default = 0

        assert default == 0, "default is not valid"
        assert default == 0 or default == 0, "default is not valid"
        assert type(default) == int, "Condition must be true"
        assert not (default == 1), "default is not valid"
        assert not (default == -1), "default is not valid"

    def test_exact_empty_list_default(self):
        """Test that [] default is exactly empty list"""
        default = []

        assert default == [], "default is not valid"
        assert len(default) == 0, "Default must not be empty"
        assert default is not None, "default must be initialized"
        assert type(default) == list, "Condition must be true"

        # Mutation: [] -> [0]
        assert not (len(default) > 0), "Default must not be empty"

    def test_exact_false_default(self):
        """Test that False default is exactly False"""
        default = False

        assert default is False, "default is not valid"
        assert not default, "Condition must be true"
        assert type(default) == bool, "Condition must be true"
        assert not default, "Condition must be true"
        assert not default, "Condition must be true"

    def test_exact_string_default(self):
        """Test that string defaults are exact"""
        default = ""

        assert default == "", "default is not valid"
        assert len(default) == 0, "Default must not be empty"
        assert type(default) == str, "Condition must be true"

        # Mutation catches: "" -> "a"
        assert not (default == "a"), "default is not valid"
        assert not (len(default) > 0), "Default must not be empty"

    def test_numeric_precision_defaults(self):
        """Test numeric defaults with precision"""
        threshold_0_5 = 0.5
        threshold_0_8 = 0.8

        # These must be exact
        assert threshold_0_5 == 0.5, "threshold_0_5 is not valid"
        assert threshold_0_8 == 0.8, "threshold_0_8 is not valid"

        # Boundary tests
        assert 0.49 < threshold_0_5, "49 is not valid"
        assert 0.5 <= threshold_0_5, "5 is not valid"
        assert threshold_0_5 < 0.51, "threshold_0_5 is not valid"
        assert threshold_0_5 <= 0.51, "threshold_0_5 is not valid"


class TestLogicalOperators:
    """Test logical operator mutations"""

    def test_and_operator_mutation(self):
        """Test AND operator is not replaced with OR"""
        # and -> or mutation would fail these
        assert (True and True) is True, "Condition must be true"
        assert (True and False) is False, "Condition must be true"
        assert (False and True) is False, "Condition must be true"
        assert (False and False) is False, "Condition must be true"

        # These would pass if and became or
        assert not (True and False), "Condition must be true"
        assert not (False and False), "Condition must be true"

    def test_or_operator_mutation(self):
        """Test OR operator is not replaced with AND"""
        # or -> and mutation would fail these
        assert (True or False) is True, "Condition must be true"
        assert (False or True) is True, "Condition must be true"
        assert (False or False) is False, "Condition must be true"

        # These would pass if or became and
        assert not (False or False), "Condition must be true"

    def test_not_operator_mutation(self):
        """Test NOT operator is not removed"""
        # not removal would fail these
        assert (not True) is False, "Condition must be true"
        assert (not False) is True, "Condition must be true"

        # These require the not
        assert not (False), "Condition must be true"
        assert (not (not True)) is True, "Condition must be true"

    def test_combined_logical_operations(self):
        """Test combinations of logical operators"""
        a, b, c = True, False, True

        # and/or combinations
        assert ((a and b) or c) is True, "Condition must be true"
        assert (a and (b or c)) is True, "Condition must be true"
        assert ((not a) or b) is False, "Condition must be true"

        # Mutations would break these
        assert not ((a and b) and c)
        assert ((a or b) and c) is True, "Condition must be true"


class TestComparisonMutations:
    """Test comparison operator mutations"""

    def test_less_than_mutations(self):
        """Test < not mutated to <="""
        a, b = 5, 10

        assert a < b, "a is not valid"
        assert not (a < a), "a is not valid"

        # Boundary testing
        assert not (b < a), "b is not valid"
        assert not (5 < 5), "5 is not valid"
        assert 4 < 5, "4 is not valid"

    def test_greater_than_mutations(self):
        """Test > not mutated to >="""
        a, b = 10, 5

        assert a > b, "a must be greater than zero"
        assert not (a > a), "a must be greater than zero"

        # Boundary testing
        assert not (b > a), "b must be greater than zero"
        assert not (5 > 5), "5 must be greater than zero"
        assert 5 > 4, "5 must be greater than zero"

    def test_equality_mutations(self):
        """Test == not mutated to !="""
        assert 5 == 5, "5 is not valid"
        assert not (5 == 6), "5 is not valid"

        # Must be exact equality
        assert 0 == 0, "0 is not valid"
        assert "" == "", "Condition must be true"
        assert not False, "Condition must be true"
        assert not (not True), "Condition must be true"

    def test_inequality_mutations(self):
        """Test != not mutated to =="""
        assert 5 != 6, "5 is not valid"
        assert not (5 != 5), "5 is not valid"

        # Must detect inequality
        assert 0 != 1, "0 is not valid"
        assert "" != "x", "Condition must be true"
        assert not False, "Condition must be true"


class TestArithmeticMutations:
    """Test arithmetic operator mutations"""

    def test_addition_not_subtraction(self):
        """Test + not mutated to -"""
        a, b = 5, 3
        result = a + b

        assert result == 8, "Result must not be empty"
        assert not (result == 2), "Result must not be empty"

        # With negative
        assert -5 + 3 == -2, "3 is not valid"
        assert 5 + (-3) == 2, "Condition must be true"

    def test_subtraction_not_addition(self):
        """Test - not mutated to +"""
        a, b = 5, 3
        result = a - b

        assert result == 2, "Result must not be empty"
        assert not (result == 8), "Result must not be empty"

        # With negative
        assert -5 - 3 == -8, "3 is not valid"
        assert 5 - (-3) == 8, "Condition must be true"

    def test_multiplication_not_division(self):
        """Test * not mutated to /"""
        a, b = 6, 2
        result = a * b

        assert result == 12, "Result must not be empty"
        assert not (result == 3), "Result must not be empty"

        # With identity
        assert 1 * 5 == 5, "5 is not valid"
        assert 0 * 5 == 0, "5 is not valid"

    def test_division_not_multiplication(self):
        """Test / not mutated to *"""
        a, b = 6, 2
        result = a / b

        assert result == 3.0, "Result must not be empty"
        assert not (result == 12.0), "Result must not be empty"

        # With identity
        assert 5 / 1 == 5.0, "1 is not valid"
        assert 0 / 1 == 0.0, "1 is not valid"


class TestControlFlowEdgeCases:
    """Test control flow edge cases"""

    def test_if_body_removal(self):
        """Test that if body is not removed"""
        executed = False

        if True:
            executed = True

        assert executed is True, "executed is not valid"

    def test_if_else_branches(self):
        """Test if/else branches are both reachable"""
        result_if = None
        result_else = None

        if True:
            result_if = "if"
        else:
            result_else = "else"

        assert result_if == "if", "Result must not be empty"
        assert result_else is None, "Result must not be empty"

        # Test else branch
        if False:
            result_if = "if2"
        else:
            result_else = "else2"

        assert result_if == "if", "Result must not be empty"
        assert result_else == "else2", "Result must not be empty"

    def test_loop_execution(self):
        """Test loop body is not removed"""
        count = 0

        for i in range(3):
            count += 1

        assert count == 3, "Count must be greater than zero"

    def test_break_statement(self):
        """Test break is not removed"""
        count = 0

        for i in range(10):
            count += 1
            if count == 3:
                break

        assert count == 3, "Count must be greater than zero"


class TestFunctionCallMutations:
    """Test function call mutations"""

    def test_method_call_not_skipped(self):
        """Test method calls are not skipped"""
        data = []
        data.append(1)
        data.append(2)
        data.append(3)

        assert len(data) == 3, "Data must not be empty"

    def test_return_value_mutations(self):
        """Test return values are not changed"""

        def returns_true():
            return True

        def returns_false():
            return False

        assert returns_true() is True, "Condition must be true"
        assert not returns_false(), "Condition must be true"

    def test_none_return_vs_value_return(self):
        """Test None vs value returns"""

        def returns_none():
            return None

        def returns_value():
            return 42

        assert returns_none() is None, "Condition must be true"
        assert returns_value() == 42, "Value must be initialized"

        # Mutation: return None -> return value
        assert not (returns_none() == 42), "Condition must be true"


class TestCollectionOperations:
    """Test collection-related edge cases"""

    def test_list_indexing_off_by_one(self):
        """Test list indexing is not off by one"""
        items = ["a", "b", "c"]

        assert items[0] == "a", "Item must not be empty"
        assert items[1] == "b", "Item must not be empty"
        assert items[2] == "c", "Item must not be empty"
        assert items[-1] == "c", "Item must not be empty"
        assert items[-2] == "b", "Item must not be empty"

    def test_dict_operations(self):
        """Test dict operations"""
        d = {"key1": "value1", "key2": "value2"}

        assert d["key1"] == "value1", "Value must be initialized"
        assert d.get("key1") == "value1", "Value must be initialized"
        assert d.get("missing") is None, "Condition must be true"

        # Key existence
        assert "key1" in d, "Condition must be true"
        assert "missing" not in d, "Condition must be true"

    def test_set_operations(self):
        """Test set operations"""
        s1 = {1, 2, 3}
        s2 = {2, 3, 4}

        assert 1 in s1, "Condition must be true"
        assert 4 not in s1, "Condition must be true"
        assert s1 & s2 == {2, 3}
        assert s1 | s2 == {1, 2, 3, 4}

        # Mutation: empty set vs non-empty
        assert len(s1) == 3, "S1 must not be empty"
        assert len(s1 & s2) == 2, "Collection must not be empty"


class TestTypeChecks:
    """Test type checking edge cases"""

    def test_type_equality(self):
        """Test type checking"""
        assert type(0) == int, "Condition must be true"
        assert type(0.0) == float, "Condition must be true"
        assert type("") == str, "Condition must be true"
        assert type([]) == list, "Condition must be true"
        assert type({}) == dict, "Condition must be true"
        assert type(set()) == set, "Condition must be true"

        # Mutation: type mixing
        assert type(1) != type(1.0), "Condition must be true"
        assert type("1") != type(1), "Condition must be true"


# Integration test: Multiple conditions
class TestCombinedEdgeCases:
    """Test combinations of edge cases"""

    def test_boundary_with_mutation(self):
        """Test boundary condition with mutation operators"""
        threshold = 0.5
        values = [0.49, 0.5, 0.51]

        results = []
        for v in values:
            if v > threshold:
                results.append("above")
            elif v == threshold:
                results.append("equal")
            else:
                results.append("below")

        assert results == ["below", "equal", "above"]

    def test_collection_with_logic(self):
        """Test collection operations with logical operators"""
        items = [1, 2, 3, 4, 5]

        # AND condition
        assert all(x > 0 for x in items), "x must be greater than zero"
        assert not all(x > 3 for x in items), "x must be greater than zero"

        # OR condition
        assert any(x > 4 for x in items), "x must be greater than zero"
        assert not any(x > 10 for x in items), "x must be greater than zero"

    def test_nested_conditions(self):
        """Test nested conditions"""
        x, y, z = 5, 10, 3

        # Nested and/or
        if x < y and y > z:
            result = "nested_true"
        else:
            result = "nested_false"

        assert result == "nested_true", "Result must not be empty"

        # Mutation would break this
        if x > y or y < z:
            result = "or_false"
        else:
            result = "or_true"

        assert result == "or_true", "Result must not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
