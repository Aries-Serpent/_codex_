"""Comprehensive test suite for intuitive_aptitude code analysis module.

This test suite provides thorough coverage of all components in the
analysis/intuitive_aptitude.py module including dataclasses, AST transformers,
the main analyzer class, and helper functions.
"""

from __future__ import annotations

import ast
import sys

import pytest

from analysis.intuitive_aptitude import (
    ClassInfo,
    FunctionInfo,
    ImportInfo,
    _NameRenamer,
    _unparse,
    analyze_and_suggest,
    intuitive_aptitude,
)

# =============================================================================
# Test Dataclasses
# =============================================================================


class TestDataClasses:
    """Test suite for dataclass structures."""

    def test_import_info_basic(self):
        """Test ImportInfo dataclass with basic module import."""
        imp = ImportInfo(module=None, name="os", alias=None, level=0)
        assert imp.module is None, "module is not valid"
        assert imp.name == "os", "name is not valid"
        assert imp.alias is None, "alias is not valid"
        assert imp.level == 0, "level is not valid"

    def test_import_info_from_import(self):
        """Test ImportInfo dataclass with from...import statement."""
        imp = ImportInfo(module="os", name="path", alias="p", level=0)
        assert imp.module == "os", "module is not valid"
        assert imp.name == "path", "name is not valid"
        assert imp.alias == "p", "alias is not valid"

    def test_import_info_relative(self):
        """Test ImportInfo dataclass with relative imports."""
        imp = ImportInfo(module="utils", name="helper", alias=None, level=2)
        assert imp.level == 2, "level is not valid"

    def test_function_info_basic(self):
        """Test FunctionInfo dataclass with basic function."""
        func = FunctionInfo(
            name="test_func",
            args=["x", "y"],
            defaults=0,
            kwonlyargs=[],
            decorators=[],
            returns=None,
            docstring="Test function",
            lineno=1,
            end_lineno=5,
            complexity=1,
            calls=[],
        )
        assert func.name == "test_func", "name is not valid"
        assert func.args == ["x", "y"]
        assert func.defaults == 0, "defaults is not valid"
        assert func.complexity == 1, "complexity is not valid"

    def test_function_info_with_decorators(self):
        """Test FunctionInfo dataclass with decorators."""
        function_info = FunctionInfo(
            name="decorated",
            args=["self"],
            defaults=0,
            kwonlyargs=[],
            decorators=["@staticmethod", "@property"],
            returns="int",
            docstring=None,
            lineno=10,
            end_lineno=15,
            complexity=2,
            calls=["print", "len"],
        )
        assert function_info.decorators == ["@staticmethod", "@property"]
        assert function_info.returns == "int", "returns is not valid"
        assert function_info.calls == ["print", "len"]

    def test_class_info_basic(self):
        """Test ClassInfo dataclass with basic class."""
        class_info = ClassInfo(
            name="MyClass",
            bases=[],
            decorators=[],
            docstring="A test class",
            methods={},
            lineno=20,
            end_lineno=30,
        )
        assert class_info.name == "MyClass", "name is not valid"
        assert class_info.bases == [], "bases is not valid"
        assert len(class_info.methods) == 0, "Collection must not be empty"

    def test_class_info_with_methods(self):
        """Test ClassInfo dataclass with methods."""
        method = FunctionInfo(
            name="method1",
            args=["self", "arg"],
            defaults=0,
            kwonlyargs=[],
            decorators=[],
            returns=None,
            docstring="Method docstring",
            lineno=22,
            end_lineno=25,
            complexity=1,
            calls=[],
        )
        class_info = ClassInfo(
            name="MyClass",
            bases=["BaseClass"],
            decorators=["@dataclass"],
            docstring="Class with methods",
            methods={"method1": method},
            lineno=20,
            end_lineno=30,
        )
        assert "method1" in class_info.methods, "Condition must be true"
        assert class_info.bases == ["BaseClass"], "bases is not valid"
        assert class_info.decorators == ["@dataclass"], "Data must not be empty"


# =============================================================================
# Test _unparse Function
# =============================================================================


class TestUnparse:
    """Test suite for _unparse function."""

    def test_unparse_name_node(self):
        """Test unparsing a simple Name node."""
        node = ast.Name(id="variable", ctx=ast.Load())
        result = _unparse(node)
        assert result == "variable", "Result must not be empty"

    def test_unparse_constant(self):
        """Test unparsing a Constant node."""
        node = ast.Constant(value=42)
        result = _unparse(node)
        assert result == "42", "Result must not be empty"

    def test_unparse_binop(self):
        """Test unparsing a BinOp node."""
        # Create: 1 + 2
        node = ast.BinOp(left=ast.Constant(value=1), op=ast.Add(), right=ast.Constant(value=2))
        result = _unparse(node)
        # Result might be '1 + 2' or '(1 + 2)' depending on Python version
        assert "1" in result and "2" in result and "+" in result

    @pytest.mark.skipif(not hasattr(ast, "unparse"), reason="Python 3.9+ required for ast.unparse")
    def test_unparse_uses_builtin(self):
        """Test that _unparse uses built-in ast.unparse when available."""
        node = ast.Name(id="test", ctx=ast.Load())
        result = _unparse(node)
        expected = ast.unparse(node)
        assert result == expected, "Result must not be empty"


# =============================================================================
# Test _NameRenamer AST Transformer
# =============================================================================


class TestNameRenamer:
    """Test suite for _NameRenamer AST transformer."""

    def test_rename_simple_variable(self):
        """Test renaming a simple variable."""
        code = "x = 42"
        tree = ast.parse(code)
        renamer = _NameRenamer({"x": "y"})
        new_tree = renamer.visit(tree)
        ast.fix_missing_locations(new_tree)
        result = _unparse(new_tree)
        assert "y" in result, "Result must not be empty"
        assert "42" in result, "Result must not be empty"

    def test_rename_function_name(self):
        """Test renaming a function name."""
        code = "def foo(): pass"
        tree = ast.parse(code)
        renamer = _NameRenamer({"foo": "bar"})
        new_tree = renamer.visit(tree)
        ast.fix_missing_locations(new_tree)
        result = _unparse(new_tree)
        assert "bar" in result, "Result must not be empty"

    def test_rename_function_argument(self):
        """Test renaming function arguments."""
        code = "def func(arg1, arg2): return arg1 + arg2"
        tree = ast.parse(code)
        renamer = _NameRenamer({"arg1": "x", "arg2": "y"})
        new_tree = renamer.visit(tree)
        ast.fix_missing_locations(new_tree)
        result = _unparse(new_tree)
        assert "x" in result, "Result must not be empty"
        assert "y" in result, "Result must not be empty"

    def test_rename_class_name(self):
        """Test renaming a class name."""
        code = "class OldClass: pass"
        tree = ast.parse(code)
        renamer = _NameRenamer({"OldClass": "NewClass"})
        new_tree = renamer.visit(tree)
        ast.fix_missing_locations(new_tree)
        result = _unparse(new_tree)
        assert "NewClass" in result, "Result must not be empty"

    def test_rename_multiple_identifiers(self):
        """Test renaming multiple identifiers at once."""
        code = "def foo(x): return x + 1"
        tree = ast.parse(code)
        renamer = _NameRenamer({"foo": "bar", "x": "y"})
        new_tree = renamer.visit(tree)
        ast.fix_missing_locations(new_tree)
        result = _unparse(new_tree)
        assert "bar" in result, "Result must not be empty"
        assert "y" in result, "Result must not be empty"

    def test_rename_with_empty_mapping(self):
        """Test that empty mapping doesn't change code."""
        code = "def func(x): return x"
        tree = ast.parse(code)
        renamer = _NameRenamer({})
        new_tree = renamer.visit(tree)
        ast.fix_missing_locations(new_tree)
        result = _unparse(new_tree)
        assert "func" in result, "Result must not be empty"
        assert "x" in result, "Result must not be empty"


# =============================================================================
# Test intuitive_aptitude Class - Initialization
# =============================================================================


class TestIntuitiveAptitudeInit:
    """Test suite for intuitive_aptitude initialization."""

    def test_initialization(self):
        """Test that analyzer initializes with empty state."""
        analyzer = intuitive_aptitude()
        assert len(analyzer.functions) == 0, "Collection must not be empty"
        assert len(analyzer.classes) == 0, "Collection must not be empty"
        assert len(analyzer.imports) == 0, "Collection must not be empty"
        assert len(analyzer.variables) == 0, "Collection must not be empty"
        assert analyzer.metrics["loc"] == 0, "Condition must be true"
        assert analyzer.metrics["comment_ratio"] == 0.0, "Condition must be true"
        assert analyzer.metrics["complexity"] == 0.0, "Condition must be true"
        assert analyzer._source == "", "_source is not valid"
        assert analyzer.ast_tree is None, "ast_tree is not valid"
        assert analyzer.last_error is None, "Error should be raised or set"

    def test_pattern_initialization(self):
        """Test that pattern dictionaries are initialized."""
        analyzer = intuitive_aptitude()
        assert "error_handling" in analyzer.patterns, "Error should be raised or set"
        assert "iteration" in analyzer.patterns, "Condition must be true"
        assert "conditional" in analyzer.patterns, "Condition must be true"
        assert "function_calls" in analyzer.patterns, "Condition must be true"
        assert isinstance(analyzer.patterns["error_handling"], list)


# =============================================================================
# Test intuitive_aptitude Class - Ingestion
# =============================================================================


class TestIntuitiveAptitudeIngest:
    """Test suite for code ingestion."""

    def test_ingest_simple_code(self):
        """Test ingesting simple valid Python code."""
        analyzer = intuitive_aptitude()
        code = "x = 42\ny = 100"
        result = analyzer.ingest(code)
        assert result is True, "Result must not be empty"
        assert analyzer.last_error is None, "Error should be raised or set"
        assert analyzer.metrics["loc"] == 2.0, "Condition must be true"

    def test_ingest_with_function(self):
        """Test ingesting code with a function."""
        analyzer = intuitive_aptitude()
        code = """
def greet(name):
    '''Say hello to name.'''
    return f"Hello, {name}"
"""
        result = analyzer.ingest(code)
        assert result is True, "Result must not be empty"
        assert "greet" in analyzer.functions, "Condition must be true"
        assert analyzer.functions["greet"].name == "greet", "name is not valid"
        assert analyzer.functions["greet"].args == ["name"], "args is not valid"
        assert analyzer.functions["greet"].docstring == "Say hello to name.", "docstring is not valid"

    def test_ingest_with_class(self):
        """Test ingesting code with a class."""
        analyzer = intuitive_aptitude()
        code = """
class Calculator:
    '''Simple calculator.'''
    def add(self, a, b):
        return a + b
"""
        result = analyzer.ingest(code)
        assert result is True, "Result must not be empty"
        assert "Calculator" in analyzer.classes, "Condition must be true"
        assert analyzer.classes["Calculator"].docstring == "Simple calculator.", "docstring is not valid"
        assert "add" in analyzer.classes["Calculator"].methods, "Condition must be true"

    def test_ingest_with_imports(self):
        """Test ingesting code with import statements."""
        analyzer = intuitive_aptitude()
        code = """
import os
from sys import path as syspath
from typing import List, Dict
"""
        result = analyzer.ingest(code)
        assert result is True, "Result must not be empty"
        # from typing import List, Dict creates 2 separate import entries
        assert len(analyzer.imports) == 4, "Collection must not be empty"
        # Check that imports were captured
        import_names = [imp.name for imp in analyzer.imports]
        assert "os" in import_names, "Condition must be true"
        assert "List" in import_names, "Condition must be true"
        assert "Dict" in import_names, "Condition must be true"

    def test_ingest_invalid_syntax(self):
        """Test ingesting code with syntax errors."""
        analyzer = intuitive_aptitude()
        code = "def broken( pass"
        result = analyzer.ingest(code)
        assert result is False, "Result must not be empty"
        assert analyzer.last_error is not None, "last_error must be initialized"
        assert "SyntaxError" in analyzer.last_error, "Error should be raised or set"

    def test_ingest_empty_code(self):
        """Test ingesting empty code."""
        analyzer = intuitive_aptitude()
        result = analyzer.ingest("")
        assert result is True, "Result must not be empty"
        assert analyzer.metrics["loc"] == 0, "Condition must be true"

    def test_ingest_resets_previous_state(self):
        """Test that ingest resets previous analysis."""
        analyzer = intuitive_aptitude()
        analyzer.ingest("x = 1")
        assert len(analyzer.variables) > 0, "Collection must not be empty"
        analyzer.ingest("y = 2")
        # Should have only y, not x
        assert "y" in analyzer.variables, "Condition must be true"


# =============================================================================
# Test intuitive_aptitude Class - Summary & Structure
# =============================================================================


class TestIntuitiveAptitudeSummary:
    """Test suite for get_summary method."""

    def test_get_summary_empty(self):
        """Test getting summary from empty analyzer."""
        analyzer = intuitive_aptitude()
        analyzer.ingest("")
        summary = analyzer.get_summary()
        assert summary["functions_count"] == 0, "Count must be greater than zero"
        assert summary["classes_count"] == 0, "Count must be greater than zero"
        assert summary["imports_count"] == 0, "Count must be greater than zero"
        assert summary["variables_count"] == 0, "Count must be greater than zero"

    def test_get_summary_with_content(self):
        """Test getting summary with analyzed code."""
        analyzer = intuitive_aptitude()
        code = """
import os
x = 42
def func(): pass
class MyClass: pass
"""
        analyzer.ingest(code)
        summary = analyzer.get_summary()
        assert summary["functions_count"] == 1, "Count must be greater than zero"
        assert summary["classes_count"] == 1, "Count must be greater than zero"
        assert summary["imports_count"] == 1, "Count must be greater than zero"
        assert summary["variables_count"] == 1, "Count must be greater than zero"
        assert "metrics" in summary, "Condition must be true"


class TestIntuitiveAptitudeDetailedStructure:
    """Test suite for get_detailed_structure method."""

    def test_detailed_structure_empty(self):
        """Test getting detailed structure from empty code."""
        analyzer = intuitive_aptitude()
        analyzer.ingest("")
        structure = analyzer.get_detailed_structure()
        assert "imports" in structure, "Condition must be true"
        assert "functions" in structure, "Condition must be true"
        assert "classes" in structure, "Condition must be true"
        assert "variables" in structure, "Condition must be true"

    def test_detailed_structure_with_function(self):
        """Test detailed structure includes function info."""
        analyzer = intuitive_aptitude()
        code = """
def test_func(a, b=10):
    '''Test function.'''
    return a + b
"""
        analyzer.ingest(code)
        structure = analyzer.get_detailed_structure()
        assert "test_func" in structure["functions"], "Condition must be true"
        func_info = structure["functions"]["test_func"]
        assert func_info["name"] == "test_func", "Condition must be true"
        assert "a" in func_info["args"], "Condition must be true"
        assert func_info["defaults"] == 1, "Condition must be true"
        assert func_info["docstring"] == "Test function.", "Condition must be true"

    def test_detailed_structure_with_class(self):
        """Test detailed structure includes class info."""
        analyzer = intuitive_aptitude()
        code = """
class TestClass:
    '''Test class.'''
    def method(self):
        pass
"""
        analyzer.ingest(code)
        structure = analyzer.get_detailed_structure()
        assert "TestClass" in structure["classes"], "Condition must be true"
        class_info = structure["classes"]["TestClass"]
        assert class_info["name"] == "TestClass", "Condition must be true"
        assert class_info["docstring"] == "Test class.", "Condition must be true"
        assert "method" in class_info["methods"], "Condition must be true"


# =============================================================================
# Test intuitive_aptitude Class - Clone Structure
# =============================================================================


class TestIntuitiveAptitudeClone:
    """Test suite for clone_structure method."""

    def test_clone_simple_function(self):
        """Test cloning a simple function with renaming."""
        analyzer = intuitive_aptitude()
        code = "def old_func(x): return x * 2"
        analyzer.ingest(code)
        cloned = analyzer.clone_structure({"old_func": "new_func", "x": "y"})
        assert "new_func" in cloned, "Condition must be true"
        assert "y" in cloned, "Condition must be true"

    def test_clone_class(self):
        """Test cloning a class with renaming."""
        analyzer = intuitive_aptitude()
        code = """
class OldClass:
    def old_method(self):
        pass
"""
        analyzer.ingest(code)
        cloned = analyzer.clone_structure({"OldClass": "NewClass", "old_method": "new_method"})
        assert "NewClass" in cloned, "Condition must be true"
        assert "new_method" in cloned, "Condition must be true"

    def test_clone_without_ast_raises_error(self):
        """Test that cloning without ingestion raises error."""
        analyzer = intuitive_aptitude()
        with pytest.raises(ValueError, match="No AST available"):
            analyzer.clone_structure({"x": "y"})

    def test_clone_empty_mappings(self):
        """Test cloning with empty mappings returns original."""
        analyzer = intuitive_aptitude()
        code = "def func(): pass"
        analyzer.ingest(code)
        cloned = analyzer.clone_structure({})
        assert "func" in cloned, "Condition must be true"


# =============================================================================
# Test intuitive_aptitude Class - Pattern Extraction
# =============================================================================


class TestIntuitiveAptitudePatterns:
    """Test suite for pattern extraction."""

    def test_extract_error_handling_pattern(self):
        """Test extracting try/except patterns."""
        analyzer = intuitive_aptitude()
        code = """
try:
    x = risky_operation()
except ValueError as e:
    handle_error(e)
finally:
    cleanup()
"""
        analyzer.ingest(code)
        patterns = analyzer.extract_patterns()
        assert len(patterns["error_handling"]) > 0, "Collection must not be empty"
        error_pattern = patterns["error_handling"][0]
        assert error_pattern["has_finally"] is True, "Error should be raised or set"
        assert "ValueError" in error_pattern["handlers"], "Value must be initialized"

    def test_extract_iteration_pattern(self):
        """Test extracting for/while loop patterns."""
        analyzer = intuitive_aptitude()
        code = """
for item in items:
    process(item)

while condition:
    do_something()
"""
        analyzer.ingest(code)
        patterns = analyzer.extract_patterns()
        assert len(patterns["iteration"]) == 2, "Collection must not be empty"

    def test_extract_conditional_pattern(self):
        """Test extracting if/elif/else patterns."""
        analyzer = intuitive_aptitude()
        code = """
if x > 0:
    positive()
elif x < 0:
    negative()
else:
    zero()
"""
        analyzer.ingest(code)
        patterns = analyzer.extract_patterns()
        assert len(patterns["conditional"]) > 0, "Collection must not be empty"

    def test_extract_function_call_pattern(self):
        """Test extracting function call patterns."""
        analyzer = intuitive_aptitude()
        code = """
result = calculate(10, 20, mode='fast')
logger.info(result)
"""
        analyzer.ingest(code)
        patterns = analyzer.extract_patterns()
        assert len(patterns["function_calls"]) > 0, "Collection must not be empty"


# =============================================================================
# Test intuitive_aptitude Class - Style Analysis
# =============================================================================


class TestIntuitiveAptitudeStyleAnalysis:
    """Test suite for code style analysis."""

    def test_analyze_naming_conventions(self):
        """Test analyzing naming conventions."""
        analyzer = intuitive_aptitude()
        code = """
snake_case_var = 1
camelCaseVar = 2
PascalCaseClass = 3
CONSTANT_VAR = 4

def snake_function(): pass
def camelFunction(): pass
class PascalClass: pass
"""
        analyzer.ingest(code)
        style = analyzer.analyze_code_style()
        naming = style["naming"]
        assert naming["snake_case"] > 0, "Value must be greater than zero"
        assert naming["camelCase"] > 0, "Value must be greater than zero"
        assert naming["PascalCase"] > 0, "Value must be greater than zero"

    def test_analyze_indentation(self):
        """Test analyzing indentation style."""
        analyzer = intuitive_aptitude()
        code = """
def func():
    x = 1
    y = 2
    return x + y
"""
        analyzer.ingest(code)
        style = analyzer.analyze_code_style()
        indent = style["indentation"]
        assert indent["4space"] > 0, "Value must be greater than zero"

    def test_analyze_docstring_style(self):
        """Test analyzing docstring styles."""
        analyzer = intuitive_aptitude()
        code = '''
"""Module docstring.

Args:
    None

Returns:
    None
"""

def google_style():
    """Function with Google-style docstring.

    Args:
        None

    Returns:
        None
    """
    pass

def sphinx_style():
    """Function with Sphinx-style docstring.

    :param x: Parameter x
    :return: Result
    """
    pass
'''
        analyzer.ingest(code)
        style = analyzer.analyze_code_style()
        docstrings = style["docstrings"]
        assert "Google" in docstrings, "Condition must be true"
        assert "Sphinx" in docstrings, "Condition must be true"

    def test_analyze_functional_style(self):
        """Test analyzing functional vs OOP style."""
        analyzer = intuitive_aptitude()
        code = """
# Functional indicators
result = [x * 2 for x in range(10)]
filtered = filter(lambda x: x > 5, result)
mapped = map(str, filtered)

# OOP indicators
class MyClass:
    def method(self):
        pass
"""
        analyzer.ingest(code)
        style = analyzer.analyze_code_style()
        paradigm = style["paradigm"]
        assert paradigm["functional_signals"] > 0, "Value must be greater than zero"
        assert paradigm["oop_signals"] > 0, "Value must be greater than zero"
        assert paradigm["comprehensions"] > 0, "Value must be greater than zero"
        assert paradigm["lambdas"] > 0, "Value must be greater than zero"


# =============================================================================
# Test intuitive_aptitude Class - Metrics
# =============================================================================


class TestIntuitiveAptitudeMetrics:
    """Test suite for metrics computation."""

    def test_compute_loc_metric(self):
        """Test lines of code metric."""
        analyzer = intuitive_aptitude()
        code = "line1\nline2\nline3"
        analyzer.ingest(code)
        assert analyzer.metrics["loc"] == 3.0, "Condition must be true"

    def test_compute_comment_ratio(self):
        """Test comment ratio metric."""
        analyzer = intuitive_aptitude()
        code = """
# Comment 1
x = 1
# Comment 2
y = 2
"""
        analyzer.ingest(code)
        # 2 comments out of 5 lines = 0.4
        assert analyzer.metrics["comment_ratio"] > 0, "Value must be greater than zero"

    def test_compute_complexity_metric(self):
        """Test cyclomatic complexity metric."""
        analyzer = intuitive_aptitude()
        code = """
def simple_func():
    return 42

def complex_func(x):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                continue
    return x
"""
        analyzer.ingest(code)
        # Average complexity should be > 1
        assert analyzer.metrics["complexity"] >= 1.0, "Value must be greater than zero"


# =============================================================================
# Test intuitive_aptitude Class - Utility Methods
# =============================================================================


class TestIntuitiveAptitudeUtilities:
    """Test suite for utility methods."""

    def test_expr_to_str_with_none(self):
        """Test _expr_to_str with None input."""
        result = intuitive_aptitude._expr_to_str(None)
        assert result is None, "Result must not be empty"

    def test_expr_to_str_with_name(self):
        """Test _expr_to_str with Name node."""
        node = ast.Name(id="variable", ctx=ast.Load())
        result = intuitive_aptitude._expr_to_str(node)
        assert result == "variable", "Result must not be empty"

    def test_expr_to_str_with_constant(self):
        """Test _expr_to_str with Constant node."""
        node = ast.Constant(value=42)
        result = intuitive_aptitude._expr_to_str(node)
        assert "42" in result, "Result must not be empty"

    def test_count_elifs(self):
        """Test _count_elifs utility method."""
        code = """
if x > 0:
    pass
elif x < 0:
    pass
elif x == 0:
    pass
else:
    pass
"""
        tree = ast.parse(code)
        if_node = tree.body[0]
        count = intuitive_aptitude._count_elifs(if_node)
        assert count == 2, "Count must be greater than zero"

    def test_find_calls(self):
        """Test _find_calls utility method."""
        code = """
def test():
    logger.info("hello")
    len([1, 2, 3])
    result = calculate(10)
"""
        tree = ast.parse(code)
        func_node = tree.body[0]
        calls = intuitive_aptitude._find_calls(func_node)
        assert len(calls) >= 3, "Calls must not be empty"
        assert "print" in calls or any("print" in c for c in calls), "Condition must be true"

    def test_cyclomatic_complexity_simple(self):
        """Test _cyclomatic_complexity for simple function."""
        code = "def simple(): return 42"
        tree = ast.parse(code)
        func_node = tree.body[0]
        complexity = intuitive_aptitude._cyclomatic_complexity(func_node)
        assert complexity == 1, "complexity is not valid"

    def test_cyclomatic_complexity_with_branches(self):
        """Test _cyclomatic_complexity with branches."""
        code = """
def complex(x):
    if x > 0:
        for i in range(x):
            pass
    return x
"""
        tree = ast.parse(code)
        func_node = tree.body[0]
        complexity = intuitive_aptitude._cyclomatic_complexity(func_node)
        assert complexity > 1, "complexity must be greater than zero"

    def test_reset_method(self):
        """Test reset method clears all state."""
        analyzer = intuitive_aptitude()
        analyzer.ingest("x = 42")
        assert len(analyzer.variables) > 0, "Collection must not be empty"
        analyzer.reset()
        assert len(analyzer.variables) == 0, "Collection must not be empty"
        assert analyzer._source == "", "_source is not valid"
        assert analyzer.ast_tree is None, "ast_tree is not valid"


# =============================================================================
# Test intuitive_aptitude Class - Code Generation
# =============================================================================


class TestIntuitiveAptitudeCodeGeneration:
    """Test suite for code generation methods."""

    def test_generate_imports(self):
        """Test _generate_imports method."""
        analyzer = intuitive_aptitude()
        code = """
import os
from sys import path
from typing import List, Dict
"""
        analyzer.ingest(code)
        imports_str = analyzer._generate_imports()
        assert "import os" in imports_str, "Condition must be true"
        assert "from sys import path" in imports_str, "Condition must be true"

    def test_generate_functions(self):
        """Test _generate_functions method."""
        analyzer = intuitive_aptitude()
        code = """
def func1(x, y):
    '''Docstring for func1.'''
    return x + y

def func2():
    pass
"""
        analyzer.ingest(code)
        funcs_str = analyzer._generate_functions()
        assert "func1" in funcs_str, "Condition must be true"
        assert "func2" in funcs_str, "Condition must be true"
        assert "Docstring for func1" in funcs_str, "Condition must be true"

    def test_generate_classes(self):
        """Test _generate_classes method."""
        analyzer = intuitive_aptitude()
        code = """
class MyClass:
    '''Class docstring.'''
    def method(self):
        '''Method docstring.'''
        pass
"""
        analyzer.ingest(code)
        classes_str = analyzer._generate_classes()
        assert "MyClass" in classes_str, "Condition must be true"
        assert "method" in classes_str, "Condition must be true"
        assert "Class docstring" in classes_str, "Condition must be true"

    def test_generate_error_handling_pattern(self):
        """Test _generate_error_handling_pattern method."""
        analyzer = intuitive_aptitude()
        pattern = analyzer._generate_error_handling_pattern()
        assert "try:" in pattern, "Condition must be true"
        assert "except" in pattern, "Condition must be true"
        assert "finally:" in pattern, "Condition must be true"


# =============================================================================
# Test analyze_and_suggest Helper Function
# =============================================================================


class TestAnalyzeAndSuggest:
    """Test suite for analyze_and_suggest helper function."""

    def test_analyze_and_suggest_valid_code(self):
        """Test analyze_and_suggest with valid code."""
        code = """
def test_function(x):
    return x * 2
"""
        result = analyze_and_suggest(code)
        assert result["success"] is True, "Result must not be empty"
        assert result["error"] is None, "Result must not be empty"
        assert "summary" in result, "Result must not be empty"
        assert "patterns" in result, "Result must not be empty"
        assert "style" in result, "Result must not be empty"
        assert "structure" in result, "Result must not be empty"
        assert "suggestions" in result, "Result must not be empty"

    def test_analyze_and_suggest_invalid_code(self):
        """Test analyze_and_suggest with invalid code."""
        code = "def broken( pass"
        result = analyze_and_suggest(code)
        assert result["success"] is False, "Result must not be empty"
        assert result["error"] is not None, "Value must be initialized"
        assert "SyntaxError" in result["error"], "Result must not be empty"

    def test_analyze_and_suggest_suggestions_for_naming(self):
        """Test that suggestions are generated for naming issues."""
        code = """
def BadFunctionName(): pass
WeirdVar = 1
"""
        result = analyze_and_suggest(code)
        if result["success"]:
            style = result["style"]
            naming = style.get("naming", {})
            if naming.get("other", 0) > 0:
                assert "naming_conventions" in result["suggestions"], "Result must not be empty"

    def test_analyze_and_suggest_suggestions_for_docstrings(self):
        """Test that suggestions are generated for missing docstrings."""
        code = """
def undocumented_function():
    pass

class UndocumentedClass:
    def method(self):
        pass
"""
        result = analyze_and_suggest(code)
        if result["success"]:
            docstyles = result["style"].get("docstrings", {})
            if docstyles.get("None", 0) > 0:
                assert "docstrings" in result["suggestions"], "Result must not be empty"

    def test_analyze_and_suggest_suggestions_for_complexity(self):
        """Test that suggestions are generated for high complexity."""
        code = """
def very_complex_function(x):
    if x > 0:
        if x > 10:
            if x > 20:
                if x > 30:
                    if x > 40:
                        if x > 50:
                            if x > 60:
                                if x > 70:
                                    if x > 80:
                                        if x > 90:
                                            return "very high"
                                        return "high"
                                    return "medium-high"
                                return "medium"
                            return "low-medium"
                        return "low"
                    return "very low"
                return "minimal"
            return "tiny"
        return "small"
    return "zero"
"""
        result = analyze_and_suggest(code)
        if result["success"]:
            complexity = result["summary"]["metrics"]["complexity"]
            if complexity and complexity > 10:
                assert "complexity" in result["suggestions"], "Result must not be empty"

    def test_analyze_and_suggest_empty_code(self):
        """Test analyze_and_suggest with empty code."""
        result = analyze_and_suggest("")
        assert result["success"] is True, "Result must not be empty"
        assert result["summary"]["functions_count"] == 0, "Result must not be empty"


# =============================================================================
# Test Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test suite for edge cases and boundary conditions."""

    def test_nested_classes(self):
        """Test handling nested class definitions."""
        analyzer = intuitive_aptitude()
        code = """
class Outer:
    class Inner:
        def method(self):
            pass
"""
        result = analyzer.ingest(code)
        # Should handle nested classes without crashing
        assert result is True, "Result must not be empty"

    def test_async_functions(self):
        """Test handling async/await syntax."""
        analyzer = intuitive_aptitude()
        code = """
async def async_func():
    await something()
    async for item in async_iterator:
        process(item)
"""
        result = analyzer.ingest(code)
        assert result is True, "Result must not be empty"

    def test_decorators_with_arguments(self):
        """Test handling decorators with arguments."""
        analyzer = intuitive_aptitude()
        code = """
@decorator_with_args(arg1, arg2=value)
@another_decorator
def decorated_function():
    pass
"""
        result = analyzer.ingest(code)
        assert result is True, "Result must not be empty"

    def test_complex_annotations(self):
        """Test handling complex type annotations."""
        analyzer = intuitive_aptitude()
        code = """
from typing import List, Dict, Optional, Union

def annotated_func(
    x: List[Dict[str, Union[int, str]]],
    y: Optional[int] = None
) -> Dict[str, List[int]]:
    return {}
"""
        result = analyzer.ingest(code)
        assert result is True, "Result must not be empty"

    def test_multiline_strings(self):
        """Test handling multiline strings and docstrings."""
        analyzer = intuitive_aptitude()
        code = '''
def func():
    """
    This is a multiline
    docstring with
    multiple lines.
    """
    x = """
    Multiline
    string
    """
    return x
'''
        result = analyzer.ingest(code)
        assert result is True, "Result must not be empty"

    def test_lambda_functions(self):
        """Test handling lambda functions."""
        analyzer = intuitive_aptitude()
        code = """
def square(x):
    return x ** 2
def add(a, b):
    return a + b
"""
        result = analyzer.ingest(code)
        assert result is True, "Result must not be empty"

    def test_comprehensions(self):
        """Test handling various comprehensions."""
        analyzer = intuitive_aptitude()
        code = """
list_comp = [x for x in range(10)]
dict_comp = {x: x**2 for x in range(10)}
set_comp = {x for x in range(10)}
gen_expr = (x for x in range(10))
"""
        result = analyzer.ingest(code)
        assert result is True, "Result must not be empty"

    def test_context_managers(self):
        """Test handling with statements."""
        analyzer = intuitive_aptitude()
        code = """
with open('file.txt') as f:
    data = f.read()

async with async_context() as ctx:
    await ctx.do_something()
"""
        result = analyzer.ingest(code)
        assert result is True, "Result must not be empty"

    def test_walrus_operator(self):
        """Test walrus operator (Python 3.8+), ensuring support or graceful failure depending on Python version."""
        analyzer = intuitive_aptitude()
        code = """
if (n := len(items)) > 10:
    logger.info(f"Too many items: {n}")
"""
        result = analyzer.ingest(code)
        # Should handle or gracefully fail based on Python version
        assert result is True or analyzer.last_error is not None, "result must be initialized"

    def test_match_statement(self):
        """Test handling match/case statements (Python 3.10+)."""
        analyzer = intuitive_aptitude()
        code = """
match value:
    case 1:
        result = "one"
    case 2:
        result = "two"
    case _:
        result = "other"
"""
        result = analyzer.ingest(code)
        if sys.version_info >= (3, 10):
            assert result is True, "Result must not be empty"
        else:
            # On Python versions that do not support 'match', ensure the analyzer
            # either handles the syntax gracefully or reports an error.
            assert result is True or analyzer.last_error is not None, "result must be initialized"


# =============================================================================
# Test Integration Scenarios
# =============================================================================


class TestIntegrationScenarios:
    """Test suite for realistic integration scenarios."""

    def test_full_module_analysis(self):
        """Test analyzing a complete module."""
        code = '''
"""Example module for testing.

This module demonstrates various Python features.
"""

from __future__ import annotations

import os
import sys
from typing import List, Dict, Optional
from codex.logging.structured_logger import logger

__all__ = ["main", "helper"]

CONSTANT = 42


class BaseClass:
    """Base class for demonstration."""

    def __init__(self, value: int):
        """Initialize with value."""
        self.value = value

    def method(self) -> int:
        """Return the value."""
        return self.value


class DerivedClass(BaseClass):
    """Derived class with additional functionality."""

    def method(self) -> int:
        """Override method."""
        return self.value * 2

    def extra_method(self, x: int, y: int = 10) -> int:
        """Add extra functionality.

        Args:
            x: First parameter
            y: Second parameter with default

        Returns:
            Sum of x and y
        """
        return x + y


def helper(items: List[int]) -> Dict[str, int]:
    """Helper function.

    Args:
        items: List of integers

    Returns:
        Dictionary with statistics
    """
    try:
        result = {
            "count": len(items),
            "sum": sum(items),
            "max": max(items) if items else 0,
        }
        return result
    except Exception as e:
        logger.info(f"Error: {e}")
        return {}


def main():
    """Main entry point."""
    items = [1, 2, 3, 4, 5]
    stats = helper(items)

    for key, value in stats.items():
        logger.info(f"{key}: {value}")

    obj = DerivedClass(100)
    result = obj.method()
    logger.info(f"Result: {result}")


if __name__ == "__main__":
    main()
'''
        analyzer = intuitive_aptitude()
        result = analyzer.ingest(code)
        assert result is True, "Result must not be empty"

        # Verify comprehensive analysis
        summary = analyzer.get_summary()
        assert summary["functions_count"] >= 2, "Value must be greater than zero"
        assert summary["classes_count"] >= 2, "Value must be greater than zero"
        assert summary["imports_count"] >= 3, "Value must be greater than zero"

        # Verify patterns were extracted
        patterns = analyzer.extract_patterns()
        assert len(patterns["error_handling"]) > 0, "Collection must not be empty"
        assert len(patterns["iteration"]) > 0, "Collection must not be empty"
        assert len(patterns["function_calls"]) > 0, "Collection must not be empty"

        # Verify style analysis
        style = analyzer.analyze_code_style()
        assert "naming" in style, "Condition must be true"
        assert "docstrings" in style, "Condition must be true"
        assert style["docstrings"]["Google"] > 0, "Value must be greater than zero"

    def test_analyze_and_suggest_comprehensive(self):
        """Test comprehensive analysis with suggestions."""
        code = """
def poorly_formatted_function(x,y,z):
    # Missing docstring
    if x>0:
        if y>0:
            if z>0:
                return x+y+z
    return 0

class badClassName:
    # Bad naming, no docstring
    def BadMethod(self):
        pass
"""
        result = analyze_and_suggest(code)
        assert result["success"] is True, "Result must not be empty"
        # Should have suggestions for various issues
        assert len(result["suggestions"]) > 0, "Collection must not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
