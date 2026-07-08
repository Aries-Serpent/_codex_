"""
Tests for RAG caching layer.

Verifies:
- Embedding caching
- Query result caching
- Cache hit/miss behavior
- Cost savings tracking
"""

import pytest

from src.rag.caching import RAGCache, get_rag_cache, set_rag_cache


class TestRAGCache:
    """Test RAG caching layer."""

    def test_embedding_cache_hit(self):
        """Test embedding cache hit."""
        cache = RAGCache()
        text = "hello world"

        # First call - miss, cache it
        cache.set_embedding(text, [0.1, 0.2, 0.3], "test-model")

        # Second call - hit
        result = cache.get_embedding(text)
        assert result is not None, "result must be initialized"
        assert result["embedding"] == [0.1, 0.2, 0.3]

    def test_embedding_cache_miss(self):
        """Test embedding cache miss."""
        cache = RAGCache()
        result = cache.get_embedding("nonexistent")
        assert result is None, "Result must not be empty"

    def test_query_cache_hit(self):
        """Test query result cache hit."""
        cache = RAGCache()
        query = "what is AI?"
        results = [
            {"id": "1", "content": "AI is...", "score": 0.9},
            {"id": "2", "content": "Machine learning is...", "score": 0.8},
        ]

        # First call - cache it
        cache.set_query_result(query, results)

        # Second call - hit
        cached = cache.get_query_result(query)
        assert cached == results, "Result must not be empty"

    def test_query_cache_with_filters(self):
        """Test query caching with filters."""
        cache = RAGCache()
        query = "search term"
        filters = {"category": "technology"}
        results = [{"id": "1", "content": "result"}]

        cache.set_query_result(query, results, filters=filters)
        cached = cache.get_query_result(query, filters=filters)

        assert cached == results, "Result must not be empty"

    def test_embedding_key_generation(self):
        """Test embedding cache key generation."""
        cache = RAGCache()
        key1 = cache._make_embedding_key("hello")
        key2 = cache._make_embedding_key("hello")

        assert key1 == key2, "key1 is not valid"

    def test_query_key_generation(self):
        """Test query cache key generation."""
        cache = RAGCache()
        key1 = cache._make_query_key("search", top_k=10)
        key2 = cache._make_query_key("search", top_k=10)
        key3 = cache._make_query_key("search", top_k=20)

        assert key1 == key2, "key1 is not valid"
        assert key1 != key3, "key1 is not valid"

    def test_cache_stats(self):
        """Test cache statistics."""
        cache = RAGCache(enable_metrics=True)

        cache.set_embedding("text1", [0.1, 0.2], "model")
        cache.get_embedding("text1")
        cache.get_embedding("text2")

        stats = cache.get_stats()
        assert "hits" in stats or "reports" in stats, "Condition must be true"


class TestGlobalRAGCache:
    """Test global RAG cache singleton."""

    def test_get_rag_cache(self):
        """Test getting global RAG cache."""
        cache1 = get_rag_cache()
        cache2 = get_rag_cache()

        assert cache1 is cache2, "cache1 is not valid"

    def test_set_rag_cache(self):
        """Test setting global RAG cache."""
        new_cache = RAGCache(enable_metrics=False)
        set_rag_cache(new_cache)

        retrieved = get_rag_cache()
        assert retrieved is new_cache, "retrieved is not valid"


class TestCachedEmbeddingPipeline:
    """Test cached embedding pipeline."""

    def test_embedding_cache_integration(self):
        """Test that embedding pipeline uses cache."""
        from src.rag.cached_embedding import CachedEmbeddingPipeline

        pipeline = CachedEmbeddingPipeline()

        # First embedding (compute)
        result1 = pipeline.embed_text("test text")
        assert result1.embedding is not None, "embedding must be initialized"

        # Second embedding (should be from cache)
        result2 = pipeline.embed_text("test text")
        assert result2.embedding == result1.embedding, "Result must not be empty"

    def test_batch_embedding_partial_cache(self):
        """Test batch embedding with partial cache hits."""
        from src.rag.cached_embedding import CachedEmbeddingPipeline

        pipeline = CachedEmbeddingPipeline()

        # Pre-cache one text
        pipeline.embed_text("cached text")

        # Batch embed with mix of cached and new texts
        results = pipeline.embed_texts(
            ["cached text", "new text 1", "new text 2"]
        )

        assert len(results) == 3, "Results must not be empty"
        assert all(r.embedding for r in results), "Result must not be empty"


class TestCachedRetrieval:
    """Test cached retrieval pipeline."""

    def test_query_cache_integration(self):
        """Test that retrieval uses cache."""
        from src.rag.cached_retrieval import CachedRetrieval

        retrieval = CachedRetrieval()

        # Add a document
        retrieval.add_document(
            "doc1",
            "This is a test document about Python.",
            {"source": "test"},
        )

        # First query (compute)
        results1 = retrieval.retrieve("Python")

        # Second query (should be from cache)
        results2 = retrieval.retrieve("Python")

        assert len(results1) > 0, "Results1 must not be empty"
        assert results1 == results2, "Result must not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
