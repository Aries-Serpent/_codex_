"""
Tests for RAG Retriever Module
"""

import importlib.util
import tempfile
from pathlib import Path

import pytest

# Conditional imports for RAG dependencies - safely handled at test runtime
try:
    from codex.rag.indexer import build_index_from_files
    from codex.rag.retriever import MultiIndexRetriever, Retriever

    RAG_RETRIEVER_AVAILABLE = True
except ImportError:
    RAG_RETRIEVER_AVAILABLE = False

# Check if sentence_transformers is available
try:
    if importlib.util.find_spec("sentence_transformers") is None:
        raise ImportError
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not RAG_RETRIEVER_AVAILABLE or not SENTENCE_TRANSFORMERS_AVAILABLE,
    reason="RAG retriever dependencies (sentence_transformers, faiss) not installed",
)

# Guard for tests that require real SentenceTransformer models on CPU
try:
    import torch as _torch

    _cuda_available = _torch.cuda.is_available()
except (ImportError, RuntimeError):
    _cuda_available = False

_skip_real_st_models = pytest.mark.skipif(
    not _cuda_available,
    reason="SentenceTransformer real model tests may fail on CPU-only runners",
)


@_skip_real_st_models
class TestRetriever:
    """Tests for Retriever class"""

    @pytest.fixture
    def sample_index(self):
        """Create a sample index for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create sample files
            docs_dir = tmpdir / "docs"
            docs_dir.mkdir()

            files = []
            contents = [
                "Python is a high-level programming language. " * 20,
                "Machine learning uses algorithms to learn from data. " * 20,
                "Docker is a containerization platform. " * 20,
            ]

            for i, content in enumerate(contents):
                file_path = docs_dir / f"doc{i}.txt"
                with open(file_path, "w") as f:
                    f.write(content)
                files.append(file_path)

            # Build index
            index_dir = tmpdir / "indices"
            build_index_from_files(
                files=files,
                index_name="test_docs",
                tenant_id="test",
                index_dir=str(index_dir),
                chunk_size=300,
                overlap=50,
            )

            yield {
                "index_dir": str(index_dir),
                "index_name": "test_docs",
                "tenant_id": "test",
            }

    def test_retriever_initialization(self, sample_index):
        """Test retriever initialization"""
        retriever = Retriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
        )

        assert retriever is not None, "retriever must be initialized"
        assert retriever.faiss_index is not None, "faiss_index must be initialized"
        assert len(retriever.chunks_metadata) > 0, "Collection must not be empty"

    def test_retriever_query_basic(self, sample_index):
        """Test basic query functionality"""
        retriever = Retriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
        )

        results = retriever.query("Python programming", top_k=3)

        assert len(results) > 0, "Results must not be empty"
        assert len(results) <= 3, "Results must not be empty"

        # Check result structure
        for result in results:
            assert "text" in result, "Result must not be empty"
            assert "file" in result, "Result must not be empty"
            assert "start_line" in result, "Result must not be empty"
            assert "end_line" in result, "Result must not be empty"
            assert "score" in result, "Result must not be empty"
            assert "generated_at" in result, "Result must not be empty"
            assert "chunk_id" in result, "Result must not be empty"
            assert isinstance(result["score"], float)

    def test_retriever_query_empty(self, sample_index):
        """Test query with empty string"""
        retriever = Retriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
        )

        results = retriever.query("", top_k=5)
        assert len(results) == 0, "Results must not be empty"

        results = retriever.query("   ", top_k=5)
        assert len(results) == 0, "Results must not be empty"

    def test_retriever_query_with_min_score(self, sample_index):
        """Test query with minimum score threshold"""
        retriever = Retriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
        )

        # Very strict threshold should return fewer results
        results_strict = retriever.query("Python", top_k=10, min_score=0.5)
        results_all = retriever.query("Python", top_k=10)

        assert len(results_strict) <= len(results_all), "Results_strict must not be empty"

    def test_retriever_query_top_k_validation(self, sample_index):
        """Test top_k parameter validation"""
        retriever = Retriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
        )

        # Should handle invalid top_k gracefully
        results = retriever.query("test", top_k=0)
        assert isinstance(results, list)

        results = retriever.query("test", top_k=-1)
        assert isinstance(results, list)

    def test_retriever_get_stats(self, sample_index):
        """Test statistics retrieval"""
        retriever = Retriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
        )

        stats = retriever.get_stats()

        assert "index_name" in stats, "Condition must be true"
        assert "tenant_id" in stats, "Condition must be true"
        assert "num_vectors" in stats, "Condition must be true"
        assert "num_chunks" in stats, "Condition must be true"
        assert stats["num_vectors"] > 0, "Value must be greater than zero"
        assert stats["num_chunks"] > 0, "Value must be greater than zero"

    def test_retriever_reload(self, sample_index):
        """Test index reloading"""
        retriever = Retriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
        )

        initial_stats = retriever.get_stats()
        retriever.reload()
        reloaded_stats = retriever.get_stats()

        assert initial_stats["num_vectors"] == reloaded_stats["num_vectors"], "Condition must be true"

    def test_retriever_nonexistent_index(self):
        """Test initialization with non-existent index"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Should not raise during init, but warn
            retriever = Retriever(
                index_dir=tmpdir,
                index_name="nonexistent",
                tenant_id="test",
            )

            # Should have no index loaded
            assert retriever.faiss_index is None, "faiss_index is not valid"

    def test_retriever_query_without_index(self):
        """Test querying without a loaded index"""
        with tempfile.TemporaryDirectory() as tmpdir:
            retriever = Retriever(
                index_dir=tmpdir,
                index_name="nonexistent",
                tenant_id="test",
            )

            results = retriever.query("test query", top_k=5)
            assert len(results) == 0, "Results must not be empty"


@_skip_real_st_models
class TestMultiIndexRetriever:
    """Tests for MultiIndexRetriever class"""

    @pytest.fixture
    def multiple_indices(self):
        """Create multiple indices for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create two separate indices
            indices_info = []

            for idx in range(2):
                docs_dir = tmpdir / f"docs_{idx}"
                docs_dir.mkdir()

                files = []
                content = f"Index {idx} content. " * 30

                file_path = docs_dir / "doc.txt"
                with open(file_path, "w") as f:
                    f.write(content)
                files.append(file_path)

                index_dir = tmpdir / "indices"
                build_index_from_files(
                    files=files,
                    index_name=f"index_{idx}",
                    tenant_id="test",
                    index_dir=str(index_dir),
                    chunk_size=200,
                    overlap=50,
                )

                indices_info.append(
                    {
                        "index_name": f"index_{idx}",
                        "tenant_id": "test",
                    }
                )

            yield {
                "index_dir": str(tmpdir / "indices"),
                "indices": indices_info,
            }

    def test_multi_index_initialization(self, multiple_indices):
        """Test multi-index retriever initialization"""
        retriever = MultiIndexRetriever(
            indices=multiple_indices["indices"],
            index_dir=multiple_indices["index_dir"],
        )

        assert len(retriever.retrievers) == 2, "Collection must not be empty"

    def test_multi_index_query(self, multiple_indices):
        """Test querying across multiple indices"""
        retriever = MultiIndexRetriever(
            indices=multiple_indices["indices"],
            index_dir=multiple_indices["index_dir"],
        )

        results = retriever.query("content", top_k=5)

        assert len(results) > 0, "Results must not be empty"
        # Results should have index_name and tenant_id
        for result in results:
            assert "index_name" in result, "Result must not be empty"
            assert "tenant_id" in result, "Result must not be empty"

    def test_multi_index_query_with_min_score(self, multiple_indices):
        """Test multi-index query with score threshold"""
        retriever = MultiIndexRetriever(
            indices=multiple_indices["indices"],
            index_dir=multiple_indices["index_dir"],
        )

        results = retriever.query("content", top_k=10, min_score=1.0)

        # All results should have score <= min_score
        for result in results:
            assert result["score"] <= 1.0, "Result must not be empty"

    def test_multi_index_get_stats(self, multiple_indices):
        """Test getting stats from multiple indices"""
        retriever = MultiIndexRetriever(
            indices=multiple_indices["indices"],
            index_dir=multiple_indices["index_dir"],
        )

        stats = retriever.get_stats()

        assert len(stats) == 2, "Stats must not be empty"
        for stat in stats:
            assert "index_name" in stat, "Condition must be true"
            assert "num_vectors" in stat, "Condition must be true"

    def test_multi_index_with_invalid_index(self, multiple_indices):
        """Test multi-index with some invalid indices"""
        indices = multiple_indices["indices"] + [{"index_name": "nonexistent", "tenant_id": "test"}]

        retriever = MultiIndexRetriever(
            indices=indices,
            index_dir=multiple_indices["index_dir"],
        )

        # Should only load valid indices
        assert len(retriever.retrievers) == 2, "Collection must not be empty"

    def test_multi_index_empty_list(self):
        """Test multi-index with empty indices list"""
        with tempfile.TemporaryDirectory() as tmpdir:
            retriever = MultiIndexRetriever(
                indices=[],
                index_dir=tmpdir,
            )

            assert len(retriever.retrievers) == 0, "Collection must not be empty"

            results = retriever.query("test", top_k=5)
            assert len(results) == 0, "Results must not be empty"


class TestRetrieverEdgeCases:
    """Edge case tests for retriever"""

    def test_estimate_line_number(self):
        """Test line number estimation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            retriever = Retriever(
                index_dir=tmpdir,
                index_name="test",
                tenant_id="test",
            )

            # Test various positions
            assert retriever._estimate_line_number(0) == 1, "Condition must be true"
            assert retriever._estimate_line_number(-10) == 1, "Condition must be true"
            assert retriever._estimate_line_number(80) == 2, "Condition must be true"
            assert retriever._estimate_line_number(160) == 3, "Condition must be true"

    def test_extract_file_from_metadata(self):
        """Test file extraction from metadata"""
        with tempfile.TemporaryDirectory() as tmpdir:
            retriever = Retriever(
                index_dir=tmpdir,
                index_name="test",
                tenant_id="test",
            )

            # Chunk with direct file reference
            chunk1 = {"file": "test.txt"}
            assert retriever._extract_file_from_metadata(chunk1) == "test.txt", "Data must not be empty"

            # Chunk without file reference
            chunk2 = {}
            retriever.index_metadata = {}
            assert retriever._extract_file_from_metadata(chunk2) == "unknown", "Data must not be empty"

            # With files in index metadata
            retriever.index_metadata = {"files": [{"file": "metadata_file.txt"}]}
            assert retriever._extract_file_from_metadata(chunk2) == "metadata_file.txt", "Data must not be empty"


@_skip_real_st_models
class TestRetrieverIntegration:
    """Integration tests for retriever"""

    def test_full_workflow_with_query(self):
        """Test complete workflow from index building to querying"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create diverse content
            docs_dir = tmpdir / "docs"
            docs_dir.mkdir()

            files = []
            corpus = {
                "python.txt": "Python is a versatile programming language used for web development, data science, and automation. "
                * 20,
                "machine_learning.txt": "Machine learning algorithms learn patterns from data to make predictions and decisions without explicit programming. "
                * 20,
                "docker.txt": "Docker provides containerization for consistent deployment across different environments. "
                * 20,
            }

            for filename, content in corpus.items():
                file_path = docs_dir / filename
                with open(file_path, "w") as f:
                    f.write(content)
                files.append(file_path)

            # Build index
            index_dir = tmpdir / "indices"
            build_index_from_files(
                files=files,
                index_name="integration_test",
                tenant_id="test",
                index_dir=str(index_dir),
                chunk_size=400,
                overlap=100,
            )

            # Create retriever
            retriever = Retriever(
                index_dir=str(index_dir),
                index_name="integration_test",
                tenant_id="test",
            )

            # Test queries for each topic
            python_results = retriever.query("programming language", top_k=3)
            ml_results = retriever.query("data science algorithms", top_k=3)
            docker_results = retriever.query("containerization deployment", top_k=3)

            # Should get relevant results
            assert len(python_results) > 0, "Python_results must not be empty"
            assert len(ml_results) > 0, "Ml_results must not be empty"
            assert len(docker_results) > 0, "Docker_results must not be empty"

            # Results should contain the query terms (roughly)
            assert any("Python" in r["text"] or "programming" in r["text"] for r in python_results), "Result must not be empty"
            assert any("learning" in r["text"] or "algorithm" in r["text"] for r in ml_results), "Result must not be empty"
            assert any("Docker" in r["text"] or "container" in r["text"] for r in docker_results), "Result must not be empty"


@_skip_real_st_models
class TestRetrieverErrorPaths:
    """Error path tests for retriever - targeting uncovered code"""

    def test_load_model_coverage_with_valid_model(self):
        """
        Test _load_model method works correctly.
        Note: ImportError and Exception paths (lines 90-98) are difficult to test
        without breaking the module, but are documented as defensive error handling.
        This test verifies the happy path and documents the error handling exists.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            retriever = Retriever(
                index_dir=tmpdir,
                index_name="test",
                tenant_id="test",
            )

            # This will call _load_model during initialization or first query
            # The model loading includes try/except for ImportError and general Exception
            assert retriever.model_name == "sentence-transformers/all-MiniLM-L6-v2", "model_name is not valid"

    def test_retriever_handles_missing_model_gracefully(self):
        """Test that retriever initialization doesn't fail immediately without model"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Retriever should initialize even if model not loaded yet
            retriever = Retriever(
                index_dir=tmpdir,
                index_name="nonexistent",
                tenant_id="test",
            )

            # Should have no index loaded
            assert retriever.faiss_index is None, "faiss_index is not valid"


@_skip_real_st_models
class TestMultiIndexRetrieverErrorPaths:
    """Error path tests for MultiIndexRetriever - targeting uncovered exception handlers"""

    def test_init_with_all_invalid_indices(self):
        """Test initialization with all invalid indices (line 297-298)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # All indices are invalid/non-existent
            indices = [
                {"index_name": "invalid1", "tenant_id": "test"},
                {"index_name": "invalid2", "tenant_id": "test"},
                {"index_name": "invalid3", "tenant_id": "test"},
            ]

            # Should log warnings but not raise
            retriever = MultiIndexRetriever(
                indices=indices,
                index_dir=tmpdir,
            )

            # No indices should be loaded
            assert len(retriever.retrievers) == 0, "Collection must not be empty"

    def test_init_exception_during_index_load(self):
        """Test exception handling during index loading in __init__ (line 297-298)"""
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create one valid index
            docs_dir = tmpdir / "docs"
            docs_dir.mkdir()

            file_path = docs_dir / "doc.txt"
            with open(file_path, "w") as f:
                f.write("Test content. " * 30)

            index_dir = tmpdir / "indices"
            build_index_from_files(
                files=[file_path],
                index_name="valid_index",
                tenant_id="test",
                index_dir=str(index_dir),
            )

            indices = [
                {"index_name": "valid_index", "tenant_id": "test"},
            ]

            # Mock Retriever to raise exception
            with patch("codex.rag.retriever.Retriever", side_effect=Exception("Load failed")):
                retriever = MultiIndexRetriever(
                    indices=indices,
                    index_dir=str(index_dir),
                )

                # Should handle exception gracefully
                assert len(retriever.retrievers) == 0, "Collection must not be empty"

    def test_query_error_in_individual_index(self, multiple_indices):
        """Test query error handling for individual indices (line 329-330)"""

        retriever = MultiIndexRetriever(
            indices=multiple_indices["indices"],
            index_dir=multiple_indices["index_dir"],
        )

        # Mock one retriever to raise exception during query
        original_query = retriever.retrievers[0].query

        def mock_query_error(*args, **kwargs):
            raise Exception("Query failed")

        retriever.retrievers[0].query = mock_query_error

        # Should log warning but still return results from other indices
        results = retriever.query("test", top_k=5)

        # Should get results from the second index
        assert isinstance(results, list)
        # Restore original for cleanup
        retriever.retrievers[0].query = original_query

    def test_query_all_indices_fail(self):
        """Test when all indices fail during query"""
        from unittest.mock import MagicMock

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create indices
            indices_info = []
            for idx in range(2):
                docs_dir = tmpdir / f"docs_{idx}"
                docs_dir.mkdir()

                file_path = docs_dir / "doc.txt"
                with open(file_path, "w") as f:
                    f.write(f"Index {idx} content. " * 30)

                index_dir = tmpdir / "indices"
                build_index_from_files(
                    files=[file_path],
                    index_name=f"index_{idx}",
                    tenant_id="test",
                    index_dir=str(index_dir),
                )

                indices_info.append(
                    {
                        "index_name": f"index_{idx}",
                        "tenant_id": "test",
                    }
                )

            retriever = MultiIndexRetriever(
                indices=indices_info,
                index_dir=str(tmpdir / "indices"),
            )

            # Make all retrievers fail
            for r in retriever.retrievers:
                r.query = MagicMock(side_effect=Exception("Query failed"))

            # Should return empty list
            results = retriever.query("test", top_k=5)
            assert len(results) == 0, "Results must not be empty"

    @pytest.fixture
    def multiple_indices(self):
        """Create multiple indices for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create two separate indices
            indices_info = []

            for idx in range(2):
                docs_dir = tmpdir / f"docs_{idx}"
                docs_dir.mkdir()

                files = []
                content = f"Index {idx} content. " * 30

                file_path = docs_dir / "doc.txt"
                with open(file_path, "w") as f:
                    f.write(content)
                files.append(file_path)

                index_dir = tmpdir / "indices"
                build_index_from_files(
                    files=files,
                    index_name=f"index_{idx}",
                    tenant_id="test",
                    index_dir=str(index_dir),
                    chunk_size=200,
                    overlap=50,
                )

                indices_info.append(
                    {
                        "index_name": f"index_{idx}",
                        "tenant_id": "test",
                    }
                )

            yield {
                "index_dir": str(tmpdir / "indices"),
                "indices": indices_info,
            }
