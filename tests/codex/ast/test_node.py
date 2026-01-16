"""
Tests for codex.ast.node module.

This module contains tests for standardized AST node representation.
"""

import pytest
from pathlib import Path


class TestNodeType:
    """Tests for NodeType enum."""

    def test_module_type(self):
        """Test MODULE type."""
        from codex.ast.node import NodeType
        
        assert NodeType.MODULE.value == "module"

    def test_function_type(self):
        """Test FUNCTION type."""
        from codex.ast.node import NodeType
        
        assert NodeType.FUNCTION.value == "function"

    def test_class_type(self):
        """Test CLASS type."""
        from codex.ast.node import NodeType
        
        assert NodeType.CLASS.value == "class"

    def test_all_types_exist(self):
        """Test all expected types exist."""
        from codex.ast.node import NodeType
        
        types = [
            "MODULE", "FUNCTION", "ASYNC_FUNCTION", "CLASS", 
            "LAMBDA", "IMPORT", "FROM_IMPORT", "STATEMENT",
            "EXPRESSION", "DECORATOR", "COMPREHENSION"
        ]
        
        for type_name in types:
            assert hasattr(NodeType, type_name)


class TestSourceLocation:
    """Tests for SourceLocation dataclass."""

    def test_basic_creation(self):
        """Test SourceLocation basic creation."""
        from codex.ast.node import SourceLocation
        
        loc = SourceLocation(
            file_path=Path("/path/to/file.py"),
            line_start=10,
            column_start=5,
            line_end=15,
            column_end=20
        )
        
        assert loc.file_path == Path("/path/to/file.py")
        assert loc.line_start == 10
        assert loc.column_start == 5
        assert loc.line_end == 15
        assert loc.column_end == 20

    def test_str_representation(self):
        """Test __str__ method."""
        from codex.ast.node import SourceLocation
        
        loc = SourceLocation(
            file_path=Path("src/module.py"),
            line_start=42,
            column_start=8,
            line_end=50,
            column_end=0
        )
        
        result = str(loc)
        
        assert "src/module.py" in result
        assert "42" in result
        assert "8" in result


class TestStandardizedASTNode:
    """Tests for StandardizedASTNode dataclass."""

    def test_basic_creation(self):
        """Test StandardizedASTNode basic creation."""
        from codex.ast.node import StandardizedASTNode, NodeType, SourceLocation
        
        loc = SourceLocation(
            file_path=Path("test.py"),
            line_start=1,
            column_start=0,
            line_end=10,
            column_end=0
        )
        
        node = StandardizedASTNode(
            node_id="node_1",
            type=NodeType.FUNCTION,
            name="my_function",
            source_location=loc
        )
        
        assert node.node_id == "node_1"
        assert node.type == NodeType.FUNCTION
        assert node.name == "my_function"
        assert node.children == []
        assert node.parent is None
        assert node.docstring is None
        assert node.decorators == []
        assert node.type_hints == {}
        assert node.metadata == {}

    def test_with_docstring(self):
        """Test node with docstring."""
        from codex.ast.node import StandardizedASTNode, NodeType, SourceLocation
        
        loc = SourceLocation(Path("t.py"), 1, 0, 5, 0)
        
        node = StandardizedASTNode(
            node_id="n1",
            type=NodeType.CLASS,
            name="MyClass",
            source_location=loc,
            docstring="This is a test class."
        )
        
        assert node.docstring == "This is a test class."

    def test_with_decorators(self):
        """Test node with decorators."""
        from codex.ast.node import StandardizedASTNode, NodeType, SourceLocation
        
        loc = SourceLocation(Path("t.py"), 1, 0, 5, 0)
        
        node = StandardizedASTNode(
            node_id="n1",
            type=NodeType.FUNCTION,
            name="decorated_func",
            source_location=loc,
            decorators=["@staticmethod", "@lru_cache"]
        )
        
        assert len(node.decorators) == 2
        assert "@staticmethod" in node.decorators

    def test_add_child(self):
        """Test add_child method."""
        from codex.ast.node import StandardizedASTNode, NodeType, SourceLocation
        
        loc = SourceLocation(Path("t.py"), 1, 0, 10, 0)
        
        parent = StandardizedASTNode(
            node_id="parent",
            type=NodeType.MODULE,
            name="module",
            source_location=loc
        )
        
        child = StandardizedASTNode(
            node_id="child",
            type=NodeType.FUNCTION,
            name="func",
            source_location=loc
        )
        
        parent.add_child(child)
        
        assert len(parent.children) == 1
        assert parent.children[0] is child
        assert child.parent is parent

    def test_add_multiple_children(self):
        """Test adding multiple children."""
        from codex.ast.node import StandardizedASTNode, NodeType, SourceLocation
        
        loc = SourceLocation(Path("t.py"), 1, 0, 10, 0)
        
        parent = StandardizedASTNode("p", NodeType.MODULE, "mod", loc)
        child1 = StandardizedASTNode("c1", NodeType.CLASS, "Class1", loc)
        child2 = StandardizedASTNode("c2", NodeType.CLASS, "Class2", loc)
        
        parent.add_child(child1)
        parent.add_child(child2)
        
        assert len(parent.children) == 2
        assert child1.parent is parent
        assert child2.parent is parent

    def test_type_hints(self):
        """Test node with type hints."""
        from codex.ast.node import StandardizedASTNode, NodeType, SourceLocation
        
        loc = SourceLocation(Path("t.py"), 1, 0, 5, 0)
        
        node = StandardizedASTNode(
            node_id="n1",
            type=NodeType.FUNCTION,
            name="typed_func",
            source_location=loc,
            type_hints={"x": "int", "y": "str", "return": "bool"}
        )
        
        assert node.type_hints["x"] == "int"
        assert node.type_hints["return"] == "bool"

    def test_metadata(self):
        """Test node with metadata."""
        from codex.ast.node import StandardizedASTNode, NodeType, SourceLocation
        
        loc = SourceLocation(Path("t.py"), 1, 0, 5, 0)
        
        node = StandardizedASTNode(
            node_id="n1",
            type=NodeType.FUNCTION,
            name="func",
            source_location=loc,
            metadata={"complexity": 5, "is_public": True}
        )
        
        assert node.metadata["complexity"] == 5
        assert node.metadata["is_public"] is True
