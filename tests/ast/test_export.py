"""Tests for Knowledge Graph Export module."""

import json
import sqlite3
from pathlib import Path

import pytest

from codex.ast.export import (
    ExportFormat,
    ExportResult,
    KnowledgeGraphExporter,
    export_knowledge_graph,
)
from codex.ast.graph import DependencyGraph
from codex.ast.metrics import CodeMetrics, MetricsAggregator
from codex.ast.node import NodeType, SourceLocation, StandardizedASTNode


@pytest.fixture
def sample_nodes():
    """Create sample AST nodes for testing."""
    loc1 = SourceLocation(Path("module.py"), 1, 0, 50, 0)
    root = StandardizedASTNode("mod1", NodeType.MODULE, "sample_module", loc1)

    loc2 = SourceLocation(Path("module.py"), 5, 0, 20, 0)
    func = StandardizedASTNode(
        "func1",
        NodeType.FUNCTION,
        "process_data",
        loc2,
        docstring="Process the data.",
    )

    loc3 = SourceLocation(Path("module.py"), 25, 0, 50, 0)
    cls = StandardizedASTNode(
        "cls1",
        NodeType.CLASS,
        "DataProcessor",
        loc3,
        docstring="Data processing class.",
    )

    root.add_child(func)
    root.add_child(cls)

    return [root]


@pytest.fixture
def sample_graph():
    """Create sample dependency graph."""
    graph = DependencyGraph()
    graph.add_edge("func1", "cls1")
    graph.add_edge("cls1", "func2")
    return graph


@pytest.fixture
def sample_metrics():
    """Create sample metrics aggregator."""
    agg = MetricsAggregator()
    agg.store_metrics("func1", CodeMetrics(5, 3.0, 50, 5, 85.0))
    agg.store_metrics("cls1", CodeMetrics(10, 7.0, 100, 10, 75.0))
    return agg


class TestKnowledgeGraphExporter:
    """Tests for KnowledgeGraphExporter class."""

    def test_export_json(self, sample_nodes):
        """Test JSON export."""
        exporter = KnowledgeGraphExporter()
        exporter.add_nodes(sample_nodes)
        exporter.set_metadata("project", "test")

        result = exporter.export(ExportFormat.JSON)

        assert result.success
        assert result.content is not None

        data = json.loads(result.content)
        assert data["version"] == "1.0"
        assert data["metadata"]["project"] == "test"
        assert len(data["nodes"]) == 1

    def test_export_json_with_graph(self, sample_nodes, sample_graph):
        """Test JSON export with dependency graph."""
        exporter = KnowledgeGraphExporter()
        exporter.add_nodes(sample_nodes)
        exporter.set_graph(sample_graph)

        result = exporter.export(ExportFormat.JSON)

        assert result.success
        data = json.loads(result.content)
        assert data["graph"] is not None
        assert len(data["graph"]["edges"]) == 2

    def test_export_json_with_metrics(self, sample_nodes, sample_metrics):
        """Test JSON export with metrics."""
        exporter = KnowledgeGraphExporter()
        exporter.add_nodes(sample_nodes)
        exporter.set_metrics(sample_metrics)

        result = exporter.export(ExportFormat.JSON)

        assert result.success
        data = json.loads(result.content)
        assert data["metrics"] is not None
        assert "summary" in data["metrics"]

    def test_export_json_to_file(self, sample_nodes, tmp_path):
        """Test JSON export to file."""
        output_file = tmp_path / "export.json"

        exporter = KnowledgeGraphExporter()
        exporter.add_nodes(sample_nodes)

        result = exporter.export(ExportFormat.JSON, output_file)

        assert result.success
        assert output_file.exists()
        assert result.content is None  # Content not returned when writing to file

        data = json.loads(output_file.read_text())
        assert len(data["nodes"]) == 1

    def test_export_graphml(self, sample_nodes, sample_graph):
        """Test GraphML export."""
        exporter = KnowledgeGraphExporter()
        exporter.add_nodes(sample_nodes)
        exporter.set_graph(sample_graph)

        result = exporter.export(ExportFormat.GRAPHML)

        assert result.success
        assert result.content is not None
        assert '<?xml version="1.0"' in result.content
        assert "<graphml" in result.content
        assert 'id="mod1"' in result.content

    def test_export_graphml_escapes_special_chars(self, tmp_path):
        """Test GraphML properly escapes XML characters."""
        loc = SourceLocation(Path("test<file>.py"), 1, 0, 10, 0)
        node = StandardizedASTNode("n1", NodeType.MODULE, "test&module", loc)

        exporter = KnowledgeGraphExporter()
        exporter.add_node(node)

        result = exporter.export(ExportFormat.GRAPHML)

        assert result.success
        assert "&lt;" in result.content  # Escaped <
        assert "&amp;" in result.content  # Escaped &

    def test_export_dot(self, sample_nodes, sample_graph):
        """Test DOT (Graphviz) export."""
        exporter = KnowledgeGraphExporter()
        exporter.add_nodes(sample_nodes)
        exporter.set_graph(sample_graph)

        result = exporter.export(ExportFormat.DOT)

        assert result.success
        assert result.content is not None
        assert "digraph" in result.content
        assert 'mod1' in result.content
        assert "->" in result.content

    def test_export_dot_highlights_cycles(self):
        """Test DOT export highlights cycles in red."""
        loc = SourceLocation(Path("test.py"), 1, 0, 10, 0)
        node = StandardizedASTNode("n1", NodeType.MODULE, "test", loc)

        graph = DependencyGraph()
        graph.add_edge("A", "B")
        graph.add_edge("B", "A")  # Cycle

        exporter = KnowledgeGraphExporter()
        exporter.add_node(node)
        exporter.set_graph(graph)

        result = exporter.export(ExportFormat.DOT)

        assert result.success
        assert "color=red" in result.content

    def test_export_sqlite(self, sample_nodes, sample_graph, sample_metrics, tmp_path):
        """Test SQLite export."""
        db_path = tmp_path / "knowledge.db"

        exporter = KnowledgeGraphExporter()
        exporter.add_nodes(sample_nodes)
        exporter.set_graph(sample_graph)
        exporter.set_metrics(sample_metrics)
        exporter.set_metadata("version", "1.0")

        result = exporter.export(ExportFormat.SQLITE, db_path)

        assert result.success
        assert db_path.exists()

        # Verify database contents
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check nodes table
        cursor.execute("SELECT COUNT(*) FROM nodes")
        node_count = cursor.fetchone()[0]
        assert node_count >= 1

        # Check edges table
        cursor.execute("SELECT COUNT(*) FROM edges")
        edge_count = cursor.fetchone()[0]
        assert edge_count == 2

        # Check metrics table
        cursor.execute("SELECT COUNT(*) FROM metrics")
        metrics_count = cursor.fetchone()[0]
        assert metrics_count == 2

        # Check metadata table
        cursor.execute("SELECT value FROM metadata WHERE key = 'version'")
        version = cursor.fetchone()[0]
        assert json.loads(version) == "1.0"

        conn.close()

    def test_export_sqlite_requires_path(self, sample_nodes):
        """Test SQLite export requires output path."""
        exporter = KnowledgeGraphExporter()
        exporter.add_nodes(sample_nodes)

        result = exporter.export(ExportFormat.SQLITE)

        assert not result.success
        assert "requires output_path" in result.error

    def test_export_sqlite_indexes(self, sample_nodes, tmp_path):
        """Test SQLite export creates indexes."""
        db_path = tmp_path / "indexed.db"

        exporter = KnowledgeGraphExporter()
        exporter.add_nodes(sample_nodes)

        result = exporter.export(ExportFormat.SQLITE, db_path)

        assert result.success

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check indexes exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in cursor.fetchall()]

        assert "idx_nodes_type" in indexes
        assert "idx_nodes_file" in indexes

        conn.close()

    def test_export_markdown(self, sample_nodes, sample_graph, sample_metrics):
        """Test Markdown export."""
        exporter = KnowledgeGraphExporter()
        exporter.add_nodes(sample_nodes)
        exporter.set_graph(sample_graph)
        exporter.set_metrics(sample_metrics)
        exporter.set_metadata("project", "test_project")

        result = exporter.export(ExportFormat.MARKDOWN)

        assert result.success
        assert result.content is not None
        assert "# Code Knowledge Graph" in result.content
        assert "test_project" in result.content
        assert "Dependency Analysis" in result.content
        assert "Metrics Summary" in result.content

    def test_export_markdown_shows_cycles(self):
        """Test Markdown export shows detected cycles."""
        loc = SourceLocation(Path("test.py"), 1, 0, 10, 0)
        node = StandardizedASTNode("n1", NodeType.MODULE, "test", loc)

        graph = DependencyGraph()
        graph.add_edge("A", "B")
        graph.add_edge("B", "C")
        graph.add_edge("C", "A")

        exporter = KnowledgeGraphExporter()
        exporter.add_node(node)
        exporter.set_graph(graph)

        result = exporter.export(ExportFormat.MARKDOWN)

        assert result.success
        assert "Circular Dependencies" in result.content
        assert "→" in result.content

    def test_add_nodes_batch(self, sample_nodes):
        """Test adding multiple nodes at once."""
        exporter = KnowledgeGraphExporter()
        exporter.add_nodes(sample_nodes)

        result = exporter.export(ExportFormat.JSON)

        assert result.success
        data = json.loads(result.content)
        assert len(data["nodes"]) == len(sample_nodes)

    def test_export_result_to_dict(self):
        """Test ExportResult serialization."""
        result = ExportResult(
            format=ExportFormat.JSON,
            output_path=Path("test.json"),
            content=None,
            success=True,
        )

        data = result.to_dict()

        assert data["format"] == "json"
        assert data["output_path"] == "test.json"
        assert data["success"] is True


class TestExportKnowledgeGraphFunction:
    """Tests for export_knowledge_graph convenience function."""

    def test_export_basic(self, sample_nodes):
        """Test basic export."""
        result = export_knowledge_graph(sample_nodes)

        assert result.success
        assert result.format == ExportFormat.JSON

    def test_export_with_graph_and_metrics(
        self, sample_nodes, sample_graph, sample_metrics
    ):
        """Test export with all components."""
        result = export_knowledge_graph(
            sample_nodes,
            format=ExportFormat.JSON,
            graph=sample_graph,
            metrics=sample_metrics,
        )

        assert result.success
        data = json.loads(result.content)
        assert data["graph"] is not None
        assert data["metrics"] is not None

    def test_export_to_file(self, sample_nodes, tmp_path):
        """Test export to file."""
        output_file = tmp_path / "export.json"

        result = export_knowledge_graph(
            sample_nodes,
            format=ExportFormat.JSON,
            output_path=output_file,
        )

        assert result.success
        assert output_file.exists()

    def test_export_different_formats(self, sample_nodes):
        """Test exporting to different formats."""
        for fmt in [ExportFormat.JSON, ExportFormat.GRAPHML, ExportFormat.DOT, ExportFormat.MARKDOWN]:
            result = export_knowledge_graph(sample_nodes, format=fmt)
            assert result.success, f"Failed for format {fmt}"
