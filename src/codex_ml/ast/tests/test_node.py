"""
Tests for AST core node data structures.
"""

from pathlib import Path

from codex_ml.ast.core.node import Finding, SourceLocation, StandardizedASTNode


class TestSourceLocation:
    """Tests for SourceLocation dataclass."""

    def test_create_source_location(self) -> None:
        """Test creating a source location."""
        loc = SourceLocation(
            file_path=Path("test.py"),
            line_start=10,
            line_end=20,
            column_start=0,
            column_end=50,
        )
        assert loc.file_path == Path("test.py")
        assert loc.line_start == 10
        assert loc.line_end == 20
        assert loc.column_start == 0
        assert loc.column_end == 50

    def test_source_location_str(self) -> None:
        """Test string representation."""
        loc = SourceLocation(
            file_path=Path("test.py"),
            line_start=10,
            line_end=20,
        )
        assert str(loc) == "test.py:10:0"

    def test_from_string_full(self) -> None:
        """Test parsing full location string."""
        loc = SourceLocation.from_string("path/to/file.py:42:10")
        assert loc.file_path == Path("path/to/file.py")
        assert loc.line_start == 42
        assert loc.column_start == 10

    def test_from_string_partial(self) -> None:
        """Test parsing partial location string."""
        loc = SourceLocation.from_string("file.py:5")
        assert loc.file_path == Path("file.py")
        assert loc.line_start == 5
        assert loc.column_start == 0

    def test_from_string_file_only(self) -> None:
        """Test parsing file-only location string."""
        loc = SourceLocation.from_string("file.py")
        assert loc.file_path == Path("file.py")
        assert loc.line_start == 1
        assert loc.column_start == 0

    def test_to_dict(self) -> None:
        """Test dictionary serialization."""
        loc = SourceLocation(
            file_path=Path("test.py"),
            line_start=10,
            line_end=20,
            column_start=5,
            column_end=15,
        )
        d = loc.to_dict()
        assert d["file_path"] == "test.py"
        assert d["line_start"] == 10
        assert d["line_end"] == 20

    def test_from_dict(self) -> None:
        """Test dictionary deserialization."""
        data = {
            "file_path": "test.py",
            "line_start": 10,
            "line_end": 20,
            "column_start": 5,
            "column_end": 15,
        }
        loc = SourceLocation.from_dict(data)
        assert loc.file_path == Path("test.py")
        assert loc.line_start == 10


class TestStandardizedASTNode:
    """Tests for StandardizedASTNode dataclass."""

    def test_create_node(self) -> None:
        """Test creating a basic node."""
        node = StandardizedASTNode(
            node_id="test-001",
            type="function",
            name="test_func",
        )
        assert node.node_id == "test-001"
        assert node.type == "function"
        assert node.name == "test_func"
        assert node.children == []
        assert node.parent is None

    def test_auto_generate_id(self) -> None:
        """Test auto-generated node ID."""
        node = StandardizedASTNode(node_id="", type="class", name="TestClass")
        assert node.node_id  # Should be non-empty UUID

    def test_depth_root(self) -> None:
        """Test depth calculation for root node."""
        root = StandardizedASTNode(node_id="root", type="module", name="module")
        assert root.depth == 0

    def test_depth_nested(self) -> None:
        """Test depth calculation for nested nodes."""
        root = StandardizedASTNode(node_id="root", type="module", name="module")
        child = StandardizedASTNode(node_id="child", type="class", name="MyClass")
        grandchild = StandardizedASTNode(node_id="grandchild", type="function", name="method")

        root.add_child(child)
        child.add_child(grandchild)

        assert root.depth == 0
        assert child.depth == 1
        assert grandchild.depth == 2

    def test_is_leaf(self) -> None:
        """Test leaf node detection."""
        parent = StandardizedASTNode(node_id="parent", type="class", name="Class")
        child = StandardizedASTNode(node_id="child", type="function", name="method")
        parent.add_child(child)

        assert not parent.is_leaf
        assert child.is_leaf

    def test_is_root(self) -> None:
        """Test root node detection."""
        parent = StandardizedASTNode(node_id="parent", type="class", name="Class")
        child = StandardizedASTNode(node_id="child", type="function", name="method")
        parent.add_child(child)

        assert parent.is_root
        assert not child.is_root

    def test_add_child(self) -> None:
        """Test adding child node."""
        parent = StandardizedASTNode(node_id="parent", type="class", name="Class")
        child = StandardizedASTNode(node_id="child", type="function", name="method")

        parent.add_child(child)

        assert len(parent.children) == 1
        assert parent.children[0] == child
        assert child.parent == parent

    def test_remove_child(self) -> None:
        """Test removing child node."""
        parent = StandardizedASTNode(node_id="parent", type="class", name="Class")
        child = StandardizedASTNode(node_id="child", type="function", name="method")

        parent.add_child(child)
        result = parent.remove_child(child)

        assert result is True
        assert len(parent.children) == 0
        assert child.parent is None

    def test_find_by_type(self) -> None:
        """Test finding nodes by type."""
        root = StandardizedASTNode(node_id="root", type="module", name="module")
        func1 = StandardizedASTNode(node_id="f1", type="function", name="func1")
        func2 = StandardizedASTNode(node_id="f2", type="function", name="func2")
        cls = StandardizedASTNode(node_id="c1", type="class", name="MyClass")

        root.add_child(func1)
        root.add_child(cls)
        cls.add_child(func2)

        functions = root.find_by_type("function")
        assert len(functions) == 2
        assert func1 in functions
        assert func2 in functions

    def test_find_by_name(self) -> None:
        """Test finding nodes by name."""
        root = StandardizedASTNode(node_id="root", type="module", name="module")
        child1 = StandardizedASTNode(node_id="c1", type="function", name="target")
        child2 = StandardizedASTNode(node_id="c2", type="variable", name="target")

        root.add_child(child1)
        root.add_child(child2)

        results = root.find_by_name("target")
        assert len(results) == 2

    def test_walk(self) -> None:
        """Test tree traversal."""
        root = StandardizedASTNode(node_id="root", type="module", name="module")
        child1 = StandardizedASTNode(node_id="c1", type="class", name="Class1")
        child2 = StandardizedASTNode(node_id="c2", type="function", name="func")
        grandchild = StandardizedASTNode(node_id="gc", type="function", name="method")

        root.add_child(child1)
        root.add_child(child2)
        child1.add_child(grandchild)

        all_nodes = root.walk()
        assert len(all_nodes) == 4
        assert root in all_nodes
        assert child1 in all_nodes
        assert child2 in all_nodes
        assert grandchild in all_nodes

    def test_to_dict(self) -> None:
        """Test dictionary serialization."""
        node = StandardizedASTNode(
            node_id="test",
            type="function",
            name="test_func",
            metadata={"docstring": "Test function"},
        )
        d = node.to_dict()
        assert d["node_id"] == "test"
        assert d["type"] == "function"
        assert d["name"] == "test_func"
        assert d["metadata"]["docstring"] == "Test function"

    def test_from_dict(self) -> None:
        """Test dictionary deserialization."""
        data = {
            "node_id": "test",
            "type": "function",
            "name": "test_func",
            "metadata": {"complexity": 5},
            "children": [],
        }
        node = StandardizedASTNode.from_dict(data)
        assert node.node_id == "test"
        assert node.type == "function"
        assert node.name == "test_func"
        assert node.metadata["complexity"] == 5


class TestFinding:
    """Tests for Finding dataclass."""

    def test_create_finding(self) -> None:
        """Test creating a finding."""
        finding = Finding(
            type="high_complexity",
            severity="warning",
            message="Function is too complex",
            analyzer="complexity",
        )
        assert finding.type == "high_complexity"
        assert finding.severity == "warning"
        assert finding.message == "Function is too complex"
        assert finding.finding_id  # Should be auto-generated

    def test_invalid_severity_normalized(self) -> None:
        """Test that invalid severity is normalized."""
        finding = Finding(type="test", severity="invalid", message="Test")
        assert finding.severity == "info"  # Normalized to info

    def test_valid_severities(self) -> None:
        """Test all valid severity levels."""
        for severity in ["info", "warning", "error", "critical"]:
            finding = Finding(type="test", severity=severity, message="Test")
            assert finding.severity == severity

    def test_to_dict(self) -> None:
        """Test dictionary serialization."""
        finding = Finding(
            finding_id="f-001",
            type="unused_import",
            severity="info",
            message="Import 'os' is unused",
            analyzer="unused_code",
        )
        d = finding.to_dict()
        assert d["finding_id"] == "f-001"
        assert d["type"] == "unused_import"
        assert d["severity"] == "info"

    def test_from_dict(self) -> None:
        """Test dictionary deserialization."""
        data = {
            "finding_id": "f-001",
            "type": "unused_import",
            "severity": "info",
            "message": "Import 'os' is unused",
            "analyzer": "unused_code",
            "metadata": {"import_name": "os"},
        }
        finding = Finding.from_dict(data)
        assert finding.finding_id == "f-001"
        assert finding.type == "unused_import"
        assert finding.metadata["import_name"] == "os"
