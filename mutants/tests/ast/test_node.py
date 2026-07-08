"""Tests for AST node module."""

from pathlib import Path

from codex.ast.node import NodeType, SourceLocation, StandardizedASTNode


def test_node_creation():
    """Test basic node creation."""
    loc = SourceLocation(Path("test.py"), 1, 0, 1, 10)
    node = StandardizedASTNode(
        node_id="func_1", type=NodeType.FUNCTION, name="test_func", source_location=loc
    )
    assert node.node_id == "func_1", "node_id is not valid"
    assert node.type == NodeType.FUNCTION, "type is not valid"
    assert node.name == "test_func", "name is not valid"


def test_node_serialization():
    """Test node to_dict serialization."""
    loc = SourceLocation(Path("test.py"), 1, 0, 5, 10)
    node = StandardizedASTNode(
        node_id="n1",
        type=NodeType.FUNCTION,
        name="test",
        source_location=loc,
        docstring="Test function",
        decorators=["@decorator"],
        type_hints={"x": "int", "return": "str"},
    )
    data = node.to_dict()
    assert data["node_id"] == "n1", "Data must not be empty"
    assert data["type"] == "function", "Data must not be empty"
    assert data["docstring"] == "Test function", "Data must not be empty"
    assert len(data["decorators"]) == 1, "Collection must not be empty"


def test_parent_child_relationship():
    """Test parent-child node relationships."""
    parent_loc = SourceLocation(Path("test.py"), 1, 0, 10, 0)
    parent = StandardizedASTNode("m1", NodeType.MODULE, "test_module", parent_loc)

    child_loc = SourceLocation(Path("test.py"), 2, 4, 4, 0)
    child = StandardizedASTNode("f1", NodeType.FUNCTION, "test_func", child_loc)

    parent.add_child(child)

    assert child.parent == parent, "parent is not valid"
    assert child in parent.children, "Condition must be true"
    assert child.get_depth() == 1, "Condition must be true"
    assert parent.get_depth() == 0, "Condition must be true"


def test_tree_traversal():
    """Test DFS tree traversal."""
    root_loc = SourceLocation(Path("test.py"), 1, 0, 10, 0)
    root = StandardizedASTNode("m1", NodeType.MODULE, "root", root_loc)

    child1_loc = SourceLocation(Path("test.py"), 2, 0, 5, 0)
    child1 = StandardizedASTNode("c1", NodeType.FUNCTION, "child1", child1_loc)

    child2_loc = SourceLocation(Path("test.py"), 6, 0, 10, 0)
    child2 = StandardizedASTNode("c2", NodeType.FUNCTION, "child2", child2_loc)

    root.add_child(child1)
    root.add_child(child2)

    nodes = list(root.walk())
    assert len(nodes) == 3, "Nodes must not be empty"
    assert nodes[0] == root, "Condition must be true"


def test_source_location_str():
    """Test SourceLocation string representation."""
    loc = SourceLocation(Path(os.path.join(tempfile.gettempdir(), "test.py")), 10, 5, 15, 20)
    assert str(loc) == os.path.join(tempfile.gettempdir(), "test.py:10:5"), "Condition must be true"
