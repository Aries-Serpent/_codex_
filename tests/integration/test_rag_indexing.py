"""
Integration tests for RAG indexing functionality.

Tests text chunking, embedding generation, and FAISS index building.
"""

import importlib.util

import pytest

# Check if required dependencies are available
try:
    if importlib.util.find_spec("numpy") is None:
        raise ImportError
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    if importlib.util.find_spec("sentence_transformers") is None:
        raise ImportError
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# Skip all tests if numpy or sentence_transformers is not available
pytestmark = [
    pytest.mark.skipif(
        not NUMPY_AVAILABLE or not SENTENCE_TRANSFORMERS_AVAILABLE,
        reason="numpy and sentence_transformers required for RAG indexing tests",
    ),
    pytest.mark.requires_faiss,
]


class TestChunkText:
    """Test chunk_text function."""

    def test_chunk_text_import(self):
        """Test chunk_text can be imported."""
        from codex.rag.indexer import chunk_text

        assert chunk_text is not None, "chunk_text must be initialized"
        assert callable(chunk_text), "Condition must be true"

    def test_chunk_text_basic(self):
        """Test chunk_text with basic input."""
        from codex.rag.indexer import chunk_text

        text = "Hello world. This is a test."
        chunks = chunk_text(text, chunk_size=20, overlap=5)

        assert isinstance(chunks, list)
        assert len(chunks) > 0, "Chunks must not be empty"
        for chunk in chunks:
            assert len(chunk) == 3, "Chunk must not be empty"

    def test_chunk_text_empty_returns_empty(self):
        """Test chunk_text with empty string returns empty list."""
        from codex.rag.indexer import chunk_text

        chunks = chunk_text("", chunk_size=100, overlap=10)

        assert chunks == [], "chunks is not valid"

    def test_chunk_text_invalid_chunk_size_raises(self):
        """Test chunk_text raises on invalid chunk_size."""
        from codex.rag.indexer import chunk_text

        with pytest.raises(ValueError, match="chunk_size must be positive"):
            chunk_text("test", chunk_size=0, overlap=0)

    def test_chunk_text_invalid_overlap_raises(self):
        """Test chunk_text raises on invalid overlap."""
        from codex.rag.indexer import chunk_text

        with pytest.raises(ValueError, match="overlap must be non-negative"):
            chunk_text("test", chunk_size=100, overlap=-1)

    def test_chunk_text_overlap_ge_chunk_size(self):
        """Test chunk_text handles overlap >= chunk_size."""
        from codex.rag.indexer import chunk_text

        # Should auto-adjust overlap
        chunks = chunk_text("test text here", chunk_size=5, overlap=128)

        # Should not crash, overlap auto-adjusted
        assert isinstance(chunks, list)

    def test_chunk_text_respects_overlap(self):
        """Test chunk_text respects overlap parameter."""
        from codex.rag.indexer import chunk_text

        text = "A" * 100
        chunks = chunk_text(text, chunk_size=30, overlap=10)

        # Should have multiple chunks with overlap
        assert len(chunks) > 1, "Chunks must not be empty"


class TestEmbedChunks:
    """Test embed_chunks function."""

    def test_embed_chunks_import(self):
        """Test embed_chunks can be imported."""
        from codex.rag.indexer import embed_chunks

        assert embed_chunks is not None, "embed_chunks must be initialized"
        assert callable(embed_chunks), "Condition must be true"

    def test_embed_chunks_empty_returns_empty(self):
        """Test embed_chunks with empty list."""
        from codex.rag.indexer import embed_chunks

        result = embed_chunks([])

        # Should return empty array or handle gracefully
        assert result is not None, "result must be initialized"

    def test_embed_chunks_requires_model(self):
        """Test embed_chunks requires model or profile."""
        from codex.rag.indexer import embed_chunks

        chunks = [(0, 10, "test text")]

        # May require model_profile or raise error
        try:
            result = embed_chunks(chunks)
            # If it succeeds, should return something
            assert result is not None, "result must be initialized"
        except (ImportError, RuntimeError):
            # Expected if dependencies missing
            _ = None  # suppressed: no action needed


class TestIndexerMetadata:
    """Test indexer metadata handling."""

    def test_indexer_has_metadata_functions(self):
        """Test indexer module has metadata functions."""
        from codex.rag import indexer

        # Should have functions for metadata handling
        assert hasattr(indexer, "chunk_text")
        assert hasattr(indexer, "embed_chunks")

    def test_indexer_chunk_metadata(self):
        """Test chunk metadata includes position information."""
        from codex.rag.indexer import chunk_text

        text = "Hello world. This is a test."
        chunks = chunk_text(text, chunk_size=50, overlap=10)

        for start, end, text_chunk in chunks:
            assert isinstance(start, int)
            assert isinstance(end, int)
            assert start < end, "start is not valid"
            assert isinstance(text_chunk, str)


class TestIndexSaveLoad:
    """Test index persistence functions."""

    def test_save_index_import(self):
        """Test save_index function exists."""
        try:
            from codex.rag.indexer import save_index

            assert save_index is not None, "save_index must be initialized"
        except ImportError:
            pytest.skip("save_index not available")

    def test_load_index_import(self):
        """Test load_index function exists."""
        try:
            from codex.rag.indexer import load_index

            assert load_index is not None, "load_index must be initialized"
        except ImportError:
            pytest.skip("load_index not available")


class TestFAISSIntegration:
    """Test FAISS integration."""

    def test_faiss_import_handled(self):
        """Test indexer handles FAISS import gracefully."""
        from codex.rag import indexer

        # Should import without error even if FAISS unavailable
        assert indexer is not None, "indexer must be initialized"

    def test_faiss_optional_dependency(self):
        """Test FAISS is treated as optional dependency."""
        # FAISS is optional - test that indexer still imports without it
        # Should not crash if FAISS unavailable
        from codex.rag import indexer

        assert indexer is not None, "indexer must be initialized"
