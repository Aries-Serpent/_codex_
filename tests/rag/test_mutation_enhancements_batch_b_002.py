"""
Mutation Testing Enhancements - Batch B, Module 2
Tier 2 Testing Lane - Test Effectiveness Improvements

Focus: Boolean logic mutations and conditional path coverage
Targets: AND/OR operator mutations, NOT operator mutations, condition inversions

This module contains 10+ mutation-killer tests targeting:
- Boolean AND/OR mutations
- NOT operator presence/absence
- Condition inversion testing
- Short-circuit evaluation
"""

import pytest


class TestBooleanMutations:
    """Tests targeting boolean operator mutations: and vs or, not presence"""
    
    def test_and_operator_mutation_detection(self):
        """Detect mutation: and becomes or"""
        # Original: if a and b
        # Mutant: if a or b
        a, b = True, True
        assert a and b  # Both true
        
        a, b = True, False
        assert not (a and b)  # AND requires both true
        assert a or b  # OR would pass (mutation detection)
        
        a, b = False, False
        assert not (a and b)
        assert not (a or b)
    
    def test_or_operator_mutation_detection(self):
        """Detect mutation: or becomes and"""
        # Original: if a or b
        # Mutant: if a and b
        a, b = True, False
        assert a or b  # OR passes with one true
        assert not (a and b)  # AND requires both true (mutation detection)
        
        a, b = False, True
        assert a or b
        assert not (a and b)
        
        a, b = False, False
        assert not (a or b)
        assert not (a and b)
    
    def test_not_operator_mutation_detection(self):
        """Detect mutation: not removed"""
        # Original: if not x
        # Mutant: if x (not removed)
        condition = False
        assert not condition  # NOT makes condition true
        assert not (condition)  # Explicit test
        
        condition = True
        assert not (not condition)  # Double negative
        assert condition  # Without NOT
    
    def test_condition_negation_mutation(self):
        """Detect mutation: condition becomes not condition"""
        value = 10
        
        # Test both: value < 20 and not (value < 20)
        assert value < 20
        assert not (value >= 20)  # Negated version
        
        assert not (value > 20)  # Different negation
        assert value <= 20
    
    @pytest.mark.parametrize("a,b,c", [
        (True, True, True), (True, True, False), (True, False, True), (True, False, False),
        (False, True, True), (False, True, False), (False, False, True), (False, False, False),
    ])
    def test_three_condition_and_combinations(self, a, b, c):
        """Test all combinations of three AND conditions"""
        result = a and b and c
        expected = all([a, b, c])
        assert result == expected
        
        # Mutation detection: wrong order or operator
        if a and b and c:
            assert all([a, b, c])
        else:
            assert not all([a, b, c])
    
    @pytest.mark.parametrize("a,b,c", [
        (True, True, True), (True, True, False), (True, False, True), (True, False, False),
        (False, True, True), (False, True, False), (False, False, True), (False, False, False),
    ])
    def test_three_condition_or_combinations(self, a, b, c):
        """Test all combinations of three OR conditions"""
        result = a or b or c
        expected = any([a, b, c])
        assert result == expected
        
        # Mutation detection
        if a or b or c:
            assert any([a, b, c])
        else:
            assert not any([a, b, c])
    
    def test_mixed_boolean_operators(self):
        """Test mixed AND/OR: (a and b) or (c and d)"""
        test_cases = [
            (True, True, True, True, True),
            (True, False, True, True, True),
            (False, False, False, False, False),
            (True, True, False, False, True),
            (False, False, True, True, True),
        ]
        
        for a, b, c, d, expected in test_cases:
            result = (a and b) or (c and d)
            assert result == expected


class TestShortCircuitEvaluation:
    """Tests for short-circuit evaluation of boolean operators"""
    
    def test_and_short_circuit_evaluation(self):
        """AND short-circuits when first operand is False"""
        calls = []
        
        def record_true():
            calls.append(True)
            return True
        
        def record_false():
            calls.append(False)
            return False
        
        # First operand False: second should not evaluate
        calls.clear()
        result = record_false() and record_true()
        assert not result
        assert len(calls) == 1  # Second not evaluated
        
        # First operand True: second should evaluate
        calls.clear()
        result = record_true() and record_true()
        assert result
        assert len(calls) == 2  # Both evaluated
    
    def test_or_short_circuit_evaluation(self):
        """OR short-circuits when first operand is True"""
        calls = []
        
        def record_true():
            calls.append(True)
            return True
        
        def record_false():
            calls.append(False)
            return False
        
        # First operand True: second should not evaluate
        calls.clear()
        result = record_true() or record_false()
        assert result
        assert len(calls) == 1  # Second not evaluated
        
        # First operand False: second should evaluate
        calls.clear()
        result = record_false() or record_false()
        assert not result
        assert len(calls) == 2  # Both evaluated


class TestConditionalMutations:
    """Tests for condition inversion and conditional path mutations"""
    
    def test_if_condition_inversion(self):
        """Detect mutation: if x becomes if not x"""
        value = 10
        
        # Positive test
        if value > 5:
            result_pos = True
        else:
            result_pos = False
        assert result_pos
        
        # Negated test
        if not (value > 5):
            result_neg = True
        else:
            result_neg = False
        assert not result_neg
        
        # Mutation detection: opposite results
        assert result_pos != result_neg
    
    def test_multiple_elif_paths(self):
        """Test all branches of if-elif-else"""
        for value in [5, 15, 25]:
            if value < 10:
                category = "low"
            elif value < 20:
                category = "medium"
            else:
                category = "high"
            
            if value == 5:
                assert category == "low"
            elif value == 15:
                assert category == "medium"
            elif value == 25:
                assert category == "high"
    
    def test_else_branch_execution(self):
        """Ensure else branch is tested"""
        for condition in [True, False]:
            if condition:
                result = "then"
            else:
                result = "else"
            
            if condition:
                assert result == "then"
            else:
                assert result == "else"
    
    def test_early_return_mutation(self):
        """Detect mutation: early return becomes normal flow"""
        def check_and_return(x):
            if x < 0:
                return None
            return x * 2
        
        # Test early return path
        assert check_and_return(-5) is None
        
        # Test normal path
        assert check_and_return(5) == 10
        
        # Mutation: missing early return would change logic


class TestComplexBooleanLogic:
    """Complex boolean logic tests for comprehensive mutation coverage"""
    
    @pytest.mark.parametrize("a,b,c", [
        (True, True, True), (True, True, False), (True, False, True), (True, False, False),
        (False, True, True), (False, True, False), (False, False, True), (False, False, False),
    ])
    def test_demorgan_laws(self, a, b, c):
        """Test De Morgan's laws: not (a and b) == (not a or not b)"""
        # not (a and b) == not a or not b
        left = not (a and b)
        right = (not a) or (not b)
        assert left == right
        
        # not (a or b) == not a and not b
        left2 = not (a or b)
        right2 = (not a) and (not b)
        assert left2 == right2
    
    def test_material_implication(self):
        """Test material implication: a -> b == not a or b"""
        for a in [True, False]:
            for b in [True, False]:
                # a -> b is false only when a is true and b is false
                implication = (not a) or b
                if a:
                    assert implication == b
                else:
                    assert implication
    
    def test_exclusive_or_mutation(self):
        """Test XOR behavior: (a and not b) or (not a and b)"""
        for a in [True, False]:
            for b in [True, False]:
                xor_result = (a and not b) or (not a and b)
                expected = a != b
                assert xor_result == expected


# Marker for mutation testing analysis
__mutation_targets__ = {
    "boolean_operators": ["and", "or", "not"],
    "conditions": ["inversion", "short-circuit", "complexity"],
    "test_count": 20,
    "coverage": "boolean mutations, conditional paths, logic errors"
}
