"""Tests for Universal Parser module."""

from pathlib import Path

import pytest

from codex.ast.node import NodeType
from codex.ast.parser import ParseError, UniversalParser, parse_python


class TestUniversalParser:
    """Tests for UniversalParser class."""

    def test_parse_simple_function(self):
        """Test parsing a simple function definition."""
        code = '''
def hello(name: str) -> str:
    """Say hello."""
    return f"Hello, {name}!"
'''
        parser = UniversalParser()
        result = parser.parse_string(code)

        assert result is not None, "result must be initialized"
        assert result.type == NodeType.MODULE, "Result must not be empty"
        assert len(result.children) >= 1, "Collection must not be empty"

        # Find function node
        func = next((c for c in result.children if c.type == NodeType.FUNCTION), None)
        assert func is not None, "func must be initialized"
        assert func.name == "hello", "name is not valid"

    def test_parse_class(self):
        """Test parsing a class definition."""
        code = '''
class MyClass:
    """A sample class."""

    def __init__(self, value):
        self.value = value

    def get_value(self):
        return self.value
'''
        parser = UniversalParser()
        result = parser.parse_string(code)

        assert result is not None, "result must be initialized"
        classes = [c for c in result.children if c.type == NodeType.CLASS]
        assert len(classes) == 1, "Classes must not be empty"
        assert classes[0].name == "MyClass", "name is not valid"

    def test_parse_async_function(self):
        """Test parsing async function."""
        code = '''
async def fetch_data():
    """Fetch data asynchronously."""
    pass
'''
        parser = UniversalParser()
        result = parser.parse_string(code)

        assert result is not None, "result must be initialized"
        async_funcs = [c for c in result.children if c.type == NodeType.ASYNC_FUNCTION]
        assert len(async_funcs) == 1, "Async_funcs must not be empty"
        assert async_funcs[0].name == "fetch_data", "Data must not be empty"

    def test_parse_imports(self):
        """Test parsing import statements."""
        code = """
import os
from pathlib import Path
"""
        parser = UniversalParser(use_libcst=False)  # Use ast for import parsing
        result = parser.parse_string(code)

        assert result is not None, "result must be initialized"
        imports = [c for c in result.children if c.type in (NodeType.IMPORT, NodeType.FROM_IMPORT)]
        assert len(imports) == 2, "Imports must not be empty"

    def test_parse_with_decorators(self):
        """Test parsing decorated functions."""
        code = """
@staticmethod
@decorator_with_args(param=True)
def decorated_func():
    pass
"""
        parser = UniversalParser()
        result = parser.parse_string(code)

        assert result is not None, "result must be initialized"
        funcs = [c for c in result.children if c.type == NodeType.FUNCTION]
        assert len(funcs) == 1, "Funcs must not be empty"
        assert len(funcs[0].decorators) >= 1, "Collection must not be empty"

    def test_parse_with_type_hints(self):
        """Test extraction of type hints."""
        code = """
def typed_func(x: int, y: str = "default") -> bool:
    return True
"""
        parser = UniversalParser(use_libcst=False)  # Use ast for predictable hints
        result = parser.parse_string(code)

        assert result is not None, "result must be initialized"
        funcs = [c for c in result.children if c.type == NodeType.FUNCTION]
        assert len(funcs) == 1, "Funcs must not be empty"
        assert "return" in funcs[0].type_hints, "Condition must be true"
        assert funcs[0].type_hints["return"] == "bool", "Condition must be true"

    def test_parse_file(self, tmp_path: Path):
        """Test parsing a Python file."""
        test_file = tmp_path / "sample.py"
        test_file.write_text('''
def sample():
    """Sample function."""
    pass
''')
        parser = UniversalParser()
        result = parser.parse_file(test_file)

        assert result is not None, "result must be initialized"
        assert result.name == "sample", "Result must not be empty"

    def test_parse_nonexistent_file(self):
        """Test handling of nonexistent file."""
        parser = UniversalParser()
        result = parser.parse_file("/nonexistent/path.py")
        assert result is None, "Result must not be empty"

    def test_parse_nonexistent_file_strict(self):
        """Test strict mode raises error for nonexistent file."""
        parser = UniversalParser(strict=True)
        with pytest.raises(ParseError):
            parser.parse_file("/nonexistent/path.py")

    def test_parse_syntax_error(self):
        """Test handling of syntax errors."""
        code = "def broken(:"
        parser = UniversalParser()
        result = parser.parse_string(code)
        assert result is None, "Result must not be empty"

    def test_parse_syntax_error_strict(self):
        """Test strict mode raises error for syntax errors."""
        code = "def broken(:"
        parser = UniversalParser(strict=True)
        with pytest.raises(ParseError):
            parser.parse_string(code)

    def test_fallback_to_ast(self):
        """Test fallback to stdlib ast when libcst disabled."""
        code = "def simple(): pass"
        parser = UniversalParser(use_libcst=False)
        result = parser.parse_string(code)

        assert result is not None, "result must be initialized"
        assert result.metadata.get("parser") == "ast", "Result must not be empty"

    def test_node_metadata(self):
        """Test that parsed nodes include metadata."""
        code = "def func(): pass"
        parser = UniversalParser()
        result = parser.parse_string(code)

        assert result is not None, "result must be initialized"
        assert "parser" in result.metadata, "Result must not be empty"
        assert "hash" in result.metadata, "Result must not be empty"

    def test_source_location(self):
        """Test source location information."""
        code = """
def first():
    pass

def second():
    pass
"""
        parser = UniversalParser(use_libcst=False)
        result = parser.parse_string(code)

        assert result is not None, "result must be initialized"
        funcs = [c for c in result.children if c.type == NodeType.FUNCTION]
        assert len(funcs) == 2, "Funcs must not be empty"

        # First function should be on earlier line
        assert funcs[0].source_location.line_start < funcs[1].source_location.line_start, "line_start is not valid"

    def test_node_id_uniqueness(self):
        """Test that generated node IDs are unique."""
        code = """
def a(): pass
def b(): pass
def c(): pass
"""
        parser = UniversalParser()
        result = parser.parse_string(code)

        assert result is not None, "result must be initialized"
        node_ids = [result.node_id]
        for child in result.children:
            node_ids.append(child.node_id)

        # All IDs should be unique
        assert len(node_ids) == len(set(node_ids)), "Node_ids must not be empty"


class TestParseFunction:
    """Tests for parse_python convenience function."""

    def test_parse_string(self):
        """Test parsing a string."""
        result = parse_python("def func(): pass")
        assert result is not None, "result must be initialized"
        assert result.type == NodeType.MODULE, "Result must not be empty"

    def test_parse_file(self, tmp_path: Path):
        """Test parsing a file path."""
        test_file = tmp_path / "test.py"
        test_file.write_text("class Test: pass")

        result = parse_python(test_file)
        assert result is not None, "result must be initialized"

    def test_parse_path_string(self, tmp_path: Path):
        """Test parsing with string path."""
        test_file = tmp_path / "test.py"
        test_file.write_text("x = 1")

        result = parse_python(str(test_file))
        assert result is not None, "result must be initialized"
