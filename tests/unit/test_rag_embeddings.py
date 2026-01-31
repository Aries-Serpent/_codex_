"""
Unit tests for codex.rag.embeddings module.

Tests embedding provider initialization and basic encoding functionality.
"""
import os
from unittest.mock import Mock, patch

import numpy as np
import pytest


class TestLocalSentenceTransformerProvider:
    """Test suite for LocalSentenceTransformerProvider."""

    @pytest.mark.skipif(
        os.environ.get("RAG_EMBEDDING_PROVIDER") == "tfidf",
        reason="Skip sentence-transformers tests in TFIDF mode"
    )
    def test_provider_initialization(self):
        """Test that provider can be initialized."""
        try:
            from codex.rag.embeddings import LocalSentenceTransformerProvider
            
            # This will attempt to load a model, which might fail in test environment
            # We just want to verify the class is importable
            assert LocalSentenceTransformerProvider is not None
        except ImportError:
            pytest.skip("sentence-transformers not available")

    @pytest.mark.skipif(
        os.environ.get("RAG_EMBEDDING_PROVIDER") == "tfidf",
        reason="Skip sentence-transformers tests in TFIDF mode"
    )
    def test_encode_method_exists(self):
        """Test that encode method signature is correct."""
        try:
            from codex.rag.embeddings import LocalSentenceTransformerProvider
            
            # Verify encode method exists and has correct signature
            assert hasattr(LocalSentenceTransformerProvider, "encode")
            assert hasattr(LocalSentenceTransformerProvider, "get_dimension")
        except ImportError:
            pytest.skip("sentence-transformers not available")


class TestOpenAIEmbeddingProvider:
    """Test suite for OpenAIEmbeddingProvider."""

    def test_provider_requires_api_key(self):
        """Test that provider raises error without API key."""
        try:
            from codex.rag.embeddings import OpenAIEmbeddingProvider
        except ImportError:
            pytest.skip("openai not available")
        
        # Remove API key from environment if present
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=True):
            with pytest.raises(ValueError, match="API key not provided"):
                OpenAIEmbeddingProvider()

    def test_provider_dimension_lookup(self):
        """Test that provider returns correct dimensions for known models."""
        try:
            from codex.rag.embeddings import OpenAIEmbeddingProvider
        except ImportError:
            pytest.skip("openai not available")
        
        # Mock OpenAI client initialization
        with patch("codex.rag.embeddings.OpenAI"):
            provider = OpenAIEmbeddingProvider(
                model_name="text-embedding-3-small",
                api_key="test_key"
            )
            
            assert provider.get_dimension() == 1536
            
            provider.model_name = "text-embedding-3-large"
            assert provider.get_dimension() == 3072


class TestCachedEmbeddingProvider:
    """Test suite for CachedEmbeddingProvider."""

    def test_cache_initialization(self, tmp_path):
        """Test that cached provider initializes correctly."""
        from codex.rag.embeddings import CachedEmbeddingProvider
        
        # Create a mock provider
        mock_provider = Mock()
        mock_provider.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_provider.get_dimension.return_value = 3
        
        cache_dir = tmp_path / "embeddings_cache"
        cached = CachedEmbeddingProvider(mock_provider, cache_dir=str(cache_dir))
        
        assert cached.provider == mock_provider
        assert cached.cache_dir.exists()
        assert cached.cache_hits == 0
        assert cached.cache_misses == 0

    def test_cache_bypass_without_key(self, tmp_path):
        """Test that cache is bypassed when no key is provided."""
        from codex.rag.embeddings import CachedEmbeddingProvider
        
        mock_provider = Mock()
        expected_embeddings = np.array([[0.1, 0.2, 0.3]])
        mock_provider.encode.return_value = expected_embeddings
        
        cache_dir = tmp_path / "embeddings_cache"
        cached = CachedEmbeddingProvider(mock_provider, cache_dir=str(cache_dir))
        
        result = cached.encode(["test text"], cache_key=None)
        
        # Should call provider directly
        mock_provider.encode.assert_called_once()
        np.testing.assert_array_equal(result, expected_embeddings)
        assert cached.cache_hits == 0
        assert cached.cache_misses == 0

    def test_cache_miss_and_save(self, tmp_path):
        """Test cache miss saves to cache."""
        from codex.rag.embeddings import CachedEmbeddingProvider
        
        mock_provider = Mock()
        expected_embeddings = np.array([[0.1, 0.2, 0.3]])
        mock_provider.encode.return_value = expected_embeddings
        
        cache_dir = tmp_path / "embeddings_cache"
        cached = CachedEmbeddingProvider(mock_provider, cache_dir=str(cache_dir))
        
        result = cached.encode(["test text"], cache_key="test_file")
        
        # Should have a cache miss
        assert cached.cache_misses == 1
        assert cached.cache_hits == 0
        np.testing.assert_array_equal(result, expected_embeddings)
        
        # Verify cache files exist
        cache_file = cache_dir / "test_file.npz"
        assert cache_file.exists()

    def test_cache_hit_loads_from_cache(self, tmp_path):
        """Test that subsequent calls use cache."""
        from codex.rag.embeddings import CachedEmbeddingProvider
        
        mock_provider = Mock()
        expected_embeddings = np.array([[0.1, 0.2, 0.3]])
        mock_provider.encode.return_value = expected_embeddings
        
        cache_dir = tmp_path / "embeddings_cache"
        cached = CachedEmbeddingProvider(mock_provider, cache_dir=str(cache_dir))
        
        # First call - cache miss
        result1 = cached.encode(["test text"], cache_key="test_key")
        assert cached.cache_misses == 1
        assert cached.cache_hits == 0
        
        # Second call - should hit cache
        result2 = cached.encode(["test text"], cache_key="test_key")
        assert cached.cache_misses == 1
        assert cached.cache_hits == 1
        
        # Should get same embeddings
        np.testing.assert_array_equal(result1, result2)
        
        # Provider should only be called once
        assert mock_provider.encode.call_count == 1
