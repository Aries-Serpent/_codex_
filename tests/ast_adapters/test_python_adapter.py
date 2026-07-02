"""Tests for Python AST adapter."""

from pathlib import Path

import pytest

pytest.importorskip("libcst", reason="libcst optional dependency not installed")

from codex.ast_adapters.python_adapter import PythonASTAdapter


def test_python_adapter_initialization():
    """Test PythonASTAdapter initialization."""
    adapter = PythonASTAdapter()

    assert adapter.file_path is None, "file_path is not valid"
    assert adapter.root_node is None, "root_node is not valid"
    assert adapter._cst_tree is None, "_cst_tree is not valid"


def test_python_adapter_parse_simple_function():
    """Test parsing a simple function."""
    source = """
def hello_world():
    \"\"\"A simple function.\"\"\"
    logger.info("Hello, World!")
"""

    adapter = PythonASTAdapter()
    root = adapter.parse(source)

    assert root is not None, "root must be initialized"
    assert root.node_type == "module", "node_type is not valid"
    assert len(root.children) > 0, "Collection must not be empty"

    # Find the function
    functions = adapter.find_nodes_by_type("function")
    assert len(functions) == 1, "Functions must not be empty"
    assert functions[0].name == "hello_world", "name is not valid"


def test_python_adapter_parse_class():
    """Test parsing a class definition."""
    source = """
class TestClass:
    \"\"\"A test class.\"\"\"

    def method1(self):
        pass

    def method2(self, arg1: str) -> int:
        return 42
"""

    adapter = PythonASTAdapter()
    adapter.parse(source)

    # Find the class
    classes = adapter.find_nodes_by_type("class")
    assert len(classes) == 1, "Classes must not be empty"
    assert classes[0].name == "TestClass", "name is not valid"

    # Find methods
    functions = adapter.find_nodes_by_type("function")
    assert len(functions) == 2, "Functions must not be empty"


def test_python_adapter_parse_with_decorators():
    """Test parsing functions with decorators."""
    source = """
@decorator1
@decorator2
def decorated_function():
    pass
"""

    adapter = PythonASTAdapter()
    adapter.parse(source)

    functions = adapter.find_nodes_by_type("function")
    assert len(functions) == 1, "Functions must not be empty"

    func = functions[0]
    assert "decorators" in func.metadata, "Data must not be empty"
    assert len(func.metadata["decorators"]) == 2, "Collection must not be empty"


def test_python_adapter_parse_with_type_hints():
    """Test parsing function with type hints."""
    source = """
def typed_function(name: str, age: int = 0) -> str:
    return f"{name} is {age}"
"""

    adapter = PythonASTAdapter()
    adapter.parse(source)

    functions = adapter.find_nodes_by_type("function")
    assert len(functions) == 1, "Functions must not be empty"

    func = functions[0]
    assert "parameters" in func.metadata, "Data must not be empty"
    assert len(func.metadata["parameters"]) == 2, "Collection must not be empty"
    assert "return_type" in func.metadata, "Data must not be empty"


def test_python_adapter_parse_imports():
    """Test parsing import statements."""
    source = """
import os
import sys
from pathlib import Path
from typing import Dict, List
from codex.logging.structured_logger import logger
"""

    adapter = PythonASTAdapter()
    adapter.parse(source)

    imports = adapter.find_nodes_by_type("import")
    import_froms = adapter.find_nodes_by_type("import_from")

    assert len(imports) >= 2, "Imports must not be empty"
    assert len(import_froms) >= 1, "Import_froms must not be empty"


def test_python_adapter_parse_assignments():
    """Test parsing variable assignments."""
    source = """
x = 42
y = "hello"
z = [1, 2, 3]
"""

    adapter = PythonASTAdapter()
    adapter.parse(source)

    assignments = adapter.find_nodes_by_type("assignment")
    assert len(assignments) >= 3, "Assignments must not be empty"


def test_python_adapter_parse_invalid_syntax():
    """Test parsing invalid Python code."""
    source = """
def invalid syntax here
"""

    adapter = PythonASTAdapter()

    with pytest.raises(SyntaxError):
        adapter.parse(source)


def test_python_adapter_get_stats():
    """Test getting AST statistics."""
    source = """
class MyClass:
    def method1(self):
        pass

    def method2(self):
        pass

def standalone_function():
    pass
"""

    adapter = PythonASTAdapter()
    adapter.parse(source)

    stats = adapter.get_stats()

    assert "module" in stats, "Condition must be true"
    assert stats["module"] == 1, "Condition must be true"
    assert "class" in stats, "Condition must be true"
    assert stats["class"] == 1, "Condition must be true"
    assert "function" in stats, "Condition must be true"
    assert stats["function"] == 3, "Condition must be true"


def test_python_adapter_traverse():
    """Test AST traversal."""
    source = """
class OuterClass:
    class InnerClass:
        def inner_method(self):
            pass

    def outer_method(self):
        pass
"""

    adapter = PythonASTAdapter()
    root = adapter.parse(source)

    all_nodes = adapter.traverse()

    assert len(all_nodes) > 0, "All_nodes must not be empty"
    assert root in all_nodes, "Condition must be true"


def test_python_adapter_extract_docstring():
    """Test docstring extraction."""
    source = '''
def documented_function():
    """
    This is a comprehensive docstring.

    It has multiple lines.
    """
    pass
'''

    adapter = PythonASTAdapter()
    adapter.parse(source)

    functions = adapter.find_nodes_by_type("function")
    assert len(functions) == 1, "Functions must not be empty"

    func = functions[0]
    assert "docstring" in func.metadata, "Data must not be empty"
    assert "comprehensive" in func.metadata["docstring"], "Data must not be empty"


def test_python_adapter_extract_class_bases():
    """Test base class extraction."""
    source = """
class DerivedClass(BaseClass, MixinClass):
    pass
"""

    adapter = PythonASTAdapter()
    adapter.parse(source)

    classes = adapter.find_nodes_by_type("class")
    assert len(classes) == 1, "Classes must not be empty"

    cls = classes[0]
    assert "bases" in cls.metadata, "Data must not be empty"
    assert len(cls.metadata["bases"]) == 2, "Collection must not be empty"


def test_python_adapter_real_file():
    """Test parsing this test file itself."""
    adapter = PythonASTAdapter()
    test_file = Path(__file__)

    if test_file.exists():
        root = adapter.parse_file(test_file)

        assert root is not None, "root must be initialized"
        assert root.node_type == "module", "node_type is not valid"

        # This file should have multiple test functions
        functions = adapter.find_nodes_by_type("function")
        assert len(functions) > 10, "Functions must not be empty"
