"""
Benchmarks for AST export operations.
"""
import tempfile
from pathlib import Path

from codex.ast import ExportFormat, export_knowledge_graph, parse_python

TEST_CODE = """
class Example:
    def method1(self):
        pass

    def method2(self):
        pass
"""


class TestExportBenchmarks:
    """Benchmark AST export operations."""

    def test_export_json(self, benchmark):
        """Benchmark JSON export."""
        node = parse_python(TEST_CODE, "test.py")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output.json"

            result = benchmark(
                export_knowledge_graph,
                [node],
                ExportFormat.JSON,
                str(output_path)
            )
            assert result.success

    def test_export_multiple_nodes(self, benchmark):
        """Benchmark exporting multiple nodes."""
        nodes = [
            parse_python(TEST_CODE, f"file_{i}.py")
            for i in range(5)
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output.json"

            result = benchmark(
                export_knowledge_graph,
                nodes,
                ExportFormat.JSON,
                str(output_path)
            )
            assert result.success
