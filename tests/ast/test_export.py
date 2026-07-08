#         assert ", "Condition must be true"
#         assert "test_project" in result.content, "Result must not be empty"
#         assert "Dependency Analysis" in result.content, "Result must not be empty"
#         assert "Metrics Summary" in result.content, "Result must not be empty"
# 
#         assert result.content is not None, "content must be initialized"
#         assert ", "Condition must be true"
#         assert "test_project" in result.content, "Result must not be empty"
#         assert "Dependency Analysis" in result.content, "Result must not be empty"
#         assert "Metrics Summary" in result.content, "Result must not be empty"
#     KnowledgeGraphExporter,
#     export_knowledge_graph,
# )
#         assert result.content is not None, "content must be initialized"
#         assert ", "Condition must be true"
#         assert "test_project" in result.content, "Result must not be empty"
#         assert "Dependency Analysis" in result.content, "Result must not be empty"
#         assert "Metrics Summary" in result.content, "Result must not be empty"
# @pytest.fixture
#         assert result.content is not None, "content must be initialized"
#         assert ", "Condition must be true"
#         assert "test_project" in result.content, "Result must not be empty"
#         assert "Dependency Analysis" in result.content, "Result must not be empty"
#         assert "Metrics Summary" in result.content, "Result must not be empty"
#     loc2 = SourceLocation(Path("module.py"), 5, 0, 20, 0)
#     func = StandardizedASTNode(
#     func = StandardizedASTNode(
#         "func1",
#         NodeType.FUNCTION,
#         "process_data",
#         loc2,
#         docstring="Process the data.",
#     )
#     loc3 = SourceLocation(Path("module.py"), 25, 0, 50, 0)
#     cls = StandardizedASTNode(
#     cls = StandardizedASTNode(
#         "cls1",
#         NodeType.CLASS,
#         "DataProcessor",
#         loc3,
#         docstring="Data processing class.",
#     )
#     root.add_child(func)
#     root.add_child(cls)
# 
#     return [root]
#         assert result.content is not None, "content must be initialized"
#         assert ", "Condition must be true"
#         assert "test_project" in result.content, "Result must not be empty"
#         assert "Dependency Analysis" in result.content, "Result must not be empty"
#         assert "Metrics Summary" in result.content, "Result must not be empty"
#     graph = DependencyGraph()
#     graph.add_edge("func1", "cls1")
#     graph.add_edge("cls1", "func2")
#     return graph
#         assert result.content is not None, "content must be initialized"
#         assert ", "Condition must be true"
#         assert "test_project" in result.content, "Result must not be empty"
#         assert "Dependency Analysis" in result.content, "Result must not be empty"
#         assert "Metrics Summary" in result.content, "Result must not be empty"
#     agg = MetricsAggregator()
#     agg.store_metrics("func1", CodeMetrics(5, 3.0, 50, 5, 85.0))
#     agg.store_metrics("cls1", CodeMetrics(10, 7.0, 100, 10, 75.0))
#     return agg
#         assert result.content is not None, "content must be initialized"
#         assert ", "Condition must be true"
#         assert "test_project" in result.content, "Result must not be empty"
#         assert "Dependency Analysis" in result.content, "Result must not be empty"
#         assert "Metrics Summary" in result.content, "Result must not be empty"
#     def test_export_json(self, sample_nodes):
#     def test_export_json(self, sample_nodes):
#         """Test JSON export."""
#         exporter = KnowledgeGraphExporter()
#         exporter.add_nodes(sample_nodes)
#         exporter.set_metadata("project", "test")
#         result = exporter.export(ExportFormat.JSON)
# 
#         assert result.success, "Result must not be empty"
#         assert result.content is not None, "content must be initialized"
# 
#         data = json.loads(result.content)
#         assert data["version"] == "1.0", "Data must not be empty"
#         assert data["metadata"]["project"] == "test", "Data must not be empty"
#         assert len(data["nodes"]) == 1, "Collection must not be empty"
# 
#     def test_export_json_with_graph(self, sample_nodes, sample_graph):
#     def test_export_json_with_graph(self, sample_nodes, sample_graph):
#         """Test JSON export with dependency graph."""
#         exporter = KnowledgeGraphExporter()
#         exporter.add_nodes(sample_nodes)
#         exporter.set_graph(sample_graph)
#         result = exporter.export(ExportFormat.JSON)
# 
#         assert result.success, "Result must not be empty"
#         data = json.loads(result.content)
#         assert data["graph"] is not None, "Value must be initialized"
#         assert len(data["graph"]["edges"]) == 2, "Collection must not be empty"
# 
#     def test_export_json_with_metrics(self, sample_nodes, sample_metrics):
#     def test_export_json_with_metrics(self, sample_nodes, sample_metrics):
#         """Test JSON export with metrics."""
#         exporter = KnowledgeGraphExporter()
#         exporter.add_nodes(sample_nodes)
#         exporter.set_metrics(sample_metrics)
#         result = exporter.export(ExportFormat.JSON)
# 
#         assert result.success, "Result must not be empty"
#         data = json.loads(result.content)
#         assert data["metrics"] is not None, "Value must be initialized"
#         assert "summary" in data["metrics"], "Data must not be empty"
# 
#     def test_export_json_to_file(self, sample_nodes, tmp_path):
#     def test_export_json_to_file(self, sample_nodes, tmp_path):
#         """Test JSON export to file."""
#         output_file = tmp_path / "export.json"
#         exporter = KnowledgeGraphExporter()
#         exporter.add_nodes(sample_nodes)
# 
#         result = exporter.export(ExportFormat.JSON, output_file)
# 
#         assert result.success, "Result must not be empty"
#         assert output_file.exists(), "Condition must be true"
#         assert result.content is None, "Result must not be empty"
# 
#         data = json.loads(output_file.read_text())
#         assert len(data["nodes"]) == 1, "Collection must not be empty"
# 
#     def test_export_graphml(self, sample_nodes, sample_graph):
#     def test_export_graphml(self, sample_nodes, sample_graph):
#         """Test GraphML export."""
#         exporter = KnowledgeGraphExporter()
#         exporter.add_nodes(sample_nodes)
#         exporter.set_graph(sample_graph)
#         result = exporter.export(ExportFormat.GRAPHML)
# 
#         assert result.success, "Result must not be empty"
#         assert result.content is not None, "content must be initialized"
#         assert '<?xml version="1.0"' in result.content, "Result must not be empty"
#         assert "<graphml" in result.content, "Result must not be empty"
#         assert 'id="mod1"' in result.content, "Result must not be empty"
# 
#     def test_export_graphml_escapes_special_chars(self, tmp_path):
#     def test_export_graphml_escapes_special_chars(self, tmp_path):
#         """Test GraphML properly escapes XML characters."""
#         loc = SourceLocation(Path("test<file>.py"), 1, 0, 10, 0)
#         node = StandardizedASTNode("n1", NodeType.MODULE, "test&module", loc)
#         exporter = KnowledgeGraphExporter()
#         exporter.add_node(node)
# 
#         result = exporter.export(ExportFormat.GRAPHML)
# 
#         assert result.success, "Result must not be empty"
#         assert "&lt;" in result.content, "Result must not be empty"
#         assert "&amp;" in result.content, "Result must not be empty"
# 
#     def test_export_dot(self, sample_nodes, sample_graph):
#     def test_export_dot(self, sample_nodes, sample_graph):
#         """Test DOT (Graphviz) export."""
#         exporter = KnowledgeGraphExporter()
#         exporter.add_nodes(sample_nodes)
#         exporter.set_graph(sample_graph)
#         result = exporter.export(ExportFormat.DOT)
# 
#         assert result.success, "Result must not be empty"
#         assert result.content is not None, "content must be initialized"
#         assert "digraph" in result.content, "Result must not be empty"
#         assert "mod1" in result.content, "Result must not be empty"
#         assert "->" in result.content, "Result must not be empty"
# 
#     def test_export_dot_highlights_cycles(self):
#     def test_export_dot_highlights_cycles(self):
#         """Test DOT export highlights cycles in red."""
#         loc = SourceLocation(Path("test.py"), 1, 0, 10, 0)
#         node = StandardizedASTNode("n1", NodeType.MODULE, "test", loc)
#         graph = DependencyGraph()
#         graph.add_edge("A", "B")
#         graph.add_edge("B", "A")  # Cycle
# 
#         exporter = KnowledgeGraphExporter()
#         exporter.add_node(node)
#         exporter.set_graph(graph)
# 
#         result = exporter.export(ExportFormat.DOT)
# 
#         assert result.success, "Result must not be empty"
#         assert "color=red" in result.content, "Result must not be empty"
# 
#     def test_export_sqlite(self, sample_nodes, sample_graph, sample_metrics, tmp_path):
#     def test_export_sqlite(self, sample_nodes, sample_graph, sample_metrics, tmp_path):
#         """Test SQLite export."""
#         db_path = tmp_path / "knowledge.db"
#         exporter = KnowledgeGraphExporter()
#         exporter.add_nodes(sample_nodes)
#         exporter.set_graph(sample_graph)
#         exporter.set_metrics(sample_metrics)
#         exporter.set_metadata("version", "1.0")
# 
#         result = exporter.export(ExportFormat.SQLITE, db_path)
# 
#         assert result.success, "Result must not be empty"
#         assert db_path.exists(), "Condition must be true"
#         # Verify database contents
#         conn = sqlite3.connect(db_path)
#         cursor = conn.cursor()
# 
#         # Check nodes table
#         cursor.execute("SELECT COUNT(*) FROM nodes")
#         node_count = cursor.fetchone()[0]
#         assert node_count >= 1, "node_count must be positive"
# 
#         # Check edges table
#         cursor.execute("SELECT COUNT(*) FROM edges")
#         edge_count = cursor.fetchone()[0]
#         assert edge_count == 2, "Count must be greater than zero"
# 
#         # Check metrics table
#         cursor.execute("SELECT COUNT(*) FROM metrics")
#         metrics_count = cursor.fetchone()[0]
#         assert metrics_count == 2, "Count must be greater than zero"
# 
#         # Check metadata table
#         cursor.execute("SELECT value FROM metadata WHERE key = 'version'")
#         version = cursor.fetchone()[0]
#         assert json.loads(version) == "1.0", "Condition must be true"
#         assert json.loads(version) == "1.0", "Condition must be true"
# 
#         conn.close()
# 
#     def test_export_sqlite_requires_path(self, sample_nodes):
#     def test_export_sqlite_requires_path(self, sample_nodes):
#         """Test SQLite export requires output path."""
#         exporter = KnowledgeGraphExporter()
#         exporter.add_nodes(sample_nodes)
#         result = exporter.export(ExportFormat.SQLITE)
# 
#         assert not result.success, "Result must not be empty"
#         assert "requires output_path" in result.error, "Result must not be empty"
# 
#     def test_export_sqlite_indexes(self, sample_nodes, tmp_path):
#     def test_export_sqlite_indexes(self, sample_nodes, tmp_path):
#         """Test SQLite export creates indexes."""
#         db_path = tmp_path / "indexed.db"
#         exporter = KnowledgeGraphExporter()
#         exporter.add_nodes(sample_nodes)
# 
#         result = exporter.export(ExportFormat.SQLITE, db_path)
# 
#         assert result.success, "Result must not be empty"
# 
#         conn = sqlite3.connect(db_path)
#         cursor = conn.cursor()
#         # Check indexes exist
#         cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
#         indexes = [row[0] for row in cursor.fetchall()]
#         indexes = [row[0] for row in cursor.fetchall()]
# 
#         assert "idx_nodes_type" in indexes, "Condition must be true"
#         assert "idx_nodes_file" in indexes, "Condition must be true"
# 
#         conn.close()
# 
#     def test_export_markdown(self, sample_nodes, sample_graph, sample_metrics):
#     def test_export_markdown(self, sample_nodes, sample_graph, sample_metrics):
#         """Test Markdown export."""
#         exporter = KnowledgeGraphExporter()
#         exporter.add_nodes(sample_nodes)
#         exporter.set_graph(sample_graph)
#         exporter.set_metrics(sample_metrics)
#         exporter.set_metadata("project", "test_project")
#         result = exporter.export(ExportFormat.MARKDOWN)
# 
#         assert result.success, "Result must not be empty"
#         assert result.content is not None, "content must be initialized"
#         assert ", "Condition must be true"
#         assert "test_project" in result.content, "Result must not be empty"
#         assert "Dependency Analysis" in result.content, "Result must not be empty"
#         assert "Metrics Summary" in result.content, "Result must not be empty"
# 
#     def test_export_markdown_shows_cycles(self):
#     def test_export_markdown_shows_cycles(self):
#         """Test Markdown export shows detected cycles."""
#         loc = SourceLocation(Path("test.py"), 1, 0, 10, 0)
#         node = StandardizedASTNode("n1", NodeType.MODULE, "test", loc)
#         graph = DependencyGraph()
#         graph.add_edge("A", "B")
#         graph.add_edge("B", "C")
#         graph.add_edge("C", "A")
# 
#         exporter = KnowledgeGraphExporter()
#         exporter.add_node(node)
#         exporter.set_graph(graph)
# 
#         result = exporter.export(ExportFormat.MARKDOWN)
# 
#         assert result.success, "Result must not be empty"
#         assert "Circular Dependencies" in result.content, "Result must not be empty"
#         assert "→" in result.content, "Result must not be empty"
# 
#     def test_add_nodes_batch(self, sample_nodes):
#     def test_add_nodes_batch(self, sample_nodes):
#         """Test adding multiple nodes at once."""
#         exporter = KnowledgeGraphExporter()
#         exporter.add_nodes(sample_nodes)
#         result = exporter.export(ExportFormat.JSON)
# 
#         assert result.success, "Result must not be empty"
#         data = json.loads(result.content)
#         assert len(data["nodes"]) == len(sample_nodes), "Sample_nodes must not be empty"
# 
#     def test_export_result_to_dict(self):
#     def test_export_result_to_dict(self):
#         """Test ExportResult serialization."""
#         result = ExportResult(
#             format=ExportFormat.JSON,
#             output_path=Path("test.json"),
#             content=None,
#             success=True,
#         )
#         data = result.to_dict()
# 
#         assert data["format"] == "json", "Data must not be empty"
#         assert data["output_path"] == "test.json", "Data must not be empty"
#         assert data["success"] is True, "Data must not be empty"


class TestExportKnowledgeGraphFunction:
    """Tests for export_knowledge_graph convenience function."""

    def test_export_basic(self, sample_nodes):
        """Test basic export."""
        result = export_knowledge_graph(sample_nodes)

        assert result.success, "Result must not be empty"
        assert result.format == ExportFormat.JSON, "Result must not be empty"

    def test_export_with_graph_and_metrics(self, sample_nodes, sample_graph, sample_metrics):
        """Test export with all components."""
        result = export_knowledge_graph(
            sample_nodes,
            format=ExportFormat.JSON,
            graph=sample_graph,
            metrics=sample_metrics,
        )

        assert result.success, "Result must not be empty"
        data = json.loads(result.content)
        assert data["graph"] is not None, "Value must be initialized"
        assert data["metrics"] is not None, "Value must be initialized"

    def test_export_to_file(self, sample_nodes, tmp_path):
        """Test export to file."""
        output_file = tmp_path / "export.json"

        result = export_knowledge_graph(
            sample_nodes,
            format=ExportFormat.JSON,
            output_path=output_file,
        )

        assert result.success, "Result must not be empty"
        assert output_file.exists(), "Condition must be true"

    def test_export_different_formats(self, sample_nodes):
        """Test exporting to different formats."""
        for fmt in [
            ExportFormat.JSON,
            ExportFormat.GRAPHML,
            ExportFormat.DOT,
            ExportFormat.MARKDOWN,
        ]:
            result = export_knowledge_graph(sample_nodes, format=fmt)
            assert result.success, f"Failed for format {fmt}"
