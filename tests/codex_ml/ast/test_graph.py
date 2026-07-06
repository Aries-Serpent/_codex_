"""
Tests for DependencyGraph.
"""

import pytest

from codex_ml.ast.core.exceptions import CycleDetectedError
from codex_ml.ast.graph.dependency_graph import DependencyGraph


class TestDependencyGraph:
    """Tests for DependencyGraph class."""

    def test_create_empty_graph(self) -> None:
        """Test creating an empty graph."""
        graph = DependencyGraph()
        assert len(graph) == 0

    def test_add_node(self) -> None:
        """Test adding a node."""
        graph = DependencyGraph()
        graph.add_node("module_a", ["module_b", "module_c"])
        assert "module_a" in graph
        assert len(graph) == 3  # a, b, c are all added

    def test_add_node_no_deps(self) -> None:
        """Test adding a node without dependencies."""
        graph = DependencyGraph()
        graph.add_node("standalone")
        assert "standalone" in graph
        assert graph.get_dependencies("standalone") == set()

    def test_get_dependencies(self) -> None:
        """Test getting node dependencies."""
        graph = DependencyGraph()
        graph.add_node("module_a", ["module_b", "module_c"])
        deps = graph.get_dependencies("module_a")
        assert deps == {"module_b", "module_c"}

    def test_get_dependents(self) -> None:
        """Test getting nodes that depend on a node."""
        graph = DependencyGraph()
        graph.add_node("module_a", ["module_b"])
        graph.add_node("module_c", ["module_b"])
        dependents = graph.get_dependents("module_b")
        assert dependents == {"module_a", "module_c"}

    def test_add_edge(self) -> None:
        """Test adding an edge."""
        graph = DependencyGraph()
        graph.add_edge("a", "b")
        assert graph.get_dependencies("a") == {"b"}
        assert graph.get_dependents("b") == {"a"}

    def test_remove_edge(self) -> None:
        """Test removing an edge."""
        graph = DependencyGraph()
        graph.add_edge("a", "b")
        result = graph.remove_edge("a", "b")
        assert result is True
        assert graph.get_dependencies("a") == set()

    def test_remove_edge_not_found(self) -> None:
        """Test removing non-existent edge."""
        graph = DependencyGraph()
        graph.add_node("a")
        result = graph.remove_edge("a", "b")
        assert result is False

    def test_remove_node(self) -> None:
        """Test removing a node."""
        graph = DependencyGraph()
        graph.add_node("a", ["b"])
        graph.add_node("c", ["a"])
        result = graph.remove_node("a")
        assert result is True
        assert "a" not in graph

    def test_remove_node_not_found(self) -> None:
        """Test removing non-existent node."""
        graph = DependencyGraph()
        result = graph.remove_node("nonexistent")
        assert result is False

    def test_get_all_dependencies(self) -> None:
        """Test getting transitive dependencies."""
        graph = DependencyGraph()
        graph.add_node("a", ["b"])
        graph.add_node("b", ["c"])
        graph.add_node("c", ["d"])
        graph.add_node("d")

        all_deps = graph.get_all_dependencies("a")
        assert all_deps == {"b", "c", "d"}

    def test_has_cycle_false(self) -> None:
        """Test cycle detection on acyclic graph."""
        graph = DependencyGraph()
        graph.add_node("a", ["b"])
        graph.add_node("b", ["c"])
        graph.add_node("c")
        assert graph.has_cycle() is False

    def test_has_cycle_true(self) -> None:
        """Test cycle detection on cyclic graph."""
        graph = DependencyGraph()
        graph.add_node("a", ["b"])
        graph.add_node("b", ["c"])
        graph.add_node("c", ["a"])  # Creates cycle
        assert graph.has_cycle() is True

    def test_has_cycle_self_reference(self) -> None:
        """Test cycle detection on self-referencing node."""
        graph = DependencyGraph()
        graph.add_node("a", ["a"])  # Self-reference
        assert graph.has_cycle() is True

    def test_find_cycle(self) -> None:
        """Test finding a cycle."""
        graph = DependencyGraph()
        graph.add_node("a", ["b"])
        graph.add_node("b", ["c"])
        graph.add_node("c", ["a"])  # Creates cycle

        cycle = graph.find_cycle()
        assert cycle is not None
        assert len(cycle) >= 3  # At least 3 nodes in cycle

    def test_find_cycle_none(self) -> None:
        """Test finding cycle when none exists."""
        graph = DependencyGraph()
        graph.add_node("a", ["b"])
        graph.add_node("b")
        assert graph.find_cycle() is None

    def test_topological_sort_simple(self) -> None:
        """Test topological sort on simple graph."""
        graph = DependencyGraph()
        graph.add_node("a", ["b"])
        graph.add_node("b", ["c"])
        graph.add_node("c")

        order = graph.topological_sort()
        assert order.index("c") < order.index("b")
        assert order.index("b") < order.index("a")

    def test_topological_sort_with_cycle(self) -> None:
        """Test topological sort raises on cyclic graph."""
        graph = DependencyGraph()
        graph.add_node("a", ["b"])
        graph.add_node("b", ["a"])

        with pytest.raises(CycleDetectedError):
            graph.topological_sort()

    def test_reverse_topological_sort(self) -> None:
        """Test reverse topological sort."""
        graph = DependencyGraph()
        graph.add_node("a", ["b"])
        graph.add_node("b", ["c"])
        graph.add_node("c")

        order = graph.reverse_topological_sort()
        assert order.index("a") < order.index("b")
        assert order.index("b") < order.index("c")

    def test_get_roots(self) -> None:
        """Test getting root nodes."""
        graph = DependencyGraph()
        graph.add_node("a", ["b"])
        graph.add_node("b", ["c"])
        graph.add_node("c")
        graph.add_node("standalone")

        roots = graph.get_roots()
        assert "c" in roots
        assert "standalone" in roots
        assert "a" not in roots

    def test_get_leaves(self) -> None:
        """Test getting leaf nodes."""
        graph = DependencyGraph()
        graph.add_node("a", ["b"])
        graph.add_node("b", ["c"])
        graph.add_node("c")

        leaves = graph.get_leaves()
        assert "a" in leaves
        assert "c" not in leaves

    def test_strongly_connected_components(self) -> None:
        """Test SCC detection."""
        graph = DependencyGraph()
        # Create a cycle: a -> b -> c -> a
        graph.add_node("a", ["b"])
        graph.add_node("b", ["c"])
        graph.add_node("c", ["a"])
        # Add standalone node
        graph.add_node("d")

        sccs = graph.get_strongly_connected_components()
        # Should have 2 SCCs: {a, b, c} and {d}
        assert len(sccs) == 2

        # Find the SCC containing the cycle
        cycle_scc = None
        for scc in sccs:
            if "a" in scc:
                cycle_scc = scc
                break

        assert cycle_scc is not None
        assert cycle_scc == {"a", "b", "c"}

    def test_repr(self) -> None:
        """Test string representation."""
        graph = DependencyGraph()
        graph.add_node("a", ["b", "c"])
        repr_str = repr(graph)
        assert "DependencyGraph" in repr_str
        assert "nodes=3" in repr_str
