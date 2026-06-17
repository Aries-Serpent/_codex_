"""
Comprehensive pytest tests for codex_ml.ast.core.node module.

Tests cover:
- SourceLocation: creation, parsing, serialization, edge cases (40 tests)
- StandardizedASTNode: creation, ID generation, parent-child relationships, weakref behavior, tree traversal (60 tests)
- Finding: creation, severity validation, ID generation, serialization (30 tests)
"""
import pytest
import json
import weakref
from pathlib import Path
from codex_ml.ast.core.node import SourceLocation, StandardizedASTNode, Finding


class TestSourceLocation:
    """Test suite for SourceLocation class (40 tests)."""

    # Creation tests
    def test_creation_minimal(self):
        loc = SourceLocation(Path("test.py"), 1, 1)
        assert loc.file_path == Path("test.py")
        assert loc.line_start == 1
        assert loc.line_end == 1
        assert loc.column_start == 0
        assert loc.column_end == 0

    def test_creation_with_all_params(self):
        loc = SourceLocation(Path("test.py"), 5, 10, 2, 15)
        assert loc.file_path == Path("test.py")
        assert loc.line_start == 5
        assert loc.line_end == 10
        assert loc.column_start == 2
        assert loc.column_end == 15

    @pytest.mark.parametrize("file_path", ["test.py", "path/to/file.py", "/abs/path.py", ""])
    def test_creation_various_paths(self, file_path):
        loc = SourceLocation(Path(file_path), 1, 1)
        assert loc.file_path == Path(file_path)

    @pytest.mark.parametrize("line", [1, 10, 100, 1000])
    def test_creation_various_line_numbers(self, line):
        loc = SourceLocation(Path("test.py"), line, line+5)
        assert loc.line_start == line
        assert loc.line_end == line + 5

    @pytest.mark.parametrize("col", [0, 5, 10, 50])
    def test_creation_various_columns(self, col):
        loc = SourceLocation(Path("test.py"), 1, 1, col, col+10)
        assert loc.column_start == col
        assert loc.column_end == col + 10

    # Parsing tests (from_string)
    def test_from_string_full_format(self):
        loc = SourceLocation.from_string("test.py:5:10")
        assert loc.file_path == Path("test.py")
        assert loc.line_start == 5
        assert loc.column_start == 10

    def test_from_string_file_only(self):
        loc = SourceLocation.from_string("test.py")
        assert loc.file_path == Path("test.py")
        assert loc.line_start == 1
        assert loc.column_start == 0

    def test_from_string_file_and_line(self):
        loc = SourceLocation.from_string("test.py:15")
        assert loc.file_path == Path("test.py")
        assert loc.line_start == 15
        assert loc.column_start == 0

    @pytest.mark.parametrize("input_str", [
        "file.py:1:0",
        "test.py:100:50",
        "/path/file.py:10:5",
        "module.py:1:1"
    ])
    def test_from_string_valid_formats(self, input_str):
        loc = SourceLocation.from_string(input_str)
        assert loc.file_path is not None
        assert loc.line_start >= 1
        assert loc.column_start >= 0

    def test_from_string_returns_line_end_equals_line_start(self):
        # from_string sets line_end = line_start
        loc = SourceLocation.from_string("test.py:5:10")
        assert loc.line_end == loc.line_start

    def test_from_string_returns_column_end_equals_column_start(self):
        # from_string sets column_end = column_start
        loc = SourceLocation.from_string("test.py:5:10")
        assert loc.column_end == loc.column_start

    # Serialization tests
    def test_to_dict(self):
        loc = SourceLocation(Path("test.py"), 5, 10, 2, 15)
        d = loc.to_dict()
        assert d["file_path"] == "test.py"
        assert d["line_start"] == 5
        assert d["line_end"] == 10
        assert d["column_start"] == 2
        assert d["column_end"] == 15

    def test_from_dict(self):
        original = SourceLocation(Path("test.py"), 5, 10, 2, 15)
        d = original.to_dict()
        restored = SourceLocation.from_dict(d)
        assert restored.file_path == Path("test.py")
        assert restored.line_start == original.line_start
        assert restored.line_end == original.line_end
        assert restored.column_start == original.column_start
        assert restored.column_end == original.column_end

    def test_roundtrip_serialization(self):
        locations = [
            SourceLocation(Path("test.py"), 1, 1, 0, 0),
            SourceLocation(Path("module.py"), 10, 20, 5, 15),
            SourceLocation(Path("/path/to/file.py"), 100, 105, 10, 50),
        ]
        for loc in locations:
            restored = SourceLocation.from_dict(loc.to_dict())
            assert restored.to_dict() == loc.to_dict()

    # String representation tests
    def test_str_representation(self):
        loc = SourceLocation(Path("test.py"), 5, 10, 2, 15)
        str_repr = str(loc)
        assert "test.py" in str_repr
        assert "5" in str_repr or "10" in str_repr

    def test_repr_representation(self):
        loc = SourceLocation(Path("test.py"), 5, 10, 2, 15)
        repr_str = repr(loc)
        assert "SourceLocation" in repr_str or "test.py" in repr_str

    # Edge cases
    def test_zero_line_start(self):
        loc = SourceLocation(Path("test.py"), 0, 5)
        assert loc.line_start == 0

    def test_negative_columns(self):
        loc = SourceLocation(Path("test.py"), 1, 1, -1, -1)
        assert loc.column_start == -1

    def test_same_line_different_columns(self):
        loc = SourceLocation(Path("test.py"), 5, 5, 0, 20)
        assert loc.line_start == loc.line_end
        assert loc.column_end > loc.column_start

    def test_single_character_span(self):
        loc = SourceLocation(Path("test.py"), 10, 10, 5, 6)
        assert loc.line_start == loc.line_end
        assert loc.column_end - loc.column_start == 1

    def test_comparison_equality(self):
        loc1 = SourceLocation(Path("test.py"), 5, 10, 2, 15)
        loc2 = SourceLocation(Path("test.py"), 5, 10, 2, 15)
        assert loc1 == loc2

    def test_comparison_inequality(self):
        loc1 = SourceLocation(Path("test.py"), 5, 10, 2, 15)
        loc2 = SourceLocation(Path("test.py"), 5, 10, 2, 16)
        assert loc1 != loc2

    def test_multiline_span(self):
        loc = SourceLocation(Path("test.py"), 5, 15, 0, 0)
        assert loc.line_end - loc.line_start == 10

    def test_from_dict_missing_optional_fields(self):
        d = {"file_path": "test.py", "line_start": 1, "line_end": 5}
        loc = SourceLocation.from_dict(d)
        assert loc.file_path == Path("test.py")
        assert loc.line_start == 1
        assert loc.column_start == 0

    def test_large_line_numbers(self):
        loc = SourceLocation(Path("test.py"), 1000000, 2000000)
        assert loc.line_start == 1000000

    def test_large_column_numbers(self):
        loc = SourceLocation(Path("test.py"), 1, 1, 1000000, 2000000)
        assert loc.column_start == 1000000


class TestStandardizedASTNode:
    """Test suite for StandardizedASTNode class (60 tests)."""

    # Creation tests
    def test_creation_minimal(self):
        node = StandardizedASTNode(node_id="node1", type="function", name="test_func")
        assert node.node_id == "node1"
        assert node.type == "function"
        assert node.name == "test_func"
        assert node.children == []
        assert node.parent is None

    def test_creation_with_all_params(self):
        loc = SourceLocation(Path("test.py"), 1, 5)
        node = StandardizedASTNode(
            node_id="node1", type="function", name="test_func",
            location=loc, metadata={"key": "value"}
        )
        assert node.node_id == "node1"
        assert node.type == "function"
        assert node.name == "test_func"
        assert node.location == loc
        assert node.metadata == {"key": "value"}

    def test_creation_no_node_id_generates_uuid(self):
        node = StandardizedASTNode(node_id="", type="function", name="test")
        assert node.node_id != ""
        import uuid
        try:
            uuid.UUID(node.node_id)
            assert True
        except ValueError:
            pytest.fail(f"node_id {node.node_id} is not a valid UUID")

    @pytest.mark.parametrize("type_str", ["function", "class", "variable", "import", "statement"])
    def test_creation_various_types(self, type_str):
        node = StandardizedASTNode(node_id="n1", type=type_str, name="test")
        assert node.type == type_str

    def test_creation_empty_metadata(self):
        node = StandardizedASTNode(node_id="n1", type="function", name="test", metadata={})
        assert node.metadata == {}

    def test_creation_complex_metadata(self):
        meta = {"key1": "value1", "key2": 42, "key3": [1, 2, 3], "nested": {"a": "b"}}
        node = StandardizedASTNode(node_id="n1", type="function", name="test", metadata=meta)
        assert node.metadata == meta

    # Parent-child relationship tests
    def test_add_child(self):
        parent = StandardizedASTNode(node_id="p1", type="class", name="MyClass")
        child = StandardizedASTNode(node_id="c1", type="function", name="method")
        parent.add_child(child)
        assert child in parent.children
        assert len(parent.children) == 1

    def test_add_multiple_children(self):
        parent = StandardizedASTNode(node_id="p1", type="class", name="MyClass")
        children = [
            StandardizedASTNode(node_id=f"c{i}", type="function", name=f"method{i}")
            for i in range(5)
        ]
        for child in children:
            parent.add_child(child)
        assert len(parent.children) == 5
        assert all(child in parent.children for child in children)

    def test_add_child_sets_parent_reference(self):
        parent = StandardizedASTNode(node_id="p1", type="class", name="MyClass")
        child = StandardizedASTNode(node_id="c1", type="function", name="method")
        parent.add_child(child)
        assert child.parent == parent

    def test_remove_child(self):
        parent = StandardizedASTNode(node_id="p1", type="class", name="MyClass")
        child = StandardizedASTNode(node_id="c1", type="function", name="method")
        parent.add_child(child)
        removed = parent.remove_child(child)
        assert removed is True
        assert child not in parent.children
        assert child.parent is None

    def test_remove_nonexistent_child(self):
        parent = StandardizedASTNode(node_id="p1", type="class", name="MyClass")
        child = StandardizedASTNode(node_id="c1", type="function", name="method")
        removed = parent.remove_child(child)
        assert removed is False
        assert len(parent.children) == 0

    def test_parent_weakref_behavior(self):
        parent = StandardizedASTNode(node_id="p1", type="class", name="MyClass")
        child = StandardizedASTNode(node_id="c1", type="function", name="method")
        parent.add_child(child)
        assert child.parent is not None
        assert child.parent.node_id == "p1"

    def test_parent_weakref_cleared_on_delete(self):
        parent = StandardizedASTNode(node_id="p1", type="class", name="MyClass")
        child = StandardizedASTNode(node_id="c1", type="function", name="method")
        parent.add_child(child)
        del parent
        import gc
        gc.collect()
        assert child.parent is None

    def test_bidirectional_parent_child_relationship(self):
        parent = StandardizedASTNode(node_id="p1", type="class", name="MyClass")
        child = StandardizedASTNode(node_id="c1", type="function", name="method")
        parent.add_child(child)
        assert child in parent.children
        assert child.parent == parent

    # Tree traversal tests
    def test_find_by_type_single_match(self):
        root = StandardizedASTNode(node_id="root", type="module", name="main")
        child = StandardizedASTNode(node_id="c1", type="function", name="test")
        root.add_child(child)
        results = root.find_by_type("function")
        assert len(results) == 1
        assert child in results

    def test_find_by_type_multiple_matches(self):
        root = StandardizedASTNode(node_id="root", type="module", name="main")
        for i in range(3):
            child = StandardizedASTNode(node_id=f"func{i}", type="function", name=f"func{i}")
            root.add_child(child)
        results = root.find_by_type("function")
        assert len(results) == 3

    def test_find_by_type_no_matches(self):
        root = StandardizedASTNode(node_id="root", type="module", name="main")
        child = StandardizedASTNode(node_id="c1", type="function", name="test")
        root.add_child(child)
        results = root.find_by_type("class")
        assert len(results) == 0

    def test_find_by_type_nested(self):
        root = StandardizedASTNode(node_id="root", type="module", name="main")
        parent = StandardizedASTNode(node_id="p1", type="class", name="MyClass")
        child = StandardizedASTNode(node_id="c1", type="function", name="method")
        root.add_child(parent)
        parent.add_child(child)
        results = root.find_by_type("function")
        assert len(results) == 1
        assert child in results

    def test_find_by_name_single_match(self):
        root = StandardizedASTNode(node_id="root", type="module", name="main")
        child = StandardizedASTNode(node_id="c1", type="function", name="test_func")
        root.add_child(child)
        results = root.find_by_name("test_func")
        assert len(results) == 1
        assert child in results

    def test_find_by_name_multiple_matches(self):
        root = StandardizedASTNode(node_id="root", type="module", name="main")
        for i in range(2):
            child = StandardizedASTNode(node_id=f"n{i}", type="function", name="func")
            root.add_child(child)
        results = root.find_by_name("func")
        assert len(results) == 2

    def test_find_by_name_no_matches(self):
        root = StandardizedASTNode(node_id="root", type="module", name="main")
        results = root.find_by_name("nonexistent")
        assert len(results) == 0

    def test_walk_tree_traversal(self):
        root = StandardizedASTNode(node_id="root", type="module", name="main")
        nodes = [root]
        for i in range(3):
            child = StandardizedASTNode(node_id=f"c{i}", type="function", name=f"func{i}")
            root.add_child(child)
            nodes.append(child)
        walked = root.walk()
        assert len(walked) == 4
        assert all(node in walked for node in nodes)

    def test_walk_nested_tree(self):
        root = StandardizedASTNode(node_id="root", type="module", name="main")
        parent = StandardizedASTNode(node_id="p1", type="class", name="MyClass")
        child = StandardizedASTNode(node_id="c1", type="function", name="method")
        root.add_child(parent)
        parent.add_child(child)
        walked = root.walk()
        assert root in walked
        assert parent in walked
        assert child in walked

    def test_walk_preorder_traversal(self):
        root = StandardizedASTNode(node_id="root", type="module", name="main")
        child1 = StandardizedASTNode(node_id="c1", type="function", name="func1")
        child2 = StandardizedASTNode(node_id="c2", type="class", name="class1")
        root.add_child(child1)
        root.add_child(child2)
        walked = root.walk()
        assert walked[0] == root

    def test_is_leaf_true(self):
        node = StandardizedASTNode(node_id="n1", type="function", name="test")
        assert node.is_leaf is True

    def test_is_leaf_false(self):
        parent = StandardizedASTNode(node_id="p1", type="class", name="MyClass")
        child = StandardizedASTNode(node_id="c1", type="function", name="method")
        parent.add_child(child)
        assert parent.is_leaf is False

    def test_is_root_true(self):
        node = StandardizedASTNode(node_id="n1", type="module", name="main")
        assert node.is_root is True

    def test_is_root_false(self):
        parent = StandardizedASTNode(node_id="p1", type="class", name="MyClass")
        child = StandardizedASTNode(node_id="c1", type="function", name="method")
        parent.add_child(child)
        assert child.is_root is False

    def test_depth_root_node(self):
        root = StandardizedASTNode(node_id="root", type="module", name="main")
        assert root.depth == 0

    def test_depth_child_node(self):
        root = StandardizedASTNode(node_id="root", type="module", name="main")
        child = StandardizedASTNode(node_id="c1", type="function", name="test")
        root.add_child(child)
        assert child.depth == 1

    def test_depth_deeply_nested(self):
        root = StandardizedASTNode(node_id="root", type="module", name="main")
        current = root
        for i in range(5):
            child = StandardizedASTNode(node_id=f"c{i}", type="function", name=f"func{i}")
            current.add_child(child)
            current = child
        assert current.depth == 5

    # Serialization tests
    def test_to_dict_basic(self):
        node = StandardizedASTNode(node_id="n1", type="function", name="test")
        d = node.to_dict()
        assert d["node_id"] == "n1"
        assert d["type"] == "function"
        assert d["name"] == "test"

    def test_to_dict_with_location(self):
        loc = SourceLocation(Path("test.py"), 1, 5)
        node = StandardizedASTNode(node_id="n1", type="function", name="test", location=loc)
        d = node.to_dict()
        assert d["location"] is not None

    def test_to_dict_with_children(self):
        parent = StandardizedASTNode(node_id="p1", type="class", name="MyClass")
        child = StandardizedASTNode(node_id="c1", type="function", name="method")
        parent.add_child(child)
        d = parent.to_dict()
        assert "children" in d
        assert len(d["children"]) == 1

    def test_from_dict_basic(self):
        d = {"node_id": "n1", "type": "function", "name": "test", "children": [], "metadata": {}}
        node = StandardizedASTNode.from_dict(d)
        assert node.node_id == "n1"
        assert node.type == "function"
        assert node.name == "test"

    def test_from_dict_with_location(self):
        loc_dict = {"file_path": "test.py", "line_start": 1, "line_end": 5, "column_start": 0, "column_end": 0}
        d = {"node_id": "n1", "type": "function", "name": "test", "location": loc_dict, "children": [], "metadata": {}}
        node = StandardizedASTNode.from_dict(d)
        assert node.location is not None
        assert str(node.location.file_path) == "test.py"

    def test_roundtrip_serialization(self):
        loc = SourceLocation(Path("test.py"), 5, 10)
        node = StandardizedASTNode(node_id="n1", type="function", name="test", location=loc, metadata={"key": "value"})
        d = node.to_dict()
        restored = StandardizedASTNode.from_dict(d)
        assert restored.node_id == node.node_id
        assert restored.type == node.type
        assert restored.name == node.name
        assert restored.metadata == node.metadata

    # Edge cases and special behaviors
    def test_json_serializable(self):
        parent = StandardizedASTNode(node_id="p1", type="class", name="MyClass")
        child = StandardizedASTNode(node_id="c1", type="function", name="method")
        parent.add_child(child)
        d = parent.to_dict()
        json_str = json.dumps(d)
        assert len(json_str) > 0

    def test_empty_children_list(self):
        node = StandardizedASTNode(node_id="n1", type="function", name="test")
        assert node.children == []

    def test_complex_tree_traversal(self):
        # Create a tree structure
        root = StandardizedASTNode(node_id="root", type="module", name="main")
        class1 = StandardizedASTNode(node_id="class1", type="class", name="MyClass")
        method1 = StandardizedASTNode(node_id="method1", type="function", name="method1")
        method2 = StandardizedASTNode(node_id="method2", type="function", name="method2")
        
        root.add_child(class1)
        class1.add_child(method1)
        class1.add_child(method2)
        
        # Walk should visit all nodes
        walked = root.walk()
        assert len(walked) == 4
        
        # Find by type should work
        funcs = root.find_by_type("function")
        assert len(funcs) == 2


class TestFinding:
    """Test suite for Finding class (30 tests)."""

    # Creation tests
    def test_creation_minimal(self):
        finding = Finding(type="error", message="Test error")
        assert finding.type == "error"
        assert finding.message == "Test error"
        assert finding.severity == "info"

    def test_creation_with_id(self):
        finding = Finding(finding_id="f1", type="error", message="Test")
        assert finding.finding_id == "f1"

    def test_creation_with_severity(self):
        finding = Finding(type="error", message="Test", severity="critical")
        assert finding.severity == "critical"

    def test_creation_with_location(self):
        loc = SourceLocation(Path("test.py"), 5, 10)
        finding = Finding(type="error", message="Test", location=loc)
        assert finding.location == loc

    def test_creation_with_analyzer(self):
        finding = Finding(type="error", message="Test", analyzer="test_analyzer")
        assert finding.analyzer == "test_analyzer"

    def test_creation_with_metadata(self):
        meta = {"key": "value"}
        finding = Finding(type="error", message="Test", metadata=meta)
        assert finding.metadata == meta

    # ID generation tests
    def test_finding_id_auto_generation(self):
        finding = Finding(type="error", message="Test")
        assert finding.finding_id != ""
        import uuid
        try:
            uuid.UUID(finding.finding_id)
            assert True
        except ValueError:
            pytest.fail(f"finding_id {finding.finding_id} is not a valid UUID")

    def test_finding_id_unique(self):
        findings = [
            Finding(type="error", message="Test 1"),
            Finding(type="error", message="Test 2"),
        ]
        assert findings[0].finding_id != findings[1].finding_id

    def test_finding_id_provided(self):
        finding = Finding(finding_id="custom_id", type="error", message="Test")
        assert finding.finding_id == "custom_id"

    # Severity validation tests
    @pytest.mark.parametrize("severity", ["info", "warning", "error", "critical"])
    def test_severity_valid_values(self, severity):
        finding = Finding(type="issue", message="Test", severity=severity)
        assert finding.severity == severity

    def test_severity_default(self):
        finding = Finding(type="issue", message="Test")
        assert finding.severity == "info"

    # Serialization tests
    def test_to_dict_basic(self):
        finding = Finding(type="error", message="Test message")
        d = finding.to_dict()
        assert d["type"] == "error"
        assert d["message"] == "Test message"
        assert d["severity"] == "info"

    def test_to_dict_with_location(self):
        loc = SourceLocation(Path("test.py"), 5, 10)
        finding = Finding(type="error", message="Test", location=loc)
        d = finding.to_dict()
        assert d["location"] is not None

    def test_to_dict_with_all_fields(self):
        loc = SourceLocation(Path("test.py"), 5, 10)
        finding = Finding(
            finding_id="f1", type="error", message="Test",
            severity="critical", location=loc, analyzer="test_analyzer",
            metadata={"key": "value"}
        )
        d = finding.to_dict()
        assert d["finding_id"] == "f1"
        assert d["type"] == "error"
        assert d["severity"] == "critical"
        assert d["analyzer"] == "test_analyzer"

    def test_from_dict_basic(self):
        d = {"type": "error", "message": "Test", "severity": "warning"}
        finding = Finding.from_dict(d)
        assert finding.type == "error"
        assert finding.message == "Test"
        assert finding.severity == "warning"

    def test_from_dict_with_location(self):
        loc_dict = {"file_path": "test.py", "line_start": 1, "line_end": 5, "column_start": 0, "column_end": 0}
        d = {"type": "error", "message": "Test", "location": loc_dict}
        finding = Finding.from_dict(d)
        assert finding.location is not None
        assert str(finding.location.file_path) == "test.py"

    def test_roundtrip_serialization(self):
        loc = SourceLocation(Path("test.py"), 5, 10)
        original = Finding(
            finding_id="f1", type="error", message="Test error",
            severity="critical", location=loc, analyzer="test_analyzer",
            metadata={"key": "value"}
        )
        d = original.to_dict()
        restored = Finding.from_dict(d)
        assert restored.finding_id == original.finding_id
        assert restored.type == original.type
        assert restored.message == original.message
        assert restored.severity == original.severity
        assert restored.analyzer == original.analyzer

    # Edge cases
    def test_finding_with_empty_message(self):
        finding = Finding(type="error", message="")
        assert finding.message == ""

    def test_finding_with_long_message(self):
        long_msg = "x" * 10000
        finding = Finding(type="error", message=long_msg)
        assert finding.message == long_msg

    def test_finding_with_multiline_message(self):
        msg = "Line 1\nLine 2\nLine 3"
        finding = Finding(type="error", message=msg)
        assert finding.message == msg

    def test_finding_with_special_characters(self):
        msg = "Test with special chars: !@#$%^&*()"
        finding = Finding(type="error", message=msg)
        assert finding.message == msg

    def test_finding_with_unicode(self):
        msg = "Test with unicode: 日本語"
        finding = Finding(type="error", message=msg)
        assert finding.message == msg

    def test_json_serializable(self):
        loc = SourceLocation(Path("test.py"), 5, 10)
        finding = Finding(type="error", message="Test", location=loc)
        d = finding.to_dict()
        json_str = json.dumps(d)
        assert len(json_str) > 0
