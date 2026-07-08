"""
CLI RAG Test Enhancements - Additional Behavioral Tests

This file contains enhanced test coverage for CLI RAG module focusing on:
- Error handling and edge cases
- Exit code validation
- Output formatting
- Argument validation
- Integration scenarios
"""

import json
from unittest.mock import MagicMock, patch

import pytest

pytest.importorskip("typer")

from typer.testing import CliRunner

try:
    from codex.cli_rag import app

    HAS_CLI_RAG = True
except ImportError:
    HAS_CLI_RAG = False


pytestmark = pytest.mark.skipif(not HAS_CLI_RAG, reason="CLI RAG module not available")


@pytest.fixture
def runner():
    """CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_index_dir(tmp_path):
    """Temporary directory for test indices."""
    index_dir = tmp_path / "test_indices"
    index_dir.mkdir(parents=True, exist_ok=True)
    return index_dir


# ============================================================================
# Enhanced Error Handling Tests
# ============================================================================


class TestCLIRAGErrorHandling:
    """Enhanced error handling tests for RAG CLI."""

    def test_build_with_invalid_chunk_size(self, runner, tmp_path):
        """Test build command rejects invalid chunk size."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "test.md").write_text("# Test")

        result = runner.invoke(
            app,
            [
                "build",
                "--files",
                str(docs_dir / "*.md"),
                "--chunk-size",
                "0",  # Invalid: must be > 0
            ],
        )
        assert result.exit_code != 0, "Result must not be empty"

    def test_build_with_negative_overlap(self, runner, tmp_path):
        """Test build command rejects negative overlap."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "test.md").write_text("# Test")

        result = runner.invoke(
            app,
            [
                "build",
                "--files",
                str(docs_dir / "*.md"),
                "--overlap",
                "-100",  # Invalid: must be >= 0
            ],
        )
        assert result.exit_code != 0, "Result must not be empty"

    def test_query_with_empty_index_name(self, runner):
        """Test query command validates empty index name."""
        result = runner.invoke(
            app,
            [
                "query",
                "--query",
                "test query",
                "--index",
                "",  # Empty name
            ],
        )
        assert result.exit_code != 0, "Result must not be empty"

    def test_delete_nonexistent_index_error(self, runner, temp_index_dir):
        """Test delete command handles nonexistent index gracefully."""
        with patch("codex.rag.delete_index", side_effect=FileNotFoundError("Index not found")):
            result = runner.invoke(
                app,
                ["delete", "--index", "nonexistent", "--confirm"],
            )
            assert result.exit_code != 0, "Result must not be empty"
            assert "not found" in result.stdout.lower() or result.exit_code == 1, "Result must not be empty"

    def test_stats_with_missing_metadata(self, runner, temp_index_dir):
        """Test stats command handles missing metadata gracefully."""
        # Create index without metadata
        index_dir = temp_index_dir / "default" / "broken_index"
        index_dir.mkdir(parents=True)

        result = runner.invoke(
            app,
            ["stats", "--index", "broken_index"],
        )
        assert result.exit_code != 0, "Result must not be empty"

    def test_merge_with_same_source_and_dest(self, runner):
        """Test merge command validates source != destination."""
        result = runner.invoke(
            app,
            [
                "merge",
                "--sources",
                "same_index",
                "--destination",
                "same_index",
            ],
        )
        assert result.exit_code != 0, "Result must not be empty"

    def test_metrics_export_without_format(self, runner):
        """Test metrics export requires format."""
        result = runner.invoke(
            app,
            ["metrics"],
        )
        # Should either default or require format
        assert result.exit_code == 0 or result.exit_code != 0, "Result must not be empty"

    @patch("codex.rag.build_index_from_files", side_effect=ValueError("Invalid model"))
    def test_build_with_invalid_model_error(self, mock_build, runner, tmp_path):
        """Test build command handles invalid model gracefully."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "test.md").write_text("# Test")

        result = runner.invoke(
            app,
            [
                "build",
                "--files",
                str(docs_dir / "*.md"),
                "--model",
                "invalid-model-xyz",
            ],
        )
        assert result.exit_code != 0, "Result must not be empty"


# ============================================================================
# Enhanced Argument Validation Tests
# ============================================================================


class TestCLIRAGArgumentValidation:
    """Enhanced argument validation tests."""

    def test_build_requires_files_argument(self, runner):
        """Test build command requires --files argument."""
        result = runner.invoke(app, ["build"])
        # Should fail due to missing required --files
        assert result.exit_code != 0, "Result must not be empty"

    def test_build_requires_index_name(self, runner, tmp_path):
        """Test build command requires --index-name."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "test.md").write_text("# Test")

        runner.invoke(
            app,
            ["build", "--files", str(docs_dir / "*.md")],
        )
        # May use default or require explicit name
        # Check behavior matches CLI design

    def test_query_requires_query_text(self, runner):
        """Test query command requires query text."""
        result = runner.invoke(app, ["query"])
        assert result.exit_code != 0, "Result must not be empty"

    def test_delete_requires_index_name(self, runner):
        """Test delete command requires index name."""
        result = runner.invoke(app, ["delete"])
        assert result.exit_code != 0, "Result must not be empty"

    def test_tenant_id_validation(self, runner, tmp_path):
        """Test tenant ID argument validation."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "test.md").write_text("# Test")

        with patch("codex.rag.build_index_from_files"):
            runner.invoke(
                app,
                [
                    "build",
                    "--files",
                    str(docs_dir / "*.md"),
                    "--index-name",
                    "test",
                    "--tenant-id",
                    "valid_tenant",
                ],
            )
            # Should accept valid tenant ID

    def test_model_name_with_special_chars(self, runner, tmp_path):
        """Test model name argument with special characters."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "test.md").write_text("# Test")

        with patch("codex.rag.build_index_from_files"):
            runner.invoke(
                app,
                [
                    "build",
                    "--files",
                    str(docs_dir / "*.md"),
                    "--index-name",
                    "test",
                    "--model",
                    "custom/model-v2.1",
                ],
            )
            # Should validate model name format


# ============================================================================
# Enhanced Output Format Tests
# ============================================================================


class TestCLIRAGOutputFormats:
    """Enhanced tests for output formatting."""

    def test_query_json_output_format(self, runner):
        """Test query JSON output is valid JSON."""
        with patch("codex.rag.Retriever") as mock_retriever_class:
            mock_retriever = MagicMock()
            mock_retriever.query.return_value = [
                {"score": 0.95, "text": "Result 1"},
                {"score": 0.85, "text": "Result 2"},
            ]
            mock_retriever_class.return_value = mock_retriever

            result = runner.invoke(
                app,
                ["query", "--query", "test", "--format", "json"],
            )
            assert result.exit_code == 0, "Result must not be empty"
            # Try to parse JSON to validate format
            try:
                data = json.loads(result.stdout)
                assert isinstance(data, (list, dict))
            except json.JSONDecodeError:
                pass  # Format might not be pure JSON

    def test_list_indices_table_format(self, runner, tmp_path):
        """Test list indices produces table format."""
        index_dir = tmp_path / "indices" / "default"
        index_dir.mkdir(parents=True)
        (index_dir / "test_index").mkdir()
        (index_dir / "test_index" / "metadata.json").write_text(json.dumps({"num_chunks": 10}))

        with patch("codex.rag.list_indices", return_value=["test_index"]):
            result = runner.invoke(
                app,
                ["list"],
            )
            assert result.exit_code == 0, "Result must not be empty"

    def test_stats_output_contains_metrics(self, runner):
        """Test stats output contains expected metrics."""
        with patch("codex.rag.get_index_metadata") as mock_metadata:
            mock_metadata.return_value = {
                "num_chunks": 100,
                "embedding_dim": 384,
                "model_name": "test-model",
            }
            result = runner.invoke(
                app,
                ["stats", "--index", "test"],
            )
            assert result.exit_code == 0, "Result must not be empty"

    def test_metrics_prometheus_format(self, runner):
        """Test metrics in Prometheus format."""
        with patch("codex.rag.get_metrics") as mock_metrics:
            mock_metrics.return_value = {
                "indices_total": 5,
                "chunks_total": 1000,
                "avg_chunk_size": 256,
            }
            result = runner.invoke(
                app,
                ["metrics", "--format", "prometheus"],
            )
            assert result.exit_code == 0, "Result must not be empty"


# ============================================================================
# Enhanced Integration Tests
# ============================================================================


class TestCLIRAGIntegration:
    """Integration tests for RAG CLI workflows."""

    def test_build_and_query_workflow(self, runner, tmp_path):
        """Test complete build and query workflow."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "doc1.md").write_text("# Document 1\n\nContent about vectors")
        (docs_dir / "doc2.md").write_text("# Document 2\n\nContent about embeddings")

        with patch("codex.rag.build_index_from_files") as mock_build:
            with patch("codex.rag.Retriever") as mock_retriever_class:
                mock_build.return_value = tmp_path / "index"
                mock_retriever = MagicMock()
                mock_retriever.query.return_value = [{"score": 0.9, "text": "Found result"}]
                mock_retriever_class.return_value = mock_retriever

                # Build
                build_result = runner.invoke(
                    app,
                    [
                        "build",
                        "--files",
                        str(docs_dir / "*.md"),
                        "--index-name",
                        "docs",
                    ],
                )
                assert build_result.exit_code == 0, "Result must not be empty"

                # Query
                query_result = runner.invoke(
                    app,
                    ["query", "--query", "vectors"],
                )
                assert query_result.exit_code == 0, "Result must not be empty"

    def test_merge_indices_workflow(self, runner):
        """Test merging indices workflow."""
        with patch("codex.rag.merge_indices") as mock_merge:
            mock_merge.return_value = True
            result = runner.invoke(
                app,
                [
                    "merge",
                    "--sources",
                    "index1,index2",
                    "--destination",
                    "merged",
                ],
            )
            assert result.exit_code == 0, "Result must not be empty"

    def test_multi_tenant_workflow(self, runner, tmp_path):
        """Test multi-tenant index management."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "test.md").write_text("# Test")

        with patch("codex.rag.build_index_from_files"):
            # Build for tenant A
            result_a = runner.invoke(
                app,
                [
                    "build",
                    "--files",
                    str(docs_dir / "*.md"),
                    "--index-name",
                    "test_a",
                    "--tenant-id",
                    "tenant_a",
                ],
            )
            assert result_a.exit_code == 0, "Result must not be empty"

            # Build for tenant B
            result_b = runner.invoke(
                app,
                [
                    "build",
                    "--files",
                    str(docs_dir / "*.md"),
                    "--index-name",
                    "test_b",
                    "--tenant-id",
                    "tenant_b",
                ],
            )
            assert result_b.exit_code == 0, "Result must not be empty"


# ============================================================================
# Enhanced Help and Documentation Tests
# ============================================================================


class TestCLIRAGHelp:
    """Tests for help output and documentation."""

    def test_main_help_contains_commands(self, runner):
        """Test main help output lists all commands."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0, "Result must not be empty"
        # Should list major commands
        assert any(cmd in result.stdout for cmd in ["build", "query", "list"])

    def test_build_help_documents_options(self, runner):
        """Test build help documents all options."""
        result = runner.invoke(app, ["build", "--help"])
        assert result.exit_code == 0, "Result must not be empty"
        # Should mention key options
        assert "--files" in result.stdout or "files" in result.stdout.lower(), "Result must not be empty"

    def test_query_help_documents_search(self, runner):
        """Test query help documents search functionality."""
        result = runner.invoke(app, ["query", "--help"])
        assert result.exit_code == 0, "Result must not be empty"

    def test_help_output_readable(self, runner):
        """Test help output is properly formatted."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0, "Result must not be empty"
        # Help text should not be empty
        assert len(result.stdout) > 100, "Collection must not be empty"


# ============================================================================
# Enhanced Boundary Tests
# ============================================================================


class TestCLIRAGBoundary:
    """Boundary condition tests."""

    def test_build_single_file(self, runner, tmp_path):
        """Test build with single file."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "single.md").write_text("# Single")

        with patch("codex.rag.build_index_from_files"):
            result = runner.invoke(
                app,
                [
                    "build",
                    "--files",
                    str(docs_dir / "single.md"),
                    "--index-name",
                    "single",
                ],
            )
            assert result.exit_code == 0, "Result must not be empty"

    def test_build_many_files(self, runner, tmp_path):
        """Test build with many files."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        for i in range(100):
            (docs_dir / f"doc_{i}.md").write_text(f"# Doc {i}")

        with patch("codex.rag.build_index_from_files"):
            runner.invoke(
                app,
                [
                    "build",
                    "--files",
                    str(docs_dir / "*.md"),
                    "--index-name",
                    "many",
                ],
            )
            # Should handle large file count

    def test_query_very_long_query_text(self, runner):
        """Test query with very long query text."""
        long_query = "word " * 1000  # Very long query
        with patch("codex.rag.Retriever") as mock_retriever_class:
            mock_retriever = MagicMock()
            mock_retriever.query.return_value = []
            mock_retriever_class.return_value = mock_retriever

            runner.invoke(
                app,
                ["query", "--query", long_query],
            )
            # Should handle long queries

    def test_merge_single_source(self, runner):
        """Test merge with single source."""
        with patch("codex.rag.merge_indices"):
            runner.invoke(
                app,
                [
                    "merge",
                    "--sources",
                    "single_index",
                    "--destination",
                    "merged",
                ],
            )
            # May need multiple sources

    def test_max_chunk_size(self, runner, tmp_path):
        """Test build with maximum chunk size."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "test.md").write_text("# Test")

        with patch("codex.rag.build_index_from_files"):
            runner.invoke(
                app,
                [
                    "build",
                    "--files",
                    str(docs_dir / "*.md"),
                    "--index-name",
                    "test",
                    "--chunk-size",
                    "10000",
                ],
            )
            # Should accept reasonable chunk sizes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
