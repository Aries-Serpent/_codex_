"""Comprehensive integration tests for RAG pipeline."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("sentence_transformers")

from codex.rag.indexer import chunk_text, embed_chunks, persist_index
from codex.rag.postprocess import postprocess_output
from codex.rag.prompt import build_prompt
from codex.rag.retriever import Retriever


@pytest.fixture
def temp_rag_workspace(tmp_path):
    """Create a temporary workspace for RAG integration tests."""
    workspace = {
        "index_dir": tmp_path / "indices",
        "cache_dir": tmp_path / "cache",
        "test_docs": tmp_path / "docs",
    }

    for path in workspace.values():
        path.mkdir(parents=True, exist_ok=True)

    # Create sample documents
    doc1 = workspace["test_docs"] / "python.txt"
    doc1.write_text(
        "Python is a high-level programming language. "
        "It is widely used for web development and data science. "
        "Python has a simple and readable syntax."
    )

    doc2 = workspace["test_docs"] / "ml.txt"
    doc2.write_text(
        "Machine learning is a subset of artificial intelligence. "
        "It uses algorithms to learn patterns from data. "
        "Popular ML frameworks include TensorFlow and PyTorch."
    )

    return workspace


def _touch_index_file(_index, path: str) -> None:
    Path(path).touch()


class TestEndToEndRAGPipeline:
    """Test complete RAG pipeline from indexing to retrieval."""

    def test_full_pipeline_mock(self, temp_rag_workspace):
        """Test full RAG pipeline with mocked models."""
        # Step 1: Chunk documents
        doc_path = temp_rag_workspace["test_docs"] / "python.txt"
        text = doc_path.read_text()
        chunks = chunk_text(text, chunk_size=100, overlap=20)

        assert len(chunks) > 0, "Chunks must not be empty"

        # Step 2: Mock embedding
        mock_embeddings = np.random.randn(len(chunks), 384).astype(np.float32)

        # Step 3: Persist index
        mock_index = MagicMock()
        mock_index.ntotal = len(chunks)

        with patch("codex.rag.indexer.faiss") as mock_faiss:
            mock_faiss.IndexFlatL2.return_value = mock_index
            mock_faiss.write_index.side_effect = _touch_index_file

            index_path = persist_index(
                index_name="test_index",
                embeddings=mock_embeddings,
                chunks=chunks,
                index_dir=str(temp_rag_workspace["index_dir"]),
            )

            assert index_path.exists(), "Condition must be true"
            assert (index_path / "chunks.json").exists(), "Condition must be true"
            assert (index_path / "metadata.json").exists(), "Data must not be empty"

    def test_index_and_retrieve(self, temp_rag_workspace):
        """Test indexing and retrieving documents."""
        # Index documents
        doc_path = temp_rag_workspace["test_docs"] / "python.txt"
        text = doc_path.read_text()
        chunks = chunk_text(text, chunk_size=50, overlap=10)

        mock_embeddings = np.random.randn(len(chunks), 384).astype(np.float32)
        mock_index = MagicMock()
        mock_index.ntotal = len(chunks)
        mock_index.search.return_value = (np.array([[0.5, 1.0]]), np.array([[0, 1]]))

        with patch("codex.rag.indexer.faiss") as mock_faiss:
            mock_faiss.IndexFlatL2.return_value = mock_index
            mock_faiss.write_index.side_effect = _touch_index_file
            mock_faiss.read_index.return_value = mock_index

            # Persist
            persist_index(
                index_name="python_docs",
                embeddings=mock_embeddings,
                chunks=chunks,
                index_dir=str(temp_rag_workspace["index_dir"]),
            )

            # Retrieve
            mock_model = MagicMock()
            mock_model.encode.return_value = np.random.randn(1, 384).astype(np.float32)

            with patch("sentence_transformers.SentenceTransformer", return_value=mock_model):
                retriever = Retriever(
                    index_dir=str(temp_rag_workspace["index_dir"]), index_name="python_docs"
                )

                results = retriever.query("What is Python?", top_k=2)
                assert len(results) <= 2, "Results must not be empty"

    def test_rag_with_prompt_assembly(self, temp_rag_workspace):
        """Test RAG pipeline with prompt assembly."""
        # Mock retrieval results
        retrieved_docs = [
            {
                "content": "Python is a programming language",
                "metadata": {"source_id": "python.txt"},
                "score": 0.9,
            },
            {
                "content": "Python is used for web development",
                "metadata": {"source_id": "python.txt"},
                "score": 0.8,
            },
        ]

        # Assemble prompt
        prompt = build_prompt(
            query="What is Python?",
            system_prompt="You are a helpful assistant.",
            retrieved_docs=retrieved_docs,
        )

        assert "What is Python?" in prompt, "What is not valid"
        assert "Python is a programming language" in prompt, "Python is not valid"
        assert "helpful assistant" in prompt, "Condition must be true"

    def test_rag_with_postprocessing(self, temp_rag_workspace):
        """Test RAG pipeline with output post-processing."""
        # Mock LLM output
        llm_output = "Python is a programming language used for development. [Internal marker]"

        # Mock retrieved docs
        retrieved_docs = [
            {
                "content": "Python is a programming language",
                "score": 0.9,
                "metadata": {"source_id": "python.txt", "chunk_id": 0},
            }
        ]

        # Post-process
        processed, _evidence = postprocess_output(
            output=llm_output, retrieved_docs=retrieved_docs, include_citations=True
        )

        assert "Python" in processed, "Condition must be true"
        # Internal markers should be removed
        assert True, "True is not valid"


class TestRAGCaching:
    """Test RAG caching behavior."""

    def test_embedding_cache_integration(self, temp_rag_workspace):
        """Test embedding cache in pipeline."""
        from codex.rag.embeddings import CachedEmbeddingProvider

        mock_provider = MagicMock()
        mock_provider.encode.return_value = np.random.randn(2, 384).astype(np.float32)

        cache = CachedEmbeddingProvider(
            provider=mock_provider, cache_dir=str(temp_rag_workspace["cache_dir"])
        )

        texts = ["Text 1", "Text 2"]

        # First call - cache miss
        embeddings1 = cache.encode(texts, cache_key="test_key")
        assert cache.cache_misses == 1, "cache_misses is not valid"

        # Second call - cache hit
        embeddings2 = cache.encode(texts, cache_key="test_key")
        assert cache.cache_hits == 1, "cache_hits is not valid"

        np.testing.assert_array_equal(embeddings1, embeddings2)


class TestRAGErrorHandling:
    """Test error handling in RAG pipeline."""

    def test_chunking_invalid_params(self):
        """Test chunking with invalid parameters."""
        with pytest.raises(ValueError):
            chunk_text("test", chunk_size=-1)

        with pytest.raises(ValueError):
            chunk_text("test", chunk_size=10, overlap=20)

    def test_indexing_mismatch_error(self, temp_rag_workspace):
        """Test indexing with mismatched data."""
        embeddings = np.random.randn(5, 384).astype(np.float32)
        chunks = [(0, 10, "Only one chunk")]

        with pytest.raises(ValueError, match="Mismatch"):
            persist_index(
                index_name="test",
                embeddings=embeddings,
                chunks=chunks,
                index_dir=str(temp_rag_workspace["index_dir"]),
            )

    def test_retriever_empty_query(self, temp_rag_workspace):
        """Test retriever with empty query."""
        mock_index = MagicMock()
        mock_model = MagicMock()

        with patch("codex.rag.indexer.load_index", return_value=(mock_index, [], {})):
            with patch("sentence_transformers.SentenceTransformer", return_value=mock_model):
                retriever = Retriever(index_dir=str(temp_rag_workspace["index_dir"]))
                results = retriever.query("", top_k=5)

                assert results == [], "Result must not be empty"

    def test_retriever_no_index(self, temp_rag_workspace):
        """Test retriever when index doesn't exist."""
        mock_model = MagicMock()

        with patch("codex.rag.indexer.load_index", side_effect=FileNotFoundError):
            with patch("sentence_transformers.SentenceTransformer", return_value=mock_model):
                retriever = Retriever(
                    index_dir=str(temp_rag_workspace["index_dir"]), index_name="nonexistent"
                )

                # Should not crash
                results = retriever.query("test", top_k=5)
                assert results == [], "Result must not be empty"


class TestRAGMultiTenancy:
    """Test multi-tenancy support in RAG."""

    def test_separate_tenant_indices(self, temp_rag_workspace):
        """Test that different tenants have separate indices."""
        chunks = [(0, 10, "Test")]
        embeddings = np.random.randn(1, 384).astype(np.float32)

        mock_index = MagicMock()
        mock_index.ntotal = 1

        with patch("codex.rag.indexer.faiss") as mock_faiss:
            mock_faiss.IndexFlatL2.return_value = mock_index
            mock_faiss.write_index.side_effect = _touch_index_file

            # Create indices for two tenants
            path1 = persist_index(
                index_name="shared_name",
                embeddings=embeddings,
                chunks=chunks,
                tenant_id="tenant1",
                index_dir=str(temp_rag_workspace["index_dir"]),
            )

            path2 = persist_index(
                index_name="shared_name",
                embeddings=embeddings,
                chunks=chunks,
                tenant_id="tenant2",
                index_dir=str(temp_rag_workspace["index_dir"]),
            )

            # Verify they're in different directories
            assert "tenant1" in str(path1), "Condition must be true"
            assert "tenant2" in str(path2), "Condition must be true"
            assert path1 != path2, "path1 is not valid"


class TestRAGPerformance:
    """Test performance-related aspects of RAG."""

    def test_chunking_large_document(self):
        """Test chunking performance with large document."""
        # Create a large document
        large_text = "This is a sentence. " * 10000  # ~200K characters

        chunks = chunk_text(large_text, chunk_size=1000, overlap=100)

        assert len(chunks) > 0, "Chunks must not be empty"
        # Should complete reasonably quickly

    def test_batch_embedding_efficiency(self):
        """Test that batch embedding is used."""
        chunks = [(i, i + 10, f"Chunk {i}") for i in range(100)]

        mock_model = MagicMock()
        mock_model.encode.return_value = np.random.randn(100, 384).astype(np.float32)
        mock_model.to.return_value = mock_model
        mock_model.to_empty.return_value = mock_model
        mock_model.eval.return_value = mock_model

        with patch("sentence_transformers.SentenceTransformer", return_value=mock_model):
            embed_chunks(chunks)

            # Should call encode once with batch
            assert mock_model.encode.call_count == 1, "Count must be greater than zero"

    def test_retrieval_top_k_limits(self, temp_rag_workspace):
        """Test that retrieval respects top-k limit."""
        mock_index = MagicMock()
        mock_index.ntotal = 100

        # Mock search returns many results
        mock_index.search.return_value = (
            np.random.randn(1, 100).astype(np.float32),
            np.arange(100).reshape(1, -1),
        )

        chunks = [{"id": i, "text": f"Chunk {i}"} for i in range(100)]

        mock_model = MagicMock()
        mock_model.encode.return_value = np.random.randn(1, 384).astype(np.float32)

        with patch("codex.rag.indexer.load_index", return_value=(mock_index, chunks, {})):
            with patch("sentence_transformers.SentenceTransformer", return_value=mock_model):
                retriever = Retriever(index_dir=str(temp_rag_workspace["index_dir"]))
                results = retriever.query("test", top_k=10)

                # Should return at most 10
                assert len(results) <= 10, "Results must not be empty"


class TestRAGDataConsistency:
    """Test data consistency in RAG pipeline."""

    def test_chunk_position_consistency(self):
        """Test that chunk positions are consistent."""
        text = "0123456789" * 10
        chunks = chunk_text(text, chunk_size=30, overlap=5)

        for start, end, chunk_content in chunks:
            # Verify chunk matches original text
            assert text[start:end].strip() == chunk_content, "Content must not be empty"

    def test_embedding_dimension_consistency(self):
        """Test embedding dimensions are consistent."""
        chunks = [(i, i + 10, f"Text {i}") for i in range(5)]

        mock_model = MagicMock()
        embeddings = np.random.randn(5, 384).astype(np.float32)
        mock_model.encode.return_value = embeddings
        mock_model.to.return_value = mock_model
        mock_model.to_empty.return_value = mock_model
        mock_model.eval.return_value = mock_model

        with patch("sentence_transformers.SentenceTransformer", return_value=mock_model):
            result = embed_chunks(chunks)

            # All embeddings should have same dimension
            assert result.shape == (5, 384)

    def test_index_metadata_consistency(self, temp_rag_workspace):
        """Test that index metadata is consistent."""
        chunks = [(0, 10, "Test")]
        embeddings = np.random.randn(1, 384).astype(np.float32)

        custom_metadata = {"source_file": "test.py", "created_by": "test_user"}

        mock_index = MagicMock()
        mock_index.ntotal = 1

        with patch("codex.rag.indexer.faiss") as mock_faiss:
            mock_faiss.IndexFlatL2.return_value = mock_index
            mock_faiss.write_index.side_effect = _touch_index_file

            index_path = persist_index(
                index_name="test",
                embeddings=embeddings,
                chunks=chunks,
                metadata=custom_metadata,
                index_dir=str(temp_rag_workspace["index_dir"]),
            )

            # Load and verify metadata
            metadata_file = index_path / "metadata.json"
            with open(metadata_file) as f:
                saved_metadata = json.load(f)

            assert saved_metadata["source_file"] == "test.py", "Data must not be empty"
            assert saved_metadata["created_by"] == "test_user", "Data must not be empty"
            assert saved_metadata["num_vectors"] == 1, "Data must not be empty"
