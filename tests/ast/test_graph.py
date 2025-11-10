"""Tests for dependency graph module."""

import pytest
from codex.ast.graph import DependencyGraph


def test_simple_cycle():
    """Test detection of simple 2-node cycle."""
    graph = DependencyGraph()
    graph.add_edge("A", "B")
    graph.add_edge("B", "A")
    
    cycles = graph.detect_cycles()
    assert len(cycles) == 1
    assert set(cycles[0]) == {"A", "B"}


def test_complex_cycle():
    """Test detection of complex 4-node cycle."""
    graph = DependencyGraph()
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    graph.add_edge("C", "D")
    graph.add_edge("D", "A")
    
    cycles = graph.detect_cycles()
    assert len(cycles) == 1
    assert set(cycles[0]) == {"A", "B", "C", "D"}


def test_no_cycles():
    """Test graph with no cycles."""
    graph = DependencyGraph()
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    
    cycles = graph.detect_cycles()
    assert len(cycles) == 0


def test_topological_sort():
    """Test topological sort on DAG."""
    graph = DependencyGraph()
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    graph.add_edge("A", "C")
    
    order = graph.topological_sort()
    assert order.index("A") < order.index("B")
    assert order.index("B") < order.index("C")


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
    
    assert "A" in graph.nodes
    assert "B" in graph.nodes
    assert len(graph.edges) == 0
