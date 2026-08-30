"""Tests for dependency graph module."""

import pytest

from codex.ast.graph import DependencyGraph


def test_simple_cycle():
    """Test detection of simple 2-node cycle."""
    graph = DependencyGraph()
    graph.add_edge("A", "B")
    graph.add_edge("B", "A")

    cycles = graph.detect_cycles()
    assert len(cycles) == 1, "Cycles must not be empty"
    assert set(cycles[0]) == {"A", "B"}


def test_complex_cycle():
    """Test detection of complex 4-node cycle."""
    graph = DependencyGraph()
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    graph.add_edge("C", "D")
    graph.add_edge("D", "A")

    cycles = graph.detect_cycles()
    assert len(cycles) == 1, "Cycles must not be empty"
    assert set(cycles[0]) == {"A", "B", "C", "D"}


def test_no_cycles():
    """Test graph with no cycles."""
    graph = DependencyGraph()
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")

    cycles = graph.detect_cycles()
    assert len(cycles) == 0, "Cycles must not be empty"


def test_topological_sort():
    """Test topological sort on DAG."""
    graph = DependencyGraph()
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    graph.add_edge("A", "C")

    order = graph.topological_sort()
    assert order.index("A") < order.index("B"), "Condition must be true"
    assert order.index("B") < order.index("C"), "Condition must be true"


def test_topological_sort_with_cycle():
    """Test topological sort fails with cycles."""
    graph = DependencyGraph()
    graph.add_edge("A", "B")
    graph.add_edge("B", "A")

    with pytest.raises(ValueError, match="Graph has cycles"):
        graph.topological_sort()


def test_transitive_deps():
    """Test transitive dependency detection."""
    graph = DependencyGraph()
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    graph.add_edge("C", "D")

    deps = graph.get_transitive_deps("A")
    assert deps == {"B", "C", "D"}


def test_add_node():
    """Test adding isolated nodes."""
    graph = DependencyGraph()
    graph.add_node("A")
    graph.add_node("B")

    assert "A" in graph.nodes, "Condition must be true"
    assert "B" in graph.nodes, "Condition must be true"
    assert len(graph.edges) == 0, "Collection must not be empty"


def test_self_loop_detected():
    """Test that self-loops are detected as cycles."""
    graph = DependencyGraph()
    graph.add_edge("A", "A")

    cycles = graph.detect_cycles()
    assert len(cycles) == 1, "Cycles must not be empty"
    assert cycles[0] == ["A"], "Condition must be true"


def test_self_loop_topological_sort_fails():
    """Test that topological sort fails with self-loops."""
    graph = DependencyGraph()
    graph.add_edge("A", "A")

    with pytest.raises(ValueError, match="Graph has cycles"):
        graph.topological_sort()


def test_multiple_self_loops():
    """Test detection of multiple independent self-loops."""
    graph = DependencyGraph()
    graph.add_edge("A", "A")
    graph.add_edge("B", "B")

    cycles = graph.detect_cycles()
    assert len(cycles) == 2, "Cycles must not be empty"
    cycle_nodes = {tuple(cycle) for cycle in cycles}
    assert ("A",) in cycle_nodes
    assert ("B",) in cycle_nodes


def test_mixed_cycles_and_self_loops():
    """Test detection of both multi-node cycles and self-loops."""
    graph = DependencyGraph()
    # Multi-node cycle
    graph.add_edge("A", "B")
    graph.add_edge("B", "A")
    # Self-loop
    graph.add_edge("C", "C")
    # Acyclic part
    graph.add_edge("D", "E")

    cycles = graph.detect_cycles()
    assert len(cycles) == 2, "Cycles must not be empty"

    # Check we have one 2-node cycle and one 1-node cycle
    cycle_sizes = sorted([len(cycle) for cycle in cycles])
    assert cycle_sizes == [1, 2]


def test_no_false_positives_for_isolated_nodes():
    """Test that isolated nodes without self-edges are not reported as cycles."""
    graph = DependencyGraph()
    graph.add_node("A")
    graph.add_node("B")
    graph.add_edge("C", "D")

    cycles = graph.detect_cycles()
    assert len(cycles) == 0, "Cycles must not be empty"
