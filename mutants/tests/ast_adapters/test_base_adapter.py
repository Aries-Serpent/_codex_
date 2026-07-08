"""Tests for base AST adapter."""

from codex.ast_adapters.base_adapter import BaseASTAdapter, StandardizedASTNode


class MockAdapter(BaseASTAdapter):
    """Mock adapter for testing base class functionality."""

    def parse(self, source_code: str) -> StandardizedASTNode:
        """Mock parse implementation."""
        self.root_node = StandardizedASTNode(
            node_id=self._generate_node_id(), node_type="root", name="mock_root"
        )
        return self.root_node

    def extract_metadata(self, node: StandardizedASTNode) -> dict:
        """Mock metadata extraction."""
        return {"mock": True}


def test_standardized_ast_node_creation():
    """Test creating a StandardizedASTNode."""
    node = StandardizedASTNode(node_id="test_1", node_type="function", name="test_function")

    assert node.node_id == "test_1", "node_id is not valid"
    assert node.node_type == "function", "node_type is not valid"
    assert node.name == "test_function", "name is not valid"
    assert node.depth == 0, "depth is not valid"
    assert len(node.children) == 0, "Collection must not be empty"


def test_standardized_ast_node_with_parent():
    """Test node with parent relationship."""
    parent = StandardizedASTNode(node_id="parent_1", node_type="class", name="TestClass")

    child = StandardizedASTNode(
        node_id="child_1", node_type="function", name="test_method", parent=parent
    )

    parent.children.append(child)

    assert child.depth == 1, "depth is not valid"
    assert child.parent == parent, "parent is not valid"
    assert len(parent.children) == 1, "Collection must not be empty"


def test_standardized_ast_node_full_name():
    """Test full name generation."""
    parent = StandardizedASTNode(node_id="parent_1", node_type="class", name="TestClass")

    child = StandardizedASTNode(
        node_id="child_1", node_type="function", name="test_method", parent=parent
    )

    assert child.full_name == "TestClass.test_method", "full_name is not valid"
    assert parent.full_name == "TestClass", "full_name is not valid"


def test_standardized_ast_node_to_dict():
    """Test node serialization to dictionary."""
    node = StandardizedASTNode(
        node_id="test_1",
        node_type="function",
        name="test_func",
        line_start=10,
        line_end=20,
        metadata={"decorator": "@pytest.fixture"},
    )

    node_dict = node.to_dict()

    assert node_dict["node_id"] == "test_1", "Condition must be true"
    assert node_dict["node_type"] == "function", "Condition must be true"
    assert node_dict["name"] == "test_func", "Condition must be true"
    assert node_dict["line_start"] == 10, "Condition must be true"
    assert node_dict["line_end"] == 20, "Condition must be true"
    assert node_dict["metadata"]["decorator"] == "@pytest.fixture", "Data must not be empty"


def test_base_adapter_initialization():
    """Test BaseASTAdapter initialization."""
    adapter = MockAdapter()

    assert adapter.file_path is None, "file_path is not valid"
    assert adapter.root_node is None, "root_node is not valid"
    assert adapter._node_counter == 0, "Count must be greater than zero"


def test_base_adapter_generate_node_id():
    """Test node ID generation."""
    adapter = MockAdapter()

    id1 = adapter._generate_node_id()
    id2 = adapter._generate_node_id()

    assert id1 == "node_1", "id1 is not valid"
    assert id2 == "node_2", "id2 is not valid"


def test_base_adapter_parse():
    """Test parse method."""
    adapter = MockAdapter()
    root = adapter.parse("mock source code")

    assert root is not None, "root must be initialized"
    assert root.node_type == "root", "node_type is not valid"
    assert root.name == "mock_root", "name is not valid"
    assert adapter.root_node == root, "root_node is not valid"


def test_base_adapter_traverse():
    """Test AST traversal."""
    adapter = MockAdapter()

    # Create a simple tree
    root = StandardizedASTNode(node_id="root", node_type="root", name="root")

    child1 = StandardizedASTNode(node_id="child1", node_type="child", name="child1", parent=root)

    child2 = StandardizedASTNode(node_id="child2", node_type="child", name="child2", parent=root)

    grandchild = StandardizedASTNode(
        node_id="grandchild", node_type="grandchild", name="grandchild", parent=child1
    )

    root.children = [child1, child2]
    child1.children = [grandchild]

    adapter.root_node = root

    nodes = adapter.traverse()

    assert len(nodes) == 4, "Nodes must not be empty"
    assert nodes[0] == root, "Condition must be true"
    assert grandchild in nodes, "gr is not valid"


def test_base_adapter_find_nodes_by_type():
    """Test finding nodes by type."""
    adapter = MockAdapter()

    root = StandardizedASTNode(node_id="root", node_type="module", name="root")

    func1 = StandardizedASTNode(node_id="func1", node_type="function", name="func1", parent=root)

    func2 = StandardizedASTNode(node_id="func2", node_type="function", name="func2", parent=root)

    cls = StandardizedASTNode(node_id="cls", node_type="class", name="TestClass", parent=root)

    root.children = [func1, func2, cls]
    adapter.root_node = root

    functions = adapter.find_nodes_by_type("function")

    assert len(functions) == 2, "Functions must not be empty"
    assert func1 in functions, "Condition must be true"
    assert func2 in functions, "Condition must be true"


def test_base_adapter_get_stats():
    """Test AST statistics."""
    adapter = MockAdapter()

    root = StandardizedASTNode(node_id="root", node_type="module", name="root")

    func = StandardizedASTNode(node_id="func", node_type="function", name="func", parent=root)

    cls = StandardizedASTNode(node_id="cls", node_type="class", name="cls", parent=root)

    root.children = [func, cls]
    adapter.root_node = root

    stats = adapter.get_stats()

    assert stats["module"] == 1, "Condition must be true"
    assert stats["function"] == 1, "Condition must be true"
    assert stats["class"] == 1, "Condition must be true"
