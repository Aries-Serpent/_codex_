"""
Tests for codex.ast.node module.

This module contains tests for standardized AST node representation.
"""

from pathlib import Path


class TestNodeType:
    """Tests for NodeType enum."""

    def test_module_type(self):
        """Test MODULE type."""
        from codex.ast.node import NodeType

        assert NodeType.MODULE.value == "module", "Value must be initialized"

    def test_function_type(self):
        """Test FUNCTION type."""
        from codex.ast.node import NodeType

        assert NodeType.FUNCTION.value == "function", "Value must be initialized"

    def test_class_type(self):
        """Test CLASS type."""
        from codex.ast.node import NodeType

        assert NodeType.CLASS.value == "class", "Value must be initialized"

    def test_all_types_exist(self):
        """Test all expected types exist."""
        from codex.ast.node import NodeType

        types = [
            "MODULE",
            "FUNCTION",
            "ASYNC_FUNCTION",
            "CLASS",
            "LAMBDA",
            "IMPORT",
            "FROM_IMPORT",
            "STATEMENT",
            "EXPRESSION",
            "DECORATOR",
            "COMPREHENSION",
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
            column_end=20,
        )

        assert loc.file_path == Path("/path/to/file.py"), "file_path is not valid"
        assert loc.line_start == 10, "line_start is not valid"
        assert loc.column_start == 5, "column_start is not valid"
        assert loc.line_end == 15, "line_end is not valid"
        assert loc.column_end == 20, "column_end is not valid"

    def test_str_representation(self):
        """Test __str__ method."""
        from codex.ast.node import SourceLocation

        loc = SourceLocation(
            file_path=Path("src/module.py"),
            line_start=42,
            column_start=8,
            line_end=50,
            column_end=0,
        )

        result = str(loc)

        assert "src/module.py" in result, "Result must not be empty"
        assert "42" in result, "Result must not be empty"
        assert "8" in result, "Result must not be empty"


class TestStandardizedASTNode:
    """Tests for StandardizedASTNode dataclass."""

    def test_basic_creation(self):
        """Test StandardizedASTNode basic creation."""
        from codex.ast.node import NodeType, SourceLocation, StandardizedASTNode

        loc = SourceLocation(
            file_path=Path("test.py"), line_start=1, column_start=0, line_end=10, column_end=0
        )

        node = StandardizedASTNode(
            node_id="node_1", type=NodeType.FUNCTION, name="my_function", source_location=loc
        )

        assert node.node_id == "node_1", "node_id is not valid"
        assert node.type == NodeType.FUNCTION, "type is not valid"
        assert node.name == "my_function", "name is not valid"
        assert node.children == [], "children is not valid"
        assert node.parent is None, "parent is not valid"
        assert node.docstring is None, "docstring is not valid"
        assert node.decorators == [], "decorators is not valid"
        assert node.type_hints == {}, "type_hints is not valid"
        assert node.metadata == {}, "Data must not be empty"

    def test_with_docstring(self):
        """Test node with docstring."""
        from codex.ast.node import NodeType, SourceLocation, StandardizedASTNode

        loc = SourceLocation(Path("t.py"), 1, 0, 5, 0)

        node = StandardizedASTNode(
            node_id="n1",
            type=NodeType.CLASS,
            name="MyClass",
            source_location=loc,
            docstring="This is a test class.",
        )

        assert node.docstring == "This is a test class.", "docstring is not valid"

    def test_with_decorators(self):
        """Test node with decorators."""
        from codex.ast.node import NodeType, SourceLocation, StandardizedASTNode

        loc = SourceLocation(Path("t.py"), 1, 0, 5, 0)

        node = StandardizedASTNode(
            node_id="n1",
            type=NodeType.FUNCTION,
            name="decorated_func",
            source_location=loc,
            decorators=["@staticmethod", "@lru_cache"],
        )

        assert len(node.decorators) == 2, "Collection must not be empty"
        assert "@staticmethod" in node.decorators, "Condition must be true"

    def test_add_child(self):
        """Test add_child method."""
        from codex.ast.node import NodeType, SourceLocation, StandardizedASTNode

        loc = SourceLocation(Path("t.py"), 1, 0, 10, 0)

        parent = StandardizedASTNode(
            node_id="parent", type=NodeType.MODULE, name="module", source_location=loc
        )

        child = StandardizedASTNode(
            node_id="child", type=NodeType.FUNCTION, name="func", source_location=loc
        )

        parent.add_child(child)

        assert len(parent.children) == 1, "Collection must not be empty"
        assert parent.children[0] is child, "Condition must be true"
        assert child.parent is parent, "parent is not valid"

    def test_add_multiple_children(self):
        """Test adding multiple children."""
        from codex.ast.node import NodeType, SourceLocation, StandardizedASTNode

        loc = SourceLocation(Path("t.py"), 1, 0, 10, 0)

        parent = StandardizedASTNode("p", NodeType.MODULE, "mod", loc)
        child1 = StandardizedASTNode("c1", NodeType.CLASS, "Class1", loc)
        child2 = StandardizedASTNode("c2", NodeType.CLASS, "Class2", loc)

        parent.add_child(child1)
        parent.add_child(child2)

        assert len(parent.children) == 2, "Collection must not be empty"
        assert child1.parent is parent, "parent is not valid"
        assert child2.parent is parent, "parent is not valid"

    def test_type_hints(self):
        """Test node with type hints."""
        from codex.ast.node import NodeType, SourceLocation, StandardizedASTNode

        loc = SourceLocation(Path("t.py"), 1, 0, 5, 0)

        node = StandardizedASTNode(
            node_id="n1",
            type=NodeType.FUNCTION,
            name="typed_func",
            source_location=loc,
            type_hints={"x": "int", "y": "str", "return": "bool"},
        )

        assert node.type_hints["x"] == "int", "Condition must be true"
        assert node.type_hints["return"] == "bool", "Condition must be true"

    def test_metadata(self):
        """Test node with metadata."""
        from codex.ast.node import NodeType, SourceLocation, StandardizedASTNode

        loc = SourceLocation(Path("t.py"), 1, 0, 5, 0)

        node = StandardizedASTNode(
            node_id="n1",
            type=NodeType.FUNCTION,
            name="func",
            source_location=loc,
            metadata={"complexity": 5, "is_public": True},
        )

        assert node.metadata["complexity"] == 5, "Data must not be empty"
        assert node.metadata["is_public"] is True, "Data must not be empty"
