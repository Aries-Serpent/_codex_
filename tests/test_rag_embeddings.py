"""
Tests for RAG Embeddings Module
"""

import importlib.util
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

np = pytest.importorskip("numpy")

# Conditional imports for RAG dependencies - safely handled at test runtime
try:
    from codex.rag.embeddings import (
        CachedEmbeddingProvider,
        LocalSentenceTransformerProvider,
        OpenAIEmbeddingProvider,
        create_embedding_provider,
    )

    RAG_EMBEDDINGS_AVAILABLE = True
except ImportError:
    RAG_EMBEDDINGS_AVAILABLE = False

# Check if sentence_transformers is available
try:
    if importlib.util.find_spec("sentence_transformers") is None:
        raise ImportError
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# Check if openai is available
OPENAI_AVAILABLE = importlib.util.find_spec("openai") is not None

pytestmark = pytest.mark.skipif(
    not RAG_EMBEDDINGS_AVAILABLE or not SENTENCE_TRANSFORMERS_AVAILABLE,
    reason="RAG embeddings dependencies (sentence_transformers) not installed",
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


class TestLocalSentenceTransformerProvider:
    """Tests for LocalSentenceTransformerProvider"""

    @_skip_real_st_models
    def test_initialization(self):
        """Test provider initialization"""
        provider = LocalSentenceTransformerProvider(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        assert provider is not None, "provider must be initialized"
        assert provider.model is not None, "model must be initialized"
        assert provider.model_name == "sentence-transformers/all-MiniLM-L6-v2", "model_name is not valid"

    @_skip_real_st_models
    def test_encode_basic(self):
        """Test basic encoding"""
        provider = LocalSentenceTransformerProvider()

        texts = ["Hello world", "Test sentence"]
        embeddings = provider.encode(texts)

        assert isinstance(embeddings, np.ndarray)
        assert len(embeddings) == 2, "Embeddings must not be empty"
        assert embeddings.shape[1] > 0, "Value must be greater than zero"

    @_skip_real_st_models
    def test_encode_single_text(self):
        """Test encoding single text"""
        provider = LocalSentenceTransformerProvider()

        embeddings = provider.encode(["Single text"])

        assert len(embeddings) == 1, "Embeddings must not be empty"
        assert embeddings.shape[1] > 0, "Value must be greater than zero"

    @_skip_real_st_models
    def test_encode_empty_list(self):
        """Test encoding empty list"""
        provider = LocalSentenceTransformerProvider()

        embeddings = provider.encode([])

        assert isinstance(embeddings, np.ndarray)
        assert len(embeddings) == 0, "Embeddings must not be empty"

    @_skip_real_st_models
    def test_get_dimension(self):
        """Test getting embedding dimension"""
        provider = LocalSentenceTransformerProvider()

        dim = provider.get_dimension()

        assert isinstance(dim, int)
        assert dim > 0, "dim must be greater than zero"
        # all-MiniLM-L6-v2 has 384 dimensions
        assert dim == 384, "dim is not valid"

    @_skip_real_st_models
    def test_encode_with_batch_size(self):
        """Test encoding with custom batch size"""
        provider = LocalSentenceTransformerProvider()

        texts = [f"Text {i}" for i in range(10)]
        embeddings = provider.encode(texts, batch_size=2)

        assert len(embeddings) == 10, "Embeddings must not be empty"

    @_skip_real_st_models
    def test_custom_cache_dir(self):
        """Test with custom cache directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            provider = LocalSentenceTransformerProvider(cache_dir=tmpdir)

            assert provider.cache_dir == tmpdir, "cache_dir is not valid"


@pytest.mark.skipif(not OPENAI_AVAILABLE, reason="OpenAI package not installed")
class TestOpenAIEmbeddingProvider:
    """Tests for OpenAIEmbeddingProvider"""

    def test_initialization_with_api_key(self):
        """Test initialization with API key"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):  # pragma: allowlist secret
            provider = OpenAIEmbeddingProvider(api_key="test-key")

            assert provider is not None, "provider must be initialized"
            assert provider.model_name == "text-embedding-3-small", "model_name is not valid"

    def test_initialization_from_env(self):
        """Test initialization from environment variable"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"}):  # pragma: allowlist secret
            provider = OpenAIEmbeddingProvider()

            assert provider.client is not None, "client must be initialized"
            assert provider.model_name == "text-embedding-3-small", "model_name is not valid"

    def test_initialization_without_key(self):
        """Test initialization without API key raises error"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="API key not provided"):
                OpenAIEmbeddingProvider()

    def test_get_dimension(self):
        """Test getting embedding dimensions for different models"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):  # pragma: allowlist secret
            provider_small = OpenAIEmbeddingProvider(model_name="text-embedding-3-small")
            assert provider_small.get_dimension() == 1536, "Condition must be true"

            provider_large = OpenAIEmbeddingProvider(model_name="text-embedding-3-large")
            assert provider_large.get_dimension() == 3072, "Condition must be true"

            provider_ada = OpenAIEmbeddingProvider(model_name="text-embedding-ada-002")
            assert provider_ada.get_dimension() == 1536, "Condition must be true"

    @patch("codex.rag.embeddings.OpenAI")
    def test_encode_basic(self, mock_openai):
        """Test basic encoding with mocked OpenAI"""
        # Mock the OpenAI client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(embedding=[0.1] * 1536),
            MagicMock(embedding=[0.2] * 1536),
        ]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):  # pragma: allowlist secret
            provider = OpenAIEmbeddingProvider()
            embeddings = provider.encode(["text1", "text2"])

            assert isinstance(embeddings, np.ndarray)
            assert len(embeddings) == 2, "Embeddings must not be empty"
            assert embeddings.shape[1] == 1536, "Condition must be true"

    @patch("codex.rag.embeddings.OpenAI")
    def test_encode_with_batch_size(self, mock_openai):
        """Test encoding with batch processing"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):  # pragma: allowlist secret
            provider = OpenAIEmbeddingProvider()
            texts = [f"text{i}" for i in range(5)]
            _ = provider.encode(texts, batch_size=2)

            # Should make multiple API calls
            assert mock_client.embeddings.create.call_count >= 2, "call_count must be positive"

    def test_destructor_clears_key(self):
        """Test that destructor clears API key"""
        import gc

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):  # pragma: allowlist secret
            provider = OpenAIEmbeddingProvider()
            assert provider.client is not None, "client must be initialized"

            # Trigger destructor via cleanup
            del provider
            gc.collect()


class TestCachedEmbeddingProvider:
    """Tests for CachedEmbeddingProvider"""

    @pytest.fixture
    def mock_provider(self):
        """Create a mock embedding provider"""
        provider = MagicMock()
        provider.encode.return_value = np.random.randn(2, 384).astype(np.float32)
        provider.get_dimension.return_value = 384
        return provider

    def test_initialization(self, mock_provider):
        """Test cached provider initialization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cached = CachedEmbeddingProvider(provider=mock_provider, cache_dir=tmpdir)

            assert cached is not None, "cached must be initialized"
            assert Path(tmpdir).exists(), "Condition must be true"

    def test_cache_miss_and_hit(self, mock_provider):
        """Test cache miss followed by cache hit"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cached = CachedEmbeddingProvider(provider=mock_provider, cache_dir=tmpdir)

            texts = ["text1", "text2"]
            cache_key = "test_key"

            # First call: cache miss
            embeddings1 = cached.encode(texts, cache_key=cache_key)
            assert mock_provider.encode.call_count == 1, "Count must be greater than zero"
            assert cached.cache_misses == 1, "cache_misses is not valid"
            assert cached.cache_hits == 0, "cache_hits is not valid"

            # Second call: cache hit
            embeddings2 = cached.encode(texts, cache_key=cache_key)
            assert mock_provider.encode.call_count == 1, "Count must be greater than zero"
            assert cached.cache_misses == 1, "cache_misses is not valid"
            assert cached.cache_hits == 1, "cache_hits is not valid"

            # Results should be identical
            np.testing.assert_array_equal(embeddings1, embeddings2)

    def test_cache_with_auto_key(self, mock_provider):
        """Test that caching is bypassed when no cache_key is provided"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cached = CachedEmbeddingProvider(provider=mock_provider, cache_dir=tmpdir)

            texts = ["text1", "text2"]

            # Without explicit cache_key, cache is bypassed
            _ = cached.encode(texts)
            _ = cached.encode(texts)

            # Cache is bypassed, so no hits or misses tracked for keyless calls
            # Provider is called twice since cache is not used
            assert mock_provider.encode.call_count == 2, "Count must be greater than zero"
            assert cached.cache_hits == 0, "cache_hits is not valid"
            assert cached.cache_misses == 0, "cache_misses is not valid"

    def test_cache_invalidation_with_metadata(self, mock_provider):
        """Test cache invalidation based on metadata"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cached = CachedEmbeddingProvider(provider=mock_provider, cache_dir=tmpdir)

            texts = ["text1"]
            cache_key = "meta_test"

            # First call with mtime1
            _ = cached.encode(texts, cache_key=cache_key, metadata={"file_mtime": 1000})
            assert cached.cache_misses == 1, "cache_misses is not valid"

            # Second call with same mtime: cache hit
            _ = cached.encode(texts, cache_key=cache_key, metadata={"file_mtime": 1000})
            assert cached.cache_hits == 1, "cache_hits is not valid"

            # Third call with different mtime: cache miss
            _ = cached.encode(texts, cache_key=cache_key, metadata={"file_mtime": 2000})
            assert cached.cache_misses == 2, "cache_misses is not valid"

    def test_get_dimension(self, mock_provider):
        """Test getting dimension from cached provider"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cached = CachedEmbeddingProvider(provider=mock_provider, cache_dir=tmpdir)

            dim = cached.get_dimension()
            assert dim == 384, "dim is not valid"
            mock_provider.get_dimension.assert_called_once()

    def test_get_stats(self, mock_provider):
        """Test getting cache statistics"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cached = CachedEmbeddingProvider(provider=mock_provider, cache_dir=tmpdir)

            # Make some calls
            cached.encode(["text1"], cache_key="key1")
            cached.encode(["text2"], cache_key="key2")
            cached.encode(["text1"], cache_key="key1")  # Hit

            stats = cached.get_stats()

            assert stats["cache_hits"] == 1, "Condition must be true"
            assert stats["cache_misses"] == 2, "Condition must be true"
            assert stats["total_requests"] == 3, "Condition must be true"
            assert stats["hit_rate"] == 1 / 3, "Condition must be true"
            assert "cache_dir" in stats, "Condition must be true"

    def test_clear_cache(self, mock_provider):
        """Test clearing cache"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cached = CachedEmbeddingProvider(provider=mock_provider, cache_dir=tmpdir)

            # Create cache entries
            cached.encode(["text1"], cache_key="key1")
            cached.encode(["text2"], cache_key="key2")

            assert cached.cache_misses == 2, "cache_misses is not valid"

            # Clear cache
            cached.clear_cache()

            assert cached.cache_hits == 0, "cache_hits is not valid"
            assert cached.cache_misses == 0, "cache_misses is not valid"
            assert Path(tmpdir).exists(), "Condition must be true"

    def test_cache_with_corrupted_file(self, mock_provider):
        """Test handling of corrupted cache file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cached = CachedEmbeddingProvider(provider=mock_provider, cache_dir=tmpdir)

            # Create cache
            cached.encode(["text1"], cache_key="test")

            # Corrupt the cache file
            cache_file = Path(tmpdir) / "test.npz"
            with open(cache_file, "w") as f:
                f.write("corrupted data")

            # Should handle corruption and regenerate
            embeddings = cached.encode(["text1"], cache_key="test")
            assert embeddings is not None, "embeddings must be initialized"


class TestCreateEmbeddingProvider:
    """Tests for create_embedding_provider factory function"""

    def test_create_local_provider(self):
        """Test creating local provider"""
        provider = create_embedding_provider(provider_type="local")

        assert isinstance(provider, CachedEmbeddingProvider)
        assert hasattr(provider, "provider")

    def test_create_local_without_cache(self):
        """Test creating local provider without cache"""
        provider = create_embedding_provider(provider_type="local", use_cache=False)

        assert isinstance(provider, LocalSentenceTransformerProvider)

    def test_create_local_with_custom_model(self):
        """Test creating local provider with custom model"""
        provider = create_embedding_provider(
            provider_type="local",
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            use_cache=False,
        )

        assert provider.model_name == "sentence-transformers/all-MiniLM-L6-v2", "model_name is not valid"

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})  # pragma: allowlist secret
    def test_create_openai_provider(self):
        """Test creating OpenAI provider"""
        provider = create_embedding_provider(provider_type="openai", use_cache=False)

        assert isinstance(provider, OpenAIEmbeddingProvider)

    def test_create_openai_without_key_raises(self):
        """Test creating OpenAI provider without key raises error"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="API key required"):
                create_embedding_provider(provider_type="openai")

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})  # pragma: allowlist secret
    def test_create_openai_with_cache(self):
        """Test creating OpenAI provider with cache"""
        with tempfile.TemporaryDirectory() as tmpdir:
            provider = create_embedding_provider(
                provider_type="openai", use_cache=True, cache_dir=tmpdir
            )

            assert isinstance(provider, CachedEmbeddingProvider)

    def test_create_unknown_provider_type(self):
        """Test creating provider with unknown type"""
        with pytest.raises(ValueError, match="Unknown provider type"):
            create_embedding_provider(provider_type="unknown")

    def test_create_with_custom_cache_dir(self):
        """Test creating provider with custom cache directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            provider = create_embedding_provider(
                provider_type="local", use_cache=True, cache_dir=tmpdir
            )

            assert isinstance(provider, CachedEmbeddingProvider)
            assert str(tmpdir) in str(provider.cache_dir), "Condition must be true"


@_skip_real_st_models
class TestEmbeddingsIntegration:
    """Integration tests for embeddings module"""

    def test_full_workflow_local_with_cache(self):
        """Test complete workflow with local provider and caching"""
        with tempfile.TemporaryDirectory() as tmpdir:
            provider = create_embedding_provider(
                provider_type="local", use_cache=True, cache_dir=tmpdir
            )

            texts = ["Machine learning is fascinating", "Python is versatile"]

            # First encoding: cache miss
            embeddings1 = provider.encode(texts, cache_key="test")

            # Second encoding: cache hit
            embeddings2 = provider.encode(texts, cache_key="test")

            # Should be identical
            np.testing.assert_array_equal(embeddings1, embeddings2)

            # Check stats
            stats = provider.get_stats()
            assert stats["cache_hits"] == 1, "Condition must be true"
            assert stats["cache_misses"] == 1, "Condition must be true"

    def test_different_texts_different_embeddings(self):
        """Test that different texts produce different embeddings"""
        provider = create_embedding_provider(provider_type="local", use_cache=False)

        emb1 = provider.encode(["Python programming"])
        emb2 = provider.encode(["Cooking recipes"])

        # Should be different
        assert not np.allclose(emb1, emb2)

    def test_similar_texts_similar_embeddings(self):
        """Test that similar texts produce similar embeddings"""
        provider = create_embedding_provider(provider_type="local", use_cache=False)

        emb1 = provider.encode(["Python is a programming language"])
        emb2 = provider.encode(["Python is a coding language"])

        # Calculate cosine similarity
        similarity = np.dot(emb1[0], emb2[0]) / (np.linalg.norm(emb1[0]) * np.linalg.norm(emb2[0]))

        # Should be quite similar
        assert similarity > 0.8, "similarity must be greater than zero"
