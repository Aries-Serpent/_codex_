"""
Tests for RAG Embeddings Module
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

# Skip tests if dependencies not available
pytest.importorskip("sentence_transformers")

# Check if openai is available
try:
    import openai  # noqa: F401
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from codex.rag.embeddings import (
    CachedEmbeddingProvider,
    LocalSentenceTransformerProvider,
    OpenAIEmbeddingProvider,
    create_embedding_provider,
)


class TestLocalSentenceTransformerProvider:
    """Tests for LocalSentenceTransformerProvider"""

    def test_initialization(self):
        """Test provider initialization"""
        provider = LocalSentenceTransformerProvider(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        assert provider is not None
        assert provider.model is not None
        assert provider.model_name == "sentence-transformers/all-MiniLM-L6-v2"

    def test_encode_basic(self):
        """Test basic encoding"""
        provider = LocalSentenceTransformerProvider()
        
        texts = ["Hello world", "Test sentence"]
        embeddings = provider.encode(texts)
        
        assert isinstance(embeddings, np.ndarray)
        assert len(embeddings) == 2
        assert embeddings.shape[1] > 0

    def test_encode_single_text(self):
        """Test encoding single text"""
        provider = LocalSentenceTransformerProvider()
        
        embeddings = provider.encode(["Single text"])
        
        assert len(embeddings) == 1
        assert embeddings.shape[1] > 0

    def test_encode_empty_list(self):
        """Test encoding empty list"""
        provider = LocalSentenceTransformerProvider()
        
        embeddings = provider.encode([])
        
        assert isinstance(embeddings, np.ndarray)
        assert len(embeddings) == 0

    def test_get_dimension(self):
        """Test getting embedding dimension"""
        provider = LocalSentenceTransformerProvider()
        
        dim = provider.get_dimension()
        
        assert isinstance(dim, int)
        assert dim > 0
        # all-MiniLM-L6-v2 has 384 dimensions
        assert dim == 384

    def test_encode_with_batch_size(self):
        """Test encoding with custom batch size"""
        provider = LocalSentenceTransformerProvider()
        
        texts = [f"Text {i}" for i in range(10)]
        embeddings = provider.encode(texts, batch_size=2)
        
        assert len(embeddings) == 10

    def test_custom_cache_dir(self):
        """Test with custom cache directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            provider = LocalSentenceTransformerProvider(
                cache_dir=tmpdir
            )
            
            assert provider.cache_dir == tmpdir


@pytest.mark.skipif(not OPENAI_AVAILABLE, reason="OpenAI package not installed")
class TestOpenAIEmbeddingProvider:
    """Tests for OpenAIEmbeddingProvider"""

    def test_initialization_with_api_key(self):
        """Test initialization with API key"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            provider = OpenAIEmbeddingProvider(api_key="test-key")
            
            assert provider is not None
            assert provider.model_name == "text-embedding-3-small"

    def test_initialization_from_env(self):
        """Test initialization from environment variable"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"}):
            provider = OpenAIEmbeddingProvider()
            
            assert provider.api_key == "env-key"

    def test_initialization_without_key(self):
        """Test initialization without API key raises error"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="API key not provided"):
                OpenAIEmbeddingProvider()

    def test_get_dimension(self):
        """Test getting embedding dimensions for different models"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            provider_small = OpenAIEmbeddingProvider(
                model_name="text-embedding-3-small"
            )
            assert provider_small.get_dimension() == 1536
            
            provider_large = OpenAIEmbeddingProvider(
                model_name="text-embedding-3-large"
            )
            assert provider_large.get_dimension() == 3072
            
            provider_ada = OpenAIEmbeddingProvider(
                model_name="text-embedding-ada-002"
            )
            assert provider_ada.get_dimension() == 1536

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
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            provider = OpenAIEmbeddingProvider()
            embeddings = provider.encode(["text1", "text2"])
            
            assert isinstance(embeddings, np.ndarray)
            assert len(embeddings) == 2
            assert embeddings.shape[1] == 1536

    @patch("codex.rag.embeddings.OpenAI")
    def test_encode_with_batch_size(self, mock_openai):
        """Test encoding with batch processing"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            provider = OpenAIEmbeddingProvider()
            texts = [f"text{i}" for i in range(5)]
            _ = provider.encode(texts, batch_size=2)
            
            # Should make multiple API calls
            assert mock_client.embeddings.create.call_count >= 2

    def test_destructor_clears_key(self):
        """Test that destructor clears API key"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            provider = OpenAIEmbeddingProvider()
            assert provider.api_key is not None
            
            # Trigger destructor via deletion
            del provider


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
            cached = CachedEmbeddingProvider(
                provider=mock_provider,
                cache_dir=tmpdir
            )
            
            assert cached is not None
            assert Path(tmpdir).exists()

    def test_cache_miss_and_hit(self, mock_provider):
        """Test cache miss followed by cache hit"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cached = CachedEmbeddingProvider(
                provider=mock_provider,
                cache_dir=tmpdir
            )
            
            texts = ["text1", "text2"]
            cache_key = "test_key"
            
            # First call: cache miss
            embeddings1 = cached.encode(texts, cache_key=cache_key)
            assert mock_provider.encode.call_count == 1
            assert cached.cache_misses == 1
            assert cached.cache_hits == 0
            
            # Second call: cache hit
            embeddings2 = cached.encode(texts, cache_key=cache_key)
            assert mock_provider.encode.call_count == 1  # Not called again
            assert cached.cache_misses == 1
            assert cached.cache_hits == 1
            
            # Results should be identical
            np.testing.assert_array_equal(embeddings1, embeddings2)

    def test_cache_with_auto_key(self, mock_provider):
        """Test caching with auto-generated key"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cached = CachedEmbeddingProvider(
                provider=mock_provider,
                cache_dir=tmpdir
            )
            
            texts = ["text1", "text2"]
            
            # Without explicit cache_key
            _ = cached.encode(texts)
            _ = cached.encode(texts)
            
            # Should use same auto-generated key
            assert cached.cache_hits == 1

    def test_cache_invalidation_with_metadata(self, mock_provider):
        """Test cache invalidation based on metadata"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cached = CachedEmbeddingProvider(
                provider=mock_provider,
                cache_dir=tmpdir
            )
            
            texts = ["text1"]
            cache_key = "meta_test"
            
            # First call with mtime1
            _ = cached.encode(
                texts,
                cache_key=cache_key,
                metadata={"file_mtime": 1000}
            )
            assert cached.cache_misses == 1
            
            # Second call with same mtime: cache hit
            _ = cached.encode(
                texts,
                cache_key=cache_key,
                metadata={"file_mtime": 1000}
            )
            assert cached.cache_hits == 1
            
            # Third call with different mtime: cache miss
            _ = cached.encode(
                texts,
                cache_key=cache_key,
                metadata={"file_mtime": 2000}
            )
            assert cached.cache_misses == 2

    def test_get_dimension(self, mock_provider):
        """Test getting dimension from cached provider"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cached = CachedEmbeddingProvider(
                provider=mock_provider,
                cache_dir=tmpdir
            )
            
            dim = cached.get_dimension()
            assert dim == 384
            mock_provider.get_dimension.assert_called_once()

    def test_get_stats(self, mock_provider):
        """Test getting cache statistics"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cached = CachedEmbeddingProvider(
                provider=mock_provider,
                cache_dir=tmpdir
            )
            
            # Make some calls
            cached.encode(["text1"], cache_key="key1")
            cached.encode(["text2"], cache_key="key2")
            cached.encode(["text1"], cache_key="key1")  # Hit
            
            stats = cached.get_stats()
            
            assert stats["cache_hits"] == 1
            assert stats["cache_misses"] == 2
            assert stats["total_requests"] == 3
            assert stats["hit_rate"] == 1/3
            assert "cache_dir" in stats

    def test_clear_cache(self, mock_provider):
        """Test clearing cache"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cached = CachedEmbeddingProvider(
                provider=mock_provider,
                cache_dir=tmpdir
            )
            
            # Create cache entries
            cached.encode(["text1"], cache_key="key1")
            cached.encode(["text2"], cache_key="key2")
            
            assert cached.cache_misses == 2
            
            # Clear cache
            cached.clear_cache()
            
            assert cached.cache_hits == 0
            assert cached.cache_misses == 0
            assert Path(tmpdir).exists()

    def test_cache_with_corrupted_file(self, mock_provider):
        """Test handling of corrupted cache file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cached = CachedEmbeddingProvider(
                provider=mock_provider,
                cache_dir=tmpdir
            )
            
            # Create cache
            cached.encode(["text1"], cache_key="test")
            
            # Corrupt the cache file
            cache_file = Path(tmpdir) / "test.npz"
            with open(cache_file, "w") as f:
                f.write("corrupted data")
            
            # Should handle corruption and regenerate
            embeddings = cached.encode(["text1"], cache_key="test")
            assert embeddings is not None


class TestCreateEmbeddingProvider:
    """Tests for create_embedding_provider factory function"""

    def test_create_local_provider(self):
        """Test creating local provider"""
        provider = create_embedding_provider(provider_type="local")
        
        assert isinstance(provider, CachedEmbeddingProvider)
        assert hasattr(provider, "provider")

    def test_create_local_without_cache(self):
        """Test creating local provider without cache"""
        provider = create_embedding_provider(
            provider_type="local",
            use_cache=False
        )
        
        assert isinstance(provider, LocalSentenceTransformerProvider)

    def test_create_local_with_custom_model(self):
        """Test creating local provider with custom model"""
        provider = create_embedding_provider(
            provider_type="local",
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            use_cache=False
        )
        
        assert provider.model_name == "sentence-transformers/all-MiniLM-L6-v2"

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_create_openai_provider(self):
        """Test creating OpenAI provider"""
        provider = create_embedding_provider(
            provider_type="openai",
            use_cache=False
        )
        
        assert isinstance(provider, OpenAIEmbeddingProvider)

    def test_create_openai_without_key_raises(self):
        """Test creating OpenAI provider without key raises error"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="API key required"):
                create_embedding_provider(provider_type="openai")

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_create_openai_with_cache(self):
        """Test creating OpenAI provider with cache"""
        with tempfile.TemporaryDirectory() as tmpdir:
            provider = create_embedding_provider(
                provider_type="openai",
                use_cache=True,
                cache_dir=tmpdir
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
                provider_type="local",
                use_cache=True,
                cache_dir=tmpdir
            )
            
            assert isinstance(provider, CachedEmbeddingProvider)
            assert str(tmpdir) in str(provider.cache_dir)


class TestEmbeddingsIntegration:
    """Integration tests for embeddings module"""

    def test_full_workflow_local_with_cache(self):
        """Test complete workflow with local provider and caching"""
        with tempfile.TemporaryDirectory() as tmpdir:
            provider = create_embedding_provider(
                provider_type="local",
                use_cache=True,
                cache_dir=tmpdir
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
            assert stats["cache_hits"] == 1
            assert stats["cache_misses"] == 1

    def test_different_texts_different_embeddings(self):
        """Test that different texts produce different embeddings"""
        provider = create_embedding_provider(
            provider_type="local",
            use_cache=False
        )
        
        emb1 = provider.encode(["Python programming"])
        emb2 = provider.encode(["Cooking recipes"])
        
        # Should be different
        assert not np.allclose(emb1, emb2)

    def test_similar_texts_similar_embeddings(self):
        """Test that similar texts produce similar embeddings"""
        provider = create_embedding_provider(
            provider_type="local",
            use_cache=False
        )
        
        emb1 = provider.encode(["Python is a programming language"])
        emb2 = provider.encode(["Python is a coding language"])
        
        # Calculate cosine similarity
        similarity = np.dot(emb1[0], emb2[0]) / (
            np.linalg.norm(emb1[0]) * np.linalg.norm(emb2[0])
        )
        
        # Should be quite similar
        assert similarity > 0.8
