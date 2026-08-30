"""Comprehensive tests for RAG embeddings module."""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("sentence_transformers")

from codex.rag.embeddings import (
    CachedEmbeddingProvider,
    EmbeddingModel,
    EmbeddingProvider,
    LocalSentenceTransformerProvider,
    OpenAIEmbeddingProvider,
    TfidfEmbeddingProvider,
    create_embedding_provider,
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
    # safe_model_to_device calls model.to() / model.to_empty() on SentenceTransformer
    # objects; ensure chained mock calls return the same configured mock so that
    # self.model.encode() and self.model.get_sentence_embedding_dimension() still
    # resolve to the return_value stubs set above.
    mock_model.to.return_value = mock_model
    mock_model.to_empty.return_value = mock_model
    mock_model.eval.return_value = mock_model
    return mock_model


class TestLocalSentenceTransformerProvider:
    """Test suite for LocalSentenceTransformerProvider."""

    def test_initialization_default_model(self, mock_sentence_transformer):
        """Test initialization with default model."""
        with patch(
            "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
        ):
            provider = LocalSentenceTransformerProvider()
            assert provider.model_name == "sentence-transformers/all-MiniLM-L6-v2", "model_name is not valid"
            assert provider.model is not None, "model must be initialized"

    def test_initialization_custom_model(self, mock_sentence_transformer):
        """Test initialization with custom model."""
        with patch(
            "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
        ):
            provider = LocalSentenceTransformerProvider(
                model_name="sentence-transformers/paraphrase-MiniLM-L6-v2"
            )
            assert provider.model_name == "sentence-transformers/paraphrase-MiniLM-L6-v2", "model_name is not valid"

    def test_initialization_with_cache_dir(self, mock_sentence_transformer, temp_cache_dir):
        """Test initialization with custom cache directory."""
        with patch(
            "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
        ):
            provider = LocalSentenceTransformerProvider(cache_dir=temp_cache_dir)
            assert provider.cache_dir == temp_cache_dir, "cache_dir is not valid"

    def test_encode_texts(self, mock_sentence_transformer):
        """Test encoding texts to embeddings."""
        with patch(
            "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
        ):
            provider = LocalSentenceTransformerProvider()
            texts = ["Hello world", "Test text", "Another example"]
            embeddings = provider.encode(texts)

            assert isinstance(embeddings, np.ndarray)
            assert embeddings.shape[0] == 3, "Condition must be true"
            mock_sentence_transformer.encode.assert_called_once()

    def test_encode_with_batch_size(self, mock_sentence_transformer):
        """Test encoding with custom batch size."""
        with patch(
            "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
        ):
            provider = LocalSentenceTransformerProvider()
            texts = ["Text 1", "Text 2", "Text 3"]
            provider.encode(texts, batch_size=2)

            call_kwargs = mock_sentence_transformer.encode.call_args[1]
            assert call_kwargs["batch_size"] == 2, "Condition must be true"

    def test_encode_with_progress(self, mock_sentence_transformer):
        """Test encoding with progress bar."""
        with patch(
            "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
        ):
            provider = LocalSentenceTransformerProvider()
            texts = ["Text 1", "Text 2"]
            provider.encode(texts, show_progress=True)

            call_kwargs = mock_sentence_transformer.encode.call_args[1]
            assert call_kwargs["show_progress_bar"] is True, "Condition must be true"

    def test_get_dimension(self, mock_sentence_transformer):
        """Test getting embedding dimension."""
        with patch(
            "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
        ):
            provider = LocalSentenceTransformerProvider()
            dimension = provider.get_dimension()
            assert dimension == 384, "dimension is not valid"

    def test_encode_without_model_raises_error(self):
        """Test encoding without loaded model raises error."""
        with patch(
            "sentence_transformers.SentenceTransformer", side_effect=ImportError("Not installed")
        ):
            with pytest.raises(ImportError):
                LocalSentenceTransformerProvider()

    def test_model_not_loaded_encode_error(self, mock_sentence_transformer):
        """Test encoding when model is not loaded."""
        with patch(
            "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
        ):
            provider = LocalSentenceTransformerProvider()
            provider.model = None

            with pytest.raises(RuntimeError, match="Model not loaded"):
                provider.encode(["test"])

    def test_model_not_loaded_dimension_error(self, mock_sentence_transformer):
        """Test getting dimension when model is not loaded."""
        with patch(
            "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
        ):
            provider = LocalSentenceTransformerProvider()
            provider.model = None

            with pytest.raises(RuntimeError, match="Model not loaded"):
                provider.get_dimension()


class TestOpenAIEmbeddingProvider:
    """Test suite for OpenAIEmbeddingProvider."""

    def test_initialization_with_api_key(self):
        """Test initialization with API key."""
        mock_client = MagicMock()
        with patch("codex.rag.embeddings.OpenAI", return_value=mock_client):
            provider = OpenAIEmbeddingProvider(api_key="test-key-123")
            assert provider.model_name == "text-embedding-3-small", "model_name is not valid"
            assert provider.client is not None, "client must be initialized"

    def test_initialization_with_env_var(self):
        """Test initialization with environment variable."""
        mock_client = MagicMock()
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env-key-456"}):  # pragma: allowlist secret
            with patch("codex.rag.embeddings.OpenAI", return_value=mock_client):
                provider = OpenAIEmbeddingProvider()
                assert provider.client is not None, "client must be initialized"

    def test_initialization_without_api_key_raises_error(self):
        """Test initialization without API key raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key not provided"):
                OpenAIEmbeddingProvider()

    def test_initialization_custom_model(self):
        """Test initialization with custom model."""
        mock_client = MagicMock()
        with patch("codex.rag.embeddings.OpenAI", return_value=mock_client):
            provider = OpenAIEmbeddingProvider(
                model_name="text-embedding-3-large", api_key="test-key"  # pragma: allowlist secret
            )
            assert provider.model_name == "text-embedding-3-large", "model_name is not valid"

    def test_encode_texts(self):
        """Test encoding texts via OpenAI API."""
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(embedding=[0.1] * 1536),
            MagicMock(embedding=[0.2] * 1536),
        ]

        mock_client = MagicMock()
        mock_client.embeddings.create.return_value = mock_response

        with patch("codex.rag.embeddings.OpenAI", return_value=mock_client):
            provider = OpenAIEmbeddingProvider(api_key="test-key")  # pragma: allowlist secret
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

        with patch("codex.rag.embeddings.OpenAI", return_value=mock_client):
            provider = OpenAIEmbeddingProvider(api_key="test-key")  # pragma: allowlist secret
            texts = ["Text " + str(i) for i in range(5)]
            provider.encode(texts, batch_size=3)

            # Should make 2 API calls (3 + 2)
            assert mock_client.embeddings.create.call_count == 2, "Count must be greater than zero"

    def test_encode_api_error_propagates(self):
        """Test that API errors are propagated."""
        mock_client = MagicMock()
        mock_client.embeddings.create.side_effect = Exception("API Error")

        with patch("codex.rag.embeddings.OpenAI", return_value=mock_client):
            provider = OpenAIEmbeddingProvider(api_key="test-key")  # pragma: allowlist secret

            with pytest.raises(Exception, match="API Error"):
                provider.encode(["test"])

    def test_get_dimension_small_model(self):
        """Test getting dimension for small model."""
        mock_client = MagicMock()
        with patch("codex.rag.embeddings.OpenAI", return_value=mock_client):
            provider = OpenAIEmbeddingProvider(
                model_name="text-embedding-3-small", api_key="test-key"  # pragma: allowlist secret
            )
            assert provider.get_dimension() == 1536, "Condition must be true"

    def test_get_dimension_large_model(self):
        """Test getting dimension for large model."""
        mock_client = MagicMock()
        with patch("codex.rag.embeddings.OpenAI", return_value=mock_client):
            provider = OpenAIEmbeddingProvider(
                model_name="text-embedding-3-large", api_key="test-key"  # pragma: allowlist secret
            )
            assert provider.get_dimension() == 3072, "Condition must be true"

    def test_get_dimension_ada_model(self):
        """Test getting dimension for Ada model."""
        mock_client = MagicMock()
        with patch("codex.rag.embeddings.OpenAI", return_value=mock_client):
            provider = OpenAIEmbeddingProvider(
                model_name="text-embedding-ada-002", api_key="test-key"  # pragma: allowlist secret
            )
            assert provider.get_dimension() == 1536, "Condition must be true"

    def test_get_dimension_unknown_model_defaults(self):
        """Test getting dimension for unknown model defaults to 1536."""
        mock_client = MagicMock()
        with patch("codex.rag.embeddings.OpenAI", return_value=mock_client):
            provider = OpenAIEmbeddingProvider(
                model_name="unknown-model", api_key="test-key"  # pragma: allowlist secret
            )
            assert provider.get_dimension() == 1536, "Condition must be true"

    def test_encode_without_client_raises_error(self):
        """Test encoding without initialized client raises error."""
        mock_client = MagicMock()
        with patch("codex.rag.embeddings.OpenAI", return_value=mock_client):
            provider = OpenAIEmbeddingProvider(api_key="test-key")  # pragma: allowlist secret
            provider.client = None

            with pytest.raises(RuntimeError, match="OpenAI client not initialized"):
                provider.encode(["test"])


class TestCachedEmbeddingProvider:
    """Test suite for CachedEmbeddingProvider."""

    def test_initialization(self, temp_cache_dir):
        """Test cache initialization."""
        mock_provider = MagicMock(spec=EmbeddingProvider)
        cache = CachedEmbeddingProvider(mock_provider, cache_dir=temp_cache_dir)

        assert cache.provider is mock_provider, "provider is not valid"
        assert cache.cache_dir == Path(temp_cache_dir), "cache_dir is not valid"
        assert cache.cache_hits == 0, "cache_hits is not valid"
        assert cache.cache_misses == 0, "cache_misses is not valid"
        assert Path(temp_cache_dir).exists(), "Condition must be true"

    def test_cache_miss_calls_provider(self, temp_cache_dir):
        """Test cache miss calls underlying provider."""
        mock_provider = MagicMock(spec=EmbeddingProvider)
        mock_provider.encode.return_value = np.random.randn(2, 384).astype(np.float32)

        cache = CachedEmbeddingProvider(mock_provider, cache_dir=temp_cache_dir)
        texts = ["Hello", "World"]
        cache.encode(texts, cache_key="test_key")

        assert cache.cache_misses == 1, "cache_misses is not valid"
        assert cache.cache_hits == 0, "cache_hits is not valid"
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
        assert cache.cache_misses == 1, "cache_misses is not valid"

        # Second call - cache hit
        embeddings2 = cache.encode(texts, cache_key="test_key")
        assert cache.cache_hits == 1, "cache_hits is not valid"
        assert mock_provider.encode.call_count == 1, "Count must be greater than zero"
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
        assert cache.cache_misses == 2, "cache_misses is not valid"
        assert cache.cache_hits == 0, "cache_hits is not valid"

    def test_encode_without_cache_key_no_caching(self, temp_cache_dir):
        """Test encoding without cache key bypasses cache."""
        mock_provider = MagicMock(spec=EmbeddingProvider)
        mock_provider.encode.return_value = np.random.randn(2, 384).astype(np.float32)

        cache = CachedEmbeddingProvider(mock_provider, cache_dir=temp_cache_dir)
        texts = ["Hello", "World"]

        cache.encode(texts)
        cache.encode(texts)

        # Should call provider both times
        assert mock_provider.encode.call_count == 2, "Count must be greater than zero"

    def test_get_dimension_delegates_to_provider(self, temp_cache_dir):
        """Test get_dimension delegates to underlying provider."""
        mock_provider = MagicMock(spec=EmbeddingProvider)
        mock_provider.get_dimension.return_value = 768

        cache = CachedEmbeddingProvider(mock_provider, cache_dir=temp_cache_dir)
        dimension = cache.get_dimension()

        assert dimension == 768, "dimension is not valid"
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

        assert cache.cache_misses == 3, "cache_misses is not valid"
        assert cache.cache_hits == 2, "cache_hits is not valid"


class TestTfidfEmbeddingProvider:
    """Tests for TfidfEmbeddingProvider (offline-capable, covers lines 558-617)."""

    def test_initialization_default(self):
        """Test default initialization creates a vectorizer with default features."""
        pytest.importorskip("sklearn")
        provider = TfidfEmbeddingProvider()
        assert provider.max_features == 384, "max_features is not valid"
        assert provider.is_fitted is False, "is_fitted is not valid"

    def test_initialization_custom_features(self):
        """Test custom max_features parameter."""
        pytest.importorskip("sklearn")
        provider = TfidfEmbeddingProvider(max_features=128)
        assert provider.max_features == 128, "max_features is not valid"

    def test_encode_fits_on_first_call(self):
        """Test that encode fits the vectorizer on first call."""
        pytest.importorskip("sklearn")
        provider = TfidfEmbeddingProvider(max_features=64)
        texts = ["hello world", "foo bar baz", "test document here"]
        embeddings = provider.encode(texts)
        assert provider.is_fitted is True, "is_fitted is not valid"
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape[0] == 3, "Condition must be true"
        assert embeddings.shape[1] <= 64, "Condition must be true"

    def test_encode_reuses_vocabulary_on_second_call(self):
        """Test that subsequent calls reuse the fitted vocabulary."""
        pytest.importorskip("sklearn")
        provider = TfidfEmbeddingProvider(max_features=64)
        provider.encode(["hello world", "foo bar"])
        assert provider.is_fitted is True, "is_fitted is not valid"
        # Second call should reuse fitted vocabulary
        embeddings = provider.encode(["another sentence"])
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape[0] == 1, "Condition must be true"

    def test_encode_empty_list_returns_empty_array(self):
        """Test that encoding an empty list returns an empty numpy array."""
        pytest.importorskip("sklearn")
        provider = TfidfEmbeddingProvider()
        result = provider.encode([])
        assert isinstance(result, np.ndarray)
        assert len(result) == 0, "Result must not be empty"

    def test_get_dimension_returns_max_features(self):
        """Test get_dimension returns the max_features value."""
        pytest.importorskip("sklearn")
        provider = TfidfEmbeddingProvider(max_features=256)
        assert provider.get_dimension() == 256, "Condition must be true"

    def test_encode_returns_dense_array(self):
        """Test that encode returns a dense numpy array."""
        pytest.importorskip("sklearn")
        provider = TfidfEmbeddingProvider(max_features=32)
        embeddings = provider.encode(["apple orange banana", "dog cat fish"])
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.ndim == 2, "ndim is not valid"


class TestEmbeddingModel:
    """Tests for EmbeddingModel facade (covers lines 630-657)."""

    def test_initialization_defaults(self):
        """Test EmbeddingModel initializes with default values."""
        model = EmbeddingModel()
        assert model.model_name == "sentence-transformers/all-MiniLM-L6-v2", "model_name is not valid"
        assert model.device == "cpu", "device is not valid"
        assert model.cache_dir is None, "cache_dir is not valid"
        assert model._provider is None, "_provider is not valid"

    def test_initialization_custom_params(self):
        """Test EmbeddingModel with custom parameters."""
        model = EmbeddingModel(
            model_name="sentence-transformers/paraphrase-MiniLM-L6-v2",
            device="cpu",
            cache_dir=os.path.join(tempfile.gettempdir(), "cache"),
        )
        assert model.model_name == "sentence-transformers/paraphrase-MiniLM-L6-v2", "model_name is not valid"
        assert model.device == "cpu", "device is not valid"
        assert model.cache_dir == os.path.join(tempfile.gettempdir(), "cache"), "cache_dir is not valid"

    def test_encode_triggers_lazy_loading(self, mock_sentence_transformer):
        """Test that encode lazy-loads the underlying provider."""
        with patch(
            "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
        ):
            model = EmbeddingModel()
            assert model._provider is None, "_provider is not valid"
            result = model.encode(["hello"])
            assert model._provider is not None, "_provider must be initialized"
            assert isinstance(result, np.ndarray)

    def test_encode_reuses_provider(self, mock_sentence_transformer):
        """Test that multiple encode calls reuse the same provider instance."""
        with patch(
            "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
        ):
            model = EmbeddingModel()
            model.encode(["first call"])
            provider_first = model._provider
            model.encode(["second call"])
            assert model._provider is provider_first, "_provider is not valid"

    def test_get_dimension_triggers_loading(self, mock_sentence_transformer):
        """Test that get_dimension also triggers provider loading."""
        with patch(
            "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
        ):
            model = EmbeddingModel()
            dim = model.get_dimension()
            assert dim == 384, "dim is not valid"
            assert model._provider is not None, "_provider must be initialized"


class TestCreateEmbeddingProvider:
    """Tests for create_embedding_provider factory function (covers lines 394-521)."""

    def test_auto_selects_sentence_transformers(self, mock_sentence_transformer):
        """Test auto mode successfully uses sentence-transformers."""
        with patch(
            "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
        ):
            provider = create_embedding_provider(provider_type="auto", use_cache=False)
            from codex.rag.embeddings import LocalSentenceTransformerProvider

            assert isinstance(provider, LocalSentenceTransformerProvider)

    def test_auto_uses_ollama_when_st_fails(self):
        """Test auto mode reaches Ollama branch when sentence-transformers fails (lines 410-425)."""
        import sys

        mock_ollama_instance = MagicMock()
        mock_ollama_instance._check_health.return_value = True
        mock_ollama_class = MagicMock(return_value=mock_ollama_instance)
        mock_ollama_module = MagicMock()
        mock_ollama_module.OllamaEmbeddingProvider = mock_ollama_class
        with (
            patch(
                "codex.rag.embeddings.LocalSentenceTransformerProvider",
                side_effect=RuntimeError("no model"),
            ),
            patch.dict(sys.modules, {"codex.rag.providers.ollama_provider": mock_ollama_module}),
        ):
            provider = create_embedding_provider(provider_type="auto", use_cache=False)
        assert provider is mock_ollama_instance, "provider is not valid"

    def test_auto_skips_ollama_when_server_down(self):
        """Test auto mode skips Ollama when health check fails (covers lines 422-425)."""
        pytest.importorskip("sklearn")
        import sys

        mock_ollama_instance = MagicMock()
        mock_ollama_instance._check_health.return_value = False
        mock_ollama_class = MagicMock(return_value=mock_ollama_instance)
        mock_ollama_module = MagicMock()
        mock_ollama_module.OllamaEmbeddingProvider = mock_ollama_class
        with (
            patch(
                "codex.rag.embeddings.LocalSentenceTransformerProvider",
                side_effect=RuntimeError("no model"),
            ),
            patch.dict(sys.modules, {"codex.rag.providers.ollama_provider": mock_ollama_module}),
        ):
            provider = create_embedding_provider(provider_type="auto", use_cache=False)
        # Ollama skipped (health check failed) → falls through to TF-IDF
        assert provider is not None, "provider must be initialized"
        assert not isinstance(provider, type(mock_ollama_instance))

    def test_auto_uses_llamacpp_when_st_and_ollama_fail(self):
        """Test auto mode reaches llamacpp branch (lines 427-439)."""
        import sys

        mock_llamacpp_instance = MagicMock()
        mock_llamacpp_class = MagicMock(return_value=mock_llamacpp_instance)
        mock_llamacpp_module = MagicMock()
        mock_llamacpp_module.LlamaCppEmbeddingProvider = mock_llamacpp_class
        mock_ollama_module = MagicMock()
        mock_ollama_module.OllamaEmbeddingProvider = MagicMock(side_effect=RuntimeError("ollama"))
        with (
            patch(
                "codex.rag.embeddings.LocalSentenceTransformerProvider",
                side_effect=RuntimeError("no model"),
            ),
            patch.dict(
                sys.modules,
                {
                    "codex.rag.providers.ollama_provider": mock_ollama_module,
                    "codex.rag.providers.llamacpp_provider": mock_llamacpp_module,
                },
            ),
        ):
            provider = create_embedding_provider(
                provider_type="auto", use_cache=False, model_path=os.path.join(tempfile.gettempdir(), "model.gguf")
            )
        assert provider is mock_llamacpp_instance, "provider is not valid"

    def test_auto_uses_gpt4all_when_st_ollama_llamacpp_fail(self):
        """Test auto mode reaches GPT4All branch (lines 441-453)."""
        pytest.importorskip("sklearn")
        import sys

        mock_gpt4all_instance = MagicMock()
        mock_gpt4all_class = MagicMock(return_value=mock_gpt4all_instance)
        mock_gpt4all_module = MagicMock()
        mock_gpt4all_module.GPT4AllEmbeddingProvider = mock_gpt4all_class
        mock_ollama_module = MagicMock()
        mock_ollama_module.OllamaEmbeddingProvider = MagicMock(side_effect=RuntimeError("ollama"))
        with (
            patch(
                "codex.rag.embeddings.LocalSentenceTransformerProvider",
                side_effect=RuntimeError("no model"),
            ),
            patch.dict(
                sys.modules,
                {
                    "codex.rag.providers.ollama_provider": mock_ollama_module,
                    "codex.rag.providers.gpt4all_provider": mock_gpt4all_module,
                },
            ),
        ):
            provider = create_embedding_provider(provider_type="auto", use_cache=False)
        assert provider is mock_gpt4all_instance, "provider is not valid"

    def test_auto_fallbacks_to_tfidf_when_st_unavailable(self):
        """Test auto mode falls back to TF-IDF when all other providers fail (lines 455-459)."""
        pytest.importorskip("sklearn")
        with patch(
            "codex.rag.embeddings.LocalSentenceTransformerProvider",
            side_effect=RuntimeError("no model"),
        ):
            provider = create_embedding_provider(provider_type="auto", use_cache=False)
            # Should fall back to TF-IDF or another provider
            assert provider is not None, "provider must be initialized"

    def test_auto_with_cache_wraps_in_cached_provider(self, mock_sentence_transformer, tmp_path):
        """Test auto mode with use_cache=True wraps result in CachedEmbeddingProvider."""
        with patch(
            "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
        ):
            provider = create_embedding_provider(
                provider_type="auto", use_cache=True, cache_dir=str(tmp_path)
            )
            assert isinstance(provider, CachedEmbeddingProvider)

    def test_explicit_local_provider(self, mock_sentence_transformer):
        """Test explicit 'local' provider type."""
        with patch(
            "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
        ):
            provider = create_embedding_provider(provider_type="local", use_cache=False)
            assert isinstance(provider, LocalSentenceTransformerProvider)

    def test_explicit_tfidf_provider(self):
        """Test explicit 'tfidf' provider type."""
        pytest.importorskip("sklearn")
        provider = create_embedding_provider(provider_type="tfidf", use_cache=False)
        assert isinstance(provider, TfidfEmbeddingProvider)

    def test_tfidf_with_cache_wraps(self, tmp_path):
        """Test 'tfidf' with use_cache=True wraps in CachedEmbeddingProvider."""
        pytest.importorskip("sklearn")
        provider = create_embedding_provider(
            provider_type="tfidf", use_cache=True, cache_dir=str(tmp_path)
        )
        assert isinstance(provider, CachedEmbeddingProvider)

    def test_explicit_ollama_provider(self):
        """Test explicit 'ollama' provider type instantiates OllamaEmbeddingProvider."""
        mock_ollama_instance = MagicMock()
        mock_ollama_class = MagicMock(return_value=mock_ollama_instance)
        mock_ollama_module = MagicMock()
        mock_ollama_module.OllamaEmbeddingProvider = mock_ollama_class
        import sys

        with patch.dict(sys.modules, {"codex.rag.providers.ollama_provider": mock_ollama_module}):
            provider = create_embedding_provider(
                provider_type="ollama", use_cache=False, model_name="nomic-embed-text"
            )
        mock_ollama_class.assert_called_once_with(model_name="nomic-embed-text")
        assert provider is mock_ollama_instance, "provider is not valid"

    def test_explicit_llamacpp_provider_without_model_path(self):
        """Test explicit 'llamacpp' provider type requires model_path."""
        import sys

        mock_llamacpp_class = MagicMock()
        mock_llamacpp_module = MagicMock()
        mock_llamacpp_module.LlamaCppEmbeddingProvider = mock_llamacpp_class
        with patch.dict(
            sys.modules, {"codex.rag.providers.llamacpp_provider": mock_llamacpp_module}
        ):
            with pytest.raises(ValueError, match="model_path"):
                create_embedding_provider(provider_type="llamacpp", use_cache=False)

    def test_explicit_llamacpp_provider_with_model_path(self):
        """Test explicit 'llamacpp' provider type succeeds with model_path."""
        import sys

        mock_llamacpp_instance = MagicMock()
        mock_llamacpp_class = MagicMock(return_value=mock_llamacpp_instance)
        mock_llamacpp_module = MagicMock()
        mock_llamacpp_module.LlamaCppEmbeddingProvider = mock_llamacpp_class
        with patch.dict(
            sys.modules, {"codex.rag.providers.llamacpp_provider": mock_llamacpp_module}
        ):
            provider = create_embedding_provider(
                provider_type="llamacpp", use_cache=False, model_path=os.path.join(tempfile.gettempdir(), "model.gguf")
            )
        assert provider is mock_llamacpp_instance, "provider is not valid"

    def test_explicit_gpt4all_provider(self):
        """Test explicit 'gpt4all' provider type instantiates GPT4AllEmbeddingProvider."""
        import sys

        mock_gpt4all_instance = MagicMock()
        mock_gpt4all_class = MagicMock(return_value=mock_gpt4all_instance)
        mock_gpt4all_module = MagicMock()
        mock_gpt4all_module.GPT4AllEmbeddingProvider = mock_gpt4all_class
        with patch.dict(sys.modules, {"codex.rag.providers.gpt4all_provider": mock_gpt4all_module}):
            provider = create_embedding_provider(
                provider_type="gpt4all", use_cache=False, model_name="nomic-embed-text-v1.5"
            )
        mock_gpt4all_class.assert_called_once_with(model_name="nomic-embed-text-v1.5")
        assert provider is mock_gpt4all_instance, "provider is not valid"

    def test_explicit_openai_provider_without_key_raises(self):
        """Test 'openai' without API key raises ValueError."""
        # Clear both OpenAI key env vars so the provider sees no key
        env_override = {
            k: v for k, v in os.environ.items() if k not in ("RAG_OPENAI_KEY", "OPENAI_API_KEY")
        }
        with patch.dict(os.environ, env_override, clear=True):
            with pytest.raises(ValueError, match="API key"):
                create_embedding_provider(provider_type="openai", use_cache=False)

    def test_unknown_provider_type_raises(self):
        """Test unknown provider type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown provider type"):
            create_embedding_provider(provider_type="unknown_xyz", use_cache=False)


class TestCachedEmbeddingProviderClearCache:
    """Tests for CachedEmbeddingProvider.clear_cache (covers lines 348-358)."""

    def test_clear_cache_removes_files(self, tmp_path):
        """Test that clear_cache removes cached files and resets counters."""
        mock_provider = MagicMock(spec=EmbeddingProvider)
        mock_provider.encode.return_value = np.random.randn(1, 384).astype(np.float32)

        cache = CachedEmbeddingProvider(mock_provider, cache_dir=str(tmp_path))
        # Populate cache
        cache.encode(["hello"], cache_key="key1")
        assert cache.cache_misses == 1, "cache_misses is not valid"
        # Place a dummy file
        (tmp_path / "dummy.npz").write_text("x")

        cache.clear_cache()

        assert cache.cache_hits == 0, "cache_hits is not valid"
        assert cache.cache_misses == 0, "cache_misses is not valid"
        assert tmp_path.exists(), "Condition must be true"

    def test_clear_cache_when_dir_missing(self, tmp_path):
        """Test clear_cache is a no-op when cache dir doesn't exist."""
        mock_provider = MagicMock(spec=EmbeddingProvider)
        cache_dir = tmp_path / "nonexistent"
        cache = CachedEmbeddingProvider(mock_provider, cache_dir=str(cache_dir))
        # Remove the directory created by __init__
        import shutil

        shutil.rmtree(cache_dir, ignore_errors=True)

        # Should not raise
        cache.clear_cache()

    def test_cache_save_error_is_logged_not_raised(self, tmp_path):
        """Test that a cache save error is swallowed with a warning (lines 295-296)."""
        mock_provider = MagicMock(spec=EmbeddingProvider)
        mock_provider.encode.return_value = np.random.randn(2, 8).astype(np.float32)

        cache = CachedEmbeddingProvider(mock_provider, cache_dir=str(tmp_path))

        # Make savez_compressed raise to trigger the except branch (lines 295-296)
        with patch("numpy.savez_compressed", side_effect=OSError("disk full")):
            # Should not raise; warning is logged
            result = cache.encode(["a", "b"], cache_key="err_key")

        assert result is not None, "result must be initialized"
        assert cache.cache_misses == 1, "cache_misses is not valid"
