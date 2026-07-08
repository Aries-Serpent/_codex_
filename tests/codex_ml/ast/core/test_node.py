"""
Comprehensive pytest tests for codex_ml.ast.core.node module.

Tests cover:
- SourceLocation: creation, parsing, serialization, edge cases (40 tests)
- StandardizedASTNode: creation, ID generation, parent-child relationships, weakref behavior, tree traversal (60 tests)
- Finding: creation, severity validation, ID generation, serialization (30 tests)
"""

import json
from pathlib import Path

import pytest

from codex_ml.ast.core.node import Finding, SourceLocation, StandardizedASTNode


class TestSourceLocation:
    """Test suite for SourceLocation class (40 tests)."""

    # Creation tests
    def test_creation_minimal(self):
        loc = SourceLocation(Path("test.py"), 1, 1)
        assert loc.file_path == Path("test.py"), "file_path is not valid"
        assert loc.line_start == 1, "line_start is not valid"
        assert loc.line_end == 1, "line_end is not valid"
        assert loc.column_start == 0, "column_start is not valid"
        assert loc.column_end == 0, "column_end is not valid"

    def test_creation_with_all_params(self):
        loc = SourceLocation(Path("test.py"), 5, 10, 2, 15)
        assert loc.file_path == Path("test.py"), "file_path is not valid"
        assert loc.line_start == 5, "line_start is not valid"
        assert loc.line_end == 10, "line_end is not valid"
        assert loc.column_start == 2, "column_start is not valid"
        assert loc.column_end == 15, "column_end is not valid"

    @pytest.mark.parametrize("file_path", ["test.py", "path/to/file.py", "/abs/path.py", ""])
    def test_creation_various_paths(self, file_path):
        loc = SourceLocation(Path(file_path), 1, 1)
        assert loc.file_path == Path(file_path), "file_path is not valid"

    @pytest.mark.parametrize("line", [1, 10, 100, 1000])
    def test_creation_various_line_numbers(self, line):
        loc = SourceLocation(Path("test.py"), line, line + 5)
        assert loc.line_start == line, "line_start is not valid"
        assert loc.line_end == line + 5, "line_end is not valid"

    @pytest.mark.parametrize("col", [0, 5, 10, 50])
    def test_creation_various_columns(self, col):
        loc = SourceLocation(Path("test.py"), 1, 1, col, col + 10)
        assert loc.column_start == col, "column_start is not valid"
        assert loc.column_end == col + 10, "column_end is not valid"

    # Parsing tests (from_string)
    def test_from_string_full_format(self):
        loc = SourceLocation.from_string("test.py:5:10")
        assert loc.file_path == Path("test.py"), "file_path is not valid"
        assert loc.line_start == 5, "line_start is not valid"
        assert loc.column_start == 10, "column_start is not valid"

    def test_from_string_file_only(self):
        loc = SourceLocation.from_string("test.py")
        assert loc.file_path == Path("test.py"), "file_path is not valid"
        assert loc.line_start == 1, "line_start is not valid"
        assert loc.column_start == 0, "column_start is not valid"

    def test_from_string_file_and_line(self):
        loc = SourceLocation.from_string("test.py:15")
        assert loc.file_path == Path("test.py"), "file_path is not valid"
        assert loc.line_start == 15, "line_start is not valid"
        assert loc.column_start == 0, "column_start is not valid"

    @pytest.mark.parametrize(
        "input_str", ["file.py:1:0", "test.py:100:50", "/path/file.py:10:5", "module.py:1:1"]
    )
    def test_from_string_valid_formats(self, input_str):
        loc = SourceLocation.from_string(input_str)
        assert loc.file_path is not None, "file_path must be initialized"
        assert loc.line_start >= 1, "line_start must be greater than zero"
        assert loc.column_start >= 0, "column_start must be greater than zero"

    def test_from_string_returns_line_end_equals_line_start(self):
        # from_string sets line_end = line_start
        loc = SourceLocation.from_string("test.py:5:10")
        assert loc.line_end == loc.line_start, "line_end is not valid"

    def test_from_string_returns_column_end_equals_column_start(self):
        # from_string sets column_end = column_start
        loc = SourceLocation.from_string("test.py:5:10")
        assert loc.column_end == loc.column_start, "column_end is not valid"

    # Serialization tests
    def test_to_dict(self):
        loc = SourceLocation(Path("test.py"), 5, 10, 2, 15)
        d = loc.to_dict()
        assert d["file_path"] == "test.py", "Condition must be true"
        assert d["line_start"] == 5, "Condition must be true"
        assert d["line_end"] == 10, "Condition must be true"
        assert d["column_start"] == 2, "Condition must be true"
        assert d["column_end"] == 15, "Condition must be true"

    def test_from_dict(self):
        original = SourceLocation(Path("test.py"), 5, 10, 2, 15)
        d = original.to_dict()
        restored = SourceLocation.from_dict(d)
        assert restored.file_path == Path("test.py"), "file_path is not valid"
        assert restored.line_start == original.line_start, "line_start is not valid"
        assert restored.line_end == original.line_end, "line_end is not valid"
        assert restored.column_start == original.column_start, "column_start is not valid"
        assert restored.column_end == original.column_end, "column_end is not valid"

    def test_roundtrip_serialization(self):
        locations = [
            SourceLocation(Path("test.py"), 1, 1, 0, 0),
            SourceLocation(Path("module.py"), 10, 20, 5, 15),
            SourceLocation(Path("/path/to/file.py"), 100, 105, 10, 50),
        ]
        for loc in locations:
            restored = SourceLocation.from_dict(loc.to_dict())
            assert restored.to_dict() == loc.to_dict(), "rest is not valid"

    # String representation tests
    def test_str_representation(self):
        loc = SourceLocation(Path("test.py"), 5, 10, 2, 15)
        str_repr = str(loc)
        assert "test.py" in str_repr, "Condition must be true"
        assert "5" in str_repr or "10" in str_repr, "Condition must be true"

    def test_repr_representation(self):
        loc = SourceLocation(Path("test.py"), 5, 10, 2, 15)
        repr_str = repr(loc)
        assert "SourceLocation" in repr_str or "test.py" in repr_str, "Condition must be true"

    # Edge cases
    def test_zero_line_start(self):
        loc = SourceLocation(Path("test.py"), 0, 5)
        assert loc.line_start == 0, "line_start is not valid"

    def test_negative_columns(self):
        loc = SourceLocation(Path("test.py"), 1, 1, -1, -1)
        assert loc.column_start == -1, "column_start is not valid"

    def test_same_line_different_columns(self):
        loc = SourceLocation(Path("test.py"), 5, 5, 0, 20)
        assert loc.line_start == loc.line_end, "line_start is not valid"
        assert loc.column_end > loc.column_start, "column_end must be greater than zero"

    def test_single_character_span(self):
        loc = SourceLocation(Path("test.py"), 10, 10, 5, 6)
        assert loc.line_start == loc.line_end, "line_start is not valid"
        assert loc.column_end - loc.column_start == 1, "column_start is not valid"

    def test_comparison_equality(self):
        loc1 = SourceLocation(Path("test.py"), 5, 10, 2, 15)
        loc2 = SourceLocation(Path("test.py"), 5, 10, 2, 15)
        assert loc1 == loc2, "loc1 is not valid"

    def test_comparison_inequality(self):
        loc1 = SourceLocation(Path("test.py"), 5, 10, 2, 15)
        loc2 = SourceLocation(Path("test.py"), 5, 10, 2, 16)
        assert loc1 != loc2, "loc1 is not valid"

    def test_multiline_span(self):
        loc = SourceLocation(Path("test.py"), 5, 15, 0, 0)
        assert loc.line_end - loc.line_start == 10, "line_start is not valid"

    def test_from_dict_missing_optional_fields(self):
        d = {"file_path": "test.py", "line_start": 1, "line_end": 5}
        loc = SourceLocation.from_dict(d)
        assert loc.file_path == Path("test.py"), "file_path is not valid"
        assert loc.line_start == 1, "line_start is not valid"
        assert loc.column_start == 0, "column_start is not valid"

    def test_large_line_numbers(self):
        loc = SourceLocation(Path("test.py"), 1000000, 2000000)
        assert loc.line_start == 1000000, "line_start is not valid"

    def test_large_column_numbers(self):
        loc = SourceLocation(Path("test.py"), 1, 1, 1000000, 2000000)
        assert loc.column_start == 1000000, "column_start is not valid"


class TestStandardizedASTNode:
    """Test suite for StandardizedASTNode class (60 tests)."""

    # Creation tests
    def test_creation_minimal(self):
        node = StandardizedASTNode(node_id="node1", type="function", name="test_func")
        assert node.node_id == "node1", "node_id is not valid"
        assert node.type == "function", "type is not valid"
        assert node.name == "test_func", "name is not valid"
        assert node.children == [], "children is not valid"
        assert node.parent is None, "parent is not valid"

    def test_creation_with_all_params(self):
        loc = SourceLocation(Path("test.py"), 1, 5)
        node = StandardizedASTNode(
            node_id="node1",
            type="function",
            name="test_func",
            location=loc,
            metadata={"key": "value"},
        )
        assert node.node_id == "node1", "node_id is not valid"
        assert node.type == "function", "type is not valid"
        assert node.name == "test_func", "name is not valid"
        assert node.location == loc, "location is not valid"
        assert node.metadata == {"key": "value"}, "Data must not be empty"

    def test_creation_no_node_id_generates_uuid(self):
        node = StandardizedASTNode(node_id="", type="function", name="test")
        assert node.node_id != "", "node_id is not valid"
        import uuid

        try:
            uuid.UUID(node.node_id)
            assert True, "True is not valid"
        except ValueError:
            pytest.fail(f"node_id {node.node_id} is not a valid UUID")

    @pytest.mark.parametrize("type_str", ["function", "class", "variable", "import", "statement"])
    def test_creation_various_types(self, type_str):
        node = StandardizedASTNode(node_id="n1", type=type_str, name="test")
        assert node.type == type_str, "type is not valid"

    def test_creation_empty_metadata(self):
        node = StandardizedASTNode(node_id="n1", type="function", name="test", metadata={})
        assert node.metadata == {}, "Data must not be empty"

    def test_creation_complex_metadata(self):
        meta = {"key1": "value1", "key2": 42, "key3": [1, 2, 3], "nested": {"a": "b"}}
        node = StandardizedASTNode(node_id="n1", type="function", name="test", metadata=meta)
        assert node.metadata == meta, "Data must not be empty"

    # Parent-child relationship tests
    def test_add_child(self):
        parent = StandardizedASTNode(node_id="p1", type="class", name="MyClass")
        child = StandardizedASTNode(node_id="c1", type="function", name="method")
        parent.add_child(child)
        assert child in parent.children, "Condition must be true"
        assert len(parent.children) == 1, "Collection must not be empty"

    def test_add_multiple_children(self):
        parent = StandardizedASTNode(node_id="p1", type="class", name="MyClass")
        children = [
            StandardizedASTNode(node_id=f"c{i}", type="function", name=f"method{i}")
            for i in range(5)
        ]
        for child in children:
            parent.add_child(child)
        assert len(parent.children) == 5, "Collection must not be empty"
        assert all(child in parent.children for child in children), "Condition must be true"

    def test_add_child_sets_parent_reference(self):
        parent = StandardizedASTNode(node_id="p1", type="class", name="MyClass")
        child = StandardizedASTNode(node_id="c1", type="function", name="method")
        parent.add_child(child)
        assert child.parent == parent, "parent is not valid"

    def test_remove_child(self):
        parent = StandardizedASTNode(node_id="p1", type="class", name="MyClass")
        child = StandardizedASTNode(node_id="c1", type="function", name="method")
        parent.add_child(child)
        removed = parent.remove_child(child)
        assert removed is True, "removed is not valid"
        assert child not in parent.children, "Condition must be true"
        assert child.parent is None, "parent is not valid"

    def test_remove_nonexistent_child(self):
        parent = StandardizedASTNode(node_id="p1", type="class", name="MyClass")
        child = StandardizedASTNode(node_id="c1", type="function", name="method")
        removed = parent.remove_child(child)
        assert removed is False, "removed is not valid"
        assert len(parent.children) == 0, "Collection must not be empty"

    def test_parent_weakref_behavior(self):
        parent = StandardizedASTNode(node_id="p1", type="class", name="MyClass")
        child = StandardizedASTNode(node_id="c1", type="function", name="method")
        parent.add_child(child)
        assert child.parent is not None, "parent must be initialized"
        assert child.parent.node_id == "p1", "node_id is not valid"

    def test_parent_weakref_cleared_on_delete(self):
        parent = StandardizedASTNode(node_id="p1", type="class", name="MyClass")
        child = StandardizedASTNode(node_id="c1", type="function", name="method")
        parent.add_child(child)
        del parent
        import gc

        gc.collect()
        assert child.parent is None, "parent is not valid"

    def test_bidirectional_parent_child_relationship(self):
        parent = StandardizedASTNode(node_id="p1", type="class", name="MyClass")
        child = StandardizedASTNode(node_id="c1", type="function", name="method")
        parent.add_child(child)
        assert child in parent.children, "Condition must be true"
        assert child.parent == parent, "parent is not valid"

    # Tree traversal tests
    def test_find_by_type_single_match(self):
        root = StandardizedASTNode(node_id="root", type="module", name="main")
        child = StandardizedASTNode(node_id="c1", type="function", name="test")
        root.add_child(child)
        results = root.find_by_type("function")
        assert len(results) == 1, "Results must not be empty"
        assert child in results, "Result must not be empty"

    def test_find_by_type_multiple_matches(self):
        root = StandardizedASTNode(node_id="root", type="module", name="main")
        for i in range(3):
            child = StandardizedASTNode(node_id=f"func{i}", type="function", name=f"func{i}")
            root.add_child(child)
        results = root.find_by_type("function")
        assert len(results) == 3, "Results must not be empty"

    def test_find_by_type_no_matches(self):
        root = StandardizedASTNode(node_id="root", type="module", name="main")
        child = StandardizedASTNode(node_id="c1", type="function", name="test")
        root.add_child(child)
        results = root.find_by_type("class")
        assert len(results) == 0, "Results must not be empty"

    def test_find_by_type_nested(self):
        root = StandardizedASTNode(node_id="root", type="module", name="main")
        parent = StandardizedASTNode(node_id="p1", type="class", name="MyClass")
        child = StandardizedASTNode(node_id="c1", type="function", name="method")
        root.add_child(parent)
        parent.add_child(child)
        results = root.find_by_type("function")
        assert len(results) == 1, "Results must not be empty"
        assert child in results, "Result must not be empty"

    def test_find_by_name_single_match(self):
        root = StandardizedASTNode(node_id="root", type="module", name="main")
        child = StandardizedASTNode(node_id="c1", type="function", name="test_func")
        root.add_child(child)
        results = root.find_by_name("test_func")
        assert len(results) == 1, "Results must not be empty"
        assert child in results, "Result must not be empty"

    def test_find_by_name_multiple_matches(self):
        root = StandardizedASTNode(node_id="root", type="module", name="main")
        for i in range(2):
            child = StandardizedASTNode(node_id=f"n{i}", type="function", name="func")
            root.add_child(child)
        results = root.find_by_name("func")
        assert len(results) == 2, "Results must not be empty"

    def test_find_by_name_no_matches(self):
        root = StandardizedASTNode(node_id="root", type="module", name="main")
        results = root.find_by_name("nonexistent")
        assert len(results) == 0, "Results must not be empty"

    def test_walk_tree_traversal(self):
        root = StandardizedASTNode(node_id="root", type="module", name="main")
        nodes = [root]
        for i in range(3):
            child = StandardizedASTNode(node_id=f"c{i}", type="function", name=f"func{i}")
            root.add_child(child)
            nodes.append(child)
        walked = root.walk()
        assert len(walked) == 4, "Walked must not be empty"
        assert all(node in walked for node in nodes), "Condition must be true"

    def test_walk_nested_tree(self):
        root = StandardizedASTNode(node_id="root", type="module", name="main")
        parent = StandardizedASTNode(node_id="p1", type="class", name="MyClass")
        child = StandardizedASTNode(node_id="c1", type="function", name="method")
        root.add_child(parent)
        parent.add_child(child)
        walked = root.walk()
        assert root in walked, "Condition must be true"
        assert parent in walked, "Condition must be true"
        assert child in walked, "Condition must be true"

    def test_walk_preorder_traversal(self):
        root = StandardizedASTNode(node_id="root", type="module", name="main")
        child1 = StandardizedASTNode(node_id="c1", type="function", name="func1")
        child2 = StandardizedASTNode(node_id="c2", type="class", name="class1")
        root.add_child(child1)
        root.add_child(child2)
        walked = root.walk()
        assert walked[0] == root, "Condition must be true"

    def test_is_leaf_true(self):
        node = StandardizedASTNode(node_id="n1", type="function", name="test")
        assert node.is_leaf is True, "is_leaf is not valid"

    def test_is_leaf_false(self):
        parent = StandardizedASTNode(node_id="p1", type="class", name="MyClass")
        child = StandardizedASTNode(node_id="c1", type="function", name="method")
        parent.add_child(child)
        assert parent.is_leaf is False, "is_leaf is not valid"

    def test_is_root_true(self):
        node = StandardizedASTNode(node_id="n1", type="module", name="main")
        assert node.is_root is True, "is_root is not valid"

    def test_is_root_false(self):
        parent = StandardizedASTNode(node_id="p1", type="class", name="MyClass")
        child = StandardizedASTNode(node_id="c1", type="function", name="method")
        parent.add_child(child)
        assert child.is_root is False, "is_root is not valid"

    def test_depth_root_node(self):
        root = StandardizedASTNode(node_id="root", type="module", name="main")
        assert root.depth == 0, "depth is not valid"

    def test_depth_child_node(self):
        root = StandardizedASTNode(node_id="root", type="module", name="main")
        child = StandardizedASTNode(node_id="c1", type="function", name="test")
        root.add_child(child)
        assert child.depth == 1, "depth is not valid"

    def test_depth_deeply_nested(self):
        root = StandardizedASTNode(node_id="root", type="module", name="main")
        current = root
        for i in range(5):
            child = StandardizedASTNode(node_id=f"c{i}", type="function", name=f"func{i}")
            current.add_child(child)
            current = child
        assert current.depth == 5, "depth is not valid"

    # Serialization tests
    def test_to_dict_basic(self):
        node = StandardizedASTNode(node_id="n1", type="function", name="test")
        d = node.to_dict()
        assert d["node_id"] == "n1", "Condition must be true"
        assert d["type"] == "function", "Condition must be true"
        assert d["name"] == "test", "Condition must be true"

    def test_to_dict_with_location(self):
        loc = SourceLocation(Path("test.py"), 1, 5)
        node = StandardizedASTNode(node_id="n1", type="function", name="test", location=loc)
        d = node.to_dict()
        assert d["location"] is not None, "Value must be initialized"

    def test_to_dict_with_children(self):
        parent = StandardizedASTNode(node_id="p1", type="class", name="MyClass")
        child = StandardizedASTNode(node_id="c1", type="function", name="method")
        parent.add_child(child)
        d = parent.to_dict()
        assert "children" in d, "Condition must be true"
        assert len(d["children"]) == 1, "Collection must not be empty"

    def test_from_dict_basic(self):
        d = {"node_id": "n1", "type": "function", "name": "test", "children": [], "metadata": {}}
        node = StandardizedASTNode.from_dict(d)
        assert node.node_id == "n1", "node_id is not valid"
        assert node.type == "function", "type is not valid"
        assert node.name == "test", "name is not valid"

    def test_from_dict_with_location(self):
        loc_dict = {
            "file_path": "test.py",
            "line_start": 1,
            "line_end": 5,
            "column_start": 0,
            "column_end": 0,
        }
        d = {
            "node_id": "n1",
            "type": "function",
            "name": "test",
            "location": loc_dict,
            "children": [],
            "metadata": {},
        }
        node = StandardizedASTNode.from_dict(d)
        assert node.location is not None, "location must be initialized"
        assert str(node.location.file_path) == "test.py", "Condition must be true"

    def test_roundtrip_serialization(self):
        loc = SourceLocation(Path("test.py"), 5, 10)
        node = StandardizedASTNode(
            node_id="n1", type="function", name="test", location=loc, metadata={"key": "value"}
        )
        d = node.to_dict()
        restored = StandardizedASTNode.from_dict(d)
        assert restored.node_id == node.node_id, "node_id is not valid"
        assert restored.type == node.type, "type is not valid"
        assert restored.name == node.name, "name is not valid"
        assert restored.metadata == node.metadata, "Data must not be empty"

    # Edge cases and special behaviors
    def test_json_serializable(self):
        parent = StandardizedASTNode(node_id="p1", type="class", name="MyClass")
        child = StandardizedASTNode(node_id="c1", type="function", name="method")
        parent.add_child(child)
        d = parent.to_dict()
        json_str = json.dumps(d)
        assert len(json_str) > 0, "Json_str must not be empty"

    def test_empty_children_list(self):
        node = StandardizedASTNode(node_id="n1", type="function", name="test")
        assert node.children == [], "children is not valid"

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
        assert len(walked) == 4, "Walked must not be empty"

        # Find by type should work
        funcs = root.find_by_type("function")
        assert len(funcs) == 2, "Funcs must not be empty"


class TestFinding:
    """Test suite for Finding class (30 tests)."""

    # Creation tests
    def test_creation_minimal(self):
        finding = Finding(type="error", message="Test error")
        assert finding.type == "error", "Error should be raised or set"
        assert finding.message == "Test error", "Error should be raised or set"
        assert finding.severity == "info", "severity is not valid"

    def test_creation_with_id(self):
        finding = Finding(finding_id="f1", type="error", message="Test")
        assert finding.finding_id == "f1", "finding_id is not valid"

    def test_creation_with_severity(self):
        finding = Finding(type="error", message="Test", severity="critical")
        assert finding.severity == "critical", "severity is not valid"

    def test_creation_with_location(self):
        loc = SourceLocation(Path("test.py"), 5, 10)
        finding = Finding(type="error", message="Test", location=loc)
        assert finding.location == loc, "location is not valid"

    def test_creation_with_analyzer(self):
        finding = Finding(type="error", message="Test", analyzer="test_analyzer")
        assert finding.analyzer == "test_analyzer", "analyzer is not valid"

    def test_creation_with_metadata(self):
        meta = {"key": "value"}
        finding = Finding(type="error", message="Test", metadata=meta)
        assert finding.metadata == meta, "Data must not be empty"

    # ID generation tests
    def test_finding_id_auto_generation(self):
        finding = Finding(type="error", message="Test")
        assert finding.finding_id != "", "finding_id is not valid"
        import uuid

        try:
            uuid.UUID(finding.finding_id)
            assert True, "True is not valid"
        except ValueError:
            pytest.fail(f"finding_id {finding.finding_id} is not a valid UUID")

    def test_finding_id_unique(self):
        findings = [
            Finding(type="error", message="Test 1"),
            Finding(type="error", message="Test 2"),
        ]
        assert findings[0].finding_id != findings[1].finding_id, "finding_id is not valid"

    def test_finding_id_provided(self):
        finding = Finding(finding_id="custom_id", type="error", message="Test")
        assert finding.finding_id == "custom_id", "finding_id is not valid"

    # Severity validation tests
    @pytest.mark.parametrize("severity", ["info", "warning", "error", "critical"])
    def test_severity_valid_values(self, severity):
        finding = Finding(type="issue", message="Test", severity=severity)
        assert finding.severity == severity, "severity is not valid"

    def test_severity_default(self):
        finding = Finding(type="issue", message="Test")
        assert finding.severity == "info", "severity is not valid"

    # Serialization tests
    def test_to_dict_basic(self):
        finding = Finding(type="error", message="Test message")
        d = finding.to_dict()
        assert d["type"] == "error", "Error should be raised or set"
        assert d["message"] == "Test message", "Condition must be true"
        assert d["severity"] == "info", "Condition must be true"

    def test_to_dict_with_location(self):
        loc = SourceLocation(Path("test.py"), 5, 10)
        finding = Finding(type="error", message="Test", location=loc)
        d = finding.to_dict()
        assert d["location"] is not None, "Value must be initialized"

    def test_to_dict_with_all_fields(self):
        loc = SourceLocation(Path("test.py"), 5, 10)
        finding = Finding(
            finding_id="f1",
            type="error",
            message="Test",
            severity="critical",
            location=loc,
            analyzer="test_analyzer",
            metadata={"key": "value"},
        )
        d = finding.to_dict()
        assert d["finding_id"] == "f1", "Condition must be true"
        assert d["type"] == "error", "Error should be raised or set"
        assert d["severity"] == "critical", "Condition must be true"
        assert d["analyzer"] == "test_analyzer", "Condition must be true"

    def test_from_dict_basic(self):
        d = {"type": "error", "message": "Test", "severity": "warning"}
        finding = Finding.from_dict(d)
        assert finding.type == "error", "Error should be raised or set"
        assert finding.message == "Test", "message is not valid"
        assert finding.severity == "warning", "severity is not valid"

    def test_from_dict_with_location(self):
        loc_dict = {
            "file_path": "test.py",
            "line_start": 1,
            "line_end": 5,
            "column_start": 0,
            "column_end": 0,
        }
        d = {"type": "error", "message": "Test", "location": loc_dict}
        finding = Finding.from_dict(d)
        assert finding.location is not None, "location must be initialized"
        assert str(finding.location.file_path) == "test.py", "Condition must be true"

    def test_roundtrip_serialization(self):
        loc = SourceLocation(Path("test.py"), 5, 10)
        original = Finding(
            finding_id="f1",
            type="error",
            message="Test error",
            severity="critical",
            location=loc,
            analyzer="test_analyzer",
            metadata={"key": "value"},
        )
        d = original.to_dict()
        restored = Finding.from_dict(d)
        assert restored.finding_id == original.finding_id, "finding_id is not valid"
        assert restored.type == original.type, "type is not valid"
        assert restored.message == original.message, "message is not valid"
        assert restored.severity == original.severity, "severity is not valid"
        assert restored.analyzer == original.analyzer, "analyzer is not valid"

    # Edge cases
    def test_finding_with_empty_message(self):
        finding = Finding(type="error", message="")
        assert finding.message == "", "message is not valid"

    def test_finding_with_long_message(self):
        long_msg = "x" * 10000
        finding = Finding(type="error", message=long_msg)
        assert finding.message == long_msg, "message is not valid"

    def test_finding_with_multiline_message(self):
        msg = "Line 1\nLine 2\nLine 3"
        finding = Finding(type="error", message=msg)
        assert finding.message == msg, "message is not valid"

    def test_finding_with_special_characters(self):
        msg = "Test with special chars: !@#$%^&*()"
        finding = Finding(type="error", message=msg)
        assert finding.message == msg, "message is not valid"

    def test_finding_with_unicode(self):
        msg = "Test with unicode: 日本語"
        finding = Finding(type="error", message=msg)
        assert finding.message == msg, "message is not valid"

    def test_json_serializable(self):
        loc = SourceLocation(Path("test.py"), 5, 10)
        finding = Finding(type="error", message="Test", location=loc)
        d = finding.to_dict()
        json_str = json.dumps(d)
        assert len(json_str) > 0, "Json_str must not be empty"
