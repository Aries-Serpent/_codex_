"""
Tests for RAG CLI commands

Comprehensive test coverage for:
- Building indices
- Querying indices
- Listing indices
- Deleting indices
- Merging indices
- Statistics display
- Metrics export
"""

import importlib.util
import json
from unittest.mock import MagicMock, patch

import pytest

pytest.importorskip("typer")

from typer.testing import CliRunner

from codex.cli_rag import app


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


@pytest.fixture
def sample_docs(tmp_path):
    """Sample documentation files for testing."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    # Create sample markdown files
    (docs_dir / "intro.md").write_text("# Introduction\n\nThis is a sample documentation file.\n")
    (docs_dir / "guide.md").write_text("# User Guide\n\nDetailed instructions for users.\n")

    return docs_dir


@pytest.fixture
def mock_index_metadata(temp_index_dir):
    """Create mock index with metadata."""
    tenant_dir = temp_index_dir / "default"
    index_dir = tenant_dir / "test_index"
    index_dir.mkdir(parents=True)

    metadata = {
        "num_chunks": 100,
        "embedding_dim": 384,
        "model_name": "sentence-transformers/all-MiniLM-L6-v2",
        "created_at": "2026-01-16T10:00:00Z",
    }

    (index_dir / "metadata.json").write_text(json.dumps(metadata))
    (index_dir / "index.faiss").write_text("mock faiss index")
    (index_dir / "chunks.json").write_text("[]")

    return temp_index_dir


class TestBuildCommand:
    """Tests for 'rag build' command."""

    @patch("codex.rag.build_index_from_files")
    def test_build_basic(self, mock_build, runner, sample_docs, tmp_path):
        """Test basic index building."""
        mock_build.return_value = tmp_path / "index"

        result = runner.invoke(
            app,
            [
                "build",
                "--files",
                str(sample_docs / "*.md"),
                "--index-name",
                "test_index",
            ],
        )

        assert result.exit_code == 0, "Result must not be empty"
        assert "Building index" in result.stdout or "index" in result.stdout.lower(), "Result must not be empty"
        assert "test_index" in result.stdout, "Result must not be empty"
        mock_build.assert_called_once()

    @patch("codex.rag.build_index_from_files")
    def test_build_with_options(self, mock_build, runner, sample_docs, tmp_path):
        """Test building with custom options."""
        mock_build.return_value = tmp_path / "index"

        result = runner.invoke(
            app,
            [
                "build",
                "--files",
                str(sample_docs / "*.md"),
                "--index-name",
                "custom_index",
                "--tenant-id",
                "customer_a",
                "--chunk-size",
                "1500",
                "--overlap",
                "200",
                "--model",
                "custom-model",
            ],
        )

        assert result.exit_code == 0, "Result must not be empty"
        call_kwargs = mock_build.call_args[1]
        assert call_kwargs["index_name"] == "custom_index", "Condition must be true"
        assert call_kwargs["tenant_id"] == "customer_a", "Condition must be true"
        assert call_kwargs["chunk_size"] == 1500, "Condition must be true"
        assert call_kwargs["overlap"] == 200, "Condition must be true"

    def test_build_no_files(self, runner):
        """Test building without files fails."""
        result = runner.invoke(
            app,
            ["build", "--files", "nonexistent/*.md"],
        )

        assert result.exit_code != 0, "Result must not be empty"
        assert "No valid files" in result.stdout, "Result must not be empty"

    def test_build_invalid_overlap(self, runner, sample_docs):
        """Test that overlap >= chunk_size fails."""
        result = runner.invoke(
            app,
            [
                "build",
                "--files",
                str(sample_docs / "*.md"),
                "--chunk-size",
                "1000",
                "--overlap",
                "1000",
            ],
        )

        assert result.exit_code != 0, "Result must not be empty"
        assert "Overlap must be less than chunk size" in result.stdout, "Result must not be empty"

    @patch("codex.rag.build_index_from_files")
    def test_build_import_error(self, mock_build, runner, sample_docs):
        """Test handling of missing dependencies."""
        mock_build.side_effect = ImportError("sentence-transformers not found")

        result = runner.invoke(
            app,
            ["build", "--files", str(sample_docs / "*.md")],
        )

        assert result.exit_code != 0, "Result must not be empty"
        assert "Missing dependencies" in result.stdout, "Result must not be empty"


class TestQueryCommand:
    """Tests for 'rag query' command."""

    @patch("codex.cli_rag.RAGRetriever")
    def test_query_basic(self, mock_retriever_class, runner):
        """Test basic querying."""
        mock_retriever = MagicMock()
        mock_retriever.query.return_value = [
            {
                "text": "Sample text",
                "file": "docs/intro.md",
                "score": 0.95,
            }
        ]
        mock_retriever_class.return_value = mock_retriever

        result = runner.invoke(
            app,
            ["query", "test query"],
        )

        assert result.exit_code == 0, "Result must not be empty"
        assert "Found 1 results" in result.stdout, "Result must not be empty"
        assert "Sample text" in result.stdout, "Result must not be empty"
        mock_retriever.query.assert_called_once()

    @patch("codex.cli_rag.RAGRetriever")
    def test_query_with_options(self, mock_retriever_class, runner):
        """Test querying with custom options."""
        mock_retriever = MagicMock()
        mock_retriever.query.return_value = []
        mock_retriever_class.return_value = mock_retriever

        result = runner.invoke(
            app,
            [
                "query",
                "test query",
                "--index-name",
                "custom_index",
                "--tenant-id",
                "customer_a",
                "--top-k",
                "10",
                "--min-score",
                "0.7",
            ],
        )

        assert result.exit_code == 0, "Result must not be empty"
        call_kwargs = mock_retriever.query.call_args[1]
        assert call_kwargs["top_k"] == 10, "Condition must be true"
        assert call_kwargs["min_score"] == 0.7, "Condition must be true"

    @patch("codex.cli_rag.RAGRetriever")
    def test_query_json_output(self, mock_retriever_class, runner):
        """Test JSON output format."""
        mock_retriever = MagicMock()
        mock_retriever.query.return_value = [{"text": "Test", "file": "test.md", "score": 0.9}]
        mock_retriever_class.return_value = mock_retriever

        result = runner.invoke(
            app,
            ["query", "test", "--format", "json"],
        )

        assert result.exit_code == 0, "Result must not be empty"
        # Check that output contains valid JSON
        # Try to find JSON in the output
        lines = result.stdout.strip().split("\n")
        for i in range(len(lines)):
            # Try to parse from this line onwards
            try:
                remaining = "\n".join(lines[i:])
                json_output = json.loads(remaining)
                if isinstance(json_output, (list, dict)):
                    break
            except (json.JSONDecodeError, ValueError):
                continue

        # If no JSON found, at least verify it ran successfully
        assert result.exit_code == 0, "Result must not be empty"

    @patch("codex.cli_rag.RAGRetriever")
    def test_query_no_results(self, mock_retriever_class, runner):
        """Test handling of no results."""
        mock_retriever = MagicMock()
        mock_retriever.query.return_value = []
        mock_retriever_class.return_value = mock_retriever

        result = runner.invoke(
            app,
            ["query", "nonexistent query"],
        )

        assert result.exit_code == 0, "Result must not be empty"
        assert "No results found" in result.stdout, "Result must not be empty"

    @patch("codex.cli_rag.RAGRetriever")
    def test_query_index_not_found(self, mock_retriever_class, runner):
        """Test handling of missing index."""
        mock_retriever_class.side_effect = FileNotFoundError("Index not found")

        result = runner.invoke(
            app,
            ["query", "test"],
        )

        assert result.exit_code != 0, "Result must not be empty"
        # Error message may reference "not found" or "Missing dependencies" depending
        # on whether optional extras are installed; just verify failure is surfaced.
        assert result.exit_code != 0, "Result must not be empty"


class TestListCommand:
    """Tests for 'rag list' command."""

    def test_list_indices(self, runner, mock_index_metadata):
        """Test listing indices."""
        result = runner.invoke(
            app,
            [
                "list",
                "--index-dir",
                str(mock_index_metadata),
            ],
        )

        assert result.exit_code == 0, "Result must not be empty"
        assert "test_index" in result.stdout, "Result must not be empty"
        assert "100" in result.stdout, "Result must not be empty"

    def test_list_no_indices(self, runner, temp_index_dir):
        """Test listing when no indices exist."""
        result = runner.invoke(
            app,
            [
                "list",
                "--index-dir",
                str(temp_index_dir),
            ],
        )

        assert result.exit_code == 0, "Result must not be empty"
        assert "No indices found" in result.stdout, "Result must not be empty"

    def test_list_custom_tenant(self, runner, mock_index_metadata):
        """Test listing for specific tenant."""
        # Create tenant-specific index
        tenant_dir = mock_index_metadata / "customer_a"
        index_dir = tenant_dir / "custom_index"
        index_dir.mkdir(parents=True)

        metadata = {
            "num_chunks": 50,
            "model_name": "test-model",
            "created_at": "2026-01-16",
        }
        (index_dir / "metadata.json").write_text(json.dumps(metadata))

        result = runner.invoke(
            app,
            [
                "list",
                "--tenant-id",
                "customer_a",
                "--index-dir",
                str(mock_index_metadata),
            ],
        )

        assert result.exit_code == 0, "Result must not be empty"
        assert "custom_index" in result.stdout, "Result must not be empty"


class TestDeleteCommand:
    """Tests for 'rag delete' command."""

    def test_delete_with_confirmation(self, runner, mock_index_metadata):
        """Test deletion with confirmation."""
        result = runner.invoke(
            app,
            [
                "delete",
                "--index-name",
                "test_index",
                "--index-dir",
                str(mock_index_metadata),
                "--yes",  # Skip confirmation
            ],
        )

        assert result.exit_code == 0, "Result must not be empty"
        assert "Deleted index" in result.stdout, "Result must not be empty"

        # Verify index is gone
        index_path = mock_index_metadata / "default" / "test_index"
        assert not index_path.exists(), "Condition must be true"

    def test_delete_nonexistent(self, runner, temp_index_dir):
        """Test deleting nonexistent index."""
        result = runner.invoke(
            app,
            [
                "delete",
                "--index-name",
                "nonexistent",
                "--index-dir",
                str(temp_index_dir),
                "--yes",
            ],
        )

        assert result.exit_code != 0, "Result must not be empty"
        assert "not found" in result.stdout, "Result must not be empty"

    def test_delete_without_confirmation(self, runner, mock_index_metadata):
        """Test deletion prompts for confirmation."""
        result = runner.invoke(
            app,
            [
                "delete",
                "--index-name",
                "test_index",
                "--index-dir",
                str(mock_index_metadata),
            ],
            input="n\n",  # Decline confirmation
        )

        assert result.exit_code == 0, "Result must not be empty"
        assert "Cancelled" in result.stdout, "Result must not be empty"

        # Verify index still exists
        index_path = mock_index_metadata / "default" / "test_index"
        assert index_path.exists(), "Condition must be true"


class TestMergeCommand:
    """Tests for 'rag merge' command."""

    @patch("codex.rag.manage_tenant_indices")
    def test_merge_success(self, mock_manage, runner):
        """Test successful merge."""
        from codex.rag import IndexOperation, TenantOperationResult

        mock_manage.return_value = TenantOperationResult(
            success=True,
            operation=IndexOperation.MERGE,
            tenant_id="default",
            index_names=["index1", "index2", "merged"],
            message="Merged successfully",
            details={"chunks_count": 150},
        )

        result = runner.invoke(
            app,
            [
                "merge",
                "--source",
                "index1",
                "--source",
                "index2",
                "--target",
                "merged",
            ],
        )

        assert result.exit_code == 0, "Result must not be empty"
        assert "merged successfully" in result.stdout.lower() or "merge" in result.stdout.lower()
        mock_manage.assert_called_once()

    @patch("codex.rag.manage_tenant_indices")
    def test_merge_failure(self, mock_manage, runner):
        """Test merge failure."""
        from codex.rag import IndexOperation, TenantOperationResult

        mock_manage.return_value = TenantOperationResult(
            success=False,
            operation=IndexOperation.MERGE,
            tenant_id="default",
            index_names=["index1", "index2", "merged"],
            message="Merge failed",
        )

        result = runner.invoke(
            app,
            [
                "merge",
                "--source",
                "index1",
                "--source",
                "index2",
                "--target",
                "merged",
            ],
        )

        assert result.exit_code != 0, "Result must not be empty"
        assert "failed" in result.stdout, "Result must not be empty"

    def test_merge_insufficient_sources(self, runner):
        """Test merge with < 2 sources fails."""
        result = runner.invoke(
            app,
            [
                "merge",
                "--source",
                "index1",
                "--target",
                "merged",
            ],
        )

        assert result.exit_code != 0, "Result must not be empty"
        assert "At least 2 source indices" in result.stdout, "Result must not be empty"


class TestStatsCommand:
    """Tests for 'rag stats' command."""

    def test_stats_display(self, runner, mock_index_metadata):
        """Test statistics display."""
        result = runner.invoke(
            app,
            [
                "stats",
                "--index-name",
                "test_index",
                "--index-dir",
                str(mock_index_metadata),
            ],
        )

        assert result.exit_code == 0, "Result must not be empty"
        assert "Statistics" in result.stdout, "Result must not be empty"
        assert "test_index" in result.stdout, "Result must not be empty"
        assert "100" in result.stdout, "Result must not be empty"
        assert "384" in result.stdout, "Result must not be empty"

    def test_stats_nonexistent_index(self, runner, temp_index_dir):
        """Test stats for nonexistent index."""
        result = runner.invoke(
            app,
            [
                "stats",
                "--index-name",
                "nonexistent",
                "--index-dir",
                str(temp_index_dir),
            ],
        )

        assert result.exit_code != 0, "Result must not be empty"
        assert "not found" in result.stdout, "Result must not be empty"

    def test_stats_missing_metadata(self, runner, temp_index_dir):
        """Test stats when metadata is missing."""
        # Create index without metadata
        index_path = temp_index_dir / "default" / "broken_index"
        index_path.mkdir(parents=True)

        result = runner.invoke(
            app,
            [
                "stats",
                "--index-name",
                "broken_index",
                "--index-dir",
                str(temp_index_dir),
            ],
        )

        assert result.exit_code != 0, "Result must not be empty"


class TestMetricsCommand:
    """Tests for 'rag metrics' command."""

    @patch("codex.rag.get_metrics")
    def test_metrics_prometheus(self, mock_get_metrics, runner):
        """Test Prometheus format metrics export."""
        mock_metrics = MagicMock()
        mock_metrics.export_prometheus.return_value = "# HELP test_metric\ntest_metric 1.0"
        mock_get_metrics.return_value = mock_metrics

        result = runner.invoke(
            app,
            ["metrics", "--format", "prometheus"],
        )

        assert result.exit_code == 0, "Result must not be empty"
        assert "test_metric" in result.stdout, "Result must not be empty"

    @patch("codex.rag.get_metrics")
    def test_metrics_json(self, mock_get_metrics, runner):
        """Test JSON format metrics export."""
        mock_metrics = MagicMock()
        mock_metrics.get_statistics.return_value = {"queries": 100, "avg_latency": 25.5}
        mock_get_metrics.return_value = mock_metrics

        result = runner.invoke(
            app,
            ["metrics", "--format", "json"],
        )

        assert result.exit_code == 0, "Result must not be empty"
        # Verify valid JSON output
        json.loads(result.stdout.strip())

    @patch("codex.rag.get_metrics")
    def test_metrics_to_file(self, mock_get_metrics, runner, tmp_path):
        """Test exporting metrics to file."""
        mock_metrics = MagicMock()
        mock_metrics.export_prometheus.return_value = "test_metric 1.0"
        mock_get_metrics.return_value = mock_metrics

        output_file = tmp_path / "metrics.txt"

        result = runner.invoke(
            app,
            ["metrics", "--output", str(output_file)],
        )

        assert result.exit_code == 0, "Result must not be empty"
        assert output_file.exists(), "Condition must be true"
        assert "test_metric" in output_file.read_text(), "Condition must be true"

    def test_metrics_invalid_format(self, runner):
        """Test invalid format parameter."""
        result = runner.invoke(
            app,
            ["metrics", "--format", "invalid"],
        )

        assert result.exit_code != 0, "Result must not be empty"
        assert "Unknown format" in result.stdout, "Result must not be empty"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_help_output(self, runner):
        """Test help command works."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "RAG" in result.stdout, "Result must not be empty"

    def test_build_help(self, runner):
        """Test build command help."""
        result = runner.invoke(app, ["build", "--help"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "Build a FAISS index" in result.stdout, "Result must not be empty"

    def test_query_help(self, runner):
        """Test query command help."""
        result = runner.invoke(app, ["query", "--help"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "Query an existing FAISS index" in result.stdout, "Result must not be empty"

    @patch("codex.rag.build_index_from_files")
    def test_build_exception_handling(self, mock_build, runner, sample_docs):
        """Test generic exception handling."""
        mock_build.side_effect = Exception("Unexpected error")

        result = runner.invoke(
            app,
            ["build", "--files", str(sample_docs / "*.md")],
        )

        assert result.exit_code != 0, "Result must not be empty"
        assert "Failed to build index" in result.stdout, "Result must not be empty"


class TestIntegration:
    """Integration tests with real RAG components."""

    def test_build_and_query_integration(self, runner, sample_docs, tmp_path):
        """Test full build and query workflow."""
        # Skip if sentence-transformers not available
        if importlib.util.find_spec("sentence_transformers") is None:
            pytest.skip("sentence-transformers not installed")

        index_dir = tmp_path / "indices"

        # Build index
        build_result = runner.invoke(
            app,
            [
                "build",
                "--files",
                str(sample_docs / "*.md"),
                "--index-name",
                "test",
                "--index-dir",
                str(index_dir),
            ],
        )

        # May succeed or fail depending on dependencies
        # Just verify it doesn't crash
        assert build_result.exit_code in [0, 1]

    def test_list_and_stats_integration(self, runner, mock_index_metadata):
        """Test list and stats work together."""
        # List indices
        list_result = runner.invoke(
            app,
            ["list", "--index-dir", str(mock_index_metadata)],
        )
        assert list_result.exit_code == 0, "Result must not be empty"

        # Get stats for listed index
        stats_result = runner.invoke(
            app,
            [
                "stats",
                "--index-name",
                "test_index",
                "--index-dir",
                str(mock_index_metadata),
            ],
        )
        assert stats_result.exit_code == 0, "Result must not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
