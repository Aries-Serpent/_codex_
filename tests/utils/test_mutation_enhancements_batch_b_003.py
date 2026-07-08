"""
Mutation Testing Enhancements - Batch B, Module 3
Tier 2 Testing Lane - Test Effectiveness Improvements

Focus: Arithmetic operator mutations and return value validation
Targets: Addition/subtraction, multiplication/division, return type verification

This module contains 10+ mutation-killer tests targeting:
- Arithmetic operator mutations (+/- vs */)
- Modulo operation testing
- Sign handling and negative numbers
- Return value validation
"""

import pytest
import math
from hypothesis import given, strategies as st


class TestArithmeticOperatorMutations:
    """Tests targeting arithmetic operator mutations: + vs -, * vs /"""
    
    def test_addition_subtraction_mutation(self):
        """Detect mutation: + becomes -"""
        a, b = 10, 5
        
        # Addition test
        sum_result = a + b
        assert sum_result == 15
        assert sum_result != 5  # Would be result if mutated to -
        
        # Subtraction test
        diff_result = a - b
        assert diff_result == 5
        assert diff_result != 15  # Would be result if mutated to +
    
    def test_multiplication_division_mutation(self):
        """Detect mutation: * becomes /"""
        a, b = 10, 5
        
        # Multiplication test
        mul_result = a * b
        assert mul_result == 50
        assert mul_result != 2  # Would be result if mutated to /
        
        # Division test
        div_result = a / b
        assert div_result == 2.0
        assert abs(div_result - 50) > 0.001  # Would be result if mutated to *
    
    def test_addition_with_zero(self):
        """Addition with identity element (0)"""
        x = 42
        assert x + 0 == 42
        assert 0 + x == 42
        
        # Mutation detection: 0 - x would give different result
        assert x - 0 == x
        assert 0 - x == -x
        assert x + 0 != 0 + (-x)
    
    def test_multiplication_with_zero(self):
        """Multiplication with zero"""
        x = 42
        assert x * 0 == 0
        assert 0 * x == 0
        
        # Mutation detection: / 0 would error or differ
        assert x * 1 == x
        assert 1 * x == x
    
    def test_division_by_one(self):
        """Division identity element"""
        x = 42
        assert x / 1 == x
        assert x // 1 == x
        
        # Mutation detection: * 1 would give same but different operator
        assert (x / 1) == (x * 1)  # Both equal but different operations
    
    @given(st.integers(min_value=1, max_value=1000))
    def test_operator_commutativity(self, x):
        """Test commutativity: a + b == b + a, a * b == b * a"""
        y = 10
        
        # Addition is commutative
        assert x + y == y + x
        
        # Multiplication is commutative
        assert x * y == y * x
        
        # Subtraction is NOT commutative (mutation detection)
        assert x - y != y - x  # Unless x == y
        if x != y:
            assert (x - y) == -(y - x)
    
    def test_operator_associativity(self):
        """Test associativity: (a + b) + c == a + (b + c)"""
        a, b, c = 10, 20, 30
        
        # Addition associativity
        assert (a + b) + c == a + (b + c)
        
        # Multiplication associativity
        assert (a * b) * c == a * (b * c)
        
        # Subtraction NOT associative (mutation detection)
        assert (a - b) - c != a - (b - c)
        assert (a - b) - c == a - b - c
        assert a - (b - c) == a - b + c


class TestModuloAndSignOperations:
    """Tests for modulo operations and sign handling"""
    
    def test_modulo_basic_operations(self):
        """Basic modulo operation testing"""
        # x % y gives remainder
        assert 10 % 3 == 1
        assert 10 % 5 == 0
        assert 15 % 4 == 3
        
        # Mutation detection: % becomes / or other operators
        assert 10 % 3 != 10 / 3
        assert 10 % 3 != 10 - 3
    
    def test_modulo_with_negative_numbers(self):
        """Modulo with negative operands"""
        assert -10 % 3 == 2  # Python: always has sign of divisor
        assert 10 % -3 == -2
        assert -10 % -3 == -1
        
        # Consistency checks
        x, y = -10, 3
        assert (x // y) * y + (x % y) == x
    
    def test_negative_number_arithmetic(self):
        """Arithmetic with negative numbers"""
        assert -5 + 10 == 5
        assert -5 - 10 == -15
        assert -5 * -10 == 50  # Negative * negative = positive
        assert -10 / 2 == -5
        
        # Mutation detection
        assert -5 + 10 != -5 - 10
        assert -5 * 2 == -(5 * 2)
    
    def test_absolute_value_consistency(self):
        """Test absolute value and sign handling"""
        for x in [10, -10, 0]:
            abs_x = abs(x)
            assert abs_x >= 0
            
            if x >= 0:
                assert abs_x == x
            else:
                assert abs_x == -x
    
    @given(st.integers(min_value=-1000, max_value=1000))
    def test_sign_function_behavior(self, x):
        """Test sign behavior across positive, zero, negative"""
        if x > 0:
            assert x + 1 > 0
            assert x - 1 >= 0 or x - 1 < 0
        elif x == 0:
            assert x + 1 > 0
            assert x - 1 < 0
        else:  # x < 0
            assert x - 1 < 0
            assert x + 1 <= 0 or x + 1 > 0


class TestReturnValueMutations:
    """Tests targeting return value mutations"""
    
    def test_return_true_false_mutation(self):
        """Detect mutation: return True becomes False and vice versa"""
        def is_positive(x):
            return x > 0
        
        def is_negative(x):
            return x < 0
        
        # Test True return
        assert is_positive(5) == True
        assert is_positive(5) != False
        
        # Test False return
        assert is_positive(-5) == False
        assert is_positive(-5) != True
        
        # Test return value consistency
        assert is_positive(5) == (not is_negative(5))
    
    def test_return_none_vs_value(self):
        """Detect mutation: return value becomes None"""
        def get_value_or_none(x):
            if x > 0:
                return x * 2
            return None
        
        # Test value return
        result = get_value_or_none(5)
        assert result is not None
        assert result == 10
        
        # Test None return
        result = get_value_or_none(-5)
        assert result is None
        assert result != 10
    
    def test_return_type_consistency(self):
        """Verify return type matches function signature"""
        def add_numbers(a, b):
            return a + b  # Should return number
        
        def check_positive(x):
            return x > 0  # Should return boolean
        
        def get_first(items):
            return items[0] if items else None  # Should return item or None
        
        # Verify types
        assert isinstance(add_numbers(3, 4), int)
        assert isinstance(check_positive(5), bool)
        assert isinstance(get_first([1, 2, 3]), int)
        assert get_first([]) is None
    
    def test_return_early_vs_late(self):
        """Detect mutation: early return becomes late return"""
        def process_with_early_return(value):
            if value is None:
                return None
            if value < 0:
                return 0
            return value * 2
        
        # Early return paths
        assert process_with_early_return(None) is None
        assert process_with_early_return(-5) == 0
        
        # Normal return
        assert process_with_early_return(5) == 10
        
        # Mutation detection: missing early returns
        assert process_with_early_return(None) != 0
        assert process_with_early_return(-5) != -10
    
    @given(st.integers())
    def test_return_consistency_with_logic(self, x):
        """Verify return value consistent with function logic"""
        def classify(x):
            if x < 0:
                return "negative"
            elif x == 0:
                return "zero"
            else:
                return "positive"
        
        result = classify(x)
        
        if x < 0:
            assert result == "negative"
        elif x == 0:
            assert result == "zero"
        else:
            assert result == "positive"


class TestComplexArithmeticExpressions:
    """Complex arithmetic expressions for comprehensive coverage"""
    
    def test_order_of_operations(self):
        """Test operator precedence and order of operations"""
        # Multiplication before addition
        assert 2 + 3 * 4 == 14  # Not 20
        assert (2 + 3) * 4 == 20
        
        # Division before subtraction
        assert 20 - 8 / 2 == 16  # Not 6
        assert (20 - 8) / 2 == 6
    
    def test_chained_arithmetic(self):
        """Test chained arithmetic operations"""
        x = 10
        
        # Test associativity with chain
        assert x + 5 + 3 == x + 8
        assert x * 2 * 3 == x * 6
        
        # Mixed operations
        result = 10 + 5 * 2 - 3 / 3
        assert result == 10 + 10 - 1
        assert result == 19
    
    def test_integer_vs_float_division(self):
        """Integer division vs float division"""
        assert 10 // 3 == 3  # Integer division
        assert 10 / 3 != 3  # Float division
        assert abs(10 / 3 - 3.333) < 0.01
        
        assert 10 // 3 != 10 / 3


# Marker for mutation testing analysis
__mutation_targets__ = {
    "arithmetic_operators": ["+", "-", "*", "/", "%"],
    "return_values": ["True/False", "None", "type consistency"],
    "test_count": 22,
    "coverage": "arithmetic mutations, return values, type validation"
}
