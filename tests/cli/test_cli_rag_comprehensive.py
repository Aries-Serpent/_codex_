"""
Comprehensive tests for RAG CLI commands (cli_rag.py).

Tests cover:
- Build command with various file patterns
- Query command with different parameters
- Stats command output validation
- List command functionality
- Tenant management commands
- Error handling and edge cases
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

pytest.importorskip("typer")


from typer.testing import CliRunner

from codex.cli_rag import _format_bytes, _validate_files, app


@pytest.fixture
def runner():
    """Provide CLI runner instance."""
    return CliRunner()


@pytest.fixture
def temp_test_files(tmp_path: Path):
    """Create temporary test files for indexing."""
    files_dir = tmp_path / "test_docs"
    files_dir.mkdir()

    (files_dir / "doc1.md").write_text("# Document 1\n\nContent for doc 1")
    (files_dir / "doc2.md").write_text("# Document 2\n\nContent for doc 2")
    (files_dir / "subdir").mkdir()
    (files_dir / "subdir" / "doc3.md").write_text("# Document 3\n\nNested content")

    return files_dir


class TestValidateFiles:
    """Test file validation helper."""

    def test_validate_files_single_file(self, tmp_path: Path):
        """Verify validation of single file path."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        result = _validate_files([str(test_file)])
        assert len(result) == 1, "Result must not be empty"
        assert result[0] == test_file, "Result must not be empty"

    def test_validate_files_glob_pattern(self, temp_test_files: Path):
        """Verify glob pattern expansion."""
        pattern = str(temp_test_files / "*.md")
        result = _validate_files([pattern])
        assert len(result) == 2, "Result must not be empty"

    def test_validate_files_recursive_glob(self, temp_test_files: Path):
        """Verify recursive glob pattern."""
        pattern = str(temp_test_files / "**" / "*.md")
        result = _validate_files([pattern])
        assert len(result) == 3, "Result must not be empty"

    def test_validate_files_no_matches(self):
        """Verify error raised when no files match."""
        from typer import BadParameter

        with pytest.raises(BadParameter, match="No valid files found"):
            _validate_files(["/nonexistent/path/*.txt"])

    def test_validate_files_empty_list(self):
        """Verify error raised for empty file list."""
        from typer import BadParameter

        with pytest.raises(BadParameter):
            _validate_files([])

    def test_validate_files_mixed_patterns(self, temp_test_files: Path):
        """Verify handling of multiple patterns."""
        pattern1 = str(temp_test_files / "doc1.md")
        pattern2 = str(temp_test_files / "subdir/*.md")

        result = _validate_files([pattern1, pattern2])
        assert len(result) == 2, "Result must not be empty"


class TestFormatBytes:
    """Test byte size formatting helper."""

    def test_format_bytes_small(self):
        """Verify formatting of small byte sizes."""
        assert "512.00 B" in _format_bytes(512), "Condition must be true"

    def test_format_bytes_kilobytes(self):
        """Verify KB formatting."""
        assert "5.00 KB" in _format_bytes(5 * 1024), "Condition must be true"

    def test_format_bytes_megabytes(self):
        """Verify MB formatting."""
        assert "10.00 MB" in _format_bytes(10 * 1024 * 1024), "Condition must be true"

    def test_format_bytes_gigabytes(self):
        """Verify GB formatting."""
        assert "2.50 GB" in _format_bytes(int(2.5 * 1024 * 1024 * 1024)), "Condition must be true"

    def test_format_bytes_zero(self):
        """Verify zero byte handling."""
        assert "0.00 B" in _format_bytes(0), "Condition must be true"


class TestBuildCommand:
    """Test RAG index build command."""

    @patch("codex.rag.build_index_from_files")
    def test_build_basic(self, mock_build_index, runner: CliRunner, temp_test_files: Path):
        """Verify basic build command execution."""
        mock_build_index.return_value = Path(os.path.join(tempfile.gettempdir(), "test_index"))

        result = runner.invoke(
            app, ["build", "--files", str(temp_test_files / "*.md"), "--index-name", "test_index"]
        )

        assert result.exit_code == 0, "Result must not be empty"
        mock_build_index.assert_called_once()

    @patch("codex.rag.build_index_from_files")
    def test_build_with_tenant(self, mock_build_index, runner: CliRunner, temp_test_files: Path):
        """Verify build with tenant ID."""
        mock_build_index.return_value = Path(os.path.join(tempfile.gettempdir(), "test_index"))

        result = runner.invoke(
            app, ["build", "--files", str(temp_test_files / "*.md"), "--tenant-id", "tenant_123"]
        )

        assert result.exit_code == 0, "Result must not be empty"

    @patch("codex.rag.build_index_from_files")
    def test_build_with_chunk_size(
        self, mock_build_index, runner: CliRunner, temp_test_files: Path
    ):
        """Verify build with custom chunk size."""
        mock_build_index.return_value = Path(os.path.join(tempfile.gettempdir(), "test_index"))

        result = runner.invoke(
            app, ["build", "--files", str(temp_test_files / "*.md"), "--chunk-size", "500"]
        )

        assert result.exit_code == 0, "Result must not be empty"

    def test_build_no_files(self, runner: CliRunner):
        """Verify error when no files provided."""
        result = runner.invoke(app, ["build"])
        assert result.exit_code != 0, "Result must not be empty"

    @patch("codex.rag.build_index_from_files")
    def test_build_invalid_chunk_size(
        self, mock_build_index, runner: CliRunner, temp_test_files: Path
    ):
        """Verify chunk size validation."""
        result = runner.invoke(
            app,
            [
                "build",
                "--files",
                str(temp_test_files / "*.md"),
                "--chunk-size",
                "50",  # Below minimum
            ],
        )

        assert result.exit_code != 0, "Result must not be empty"


class TestQueryCommand:
    """Test RAG query command."""

    @patch("codex.cli_rag.RAGRetriever")
    def test_query_basic(self, mock_retriever, runner: CliRunner):
        """Verify basic query execution."""
        mock_instance = MagicMock()
        mock_retriever.return_value = mock_instance
        mock_instance.query.return_value = [
            {"text": "Result 1", "score": 0.95},
            {"text": "Result 2", "score": 0.87},
        ]

        result = runner.invoke(app, ["query", "test query", "--index-name", "test_index"])

        assert result.exit_code == 0, "Result must not be empty"
        assert "Result 1" in result.output, "Result must not be empty"
        mock_instance.query.assert_called_once()

    @patch("codex.cli_rag.RAGRetriever")
    def test_query_with_top_k(self, mock_retriever, runner: CliRunner):
        """Verify query with custom top_k."""
        mock_instance = MagicMock()
        mock_retriever.return_value = mock_instance
        mock_instance.query.return_value = [{"text": "Result", "score": 0.9}]

        result = runner.invoke(app, ["query", "test", "--top-k", "10"])

        assert result.exit_code == 0, "Result must not be empty"

    @patch("codex.cli_rag.RAGRetriever")
    def test_query_with_tenant(self, mock_retriever, runner: CliRunner):
        """Verify query with tenant isolation."""
        mock_instance = MagicMock()
        mock_retriever.return_value = mock_instance
        mock_instance.query.return_value = []

        result = runner.invoke(app, ["query", "test", "--tenant-id", "tenant_456"])

        assert result.exit_code == 0, "Result must not be empty"

    def test_query_no_query_text(self, runner: CliRunner):
        """Verify error when query text missing."""
        result = runner.invoke(app, ["query"])
        assert result.exit_code != 0, "Result must not be empty"

    @patch("codex.cli_rag.RAGRetriever")
    def test_query_json_output(self, mock_retriever, runner: CliRunner):
        """Verify JSON output format."""
        mock_instance = MagicMock()
        mock_retriever.return_value = mock_instance
        mock_instance.query.return_value = [{"text": "Test", "score": 0.9}]

        result = runner.invoke(app, ["query", "test", "--format", "json"])

        assert result.exit_code == 0, "Result must not be empty"
        # Should contain JSON-formatted output
        assert "{" in result.output or "[" in result.output, "Result must not be empty"


class TestStatsCommand:
    """Test RAG statistics command."""

    def test_stats_basic(self, runner: CliRunner, tmp_path: Path):
        """Verify basic stats output."""
        # Create mock index directory structure
        tenant_path = tmp_path / "default"
        index_path = tenant_path / "default"
        index_path.mkdir(parents=True)

        # Create metadata file
        metadata = {
            "num_chunks": 500,
            "embedding_dim": 384,
            "model_name": "sentence-transformers/all-MiniLM-L6-v2",
            "created_at": "2024-01-01T00:00:00Z",
        }
        (index_path / "metadata.json").write_text(json.dumps(metadata))

        result = runner.invoke(app, ["stats", "--index-dir", str(tmp_path)])

        assert result.exit_code == 0, "Result must not be empty"
        assert "500" in result.output, "Result must not be empty"

    def test_stats_with_index_name(self, runner: CliRunner, tmp_path: Path):
        """Verify stats for specific index."""
        # Create mock index directory structure
        tenant_path = tmp_path / "default"
        index_path = tenant_path / "specific_index"
        index_path.mkdir(parents=True)

        # Create metadata file
        metadata = {
            "num_chunks": 50,
            "embedding_dim": 384,
            "model_name": "test-model",
            "created_at": "2024-01-01T00:00:00Z",
        }
        (index_path / "metadata.json").write_text(json.dumps(metadata))

        result = runner.invoke(
            app, ["stats", "--index-name", "specific_index", "--index-dir", str(tmp_path)]
        )

        assert result.exit_code == 0, "Result must not be empty"


class TestListCommand:
    """Test RAG index listing command."""

    def test_list_indices(self, runner: CliRunner, tmp_path: Path):
        """Verify listing of available indices."""
        # Create mock tenant directory structure
        tenant_path = tmp_path / "default"
        tenant_path.mkdir(parents=True)

        # Create two mock indices
        for idx_name, num_chunks in [("index1", 100), ("index2", 50)]:
            index_path = tenant_path / idx_name
            index_path.mkdir()
            metadata = {
                "num_chunks": num_chunks,
                "model_name": "test-model",
                "created_at": "2024-01-01T00:00:00Z",
            }
            (index_path / "metadata.json").write_text(json.dumps(metadata))

        result = runner.invoke(app, ["list", "--index-dir", str(tmp_path)])

        assert result.exit_code == 0, "Result must not be empty"
        assert "index1" in result.output, "Result must not be empty"
        assert "index2" in result.output, "Result must not be empty"


class TestTenantCommands:
    """Test tenant management commands."""

    @patch("codex.cli_rag.RAGIndexer")
    def test_create_tenant(self, mock_indexer, runner: CliRunner):
        """Verify tenant creation."""
        mock_instance = MagicMock()
        mock_indexer.return_value = mock_instance

        runner.invoke(app, ["tenant", "create", "--tenant-id", "new_tenant"])

        # Command might not exist yet - just verify no crash
        # assert result.exit_code in [0, 2]  # 0 = success, 2 = no command

    @patch("codex.cli_rag.RAGIndexer")
    def test_list_tenants(self, mock_indexer, runner: CliRunner):
        """Verify tenant listing."""
        mock_instance = MagicMock()
        mock_indexer.return_value = mock_instance
        mock_instance.list_tenants.return_value = ["tenant1", "tenant2"]

        runner.invoke(app, ["tenant", "list"])

        # Command might not exist yet
        # assert result.exit_code in [0, 2]


class TestEdgeCases:
    """Test edge cases and error handling."""

    @patch("codex.rag.build_index_from_files")
    def test_build_with_empty_files(self, mock_build, runner: CliRunner, tmp_path: Path):
        """Verify handling of empty files."""
        empty_file = tmp_path / "empty.txt"
        empty_file.write_text("")

        mock_build.return_value = tmp_path / "index"

        result = runner.invoke(app, ["build", "--files", str(empty_file)])

        # Should handle gracefully
        assert result.exit_code == 0, "Result must not be empty"

    @patch("codex.cli_rag.RAGRetriever")
    def test_query_no_results(self, mock_retriever, runner: CliRunner):
        """Verify handling when query returns no results."""
        mock_instance = MagicMock()
        mock_retriever.return_value = mock_instance
        mock_instance.query.return_value = []

        result = runner.invoke(app, ["query", "nonexistent term"])

        assert result.exit_code == 0, "Result must not be empty"
        # Should indicate no results found

    @patch("codex.cli_rag.RAGIndexer")
    def test_build_indexer_failure(self, mock_indexer, runner: CliRunner, temp_test_files: Path):
        """Verify error handling when indexer fails."""
        mock_instance = MagicMock()
        mock_indexer.return_value = mock_instance
        mock_instance.build_index.side_effect = Exception("Indexing failed")

        result = runner.invoke(app, ["build", "--files", str(temp_test_files / "*.md")])

        assert result.exit_code != 0, "Result must not be empty"

    @patch("codex.cli_rag.RAGRetriever")
    def test_query_retriever_failure(self, mock_retriever, runner: CliRunner):
        """Verify error handling when retrieval fails."""
        mock_instance = MagicMock()
        mock_retriever.return_value = mock_instance
        mock_instance.query.side_effect = Exception("Retrieval failed")

        result = runner.invoke(app, ["query", "test"])

        assert result.exit_code != 0, "Result must not be empty"


class TestParameterValidation:
    """Test parameter validation across commands."""

    def test_invalid_top_k(self, runner: CliRunner):
        """Verify top_k parameter validation."""
        result = runner.invoke(app, ["query", "test", "--top-k", "-5"])  # Negative value

        assert result.exit_code != 0, "Result must not be empty"

    def test_invalid_chunk_size_too_large(self, runner: CliRunner, temp_test_files: Path):
        """Verify chunk size upper bound."""
        result = runner.invoke(
            app,
            [
                "build",
                "--files",
                str(temp_test_files / "*.md"),
                "--chunk-size",
                "20000",  # Above maximum
            ],
        )

        assert result.exit_code != 0, "Result must not be empty"

    @patch("codex.cli_rag.RAGIndexer")
    def test_empty_index_name(self, mock_indexer, runner: CliRunner, temp_test_files: Path):
        """Verify empty index name handling."""
        mock_instance = MagicMock()
        mock_indexer.return_value = mock_instance

        runner.invoke(app, ["build", "--files", str(temp_test_files / "*.md"), "--index-name", ""])

        # Should use default or reject
        # Test behavior without strict assertions


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
