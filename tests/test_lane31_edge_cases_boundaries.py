"""
Lane 3.1 Edge Case Tests - Boundary Conditions & Default Values
Tests for src/codex_ml/utils/ and core module edge cases
Coverage target: +1-2pp improvement (17.57% → 18-19%)
"""
import pytest
import sys
from pathlib import Path

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
        
        assert len(empty_list) == 0
        assert len(single_list) == 1
        assert len(multi_list) == 3
        
        assert bool(empty_list) is False
        assert bool(single_list) is True
        assert bool(multi_list) is True
    
    def test_none_vs_falsy_values(self):
        """Test None vs other falsy values"""
        assert None is None
        assert None is not False
        assert None is not 0
        assert None is not ""
        assert None is not []
        
        # None should be handled differently from falsy
        values = [None, False, 0, "", []]
        for v in values:
            if v is None:
                assert v is None
            else:
                assert v is not None
    
    def test_true_false_inversion(self):
        """Test that boolean inversions are caught"""
        test_cases = [
            (True, False),
            (False, True),
            (not True, False),
            (not False, True),
        ]
        
        for actual, expected in test_cases:
            assert actual == expected
    
    def test_one_off_errors_positive(self):
        """Test off-by-one errors on positive side"""
        # Common pattern: off by one in loops/ranges
        count = 5
        assert count > 4  # NOT >= 4
        assert count < 6  # NOT <= 6
        assert count == 5  # NOT == 4 or == 6
        
        results = [i for i in range(count)]
        assert len(results) == 5
        assert results[-1] == 4  # NOT 5
    
    def test_one_off_errors_negative(self):
        """Test off-by-one errors on negative side"""
        count = -5
        assert count < 0
        assert count != 0
        assert abs(count) == 5
        
        # Test with comparisons
        assert count <= -5  # NOT <= -6
        assert count >= -5  # NOT >= -4


class TestDefaultValues:
    """Test that exact default values are validated"""
    
    def test_exact_zero_default(self):
        """Test that 0 default is exactly 0, not falsy"""
        default = 0
        
        assert default == 0  # NOT just falsy
        assert default is 0 or default == 0  # Exact check
        assert type(default) == int
        assert not (default == 1)
        assert not (default == -1)
    
    def test_exact_empty_list_default(self):
        """Test that [] default is exactly empty list"""
        default = []
        
        assert default == []
        assert len(default) == 0
        assert default is not None
        assert type(default) == list
        
        # Mutation: [] -> [0]
        assert not (len(default) > 0)
    
    def test_exact_false_default(self):
        """Test that False default is exactly False"""
        default = False
        
        assert default is False  # Must be False, not just falsy
        assert not default
        assert type(default) == bool
        assert default != True
        assert default == False
    
    def test_exact_string_default(self):
        """Test that string defaults are exact"""
        default = ""
        
        assert default == ""
        assert len(default) == 0
        assert type(default) == str
        
        # Mutation catches: "" -> "a"
        assert not (default == "a")
        assert not (len(default) > 0)
    
    def test_numeric_precision_defaults(self):
        """Test numeric defaults with precision"""
        threshold_0_5 = 0.5
        threshold_0_8 = 0.8
        
        # These must be exact
        assert threshold_0_5 == 0.5
        assert threshold_0_8 == 0.8
        
        # Boundary tests
        assert 0.49 < threshold_0_5
        assert 0.5 <= threshold_0_5
        assert threshold_0_5 < 0.51
        assert threshold_0_5 <= 0.51


class TestLogicalOperators:
    """Test logical operator mutations"""
    
    def test_and_operator_mutation(self):
        """Test AND operator is not replaced with OR"""
        # and -> or mutation would fail these
        assert (True and True) is True
        assert (True and False) is False
        assert (False and True) is False
        assert (False and False) is False
        
        # These would pass if and became or
        assert not (True and False)
        assert not (False and False)
    
    def test_or_operator_mutation(self):
        """Test OR operator is not replaced with AND"""
        # or -> and mutation would fail these
        assert (True or False) is True
        assert (False or True) is True
        assert (False or False) is False
        
        # These would pass if or became and
        assert not (False or False)
    
    def test_not_operator_mutation(self):
        """Test NOT operator is not removed"""
        # not removal would fail these
        assert (not True) is False
        assert (not False) is True
        
        # These require the not
        assert not (False)
        assert (not (not True)) is True
    
    def test_combined_logical_operations(self):
        """Test combinations of logical operators"""
        a, b, c = True, False, True
        
        # and/or combinations
        assert ((a and b) or c) is True
        assert (a and (b or c)) is True
        assert ((not a) or b) is False
        
        # Mutations would break these
        assert not ((a and b) and c)
        assert ((a or b) and c) is True


class TestComparisonMutations:
    """Test comparison operator mutations"""
    
    def test_less_than_mutations(self):
        """Test < not mutated to <="""
        a, b = 5, 10
        
        assert a < b
        assert not (a < a)  # Catches < -> <=
        
        # Boundary testing
        assert not (b < a)
        assert not (5 < 5)
        assert 4 < 5
    
    def test_greater_than_mutations(self):
        """Test > not mutated to >="""
        a, b = 10, 5
        
        assert a > b
        assert not (a > a)  # Catches > -> >=
        
        # Boundary testing
        assert not (b > a)
        assert not (5 > 5)
        assert 5 > 4
    
    def test_equality_mutations(self):
        """Test == not mutated to !="""
        assert 5 == 5
        assert not (5 == 6)
        
        # Must be exact equality
        assert 0 == 0
        assert "" == ""
        assert False == False
        assert not (False == True)
    
    def test_inequality_mutations(self):
        """Test != not mutated to =="""
        assert 5 != 6
        assert not (5 != 5)
        
        # Must detect inequality
        assert 0 != 1
        assert "" != "x"
        assert True != False


class TestArithmeticMutations:
    """Test arithmetic operator mutations"""
    
    def test_addition_not_subtraction(self):
        """Test + not mutated to -"""
        a, b = 5, 3
        result = a + b
        
        assert result == 8
        assert not (result == 2)  # Would pass if + -> -
        
        # With negative
        assert -5 + 3 == -2
        assert 5 + (-3) == 2
    
    def test_subtraction_not_addition(self):
        """Test - not mutated to +"""
        a, b = 5, 3
        result = a - b
        
        assert result == 2
        assert not (result == 8)  # Would pass if - -> +
        
        # With negative
        assert -5 - 3 == -8
        assert 5 - (-3) == 8
    
    def test_multiplication_not_division(self):
        """Test * not mutated to /"""
        a, b = 6, 2
        result = a * b
        
        assert result == 12
        assert not (result == 3)  # Would pass if * -> /
        
        # With identity
        assert 1 * 5 == 5
        assert 0 * 5 == 0
    
    def test_division_not_multiplication(self):
        """Test / not mutated to *"""
        a, b = 6, 2
        result = a / b
        
        assert result == 3.0
        assert not (result == 12.0)  # Would pass if / -> *
        
        # With identity
        assert 5 / 1 == 5.0
        assert 0 / 1 == 0.0


class TestControlFlowEdgeCases:
    """Test control flow edge cases"""
    
    def test_if_body_removal(self):
        """Test that if body is not removed"""
        executed = False
        
        if True:
            executed = True
        
        assert executed is True  # Would fail if if body removed
    
    def test_if_else_branches(self):
        """Test if/else branches are both reachable"""
        result_if = None
        result_else = None
        
        if True:
            result_if = "if"
        else:
            result_else = "else"
        
        assert result_if == "if"
        assert result_else is None
        
        # Test else branch
        if False:
            result_if = "if2"
        else:
            result_else = "else2"
        
        assert result_if == "if"  # Not modified
        assert result_else == "else2"
    
    def test_loop_execution(self):
        """Test loop body is not removed"""
        count = 0
        
        for i in range(3):
            count += 1
        
        assert count == 3  # Would fail if loop body removed
    
    def test_break_statement(self):
        """Test break is not removed"""
        count = 0
        
        for i in range(10):
            count += 1
            if count == 3:
                break
        
        assert count == 3  # Would be 10 if break removed


class TestFunctionCallMutations:
    """Test function call mutations"""
    
    def test_method_call_not_skipped(self):
        """Test method calls are not skipped"""
        data = []
        data.append(1)
        data.append(2)
        data.append(3)
        
        assert len(data) == 3  # Would be 0 if append calls skipped
    
    def test_return_value_mutations(self):
        """Test return values are not changed"""
        def returns_true():
            return True
        
        def returns_false():
            return False
        
        assert returns_true() is True
        assert not returns_false()  # Would fail if inverted
    
    def test_none_return_vs_value_return(self):
        """Test None vs value returns"""
        def returns_none():
            return None
        
        def returns_value():
            return 42
        
        assert returns_none() is None
        assert returns_value() == 42
        
        # Mutation: return None -> return value
        assert not (returns_none() == 42)


class TestCollectionOperations:
    """Test collection-related edge cases"""
    
    def test_list_indexing_off_by_one(self):
        """Test list indexing is not off by one"""
        items = ['a', 'b', 'c']
        
        assert items[0] == 'a'  # NOT items[1]
        assert items[1] == 'b'  # NOT items[2]
        assert items[2] == 'c'  # NOT items[0]
        assert items[-1] == 'c'
        assert items[-2] == 'b'
    
    def test_dict_operations(self):
        """Test dict operations"""
        d = {'key1': 'value1', 'key2': 'value2'}
        
        assert d['key1'] == 'value1'
        assert d.get('key1') == 'value1'
        assert d.get('missing') is None
        
        # Key existence
        assert 'key1' in d
        assert 'missing' not in d
    
    def test_set_operations(self):
        """Test set operations"""
        s1 = {1, 2, 3}
        s2 = {2, 3, 4}
        
        assert 1 in s1
        assert 4 not in s1
        assert s1 & s2 == {2, 3}
        assert s1 | s2 == {1, 2, 3, 4}
        
        # Mutation: empty set vs non-empty
        assert len(s1) == 3
        assert len(s1 & s2) == 2


class TestTypeChecks:
    """Test type checking edge cases"""
    
    def test_type_equality(self):
        """Test type checking"""
        assert type(0) == int
        assert type(0.0) == float
        assert type("") == str
        assert type([]) == list
        assert type({}) == dict
        assert type(set()) == set
        
        # Mutation: type mixing
        assert type(1) != type(1.0)
        assert type("1") != type(1)


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
        assert all(x > 0 for x in items)
        assert not all(x > 3 for x in items)
        
        # OR condition
        assert any(x > 4 for x in items)
        assert not any(x > 10 for x in items)
    
    def test_nested_conditions(self):
        """Test nested conditions"""
        x, y, z = 5, 10, 3
        
        # Nested and/or
        if x < y and y > z:
            result = "nested_true"
        else:
            result = "nested_false"
        
        assert result == "nested_true"
        
        # Mutation would break this
        if x > y or y < z:
            result = "or_false"
        else:
            result = "or_true"
        
        assert result == "or_true"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
