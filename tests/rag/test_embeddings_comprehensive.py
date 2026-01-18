"""Comprehensive tests for RAG embeddings module."""

import hashlib
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest

from codex.rag.embeddings import (
    CachedEmbeddingProvider,
    EmbeddingProvider,
    LocalSentenceTransformerProvider,
    OpenAIEmbeddingProvider,
)


@pytest.fixture
def temp_cache_dir(tmp_path):
    """Create a temporary cache directory."""
    cache_dir = tmp_path / "embeddings_cache"
    cache_dir.mkdir()
    return str(cache_dir)


@pytest.fixture
def mock_sentence_transformer():
    """Mock SentenceTransformer model."""
    mock_model = MagicMock()
    mock_model.encode.return_value = np.random.randn(3, 384).astype(np.float32)
    mock_model.get_sentence_embedding_dimension.return_value = 384
    return mock_model


class TestLocalSentenceTransformerProvider:
    """Test suite for LocalSentenceTransformerProvider."""

    def test_initialization_default_model(self, mock_sentence_transformer):
        """Test initialization with default model."""
        with patch('sentence_transformers.SentenceTransformer', return_value=mock_sentence_transformer):
            provider = LocalSentenceTransformerProvider()
            assert provider.model_name == "sentence-transformers/all-MiniLM-L6-v2"
            assert provider.model is not None

    def test_initialization_custom_model(self, mock_sentence_transformer):
        """Test initialization with custom model."""
        with patch('sentence_transformers.SentenceTransformer', return_value=mock_sentence_transformer):
            provider = LocalSentenceTransformerProvider(
                model_name="sentence-transformers/paraphrase-MiniLM-L6-v2"
            )
            assert provider.model_name == "sentence-transformers/paraphrase-MiniLM-L6-v2"

    def test_initialization_with_cache_dir(self, mock_sentence_transformer, temp_cache_dir):
        """Test initialization with custom cache directory."""
        with patch('sentence_transformers.SentenceTransformer', return_value=mock_sentence_transformer):
            provider = LocalSentenceTransformerProvider(cache_dir=temp_cache_dir)
            assert provider.cache_dir == temp_cache_dir

    def test_encode_texts(self, mock_sentence_transformer):
        """Test encoding texts to embeddings."""
        with patch('sentence_transformers.SentenceTransformer', return_value=mock_sentence_transformer):
            provider = LocalSentenceTransformerProvider()
            texts = ["Hello world", "Test text", "Another example"]
            embeddings = provider.encode(texts)
            
            assert isinstance(embeddings, np.ndarray)
            assert embeddings.shape[0] == 3
            mock_sentence_transformer.encode.assert_called_once()

    def test_encode_with_batch_size(self, mock_sentence_transformer):
        """Test encoding with custom batch size."""
        with patch('sentence_transformers.SentenceTransformer', return_value=mock_sentence_transformer):
            provider = LocalSentenceTransformerProvider()
            texts = ["Text 1", "Text 2", "Text 3"]
            embeddings = provider.encode(texts, batch_size=2)
            
            call_kwargs = mock_sentence_transformer.encode.call_args[1]
            assert call_kwargs['batch_size'] == 2

    def test_encode_with_progress(self, mock_sentence_transformer):
        """Test encoding with progress bar."""
        with patch('sentence_transformers.SentenceTransformer', return_value=mock_sentence_transformer):
            provider = LocalSentenceTransformerProvider()
            texts = ["Text 1", "Text 2"]
            embeddings = provider.encode(texts, show_progress=True)
            
            call_kwargs = mock_sentence_transformer.encode.call_args[1]
            assert call_kwargs['show_progress_bar'] is True

    def test_get_dimension(self, mock_sentence_transformer):
        """Test getting embedding dimension."""
        with patch('sentence_transformers.SentenceTransformer', return_value=mock_sentence_transformer):
            provider = LocalSentenceTransformerProvider()
            dimension = provider.get_dimension()
            assert dimension == 384

    def test_encode_without_model_raises_error(self):
        """Test encoding without loaded model raises error."""
        with patch('sentence_transformers.SentenceTransformer', side_effect=ImportError("Not installed")):
            with pytest.raises(ImportError):
                LocalSentenceTransformerProvider()

    def test_model_not_loaded_encode_error(self, mock_sentence_transformer):
        """Test encoding when model is not loaded."""
        with patch('sentence_transformers.SentenceTransformer', return_value=mock_sentence_transformer):
            provider = LocalSentenceTransformerProvider()
            provider.model = None
            
            with pytest.raises(RuntimeError, match="Model not loaded"):
                provider.encode(["test"])

    def test_model_not_loaded_dimension_error(self, mock_sentence_transformer):
        """Test getting dimension when model is not loaded."""
        with patch('sentence_transformers.SentenceTransformer', return_value=mock_sentence_transformer):
            provider = LocalSentenceTransformerProvider()
            provider.model = None
            
            with pytest.raises(RuntimeError, match="Model not loaded"):
                provider.get_dimension()


class TestOpenAIEmbeddingProvider:
    """Test suite for OpenAIEmbeddingProvider."""

    def test_initialization_with_api_key(self):
        """Test initialization with API key."""
        mock_client = MagicMock()
        with patch('codex.rag.embeddings.OpenAI', return_value=mock_client):
            provider = OpenAIEmbeddingProvider(api_key="test-key-123")
            assert provider.model_name == "text-embedding-3-small"
            assert provider.client is not None

    def test_initialization_with_env_var(self):
        """Test initialization with environment variable."""
        mock_client = MagicMock()
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'env-key-456'}):
            with patch('codex.rag.embeddings.OpenAI', return_value=mock_client):
                provider = OpenAIEmbeddingProvider()
                assert provider.client is not None

    def test_initialization_without_api_key_raises_error(self):
        """Test initialization without API key raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key not provided"):
                OpenAIEmbeddingProvider()

    def test_initialization_custom_model(self):
        """Test initialization with custom model."""
        mock_client = MagicMock()
        with patch('codex.rag.embeddings.OpenAI', return_value=mock_client):
            provider = OpenAIEmbeddingProvider(
                model_name="text-embedding-3-large",
                api_key="test-key"
            )
            assert provider.model_name == "text-embedding-3-large"

    def test_encode_texts(self):
        """Test encoding texts via OpenAI API."""
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(embedding=[0.1] * 1536),
            MagicMock(embedding=[0.2] * 1536),
        ]
        
        mock_client = MagicMock()
        mock_client.embeddings.create.return_value = mock_response
        
        with patch('codex.rag.embeddings.OpenAI', return_value=mock_client):
            provider = OpenAIEmbeddingProvider(api_key="test-key")
            texts = ["Hello world", "Test text"]
            embeddings = provider.encode(texts)
            
            assert isinstance(embeddings, np.ndarray)
            assert embeddings.shape == (2, 1536)
            mock_client.embeddings.create.assert_called_once()

    def test_encode_with_batching(self):
        """Test encoding with batch processing."""
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536) for _ in range(5)]
        
        mock_client = MagicMock()
        mock_client.embeddings.create.return_value = mock_response
        
        with patch('codex.rag.embeddings.OpenAI', return_value=mock_client):
            provider = OpenAIEmbeddingProvider(api_key="test-key")
            texts = ["Text " + str(i) for i in range(5)]
            embeddings = provider.encode(texts, batch_size=3)
            
            # Should make 2 API calls (3 + 2)
            assert mock_client.embeddings.create.call_count == 2

    def test_encode_api_error_propagates(self):
        """Test that API errors are propagated."""
        mock_client = MagicMock()
        mock_client.embeddings.create.side_effect = Exception("API Error")
        
        with patch('codex.rag.embeddings.OpenAI', return_value=mock_client):
            provider = OpenAIEmbeddingProvider(api_key="test-key")
            
            with pytest.raises(Exception, match="API Error"):
                provider.encode(["test"])

    def test_get_dimension_small_model(self):
        """Test getting dimension for small model."""
        mock_client = MagicMock()
        with patch('codex.rag.embeddings.OpenAI', return_value=mock_client):
            provider = OpenAIEmbeddingProvider(
                model_name="text-embedding-3-small",
                api_key="test-key"
            )
            assert provider.get_dimension() == 1536

    def test_get_dimension_large_model(self):
        """Test getting dimension for large model."""
        mock_client = MagicMock()
        with patch('codex.rag.embeddings.OpenAI', return_value=mock_client):
            provider = OpenAIEmbeddingProvider(
                model_name="text-embedding-3-large",
                api_key="test-key"
            )
            assert provider.get_dimension() == 3072

    def test_get_dimension_ada_model(self):
        """Test getting dimension for Ada model."""
        mock_client = MagicMock()
        with patch('codex.rag.embeddings.OpenAI', return_value=mock_client):
            provider = OpenAIEmbeddingProvider(
                model_name="text-embedding-ada-002",
                api_key="test-key"
            )
            assert provider.get_dimension() == 1536

    def test_get_dimension_unknown_model_defaults(self):
        """Test getting dimension for unknown model defaults to 1536."""
        mock_client = MagicMock()
        with patch('codex.rag.embeddings.OpenAI', return_value=mock_client):
            provider = OpenAIEmbeddingProvider(
                model_name="unknown-model",
                api_key="test-key"
            )
            assert provider.get_dimension() == 1536

    def test_encode_without_client_raises_error(self):
        """Test encoding without initialized client raises error."""
        mock_client = MagicMock()
        with patch('codex.rag.embeddings.OpenAI', return_value=mock_client):
            provider = OpenAIEmbeddingProvider(api_key="test-key")
            provider.client = None
            
            with pytest.raises(RuntimeError, match="OpenAI client not initialized"):
                provider.encode(["test"])


class TestCachedEmbeddingProvider:
    """Test suite for CachedEmbeddingProvider."""

    def test_initialization(self, temp_cache_dir):
        """Test cache initialization."""
        mock_provider = MagicMock(spec=EmbeddingProvider)
        cache = CachedEmbeddingProvider(mock_provider, cache_dir=temp_cache_dir)
        
        assert cache.provider is mock_provider
        assert cache.cache_dir == Path(temp_cache_dir)
        assert cache.cache_hits == 0
        assert cache.cache_misses == 0
        assert Path(temp_cache_dir).exists()

    def test_cache_miss_calls_provider(self, temp_cache_dir):
        """Test cache miss calls underlying provider."""
        mock_provider = MagicMock(spec=EmbeddingProvider)
        mock_provider.encode.return_value = np.random.randn(2, 384).astype(np.float32)
        
        cache = CachedEmbeddingProvider(mock_provider, cache_dir=temp_cache_dir)
        texts = ["Hello", "World"]
        embeddings = cache.encode(texts, cache_key="test_key")
        
        assert cache.cache_misses == 1
        assert cache.cache_hits == 0
        mock_provider.encode.assert_called_once_with(texts)

    def test_cache_hit_returns_cached(self, temp_cache_dir):
        """Test cache hit returns cached embeddings."""
        mock_provider = MagicMock(spec=EmbeddingProvider)
        expected_embeddings = np.random.randn(2, 384).astype(np.float32)
        mock_provider.encode.return_value = expected_embeddings
        
        cache = CachedEmbeddingProvider(mock_provider, cache_dir=temp_cache_dir)
        texts = ["Hello", "World"]
        
        # First call - cache miss
        embeddings1 = cache.encode(texts, cache_key="test_key")
        assert cache.cache_misses == 1
        
        # Second call - cache hit
        embeddings2 = cache.encode(texts, cache_key="test_key")
        assert cache.cache_hits == 1
        assert mock_provider.encode.call_count == 1  # Only called once
        np.testing.assert_array_almost_equal(embeddings1, embeddings2)

    def test_different_cache_keys_separate_entries(self, temp_cache_dir):
        """Test different cache keys create separate entries."""
        mock_provider = MagicMock(spec=EmbeddingProvider)
        mock_provider.encode.return_value = np.random.randn(2, 384).astype(np.float32)
        
        cache = CachedEmbeddingProvider(mock_provider, cache_dir=temp_cache_dir)
        texts = ["Hello", "World"]
        
        cache.encode(texts, cache_key="key1")
        cache.encode(texts, cache_key="key2")
        
        # Both should be cache misses
        assert cache.cache_misses == 2
        assert cache.cache_hits == 0

    def test_encode_without_cache_key_no_caching(self, temp_cache_dir):
        """Test encoding without cache key bypasses cache."""
        mock_provider = MagicMock(spec=EmbeddingProvider)
        mock_provider.encode.return_value = np.random.randn(2, 384).astype(np.float32)
        
        cache = CachedEmbeddingProvider(mock_provider, cache_dir=temp_cache_dir)
        texts = ["Hello", "World"]
        
        cache.encode(texts)
        cache.encode(texts)
        
        # Should call provider both times
        assert mock_provider.encode.call_count == 2

    def test_get_dimension_delegates_to_provider(self, temp_cache_dir):
        """Test get_dimension delegates to underlying provider."""
        mock_provider = MagicMock(spec=EmbeddingProvider)
        mock_provider.get_dimension.return_value = 768
        
        cache = CachedEmbeddingProvider(mock_provider, cache_dir=temp_cache_dir)
        dimension = cache.get_dimension()
        
        assert dimension == 768
        mock_provider.get_dimension.assert_called_once()

    def test_cache_stats_tracking(self, temp_cache_dir):
        """Test cache hit/miss statistics tracking."""
        mock_provider = MagicMock(spec=EmbeddingProvider)
        mock_provider.encode.return_value = np.random.randn(2, 384).astype(np.float32)
        
        cache = CachedEmbeddingProvider(mock_provider, cache_dir=temp_cache_dir)
        
        # Three cache misses
        cache.encode(["text1"], cache_key="key1")
        cache.encode(["text2"], cache_key="key2")
        cache.encode(["text3"], cache_key="key3")
        
        # Two cache hits
        cache.encode(["text1"], cache_key="key1")
        cache.encode(["text2"], cache_key="key2")
        
        assert cache.cache_misses == 3
        assert cache.cache_hits == 2
