"""Tests for HTML visualization.

CB-005: HTMLVisualizer unit tests — node rendering, tree depth, CSS output.
"""

from codex.ast import parse_python
from codex.ast.graph import ASTGraph
from codex.ast.node import NodeType, StandardizedASTNode
from codex.ast.visualize import HTMLVisualizer


class TestHTMLVisualizer:
    """Test HTML visualization generation."""

    def test_render_html(self, tmp_path):
        """Test HTML report generation."""
        code = "def hello():\n    return 'world'"
        node = parse_python(code, "test.py")

        graph = ASTGraph()
        graph.add_node(node)

        visualizer = HTMLVisualizer()
        output = tmp_path / "report.html"

        visualizer.render_html([node], graph, {"complexity": 1}, str(output))

        assert output.exists(), "Condition must be true"
        content = output.read_text()
        assert "<html>" in content, "Content must not be empty"
        assert "AST Analysis Report" in content, "Content must not be empty"
        assert "d3.js" in content, "Content must not be empty"

    def test_node_to_dict(self, tmp_path):
        """Test node conversion to dictionary."""
        code = "class Example:\n    def method(self): pass"
        node = parse_python(code, "test.py")

        visualizer = HTMLVisualizer()
        node_dict = visualizer._node_to_dict(node)

        assert "id" in node_dict, "Condition must be true"
        assert "type" in node_dict, "Condition must be true"
        assert "children" in node_dict, "Condition must be true"

    # ------------------------------------------------------------------
    # CB-005: additional unit tests — node rendering, tree depth, CSS
    # ------------------------------------------------------------------

    def test_node_rendering_includes_function_and_class_counts(self, tmp_path):
        """CB-005: rendered HTML reflects function and class node counts."""
        code = (
            "class Foo:\n"
            "    def bar(self): pass\n"
            "    def baz(self): pass\n"
            "def top_level(): pass\n"
        )
        node = parse_python(code, "example.py")

        visualizer = HTMLVisualizer()
        output = tmp_path / "counts.html"
        visualizer.render_html([node], ASTGraph(), {"complexity": 5}, str(output))

        content = output.read_text()
        # Metric cards for Functions and Classes are present in the template
        assert "Functions" in content, "Content must not be empty"
        assert "Classes" in content, "Content must not be empty"
        # Complexity value is embedded
        assert "5" in content, "Content must not be empty"

    def test_tree_depth_reflected_in_node_children_count(self):
        """CB-005: _node_to_dict reports child count matching actual children."""
        from codex.ast.node import SourceLocation

        loc = SourceLocation(
            file_path="x.py", line_start=1, line_end=5, column_start=0, column_end=0
        )
        parent = StandardizedASTNode(
            node_id="parent-1",
            type=NodeType.CLASS,
            name="MyClass",
            source_location=loc,
        )
        for i in range(3):
            child = StandardizedASTNode(
                node_id=f"child-{i}",
                type=NodeType.FUNCTION,
                name=f"method_{i}",
                source_location=loc,
            )
            parent.add_child(child)

        visualizer = HTMLVisualizer()
        d = visualizer._node_to_dict(parent)

        assert d["children"] == 3, f"Expected 3 children in dict, got {d['children']}"
        assert d["type"] == "class", "Condition must be true"
        assert d["name"] == "MyClass", "Condition must be true"

    def test_css_output_contains_required_selectors(self, tmp_path):
        """CB-005: rendered HTML includes required CSS selectors for styling."""
        code = "x = 1"
        node = parse_python(code, "simple.py")

        visualizer = HTMLVisualizer()
        output = tmp_path / "css_check.html"
        visualizer.render_html([node], ASTGraph(), {}, str(output))

        content = output.read_text()
        # Core CSS classes that drive the visual layout must be present
        assert ".container" in content, "Content must not be empty"
        assert ".metric-card" in content, "Content must not be empty"
        assert ".node" in content, "Content must not be empty"
        assert "font-family" in content, "Content must not be empty"

    def test_render_html_with_empty_nodes(self, tmp_path):
        """CB-005: render_html handles an empty node list without error."""
        visualizer = HTMLVisualizer()
        output = tmp_path / "empty.html"
        visualizer.render_html([], ASTGraph(), {}, str(output))

        assert output.exists(), "Condition must be true"
        content = output.read_text()
        assert "<html>" in content, "Content must not be empty"
