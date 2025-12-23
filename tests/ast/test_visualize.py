"""Tests for HTML visualization."""
import pytest
from pathlib import Path

from codex.ast import parse_python
from codex.ast.visualize import HTMLVisualizer
from codex.ast.graph import ASTGraph


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
        
        visualizer.render_html(
            [node],
            graph,
            {'complexity': 1},
            str(output)
        )
        
        assert output.exists()
        content = output.read_text()
        assert '<html>' in content
        assert 'AST Analysis Report' in content
        assert 'd3.js' in content
    
    def test_node_to_dict(self, tmp_path):
        """Test node conversion to dictionary."""
        code = "class Example:\n    def method(self): pass"
        node = parse_python(code, "test.py")
        
        visualizer = HTMLVisualizer()
        node_dict = visualizer._node_to_dict(node)
        
        assert 'id' in node_dict
        assert 'type' in node_dict
        assert 'children' in node_dict
