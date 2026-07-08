"""Shared test fixtures for AST module."""

from pathlib import Path

import pytest

from codex.ast.graph import DependencyGraph
from codex.ast.metrics import CodeMetrics
from codex.ast.node import NodeType, SourceLocation, StandardizedASTNode


@pytest.fixture
def sample_location() -> SourceLocation:
    """Sample source location."""
    return SourceLocation(Path("test.py"), 1, 0, 5, 20)


@pytest.fixture
def sample_node(sample_location) -> StandardizedASTNode:
    """Sample AST node."""
    return StandardizedASTNode(
        node_id="test_func",
        type=NodeType.FUNCTION,
        name="test_function",
        source_location=sample_location,
        docstring="Test function",
    )


@pytest.fixture
def sample_graph() -> DependencyGraph:
    """Sample dependency graph."""
    graph = DependencyGraph()
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    return graph


@pytest.fixture
def sample_metrics() -> CodeMetrics:
    """Sample code metrics."""
    return CodeMetrics(
        cyclomatic_complexity=5,
        cognitive_complexity=4.0,
        lines_of_code=50,
        comment_lines=5,
        maintainability_index=85.0,
    )
