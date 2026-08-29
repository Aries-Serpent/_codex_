"""
Basic unit tests for codex.rag.embeddings module.

Tests provider protocol and TF-IDF fallback (no model downloads required).
"""

import pytest

pytest.importorskip("numpy")


import numpy as np


class TestEmbeddingProviderProtocol:
    """Test EmbeddingProvider protocol compliance."""

    def test_tfidf_provider_implements_protocol(self):
        """Test TfidfEmbeddingProvider implements protocol."""
        from codex.rag.embeddings import TfidfEmbeddingProvider

        provider = TfidfEmbeddingProvider()

        # Should have encode method
        assert hasattr(provider, "encode")
        assert callable(provider.encode), "Condition must be true"

        # Should have get_dimension method
        assert hasattr(provider, "get_dimension")
        assert callable(provider.get_dimension), "Condition must be true"

    def test_tfidf_encode_returns_ndarray(self):
        """Test TF-IDF encode returns numpy array."""
        from codex.rag.embeddings import TfidfEmbeddingProvider

        provider = TfidfEmbeddingProvider()
        texts = ["hello world", "goodbye world"]

        embeddings = provider.encode(texts)

        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape[0] == 2, "Condition must be true"
        assert embeddings.shape[1] > 0, "Value must be greater than zero"

    def test_tfidf_dimension_consistency(self):
        """Test TF-IDF dimension is consistent for same corpus."""
        from codex.rag.embeddings import TfidfEmbeddingProvider

        provider = TfidfEmbeddingProvider()
        texts = ["hello world", "goodbye world", "test document"]

        # First encoding - fits the vectorizer
        embeddings1 = provider.encode(texts)

        # Second encoding with same texts - should have consistent dimension
        embeddings2 = provider.encode(texts)
        assert embeddings2.shape[1] == embeddings1.shape[1], "Condition must be true"

        # Dimension should be positive
        dimension = provider.get_dimension()
        assert dimension > 0, "dimension must be greater than zero"

    def test_empty_text_handling(self):
        """Test handling of empty texts."""
        from codex.rag.embeddings import TfidfEmbeddingProvider

        provider = TfidfEmbeddingProvider()
        texts = ["", "non-empty text"]

        # Should not crash on empty strings
        embeddings = provider.encode(texts)

        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape[0] == 2, "Condition must be true"


class TestCreateEmbeddingProvider:
    """Test create_embedding_provider factory function."""

    def test_create_provider_tfidf(self):
        """Test creating TF-IDF provider."""
        from codex.rag.embeddings import create_embedding_provider

        provider = create_embedding_provider(provider_type="tfidf")

        assert provider is not None, "provider must be initialized"
        assert hasattr(provider, "encode")

    def test_provider_basic_encode(self):
        """Test basic encoding workflow."""
        from codex.rag.embeddings import create_embedding_provider

        provider = create_embedding_provider(provider_type="tfidf")
        texts = ["hello world", "test document"]

        embeddings = provider.encode(texts)

        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape[0] == 2, "Condition must be true"
