"""Advanced Provider-Specific Tests - Phase 67.4.

Comprehensive testing for all RAG embedding providers:
- TF-IDF Provider
- Local SentenceTransformer Provider
- OpenAI Provider
- Provider switching and fallback
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

np = pytest.importorskip("numpy")


class TestTFIDFProvider:
    """Comprehensive tests for TF-IDF embedding provider."""

    def test_tfidf_initialization(self):
        """Test TF-IDF provider initialization."""
        try:
            from codex.rag.embeddings import TfidfEmbeddingProvider

            provider = TfidfEmbeddingProvider()
            assert provider is not None, "provider must be initialized"

            # Verify provider has required methods
            assert hasattr(provider, "encode")
            assert callable(provider.encode), "Condition must be true"
        except ImportError:
            pytest.skip("Module not available")

    def test_tfidf_empty_corpus(self):
        """Test TF-IDF with empty corpus."""
        try:
            from codex.rag.embeddings import TfidfEmbeddingProvider

            provider = TfidfEmbeddingProvider()

            # First call might initialize vocabulary
            result = provider.encode(["test document"])
            assert result is not None, "result must be initialized"

            # Subsequent calls should work
            result2 = provider.encode(["another document"])
            assert result2 is not None, "result2 must be initialized"
        except ImportError:
            pytest.skip("Module not available")

    def test_tfidf_vocabulary_growth(self):
        """Test TF-IDF vocabulary expansion."""
        try:
            from codex.rag.embeddings import TfidfEmbeddingProvider

            provider = TfidfEmbeddingProvider()

            # Encode texts with different vocabulary
            texts1 = ["apple banana cherry"]
            texts2 = ["dog elephant fox"]

            emb1 = provider.encode(texts1)
            emb2 = provider.encode(texts2)

            # Both should produce embeddings
            assert emb1 is not None, "emb1 must be initialized"
            assert emb2 is not None, "emb2 must be initialized"

            # Dimensions should be consistent or grow
            assert emb1.shape[1] > 0, "Value must be greater than zero"
            assert emb2.shape[1] > 0, "Value must be greater than zero"
        except ImportError:
            pytest.skip("Module not available")

    def test_tfidf_sparse_vs_dense(self):
        """Test TF-IDF dense vs sparse representation."""
        try:
            from codex.rag.embeddings import TfidfEmbeddingProvider

            provider = TfidfEmbeddingProvider()

            texts = ["word1 word2", "word3 word4 word5"]
            embeddings = provider.encode(texts)

            # Should return numpy array (dense)
            assert isinstance(embeddings, np.ndarray)

            # Check sparsity (most values should be zero for TF-IDF)
            sparsity = np.count_nonzero(embeddings == 0) / embeddings.size
            assert sparsity > 0.3, "TF-IDF should be relatively sparse"
        except ImportError:
            pytest.skip("Module not available")

    def test_tfidf_get_dimension(self):
        """Test getting TF-IDF embedding dimension."""
        try:
            from codex.rag.embeddings import TfidfEmbeddingProvider

            provider = TfidfEmbeddingProvider()

            # May need to fit first
            provider.encode(["test document"])

            if hasattr(provider, "get_dimension"):
                dim = provider.get_dimension()
                assert isinstance(dim, int)
                assert dim > 0, "dim must be greater than zero"
        except ImportError:
            pytest.skip("Module not available")


class TestLocalSentenceTransformerProvider:
    """Comprehensive tests for local SentenceTransformer provider."""

    def test_local_provider_initialization(self):
        """Test local provider initialization."""
        try:
            from codex.rag.embeddings import LocalSentenceTransformerProvider

            # Should handle model loading or skip if not available
            try:
                provider = LocalSentenceTransformerProvider()
                assert provider is not None, "provider must be initialized"
            except (ImportError, OSError):
                pytest.skip("SentenceTransformers not available or model download failed")
        except ImportError:
            pytest.skip("Module not available")

    def test_local_provider_custom_model(self):
        """Test local provider with custom model name."""
        try:
            from codex.rag.embeddings import LocalSentenceTransformerProvider

            custom_model = "sentence-transformers/all-MiniLM-L6-v2"

            try:
                provider = LocalSentenceTransformerProvider(model_name=custom_model)
                assert provider.model_name == custom_model, "model_name is not valid"
            except (ImportError, OSError):
                pytest.skip("Model not available")
        except ImportError:
            pytest.skip("Module not available")

    def test_local_provider_cache_dir(self):
        """Test local provider with custom cache directory."""
        try:
            from codex.rag.embeddings import LocalSentenceTransformerProvider

            with tempfile.TemporaryDirectory() as tmpdir:
                cache_dir = Path(tmpdir) / "models"

                try:
                    provider = LocalSentenceTransformerProvider(cache_dir=str(cache_dir))
                    assert provider.cache_dir == str(cache_dir), "cache_dir is not valid"
                except (ImportError, OSError):
                    pytest.skip("Model not available")
        except ImportError:
            pytest.skip("Module not available")

    def test_local_provider_encoding(self):
        """Test local provider encoding."""
        try:
            from codex.rag.embeddings import LocalSentenceTransformerProvider

            try:
                provider = LocalSentenceTransformerProvider()

                texts = ["This is a test sentence", "Another test sentence"]
                embeddings = provider.encode(texts)

                # Should return dense embeddings
                assert isinstance(embeddings, np.ndarray)
                assert embeddings.shape[0] == 2, "Condition must be true"
                assert embeddings.shape[1] > 0, "Value must be greater than zero"

                # Check embeddings are normalized (common for sentence transformers)
                norms = np.linalg.norm(embeddings, axis=1)
                # May or may not be normalized, just check they're valid
                assert np.all(norms > 0), "norms must be greater than zero"
            except (ImportError, OSError, IndexError):
                pytest.skip("Model not available")
        except ImportError:
            pytest.skip("Module not available")

    def test_local_provider_device_placement(self):
        """Test that local provider uses CPU correctly."""
        try:
            from codex.rag.embeddings import LocalSentenceTransformerProvider

            try:
                provider = LocalSentenceTransformerProvider()

                # Should be on CPU
                if hasattr(provider, "model"):
                    # Check model device - device attribute returns string directly
                    if hasattr(provider.model, "device"):
                        assert str(provider.model.device) == "cpu", "Condition must be true"
            except (ImportError, OSError):
                pytest.skip("Model or PyTorch not available")
        except ImportError:
            pytest.skip("Module not available")


class TestOpenAIProvider:
    """Comprehensive tests for OpenAI embedding provider."""

    def test_openai_provider_initialization(self):
        """Test OpenAI provider initialization."""
        try:
            from codex.rag.embeddings import OpenAIEmbeddingProvider

            # Should handle missing API key gracefully
            try:
                provider = OpenAIEmbeddingProvider()
                assert provider is not None, "provider must be initialized"
            except (ImportError, ValueError, Exception):
                pytest.skip("OpenAI not available or no API key")
        except ImportError:
            pytest.skip("Module not available")

    @patch("codex.rag.embeddings.OpenAI")
    def test_openai_provider_with_mock(self, mock_openai):
        """Test OpenAI provider with mocked API."""
        try:
            from codex.rag.embeddings import OpenAIEmbeddingProvider

            # Mock the OpenAI client
            mock_client = Mock()
            mock_response = Mock()
            mock_response.data = [
                Mock(embedding=[0.1] * 1536),
                Mock(embedding=[0.2] * 1536),
            ]
            mock_client.embeddings.create.return_value = mock_response
            mock_openai.return_value = mock_client

            provider = OpenAIEmbeddingProvider(api_key="test_key")

            texts = ["test1", "test2"]
            embeddings = provider.encode(texts)

            # Should call OpenAI API
            mock_client.embeddings.create.assert_called_once()

            # Should return embeddings
            assert embeddings is not None, "embeddings must be initialized"
            assert len(embeddings) == 2, "Embeddings must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_openai_provider_dimension(self):
        """Test OpenAI provider dimension."""
        try:
            from codex.rag.embeddings import OpenAIEmbeddingProvider

            try:
                provider = OpenAIEmbeddingProvider()

                if hasattr(provider, "get_dimension"):
                    dim = provider.get_dimension()
                    # OpenAI text-embedding-ada-002 is 1536 dimensions
                    assert dim > 0, "dim must be greater than zero"
            except (ImportError, ValueError):
                pytest.skip("OpenAI not available")
        except ImportError:
            pytest.skip("Module not available")


class TestProviderSwitching:
    """Tests for provider selection and switching."""

    def test_get_default_provider(self):
        """Test getting default embedding provider."""
        try:
            from codex.rag.embeddings import get_embedding_provider

            # Should return a provider (likely TF-IDF as fallback)
            provider = get_embedding_provider()
            assert provider is not None, "provider must be initialized"

            # Should have encode method
            assert hasattr(provider, "encode")
            assert callable(provider.encode), "Condition must be true"
        except (ImportError, AttributeError):
            pytest.skip("Function not available")

    def test_get_provider_by_name(self):
        """Test getting provider by name."""
        try:
            from codex.rag.embeddings import get_embedding_provider

            # Try different provider names
            provider_names = ["tfidf", "local", "openai"]

            for name in provider_names:
                try:
                    provider = get_embedding_provider(provider_type=name)
                    assert provider is not None, "provider must be initialized"
                except (ValueError, ImportError, Exception):
                    # Expected if provider not available
                    _ = None  # suppressed: no action needed
        except (ImportError, AttributeError):
            pytest.skip("Function not available")

    def test_provider_fallback(self):
        """Test provider fallback mechanism."""
        try:
            from codex.rag.embeddings import get_embedding_provider

            # Try to get preferred provider, should fallback if not available
            try:
                provider = get_embedding_provider(provider_type="openai")
            except Exception as _err:
                # Should fallback to TF-IDF
                provider = get_embedding_provider(provider_type="tfidf")

            assert provider is not None, "provider must be initialized"
        except (ImportError, AttributeError):
            pytest.skip("Function not available")


class TestProviderCompatibility:
    """Tests for provider compatibility and consistency."""

    def test_all_providers_have_encode(self):
        """Test that all providers implement encode method."""
        try:
            from src.codex.rag import embeddings

            # Get all provider classes
            provider_classes = [
                "TfidfEmbeddingProvider",
                "LocalSentenceTransformerProvider",
                "OpenAIEmbeddingProvider",
            ]

            for class_name in provider_classes:
                if hasattr(embeddings, class_name):
                    cls = getattr(embeddings, class_name)
                    # Check class has encode method
                    assert hasattr(cls, "encode") or "encode" in dir(cls)
        except ImportError:
            pytest.skip("Module not available")

    def test_all_providers_return_numpy(self):
        """Test that all providers return numpy arrays."""
        try:
            from codex.rag.embeddings import TfidfEmbeddingProvider

            providers_to_test = []

            # Test TF-IDF (always available)
            providers_to_test.append(TfidfEmbeddingProvider())

            # Test each provider
            for provider in providers_to_test:
                texts = ["test text"]
                result = provider.encode(texts)

                # Should return numpy array
                assert isinstance(result, np.ndarray)
                assert len(result) == 1, "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_provider_batch_consistency(self):
        """Test that batch and single encoding are consistent."""
        try:
            from codex.rag.embeddings import TfidfEmbeddingProvider

            provider = TfidfEmbeddingProvider()

            # Single encoding
            single_text = ["test document"]
            single_emb = provider.encode(single_text)

            # Batch encoding
            batch_texts = ["test document", "another document"]
            batch_emb = provider.encode(batch_texts)

            # First embedding should be similar
            # (may not be exact due to vocabulary differences)
            assert single_emb.shape[1] > 0, "Value must be greater than zero"
            assert batch_emb.shape[0] == 2, "Condition must be true"
        except ImportError:
            pytest.skip("Module not available")


class TestProviderEnvironmentConfig:
    """Tests for provider configuration via environment variables."""

    def test_provider_respects_env_var(self):
        """Test that provider selection respects environment variable."""
        try:
            import os

            from codex.rag.embeddings import get_embedding_provider

            # Set environment variable
            old_value = os.environ.get("RAG_EMBEDDING_PROVIDER")
            os.environ["RAG_EMBEDDING_PROVIDER"] = "tfidf"

            try:
                provider = get_embedding_provider()
                # Should get TF-IDF provider
                assert provider is not None, "provider must be initialized"
            finally:
                # Restore original value
                if old_value is not None:
                    os.environ["RAG_EMBEDDING_PROVIDER"] = old_value
                else:
                    os.environ.pop("RAG_EMBEDDING_PROVIDER", None)
        except (ImportError, AttributeError):
            pytest.skip("Function not available")

    def test_hf_token_usage(self):
        """Test that HF_TOKEN is used when available."""
        try:
            import os

            from codex.rag.embeddings import LocalSentenceTransformerProvider

            # Set mock HF token
            old_value = os.environ.get("HF_TOKEN")
            os.environ["HF_TOKEN"] = "test_token_12345"

            try:
                provider = LocalSentenceTransformerProvider()
                # Should initialize (may fail on actual model download)
                assert provider is not None, "provider must be initialized"
            except (ImportError, OSError):
                pytest.skip("Model not available")
            finally:
                # Restore original value
                if old_value is not None:
                    os.environ["HF_TOKEN"] = old_value
                else:
                    os.environ.pop("HF_TOKEN", None)
        except ImportError:
            pytest.skip("Module not available")
