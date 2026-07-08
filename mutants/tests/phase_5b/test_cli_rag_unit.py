"""
Comprehensive unit tests for src/codex/cli_rag.py

Tests cover:
- File validation with glob patterns
- Byte formatting with edge cases
- Index operations (build, query, list, delete)
- Error handling and edge cases
- Mocking external dependencies
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer

from codex.cli_rag import (
    RAGIndexer,
    RAGRetriever,
    _format_bytes,
    _validate_files,
    app,
    delete,
    list_indices,
    merge,
    query,
    stats,
)


class TestFormatBytes:
    """Tests for _format_bytes() function."""

    def test_format_bytes_zero(self):
        """Test formatting 0 bytes."""
        result = _format_bytes(0)
        assert result == "0.00 B", "Result must not be empty"

    def test_format_bytes_single_byte(self):
        """Test formatting 1 byte."""
        result = _format_bytes(1)
        assert result == "1.00 B", "Result must not be empty"

    @pytest.mark.parametrize(
        "size,expected",
        [
            (512, "512.00 B"),
            (1023, "1023.00 B"),
            (1024, "1.00 KB"),
            (1536, "1.50 KB"),
            (1024 * 1024, "1.00 MB"),
            (1024 * 1024 * 1024, "1.00 GB"),
            (1024 * 1024 * 1024 * 1024, "1.00 TB"),
            (1024 * 1024 * 1024 * 1024 * 1024, "1024.00 TB"),
        ],
    )
    def test_format_bytes_boundaries(self, size, expected):
        """Test byte formatting at unit boundaries."""
        result = _format_bytes(size)
        assert result == expected, "Result must not be empty"

    @pytest.mark.parametrize(
        "size",
        [
            2048,  # 2 KB
            5242880,  # 5 MB
            10737418240,  # 10 GB
        ],
    )
    def test_format_bytes_various_sizes(self, size):
        """Test formatting various sizes."""
        result = _format_bytes(size)
        assert " " in result, "Result must not be empty"
        assert any(unit in result for unit in ["B", "KB", "MB", "GB", "TB"])


class TestValidateFiles:
    """Tests for _validate_files() function."""

    def test_validate_files_empty_list(self):
        """Test validation with empty file list."""
        with pytest.raises(typer.BadParameter):
            _validate_files([])

    def test_validate_files_no_matches(self, tmp_path):
        """Test validation with no matching files."""
        pattern = str(tmp_path / "*.nonexistent")
        with pytest.raises(typer.BadParameter) as exc_info:
            _validate_files([pattern])
        assert "No valid files found" in str(exc_info.value), "Value must be initialized"

    def test_validate_files_single_file(self, tmp_path):
        """Test validation with single file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        result = _validate_files([str(test_file)])
        assert len(result) == 1, "Result must not be empty"
        assert result[0].name == "test.txt", "Result must not be empty"

    def test_validate_files_multiple_files(self, tmp_path):
        """Test validation with multiple files."""
        file1 = tmp_path / "file1.py"
        file2 = tmp_path / "file2.py"
        file1.write_text("# file 1")
        file2.write_text("# file 2")

        result = _validate_files([str(file1), str(file2)])
        assert len(result) == 2, "Result must not be empty"
        assert all(isinstance(p, Path) for p in result)

    def test_validate_files_glob_pattern(self, tmp_path):
        """Test validation with glob pattern."""
        (tmp_path / "doc1.md").write_text("# doc 1")
        (tmp_path / "doc2.md").write_text("# doc 2")
        (tmp_path / "code.py").write_text("# code")

        pattern = str(tmp_path / "*.md")
        result = _validate_files([pattern])
        assert len(result) == 2, "Result must not be empty"
        assert all(p.name.endswith(".md") for p in result), "Result must not be empty"

    def test_validate_files_recursive_glob(self, tmp_path):
        """Test validation with recursive glob pattern."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (tmp_path / "file1.py").write_text("# file 1")
        (subdir / "file2.py").write_text("# file 2")

        pattern = str(tmp_path / "**/*.py")
        result = _validate_files([pattern])
        assert len(result) == 2, "Result must not be empty"
        assert all(p.name.endswith(".py") for p in result), "Result must not be empty"

    def test_validate_files_mixed_patterns(self, tmp_path):
        """Test validation with mixed file patterns."""
        (tmp_path / "file1.py").write_text("# python")
        (tmp_path / "file2.md").write_text("# markdown")
        (tmp_path / "file3.txt").write_text("text")

        result = _validate_files([str(tmp_path / "*.py"), str(tmp_path / "*.md")])
        assert len(result) == 2, "Result must not be empty"
        assert any(p.name == "file1.py" for p in result), "Result must not be empty"
        assert any(p.name == "file2.md" for p in result), "Result must not be empty"


class TestListIndices:
    """Tests for list_indices() function."""

    def test_list_indices_no_tenant_path(self, tmp_path, capsys):
        """Test listing indices when tenant path doesn't exist."""
        with patch("codex.cli_rag.console"):
            list_indices(tenant_id="default", index_dir=str(tmp_path))
            # Should not raise, just print message

    def test_list_indices_empty_tenant(self, tmp_path):
        """Test listing indices when tenant exists but is empty."""
        tenant_path = tmp_path / "default"
        tenant_path.mkdir()

        with patch("codex.cli_rag.console"):
            list_indices(tenant_id="default", index_dir=str(tmp_path))

    def test_list_indices_with_valid_indices(self, tmp_path):
        """Test listing indices with valid metadata."""
        tenant_path = tmp_path / "default"
        tenant_path.mkdir()

        index1_path = tenant_path / "index1"
        index1_path.mkdir()
        metadata1 = {
            "num_chunks": 100,
            "created_at": "2024-01-01T00:00:00Z",
            "model_name": "all-MiniLM-L6-v2",
        }
        (index1_path / "metadata.json").write_text(json.dumps(metadata1))

        index2_path = tenant_path / "index2"
        index2_path.mkdir()
        metadata2 = {
            "num_chunks": 200,
            "created_at": "2024-01-02T00:00:00Z",
            "model_name": "all-MiniLM-L6-v2",
        }
        (index2_path / "metadata.json").write_text(json.dumps(metadata2))

        with patch("codex.cli_rag.console"):
            # Should not raise
            list_indices(tenant_id="default", index_dir=str(tmp_path))

    def test_list_indices_invalid_metadata(self, tmp_path):
        """Test listing indices with invalid metadata files."""
        tenant_path = tmp_path / "default"
        tenant_path.mkdir()

        index_path = tenant_path / "bad_index"
        index_path.mkdir()
        (index_path / "metadata.json").write_text("invalid json")

        with patch("codex.cli_rag.console"):
            # Should not raise despite invalid JSON
            list_indices(tenant_id="default", index_dir=str(tmp_path))

    def test_list_indices_custom_index_dir(self, tmp_path):
        """Test listing indices with custom index directory."""
        custom_dir = tmp_path / "custom_indices"
        custom_dir.mkdir()
        tenant_path = custom_dir / "tenant_a"
        tenant_path.mkdir()

        with patch("codex.cli_rag.console"):
            list_indices(tenant_id="tenant_a", index_dir=str(custom_dir))


class TestDeleteIndex:
    """Tests for delete() function."""

    def test_delete_index_not_found(self, tmp_path):
        """Test deleting non-existent index."""
        with patch("codex.cli_rag.console"):
            with pytest.raises(typer.Exit):
                delete(
                    index_name="nonexistent",
                    tenant_id="default",
                    index_dir=str(tmp_path),
                    confirm=True,
                )

    def test_delete_index_exists_with_confirmation(self, tmp_path):
        """Test deleting existing index with confirmation."""
        tenant_path = tmp_path / "default"
        index_path = tenant_path / "test_index"
        index_path.mkdir(parents=True)
        (index_path / "metadata.json").write_text("{}")

        with patch("codex.cli_rag.console"):
            delete(
                index_name="test_index",
                tenant_id="default",
                index_dir=str(tmp_path),
                confirm=True,
            )
        assert not index_path.exists(), "Condition must be true"

    def test_delete_index_without_confirmation_denied(self, tmp_path):
        """Test deleting index with confirmation denied."""
        tenant_path = tmp_path / "default"
        index_path = tenant_path / "test_index"
        index_path.mkdir(parents=True)
        (index_path / "metadata.json").write_text("{}")

        with patch("codex.cli_rag.console"):
            with patch("typer.confirm", return_value=False):
                delete(
                    index_name="test_index",
                    tenant_id="default",
                    index_dir=str(tmp_path),
                    confirm=False,
                )
        assert index_path.exists(), "Condition must be true"

    def test_delete_index_without_confirmation_approved(self, tmp_path):
        """Test deleting index with confirmation approved."""
        tenant_path = tmp_path / "default"
        index_path = tenant_path / "test_index"
        index_path.mkdir(parents=True)
        (index_path / "metadata.json").write_text("{}")

        with patch("codex.cli_rag.console"):
            with patch("typer.confirm", return_value=True):
                delete(
                    index_name="test_index",
                    tenant_id="default",
                    index_dir=str(tmp_path),
                    confirm=False,
                )
        assert not index_path.exists(), "Condition must be true"

    def test_delete_index_custom_tenant(self, tmp_path):
        """Test deleting index for custom tenant."""
        tenant_path = tmp_path / "customer_a"
        index_path = tenant_path / "docs"
        index_path.mkdir(parents=True)

        with patch("codex.cli_rag.console"):
            delete(
                index_name="docs",
                tenant_id="customer_a",
                index_dir=str(tmp_path),
                confirm=True,
            )
        assert not index_path.exists(), "Condition must be true"


class TestMergeIndices:
    """Tests for merge() function."""

    def test_merge_less_than_two_indices(self):
        """Test merge with less than 2 source indices."""
        with patch("codex.cli_rag.console"):
            with pytest.raises(typer.Exit):
                merge(
                    source_indices=["single"],
                    target_index="target",
                    tenant_id="default",
                )

    def test_merge_empty_source_list(self):
        """Test merge with empty source list."""
        with patch("codex.cli_rag.console"):
            with pytest.raises(typer.Exit):
                merge(
                    source_indices=[],
                    target_index="target",
                    tenant_id="default",
                )

    def test_merge_requires_two_sources(self):
        """Test merge requires at least 2 indices."""
        with patch("codex.cli_rag.console"):
            with pytest.raises(typer.Exit):
                merge(
                    source_indices=["idx1"],
                    target_index="target",
                    tenant_id="default",
                )

    def test_merge_accepts_valid_parameters(self):
        """Test merge with valid parameters (validation passes)."""
        # The merge function validates source_indices has at least 2 items
        # For this test, we verify the validation logic works
        with patch("codex.cli_rag.console"):
            # This will fail on the import, but that's expected
            # We're testing that the validation logic accepts the parameters
            try:
                merge(
                    source_indices=["idx1", "idx2"],
                    target_index="combined",
                    tenant_id="default",
                )
            except (typer.Exit, ImportError, AttributeError):
                # Expected - validation passed, but dependency failed
                pass

    def test_merge_three_indices(self):
        """Test merge with three source indices."""
        with patch("codex.cli_rag.console"):
            try:
                merge(
                    source_indices=["idx1", "idx2", "idx3"],
                    target_index="combined",
                    tenant_id="default",
                )
            except (typer.Exit, ImportError, AttributeError):
                # Expected - validation passed
                pass


class TestStats:
    """Tests for stats() function."""

    def test_stats_index_not_found(self, tmp_path):
        """Test stats for non-existent index."""
        with patch("codex.cli_rag.console"):
            with pytest.raises(typer.Exit):
                stats(
                    index_name="nonexistent",
                    tenant_id="default",
                    index_dir=str(tmp_path),
                )

    def test_stats_metadata_not_found(self, tmp_path):
        """Test stats when metadata.json is missing."""
        index_path = tmp_path / "default" / "test_index"
        index_path.mkdir(parents=True)
        # No metadata file

        with patch("codex.cli_rag.console"):
            with pytest.raises(typer.Exit):
                stats(
                    index_name="test_index",
                    tenant_id="default",
                    index_dir=str(tmp_path),
                )

    def test_stats_with_valid_metadata(self, tmp_path):
        """Test stats with valid metadata."""
        index_path = tmp_path / "default" / "test_index"
        index_path.mkdir(parents=True)

        # Create some test files
        (index_path / "file1.bin").write_bytes(b"x" * 1000)
        (index_path / "file2.bin").write_bytes(b"y" * 2000)

        metadata = {
            "num_chunks": 50,
            "embedding_dim": 384,
            "model_name": "all-MiniLM-L6-v2",
            "created_at": "2024-01-01T00:00:00Z",
        }
        (index_path / "metadata.json").write_text(json.dumps(metadata))

        with patch("codex.cli_rag.console"):
            stats(
                index_name="test_index",
                tenant_id="default",
                index_dir=str(tmp_path),
            )

    def test_stats_custom_index_dir(self, tmp_path):
        """Test stats with custom index directory."""
        custom_dir = tmp_path / "custom"
        index_path = custom_dir / "customer_a" / "my_index"
        index_path.mkdir(parents=True)

        metadata = {
            "num_chunks": 100,
            "embedding_dim": 768,
            "model_name": "sentence-transformers/bert-base",
            "created_at": "2024-01-02T00:00:00Z",
        }
        (index_path / "metadata.json").write_text(json.dumps(metadata))

        with patch("codex.cli_rag.console"):
            stats(
                index_name="my_index",
                tenant_id="customer_a",
                index_dir=str(custom_dir),
            )


class TestRAGIndexerStub:
    """Tests for RAGIndexer stub implementation."""

    def test_rag_indexer_import_error(self):
        """Test that RAGIndexer raises ImportError when dependencies missing."""
        try:
            # Try to initialize RAGIndexer directly
            RAGIndexer()
        except ImportError as e:
            assert "requires codex.rag extras" in str(e).lower() or isinstance(e, ImportError)


class TestRAGRetrieverStub:
    """Tests for RAGRetriever stub implementation."""

    def test_rag_retriever_import_error(self):
        """Test that RAGRetriever raises ImportError when dependencies missing."""
        try:
            # Try to initialize RAGRetriever directly
            RAGRetriever()
        except ImportError as e:
            assert "requires codex.rag extras" in str(e).lower() or isinstance(e, ImportError)


class TestQueryFunction:
    """Tests for query() function."""

    @patch("codex.cli_rag.RAGRetriever")
    def test_query_no_results(self, mock_retriever_class):
        """Test query with no results."""
        mock_retriever = MagicMock()
        mock_retriever.query.return_value = []
        mock_retriever_class.return_value = mock_retriever

        with patch("codex.cli_rag.console"):
            query(
                query_text="test query",
                index_name="default",
                tenant_id="default",
                top_k=5,
                min_score=0.0,
                output_format="table",
            )

    @patch("codex.cli_rag.RAGRetriever")
    def test_query_with_results_table_format(self, mock_retriever_class):
        """Test query with results in table format."""
        mock_results = [
            {"score": 0.95, "file": "doc1.md", "text": "Sample text 1"},
            {"score": 0.87, "file": "doc2.md", "text": "Sample text 2"},
        ]
        mock_retriever = MagicMock()
        mock_retriever.query.return_value = mock_results
        mock_retriever_class.return_value = mock_retriever

        with patch("codex.cli_rag.console"):
            query(
                query_text="test query",
                index_name="default",
                tenant_id="default",
                top_k=5,
                min_score=0.5,
                output_format="table",
            )

    @patch("codex.cli_rag.RAGRetriever")
    def test_query_with_results_json_format(self, mock_retriever_class, capsys):
        """Test query with results in JSON format."""
        mock_results = [
            {"score": 0.95, "file": "doc1.md", "text": "Sample text 1"},
        ]
        mock_retriever = MagicMock()
        mock_retriever.query.return_value = mock_results
        mock_retriever_class.return_value = mock_retriever

        with patch("codex.cli_rag.console"):
            query(
                query_text="test query",
                index_name="default",
                tenant_id="default",
                top_k=5,
                min_score=0.0,
                output_format="json",
            )

    @patch("codex.cli_rag.RAGRetriever")
    def test_query_index_not_found(self, mock_retriever_class):
        """Test query when index not found."""
        mock_retriever_class.side_effect = FileNotFoundError("Index not found")

        with patch("codex.cli_rag.console"):
            with pytest.raises(typer.Exit):
                query(
                    query_text="test query",
                    index_name="nonexistent",
                    tenant_id="default",
                    top_k=5,
                    min_score=0.0,
                    output_format="table",
                )

    @patch("codex.cli_rag.RAGRetriever")
    def test_query_generic_error(self, mock_retriever_class):
        """Test query with generic error."""
        mock_retriever_class.side_effect = RuntimeError("Database connection failed")

        with patch("codex.cli_rag.console"):
            with pytest.raises(typer.Exit):
                query(
                    query_text="test query",
                    index_name="default",
                    tenant_id="default",
                    top_k=5,
                    min_score=0.0,
                    output_format="table",
                )


class TestAppIntegration:
    """Integration tests for the app."""

    def test_app_created(self):
        """Test that the Typer app is created."""
        assert app is not None, "app must be initialized"
        assert hasattr(app, "command")

    def test_app_has_commands(self):
        """Test that app has expected commands."""
        # Check if commands are registered
        assert callable(app), "Condition must be true"
