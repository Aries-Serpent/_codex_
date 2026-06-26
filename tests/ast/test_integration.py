"""Integration tests for AST module."""

from pathlib import Path

from codex.ast.graph import DependencyGraph
from codex.ast.metrics import CodeMetrics, MetricsAggregator
from codex.ast.node import NodeType, SourceLocation, StandardizedASTNode


def test_complete_workflow():
    """Test complete AST analysis workflow."""
    # 1. Create AST nodes
    loc1 = SourceLocation(Path("module.py"), 1, 0, 10, 0)
    module = StandardizedASTNode("mod1", NodeType.MODULE, "module", loc1)

    loc2 = SourceLocation(Path("module.py"), 2, 0, 5, 0)
    func1 = StandardizedASTNode("func1", NodeType.FUNCTION, "process", loc2)

    loc3 = SourceLocation(Path("module.py"), 6, 0, 10, 0)
    func2 = StandardizedASTNode("func2", NodeType.FUNCTION, "validate", loc3)

    module.add_child(func1)
    module.add_child(func2)

    # 2. Build dependency graph
    graph = DependencyGraph()
    graph.add_edge("func1", "func2")

    # 3. Collect metrics
    metrics1 = CodeMetrics(5, 3.0, 50, 5, 80.0)
    metrics2 = CodeMetrics(3, 2.0, 30, 3, 90.0)

    agg = MetricsAggregator()
    agg.store_metrics("func1", metrics1)
    agg.store_metrics("func2", metrics2)

    # Verify workflow
    assert len(list(module.walk())) == 3, "Collection must not be empty"
    assert graph.detect_cycles() == [], "Condition must be true"
    assert agg.summary()["total_entities"] == 2, "Condition must be true"


def test_node_to_graph():
    """Test converting AST nodes to dependency graph."""
    # Create a tree of nodes
    root = StandardizedASTNode(
        "root", NodeType.MODULE, "main", SourceLocation(Path("main.py"), 1, 0, 20, 0)
    )

    child1 = StandardizedASTNode(
        "child1", NodeType.FUNCTION, "helper", SourceLocation(Path("main.py"), 2, 0, 10, 0)
    )

    child2 = StandardizedASTNode(
        "child2", NodeType.FUNCTION, "worker", SourceLocation(Path("main.py"), 11, 0, 20, 0)
    )

    root.add_child(child1)
    root.add_child(child2)

    # Build graph from tree structure
    graph = DependencyGraph()
    for node in root.walk():
        graph.add_node(node.node_id)
        if node.parent:
            graph.add_edge(node.parent.node_id, node.node_id)

    # Verify graph structure
    assert "root" in graph.nodes, "Condition must be true"
    assert "child1" in graph.nodes, "Condition must be true"
    assert "child2" in graph.nodes, "Condition must be true"
    assert len(graph.detect_cycles()) == 0, "Collection must not be empty"


def test_metrics_across_modules():
    """Test aggregating metrics across multiple modules."""
    agg = MetricsAggregator()

    # Module 1 metrics
    for i in range(5):
        m = CodeMetrics(
            cyclomatic_complexity=i + 1,
            cognitive_complexity=float(i),
            lines_of_code=(i + 1) * 20,
            comment_lines=(i + 1) * 2,
            maintainability_index=90.0 - i * 5,
        )
        agg.store_metrics(f"mod1_func{i}", m)

    # Module 2 metrics
    for i in range(3):
        m = CodeMetrics(
            cyclomatic_complexity=i + 2,
            cognitive_complexity=float(i + 1),
            lines_of_code=(i + 2) * 15,
            comment_lines=(i + 2) * 3,
            maintainability_index=85.0 - i * 5,
        )
        agg.store_metrics(f"mod2_func{i}", m)

    summary = agg.summary()
    assert summary["total_entities"] == 8, "Condition must be true"
    assert summary["total_lines_of_code"] > 0, "Value must be greater than zero"


def test_cycle_detection_with_nodes():
    """Test cycle detection with actual node dependencies."""
    graph = DependencyGraph()

    # Create cyclic dependency: A -> B -> C -> A
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    graph.add_edge("C", "A")

    cycles = graph.detect_cycles()
    assert len(cycles) == 1, "Cycles must not be empty"
    assert set(cycles[0]) == {"A", "B", "C"}


def test_serialization_roundtrip():
    """Test node serialization and data integrity."""
    loc = SourceLocation(Path("test.py"), 1, 0, 10, 20)
    node = StandardizedASTNode(
        node_id="test_node",
        type=NodeType.CLASS,
        name="TestClass",
        source_location=loc,
        docstring="Test class docstring",
        decorators=["@dataclass"],
        type_hints={"attr": "str"},
        metadata={"complexity": 5},
    )

    data = node.to_dict()

    # Verify all fields are serialized
    assert data["node_id"] == "test_node", "Data must not be empty"
    assert data["type"] == "class", "Data must not be empty"
    assert data["name"] == "TestClass", "Data must not be empty"
    assert data["docstring"] == "Test class docstring", "Data must not be empty"
    assert data["decorators"] == ["@dataclass"], "Data must not be empty"
    assert data["type_hints"] == {"attr": "str"}, "Data must not be empty"
    assert data["metadata"] == {"complexity": 5}, "Data must not be empty"


def test_multiple_cycles_detection():
    """Test detection of multiple independent cycles."""
    graph = DependencyGraph()

    # Cycle 1: A -> B -> A
    graph.add_edge("A", "B")
    graph.add_edge("B", "A")

    # Cycle 2: C -> D -> E -> C
    graph.add_edge("C", "D")
    graph.add_edge("D", "E")
    graph.add_edge("E", "C")

    cycles = graph.detect_cycles()
    assert len(cycles) == 2, "Cycles must not be empty"


def test_empty_metrics_summary():
    """Test summary with no metrics stored."""
    agg = MetricsAggregator()
    summary = agg.summary()
    assert summary == {}, "summary is not valid"
