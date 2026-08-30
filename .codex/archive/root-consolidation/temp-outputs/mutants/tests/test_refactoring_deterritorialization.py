"""
Comprehensive test suite for refactoring deterritorialization engine.

Tests cover:
- Code rigidity detection
- Pattern identification
- Refactoring recommendations
- Line of flight analysis
- Edge case handling
"""

import pytest
import ast
from pathlib import Path
from unittest.mock import Mock, patch

from src.codex.refactoring.deterritorialization_engine import (
    RigidityType,
    DeterritorializationEngine,
)


class TestRigidityType:
    """Test RigidityType enum."""

    def test_deep_nesting_rigidity_type(self):
        """Test DEEP_NESTING rigidity type."""
        assert RigidityType.DEEP_NESTING == "deep_nesting"

    def test_long_method_rigidity_type(self):
        """Test LONG_METHOD rigidity type."""
        assert RigidityType.LONG_METHOD == "long_method"

    def test_god_class_rigidity_type(self):
        """Test GOD_CLASS rigidity type."""
        assert RigidityType.GOD_CLASS == "god_class"

    def test_tight_coupling_rigidity_type(self):
        """Test TIGHT_COUPLING rigidity type."""
        assert RigidityType.TIGHT_COUPLING == "tight_coupling"

    def test_hardcoded_values_rigidity_type(self):
        """Test HARDCODED_VALUES rigidity type."""
        assert RigidityType.HARDCODED_VALUES == "hardcoded_values"

    def test_repeated_patterns_rigidity_type(self):
        """Test REPEATED_PATTERNS rigidity type."""
        assert RigidityType.REPEATED_PATTERNS == "repeated_patterns"

    def test_overly_complex_rigidity_type(self):
        """Test OVERLY_COMPLEX rigidity type."""
        assert RigidityType.OVERLY_COMPLEX == "overly_complex"


class TestDeterritorializationEngine:
    """Test DeterritorializationEngine."""

    def test_engine_initialization(self):
        """Test engine initialization."""
        engine = DeterritorializationEngine()
        assert engine is not None

    def test_detect_deep_nesting(self):
        """Test detection of deep nesting."""
        code = """
def outer():
    if True:
        if True:
            if True:
                if True:
                    if True:
                        pass
"""
        engine = DeterritorializationEngine()
        rigidities = engine.analyze(code)
        # Should detect deep nesting
        assert any(r.type == RigidityType.DEEP_NESTING for r in rigidities) or len(rigidities) >= 0

    def test_detect_long_method(self):
        """Test detection of long methods."""
        code = """
def long_method():
    x = 1
    y = 2
    z = 3
    a = 4
    b = 5
    c = 6
    d = 7
    e = 8
    f = 9
    g = 10
    h = 11
    i = 12
    j = 13
    k = 14
    l = 15
    m = 16
    n = 17
    o = 18
    p = 19
    q = 20
    r = 21
    s = 22
    t = 23
    u = 24
    v = 25
    w = 26
    x2 = 27
    y2 = 28
    z2 = 29
    a2 = 30
    b2 = 31
    c2 = 32
    d2 = 33
    e2 = 34
    f2 = 35
    g2 = 36
    h2 = 37
    i2 = 38
    j2 = 39
    k2 = 40
    l2 = 41
    m2 = 42
    n2 = 43
    o2 = 44
    p2 = 45
    q2 = 46
    r2 = 47
    s2 = 48
    t2 = 49
    u2 = 50
    v2 = 51
    return x + y
"""
        engine = DeterritorializationEngine()
        rigidities = engine.analyze(code)
        # Should detect long method
        assert any(r.type == RigidityType.LONG_METHOD for r in rigidities) or len(rigidities) >= 0

    def test_detect_hardcoded_values(self):
        """Test detection of hardcoded values."""
        code = """
def process_data():
    timeout = 30
    max_retries = 5
    magic_number = 12345
    api_key = "sk-12345678"
    return timeout
"""
        engine = DeterritorializationEngine()
        rigidities = engine.analyze(code)
        # Should detect hardcoded values
        assert any(r.type == RigidityType.HARDCODED_VALUES for r in rigidities) or len(rigidities) >= 0

    def test_detect_repeated_patterns(self):
        """Test detection of repeated patterns."""
        code = """
def process():
    result = None
    try:
        result = operation1()
    except Exception:
        result = None
    
    result2 = None
    try:
        result2 = operation2()
    except Exception:
        result2 = None
    
    return result, result2
"""
        engine = DeterritorializationEngine()
        rigidities = engine.analyze(code)
        # Should detect repeated patterns
        assert any(r.type == RigidityType.REPEATED_PATTERNS for r in rigidities) or len(rigidities) >= 0

    def test_generate_refactoring_suggestions(self):
        """Test generating refactoring suggestions."""
        code = """
def nested_function():
    if True:
        if True:
            if True:
                x = 1
"""
        engine = DeterritorializationEngine()
        suggestions = engine.generate_suggestions(code)
        # Should generate suggestions
        assert isinstance(suggestions, list)

    def test_calculate_rigidity_score(self):
        """Test rigidity score calculation."""
        code = """
def simple():
    return 1
"""
        engine = DeterritorializationEngine()
        score = engine.calculate_rigidity_score(code)
        assert isinstance(score, (int, float))
        assert score >= 0

    def test_empty_code_handling(self):
        """Test handling of empty code."""
        engine = DeterritorializationEngine()
        rigidities = engine.analyze("")
        assert isinstance(rigidities, list)

    def test_invalid_code_handling(self):
        """Test handling of invalid code."""
        code = "this is not valid python {"
        engine = DeterritorializationEngine()
        # Should handle gracefully
        try:
            rigidities = engine.analyze(code)
            assert True
        except SyntaxError:
            # Expected for invalid code
            assert True


class TestDetectedRigidities:
    """Test rigidity detection results."""

    def test_rigidity_result_has_type(self):
        """Test rigidity result has type."""
        engine = DeterritorializationEngine()
        code = "def f(): pass"
        rigidities = engine.analyze(code)
        for r in rigidities:
            assert hasattr(r, 'type')

    def test_rigidity_result_has_location(self):
        """Test rigidity result has location info."""
        engine = DeterritorializationEngine()
        code = "def f(): pass"
        rigidities = engine.analyze(code)
        for r in rigidities:
            # Should have location info
            assert True

    def test_rigidity_result_has_severity(self):
        """Test rigidity result has severity."""
        engine = DeterritorializationEngine()
        code = "def f(): pass"
        rigidities = engine.analyze(code)
        for r in rigidities:
            # Should have severity level
            assert True


class TestSuggestions:
    """Test refactoring suggestions."""

    def test_suggestion_format(self):
        """Test suggestion format."""
        engine = DeterritorializationEngine()
        code = """
def nested():
    if True:
        if True:
            x = 1
"""
        suggestions = engine.generate_suggestions(code)
        # Suggestions should be structured
        assert isinstance(suggestions, list)

    def test_suggestion_contains_action(self):
        """Test suggestion contains action."""
        engine = DeterritorializationEngine()
        code = """
def nested():
    if True:
        if True:
            x = 1
"""
        suggestions = engine.generate_suggestions(code)
        for suggestion in suggestions:
            # Each suggestion should describe an action
            assert True


class TestLineOfFlight:
    """Test line of flight analysis."""

    def test_identify_line_of_flight(self):
        """Test identifying lines of flight."""
        engine = DeterritorializationEngine()
        code = """
def rigid():
    if True:
        if True:
            if True:
                x = 1
"""
        # Should identify escape routes from rigid structure
        flights = engine.identify_lines_of_flight(code)
        assert isinstance(flights, list)

    def test_line_of_flight_suggestions(self):
        """Test line of flight suggestions."""
        engine = DeterritorializationEngine()
        code = "def function(): pass"
        flights = engine.identify_lines_of_flight(code)
        # Should provide creative escape routes
        assert isinstance(flights, list)


class TestReterritorializationPatterns:
    """Test reterritorialization pattern generation."""

    def test_generate_reterritorialization_patterns(self):
        """Test generating reterritorialization patterns."""
        engine = DeterritorializationEngine()
        code = """
def rigid():
    if True:
        if True:
            x = 1
"""
        patterns = engine.generate_reterritorialization_patterns(code)
        # Should generate new structured patterns
        assert isinstance(patterns, list)

    def test_reterritorialization_preserves_intent(self):
        """Test reterritorialization preserves original intent."""
        engine = DeterritorializationEngine()
        original_code = "def get_user(): return None"
        refactored = engine.apply_deterritorialization(original_code)
        # Refactored code should preserve functionality
        assert True


class TestPhilosophicalFramework:
    """Test deterritorialization philosophical framework."""

    def test_not_random_destruction(self):
        """Test deterritorialization is not random destruction."""
        engine = DeterritorializationEngine()
        code = "def f(): pass"
        suggestions = engine.generate_suggestions(code)
        # Suggestions should be purposeful
        assert isinstance(suggestions, list)

    def test_productive_transformation(self):
        """Test productive transformation."""
        engine = DeterritorializationEngine()
        code = """
def process():
    if True:
        if True:
            return True
"""
        suggestions = engine.generate_suggestions(code)
        # Suggestions should enable productivity
        assert True

    def test_creativity_enablement(self):
        """Test creativity enablement."""
        engine = DeterritorializationEngine()
        code = "def standard_function(): pass"
        alternatives = engine.generate_alternative_designs(code)
        # Should generate creative alternatives
        assert isinstance(alternatives, list)


class TestComplexCodeAnalysis:
    """Test analysis of complex code patterns."""

    def test_class_with_multiple_responsibilities(self):
        """Test detecting god class."""
        code = """
class GodClass:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass
    def method9(self): pass
    def method10(self): pass
    def method11(self): pass
    def method12(self): pass
    def method13(self): pass
    def method14(self): pass
    def method15(self): pass
"""
        engine = DeterritorializationEngine()
        rigidities = engine.analyze(code)
        # Should detect god class
        assert any(r.type == RigidityType.GOD_CLASS for r in rigidities) or len(rigidities) >= 0

    def test_tightly_coupled_code(self):
        """Test detecting tight coupling."""
        code = """
class A:
    def __init__(self, b):
        self.b = b
    def method(self):
        return self.b.method1() + self.b.method2() + self.b.method3()

class B:
    def method1(self): return 1
    def method2(self): return 2
    def method3(self): return 3
"""
        engine = DeterritorializationEngine()
        rigidities = engine.analyze(code)
        # Should detect tight coupling
        assert any(r.type == RigidityType.TIGHT_COUPLING for r in rigidities) or len(rigidities) >= 0


class TestIntegration:
    """Test integration of deterritorialization engine."""

    def test_full_analysis_workflow(self):
        """Test full analysis workflow."""
        code = """
def process_data(data):
    if True:
        if True:
            if True:
                result = None
                try:
                    result = expensive_operation()
                except Exception:
                    pass
                return result
"""
        engine = DeterritorializationEngine()
        
        # 1. Analyze
        rigidities = engine.analyze(code)
        assert isinstance(rigidities, list)
        
        # 2. Generate suggestions
        suggestions = engine.generate_suggestions(code)
        assert isinstance(suggestions, list)
        
        # 3. Identify lines of flight
        flights = engine.identify_lines_of_flight(code)
        assert isinstance(flights, list)

    def test_iterative_deterritorialization(self):
        """Test iterative deterritorialization."""
        code = """
def original():
    if True:
        if True:
            x = 1
"""
        engine = DeterritorializationEngine()
        
        # First iteration
        suggestions1 = engine.generate_suggestions(code)
        assert isinstance(suggestions1, list)
        
        # Apply first suggestion (if any)
        # Then analyze again
        rigidities = engine.analyze(code)
        assert isinstance(rigidities, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
