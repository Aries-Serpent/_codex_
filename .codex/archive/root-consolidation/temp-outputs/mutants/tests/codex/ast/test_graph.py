"""
Tests for codex.ast.graph module.

This module contains tests for dependency graph and cycle detection.
"""


class TestDependencyGraph:
    """Tests for DependencyGraph class."""

    def test_init_empty(self):
        """Test DependencyGraph initialization."""
        from codex.ast.graph import DependencyGraph

        graph = DependencyGraph()

        assert graph.nodes == set(), "nodes is not valid"
        assert len(graph.edges) == 0, "Collection must not be empty"

    def test_add_node(self):
        """Test adding a node."""
        from codex.ast.graph import DependencyGraph

        graph = DependencyGraph()
        graph.add_node("A")

        assert "A" in graph.nodes, "Condition must be true"

    def test_add_multiple_nodes(self):
        """Test adding multiple nodes."""
        from codex.ast.graph import DependencyGraph

        graph = DependencyGraph()
        graph.add_node("A")
        graph.add_node("B")
        graph.add_node("C")

        assert len(graph.nodes) == 3, "Collection must not be empty"

    def test_add_edge(self):
        """Test adding an edge."""
        from codex.ast.graph import DependencyGraph

        graph = DependencyGraph()
        graph.add_edge("A", "B")

        assert "A" in graph.nodes, "Condition must be true"
        assert "B" in graph.nodes, "Condition must be true"
        assert "B" in graph.edges["A"], "Condition must be true"

    def test_add_edge_creates_nodes(self):
        """Test adding edge creates nodes automatically."""
        from codex.ast.graph import DependencyGraph

        graph = DependencyGraph()
        graph.add_edge("X", "Y")

        assert "X" in graph.nodes, "Condition must be true"
        assert "Y" in graph.nodes, "Condition must be true"

    def test_detect_cycles_no_cycles(self):
        """Test cycle detection with no cycles."""
        from codex.ast.graph import DependencyGraph

        graph = DependencyGraph()
        graph.add_edge("A", "B")
        graph.add_edge("B", "C")
        graph.add_edge("A", "C")

        cycles = graph.detect_cycles()

        assert cycles == [], "cycles is not valid"

    def test_detect_cycles_simple_cycle(self):
        """Test detecting a simple cycle."""
        from codex.ast.graph import DependencyGraph

        graph = DependencyGraph()
        graph.add_edge("A", "B")
        graph.add_edge("B", "C")
        graph.add_edge("C", "A")  # Creates cycle

        cycles = graph.detect_cycles()

        assert len(cycles) == 1, "Cycles must not be empty"
        assert set(cycles[0]) == {"A", "B", "C"}

    def test_detect_cycles_self_loop(self):
        """Test detecting a self-loop cycle."""
        from codex.ast.graph import DependencyGraph

        graph = DependencyGraph()
        graph.add_edge("A", "A")  # Self-loop

        cycles = graph.detect_cycles()

        assert len(cycles) == 1, "Cycles must not be empty"
        assert cycles[0] == ["A"], "Condition must be true"

    def test_detect_cycles_multiple_cycles(self):
        """Test detecting multiple independent cycles."""
        from codex.ast.graph import DependencyGraph

        graph = DependencyGraph()
        # First cycle: A -> B -> A
        graph.add_edge("A", "B")
        graph.add_edge("B", "A")
        # Second cycle: C -> D -> C
        graph.add_edge("C", "D")
        graph.add_edge("D", "C")

        cycles = graph.detect_cycles()

        assert len(cycles) == 2, "Cycles must not be empty"

    def test_detect_cycles_empty_graph(self):
        """Test cycle detection on empty graph."""
        from codex.ast.graph import DependencyGraph

        graph = DependencyGraph()

        cycles = graph.detect_cycles()

        assert cycles == [], "cycles is not valid"

    def test_detect_cycles_single_node(self):
        """Test cycle detection with single node no edges."""
        from codex.ast.graph import DependencyGraph

        graph = DependencyGraph()
        graph.add_node("A")

        cycles = graph.detect_cycles()

        assert cycles == [], "cycles is not valid"

    def test_complex_graph(self):
        """Test with more complex graph structure."""
        from codex.ast.graph import DependencyGraph

        graph = DependencyGraph()
        # Linear chain with branch
        graph.add_edge("A", "B")
        graph.add_edge("B", "C")
        graph.add_edge("C", "D")
        graph.add_edge("A", "E")
        graph.add_edge("E", "F")

        cycles = graph.detect_cycles()

        assert cycles == [], "cycles is not valid"
