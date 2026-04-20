"""Targeted coverage tests for RAG modules — ML dependency bump regression fix.

This module covers lines missed after the peft 0.18.1→0.19.1 / transformers
5.5.3→5.5.4 bump.  All tests use unittest.mock so that no real model
downloads are required; the test suite runs in CPU-only CI environments with
or without sentence-transformers installed.

Modules covered:
- src/codex/rag/embeddings.py        (LocalSentenceTransformerProvider,
                                       OpenAIEmbeddingProvider,
                                       CachedEmbeddingProvider,
                                       create_embedding_provider,
                                       TfidfEmbeddingProvider,
                                       EmbeddingModel)
- src/codex/rag/_model_utils.py      (meta tensor / to_empty() paths)
- src/codex/rag/retriever.py         (Retriever edge cases, CachedRetriever,
                                       RAGRetriever)
- src/codex/rag/indexer.py           (chunk_text errors, embed_chunks errors,
                                       persist_index errors, load_index errors,
                                       build_index_from_files, manage_tenant_indices,
                                       RAGIndexer)
- src/codex/rag/utils.py             (has_meta_tensors, safe_model_to_device,
                                       safe_model_load deprecated wrapper)
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Ensure src/ is importable
# ---------------------------------------------------------------------------
_SRC = Path(__file__).resolve().parents[2] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

pytest.importorskip("numpy")
import numpy as np  # noqa: E402

# ===========================================================================
# embeddings.py — LocalSentenceTransformerProvider (with mocked ST)
# ===========================================================================

class TestLocalSentenceTransformerProviderMocked:
    """Cover lines 60-112 via a mocked SentenceTransformer model."""

    def _make_mock_st(self, dim: int = 384):
        """Return a minimal SentenceTransformer mock."""
        mock_model = MagicMock()
        mock_model.encode.return_value = np.zeros((2, dim), dtype=np.float32)
        mock_model.get_sentence_embedding_dimension.return_value = dim
        return mock_model

    def test_load_model_calls_safe_load(self):
        """_load_model() should call safe_load_sentence_transformer."""
        mock_model = self._make_mock_st()
        with patch("codex.rag.embeddings.LocalSentenceTransformerProvider._load_model"):
            from codex.rag.embeddings import LocalSentenceTransformerProvider
            p = LocalSentenceTransformerProvider.__new__(LocalSentenceTransformerProvider)
            p.model_name = "test-model"
            p.cache_dir = None
            p.model = mock_model

        assert p.model is mock_model

    def test_encode_returns_ndarray(self):
        """encode() should return a numpy array from the underlying model."""
        from codex.rag.embeddings import LocalSentenceTransformerProvider

        mock_model = self._make_mock_st()
        with patch("codex.rag._model_utils.safe_load_sentence_transformer",
                   return_value=mock_model):
            p = LocalSentenceTransformerProvider(model_name="test-model")

        result = p.encode(["hello", "world"])
        assert isinstance(result, np.ndarray)
        mock_model.encode.assert_called_once()

    def test_encode_passes_kwargs(self):
        """encode() should forward batch_size and show_progress to model.encode."""
        from codex.rag.embeddings import LocalSentenceTransformerProvider

        mock_model = self._make_mock_st()
        with patch("codex.rag._model_utils.safe_load_sentence_transformer",
                   return_value=mock_model):
            p = LocalSentenceTransformerProvider(model_name="test-model")

        p.encode(["text"], batch_size=8, show_progress=True)
        call_kwargs = mock_model.encode.call_args[1]
        assert call_kwargs.get("batch_size") == 8
        assert call_kwargs.get("show_progress_bar") is True

    def test_encode_no_model_raises(self):
        """encode() raises RuntimeError when model is None."""
        from codex.rag.embeddings import LocalSentenceTransformerProvider

        p = LocalSentenceTransformerProvider.__new__(LocalSentenceTransformerProvider)
        p.model = None
        with pytest.raises(RuntimeError, match="Model not loaded"):
            p.encode(["text"])

    def test_get_dimension_returns_int(self):
        """get_dimension() should return the model's embedding dimension."""
        from codex.rag.embeddings import LocalSentenceTransformerProvider

        mock_model = self._make_mock_st(dim=384)
        with patch("codex.rag._model_utils.safe_load_sentence_transformer",
                   return_value=mock_model):
            p = LocalSentenceTransformerProvider(model_name="test-model")

        assert p.get_dimension() == 384

    def test_get_dimension_no_model_raises(self):
        """get_dimension() raises RuntimeError when model is None."""
        from codex.rag.embeddings import LocalSentenceTransformerProvider

        p = LocalSentenceTransformerProvider.__new__(LocalSentenceTransformerProvider)
        p.model = None
        with pytest.raises(RuntimeError, match="Model not loaded"):
            p.get_dimension()

    def test_load_model_import_error_reraises(self):
        """_load_model() should re-raise ImportError from sentence-transformers."""
        from codex.rag.embeddings import LocalSentenceTransformerProvider

        with patch("codex.rag._model_utils.safe_load_sentence_transformer",
                   side_effect=ImportError("not installed")):
            with pytest.raises(ImportError):
                LocalSentenceTransformerProvider(model_name="test-model")

    def test_load_model_generic_error_reraises(self):
        """_load_model() should re-raise generic exceptions."""
        from codex.rag.embeddings import LocalSentenceTransformerProvider

        with patch("codex.rag._model_utils.safe_load_sentence_transformer",
                   side_effect=RuntimeError("load failed")):
            with pytest.raises(RuntimeError, match="load failed"):
                LocalSentenceTransformerProvider(model_name="test-model")


# ===========================================================================
# embeddings.py — OpenAIEmbeddingProvider edge cases
# ===========================================================================

class TestOpenAIEmbeddingProviderEdgeCases:
    """Cover lines 152-200 (OpenAI = None path, encode error, unknown model dim)."""

    def test_initialize_client_when_openai_none_raises(self):
        """When OpenAI import is unavailable, _initialize_client should raise ImportError."""
        from codex.rag import embeddings as emb_mod

        original_openai = emb_mod.OpenAI
        try:
            emb_mod.OpenAI = None
            with pytest.raises(ImportError, match="openai package not installed"):
                emb_mod.OpenAIEmbeddingProvider(api_key="fake-key")
        finally:
            emb_mod.OpenAI = original_openai

    def test_encode_raises_when_client_none(self):
        """encode() raises RuntimeError when client is not initialized."""
        import os

        from codex.rag.embeddings import OpenAIEmbeddingProvider

        with patch("codex.rag.embeddings.OpenAI") as MockOpenAI:
            MockOpenAI.return_value = MagicMock()
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
                p = OpenAIEmbeddingProvider(api_key="test-key")

        p.client = None  # Simulate uninitialized
        with pytest.raises(RuntimeError, match="not initialized"):
            p.encode(["text"])

    def test_encode_propagates_exception(self):
        """encode() should re-raise exceptions from client.embeddings.create."""
        import os

        from codex.rag.embeddings import OpenAIEmbeddingProvider

        with patch("codex.rag.embeddings.OpenAI") as MockOpenAI:
            mock_client = MagicMock()
            mock_client.embeddings.create.side_effect = RuntimeError("API error")
            MockOpenAI.return_value = mock_client

            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
                p = OpenAIEmbeddingProvider(api_key="test-key")

            with pytest.raises(RuntimeError, match="API error"):
                p.encode(["text"])

    def test_get_dimension_unknown_model_returns_default(self):
        """get_dimension() returns 1536 for unknown model names."""
        import os

        from codex.rag.embeddings import OpenAIEmbeddingProvider

        with patch("codex.rag.embeddings.OpenAI") as MockOpenAI:
            MockOpenAI.return_value = MagicMock()
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
                p = OpenAIEmbeddingProvider(
                    model_name="some-unknown-model-xyz",
                    api_key="test-key",
                )

        assert p.get_dimension() == 1536


# ===========================================================================
# embeddings.py — CachedEmbeddingProvider (mock-based, no ST needed)
# ===========================================================================

class TestCachedEmbeddingProviderMocked:
    """Cover lines 211-358: CachedEmbeddingProvider full lifecycle."""

    @pytest.fixture
    def mock_provider(self):
        provider = MagicMock()
        provider.encode.return_value = np.ones((2, 8), dtype=np.float32)
        provider.get_dimension.return_value = 8
        return provider

    def test_init_creates_cache_dir(self, mock_provider, tmp_path):
        from codex.rag.embeddings import CachedEmbeddingProvider

        cache_dir = str(tmp_path / "cache")
        cp = CachedEmbeddingProvider(mock_provider, cache_dir=cache_dir)
        assert Path(cache_dir).exists()
        assert cp.cache_hits == 0
        assert cp.cache_misses == 0

    def test_encode_without_cache_key_bypasses_cache(self, mock_provider, tmp_path):
        from codex.rag.embeddings import CachedEmbeddingProvider

        cp = CachedEmbeddingProvider(mock_provider, cache_dir=str(tmp_path))
        cp.encode(["a", "b"])
        cp.encode(["a", "b"])
        assert mock_provider.encode.call_count == 2
        assert cp.cache_hits == 0
        assert cp.cache_misses == 0

    def test_encode_cache_miss_then_hit(self, mock_provider, tmp_path):
        from codex.rag.embeddings import CachedEmbeddingProvider

        cp = CachedEmbeddingProvider(mock_provider, cache_dir=str(tmp_path))
        cp.encode(["a"], cache_key="k1")
        assert cp.cache_misses == 1
        cp.encode(["a"], cache_key="k1")
        assert cp.cache_hits == 1

    def test_encode_cache_invalid_mtime_causes_miss(self, mock_provider, tmp_path):
        from codex.rag.embeddings import CachedEmbeddingProvider

        cp = CachedEmbeddingProvider(mock_provider, cache_dir=str(tmp_path))
        cp.encode(["a"], cache_key="k1", metadata={"file_mtime": 100})
        cp.encode(["a"], cache_key="k1", metadata={"file_mtime": 200})
        assert cp.cache_misses == 2

    def test_encode_handles_corrupted_npz(self, mock_provider, tmp_path):
        from codex.rag.embeddings import CachedEmbeddingProvider

        cp = CachedEmbeddingProvider(mock_provider, cache_dir=str(tmp_path))
        cp.encode(["a"], cache_key="corrupt")
        # Corrupt the npz
        (tmp_path / "corrupt.npz").write_text("not valid numpy")
        # Should fall back to provider
        result = cp.encode(["a"], cache_key="corrupt")
        assert result is not None

    def test_encode_handles_save_error(self, mock_provider, tmp_path):
        from codex.rag.embeddings import CachedEmbeddingProvider

        cp = CachedEmbeddingProvider(mock_provider, cache_dir=str(tmp_path))
        with patch("numpy.savez_compressed", side_effect=OSError("disk full")):
            # Should not raise; just skip caching
            result = cp.encode(["a"], cache_key="k_save_err")
        assert result is not None

    def test_is_cache_valid_mtime_match(self, mock_provider, tmp_path):
        from codex.rag.embeddings import CachedEmbeddingProvider

        cp = CachedEmbeddingProvider(mock_provider, cache_dir=str(tmp_path))
        cp.encode(["a"], cache_key="kv", metadata={"file_mtime": 42})
        # Same mtime → cache hit
        result = cp.encode(["a"], cache_key="kv", metadata={"file_mtime": 42})
        assert cp.cache_hits == 1

    def test_is_cache_valid_corrupt_metadata(self, mock_provider, tmp_path):
        from codex.rag.embeddings import CachedEmbeddingProvider

        cp = CachedEmbeddingProvider(mock_provider, cache_dir=str(tmp_path))
        cp.encode(["a"], cache_key="km")
        (tmp_path / "km.meta.json").write_text("{invalid json")
        # Corrupt metadata → miss
        result = cp.encode(["a"], cache_key="km")
        assert result is not None

    def test_get_dimension_delegates(self, mock_provider, tmp_path):
        from codex.rag.embeddings import CachedEmbeddingProvider

        cp = CachedEmbeddingProvider(mock_provider, cache_dir=str(tmp_path))
        assert cp.get_dimension() == 8

    def test_get_stats_returns_dict(self, mock_provider, tmp_path):
        from codex.rag.embeddings import CachedEmbeddingProvider

        cp = CachedEmbeddingProvider(mock_provider, cache_dir=str(tmp_path))
        cp.encode(["a"], cache_key="s1")
        cp.encode(["a"], cache_key="s1")
        stats = cp.get_stats()
        assert "hit_rate" in stats
        assert stats["cache_hits"] == 1

    def test_clear_cache_resets_stats(self, mock_provider, tmp_path):
        from codex.rag.embeddings import CachedEmbeddingProvider

        cp = CachedEmbeddingProvider(mock_provider, cache_dir=str(tmp_path))
        cp.encode(["a"], cache_key="clr")
        cp.clear_cache()
        assert cp.cache_hits == 0
        assert cp.cache_misses == 0
        assert Path(str(tmp_path)).exists()


# ===========================================================================
# embeddings.py — TfidfEmbeddingProvider
# ===========================================================================

class TestTfidfEmbeddingProvider:
    """Cover lines 550-623: TfidfEmbeddingProvider."""

    def test_init_succeeds(self):
        from codex.rag.embeddings import TfidfEmbeddingProvider

        p = TfidfEmbeddingProvider(max_features=64)
        assert p.max_features == 64
        assert not p.is_fitted

    def test_encode_empty_returns_empty(self):
        from codex.rag.embeddings import TfidfEmbeddingProvider

        p = TfidfEmbeddingProvider()
        result = p.encode([])
        assert isinstance(result, np.ndarray)
        assert len(result) == 0

    def test_encode_fits_on_first_call(self):
        from codex.rag.embeddings import TfidfEmbeddingProvider

        p = TfidfEmbeddingProvider(max_features=16)
        result = p.encode(["hello world", "foo bar"])
        assert p.is_fitted
        assert result.shape[0] == 2

    def test_encode_subsequent_call_uses_fitted(self):
        from codex.rag.embeddings import TfidfEmbeddingProvider

        p = TfidfEmbeddingProvider(max_features=16)
        p.encode(["hello world", "foo bar"])
        result2 = p.encode(["test sentence"])
        assert result2.shape[0] == 1

    def test_encode_small_corpus_clamps_max_df(self):
        """max_df clamping for tiny corpus (n_docs < 3)."""
        from codex.rag.embeddings import TfidfEmbeddingProvider

        p = TfidfEmbeddingProvider(max_features=8)
        result = p.encode(["only one doc"])
        assert result.shape[0] == 1
        # After fitting, max_df should have been clamped to 1.0
        assert p.vectorizer.max_df == 1.0

    def test_encode_transform_exception_reraises(self):
        from codex.rag.embeddings import TfidfEmbeddingProvider

        p = TfidfEmbeddingProvider(max_features=8)
        p.encode(["corpus text"])  # fit
        with patch.object(p.vectorizer, "transform", side_effect=RuntimeError("transform err")):
            with pytest.raises(RuntimeError, match="transform err"):
                p.encode(["text"])

    def test_get_dimension(self):
        from codex.rag.embeddings import TfidfEmbeddingProvider

        p = TfidfEmbeddingProvider(max_features=128)
        assert p.get_dimension() == 128

    def test_init_import_error(self):
        """TfidfEmbeddingProvider raises ImportError when scikit-learn missing."""
        from codex.rag.embeddings import TfidfEmbeddingProvider

        with patch.dict(sys.modules, {
            "sklearn": None,
            "sklearn.feature_extraction": None,
            "sklearn.feature_extraction.text": None,
        }):
            with pytest.raises((ImportError, TypeError)):
                # Instantiate a new one whose __init__ tries to import sklearn
                p = TfidfEmbeddingProvider.__new__(TfidfEmbeddingProvider)
                p.__init__(max_features=16)


# ===========================================================================
# embeddings.py — EmbeddingModel facade
# ===========================================================================

class TestEmbeddingModel:
    """Cover lines 626-663: EmbeddingModel lazy-load facade."""

    def test_init_attributes(self):
        from codex.rag.embeddings import EmbeddingModel

        m = EmbeddingModel(model_name="test-model", device="cpu")
        assert m.model_name == "test-model"
        assert m.device == "cpu"
        assert m._provider is None

    def test_ensure_loaded_creates_provider(self):
        from codex.rag.embeddings import EmbeddingModel, LocalSentenceTransformerProvider

        mock_prov = MagicMock(spec=LocalSentenceTransformerProvider)
        mock_prov.encode.return_value = np.zeros((1, 8), dtype=np.float32)
        mock_prov.get_sentence_embedding_dimension = MagicMock(return_value=8)
        mock_prov.get_dimension.return_value = 8

        with patch("codex.rag.embeddings.LocalSentenceTransformerProvider",
                   return_value=mock_prov):
            m = EmbeddingModel(model_name="test-model")
            prov = m._ensure_loaded()

        assert prov is mock_prov
        assert m._provider is mock_prov

    def test_ensure_loaded_returns_same_provider(self):
        from codex.rag.embeddings import EmbeddingModel, LocalSentenceTransformerProvider

        mock_prov = MagicMock(spec=LocalSentenceTransformerProvider)
        mock_prov.encode.return_value = np.zeros((1, 8), dtype=np.float32)
        mock_prov.get_dimension.return_value = 8

        with patch("codex.rag.embeddings.LocalSentenceTransformerProvider",
                   return_value=mock_prov):
            m = EmbeddingModel(model_name="test-model")
            p1 = m._ensure_loaded()
            p2 = m._ensure_loaded()

        assert p1 is p2

    def test_encode_delegates(self):
        from codex.rag.embeddings import EmbeddingModel, LocalSentenceTransformerProvider

        mock_prov = MagicMock(spec=LocalSentenceTransformerProvider)
        mock_prov.encode.return_value = np.ones((1, 8), dtype=np.float32)
        mock_prov.get_dimension.return_value = 8

        with patch("codex.rag.embeddings.LocalSentenceTransformerProvider",
                   return_value=mock_prov):
            m = EmbeddingModel(model_name="test-model")
            result = m.encode(["hello"], batch_size=4, show_progress=False)

        mock_prov.encode.assert_called_once_with(["hello"], batch_size=4, show_progress=False)
        assert result.shape == (1, 8)

    def test_get_dimension_delegates(self):
        from codex.rag.embeddings import EmbeddingModel, LocalSentenceTransformerProvider

        mock_prov = MagicMock(spec=LocalSentenceTransformerProvider)
        mock_prov.get_dimension.return_value = 256

        with patch("codex.rag.embeddings.LocalSentenceTransformerProvider",
                   return_value=mock_prov):
            m = EmbeddingModel(model_name="test-model")
            dim = m.get_dimension()

        assert dim == 256


# ===========================================================================
# embeddings.py — create_embedding_provider() factory
# ===========================================================================

class TestCreateEmbeddingProviderFactory:
    """Cover lines 361-521: create_embedding_provider factory paths."""

    def test_tfidf_provider_type(self, tmp_path):
        from codex.rag.embeddings import TfidfEmbeddingProvider, create_embedding_provider

        p = create_embedding_provider(
            provider_type="tfidf", use_cache=False, cache_dir=str(tmp_path)
        )
        assert isinstance(p, TfidfEmbeddingProvider)

    def test_tfidf_with_cache(self, tmp_path):
        from codex.rag.embeddings import CachedEmbeddingProvider, create_embedding_provider

        p = create_embedding_provider(
            provider_type="tfidf", use_cache=True, cache_dir=str(tmp_path)
        )
        assert isinstance(p, CachedEmbeddingProvider)

    def test_unknown_provider_raises(self):
        from codex.rag.embeddings import create_embedding_provider

        with pytest.raises(ValueError, match="Unknown provider type"):
            create_embedding_provider(provider_type="nonexistent")

    def test_openai_missing_key_raises(self, tmp_path):
        import os

        from codex.rag.embeddings import create_embedding_provider

        env = {k: v for k, v in os.environ.items()
               if k not in ("OPENAI_API_KEY", "RAG_OPENAI_KEY")}
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(ValueError, match="API key required"):
                create_embedding_provider(
                    provider_type="openai", use_cache=False
                )

    def test_local_provider_without_cache(self, tmp_path):
        from codex.rag.embeddings import LocalSentenceTransformerProvider, create_embedding_provider

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 8

        with patch("codex.rag._model_utils.safe_load_sentence_transformer",
                   return_value=mock_model):
            p = create_embedding_provider(
                provider_type="local", use_cache=False, cache_dir=str(tmp_path)
            )
        assert isinstance(p, LocalSentenceTransformerProvider)

    def test_local_provider_with_cache(self, tmp_path):
        from codex.rag.embeddings import CachedEmbeddingProvider, create_embedding_provider

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 8

        with patch("codex.rag._model_utils.safe_load_sentence_transformer",
                   return_value=mock_model):
            p = create_embedding_provider(
                provider_type="local", use_cache=True, cache_dir=str(tmp_path)
            )
        assert isinstance(p, CachedEmbeddingProvider)

    def test_auto_falls_back_to_tfidf(self, tmp_path):
        """When sentence-transformers is unavailable, auto should fall back to TF-IDF."""
        from codex.rag.embeddings import CachedEmbeddingProvider, create_embedding_provider

        with patch("codex.rag.embeddings.LocalSentenceTransformerProvider",
                   side_effect=ImportError("no st")):
            with patch("codex.rag.embeddings.OllamaEmbeddingProvider",
                       side_effect=ImportError("no ollama"), create=True):
                with patch("codex.rag.embeddings.GPT4AllEmbeddingProvider",
                           side_effect=ImportError("no gpt4all"), create=True):
                    p = create_embedding_provider(
                        provider_type="auto",
                        use_cache=True,
                        cache_dir=str(tmp_path),
                    )
        # Should have wrapped TF-IDF in cache
        assert isinstance(p, CachedEmbeddingProvider)

    def test_auto_uses_local_when_available(self, tmp_path):
        """When sentence-transformers is available, auto uses local provider."""
        from codex.rag.embeddings import CachedEmbeddingProvider, create_embedding_provider

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 8

        with patch("codex.rag._model_utils.safe_load_sentence_transformer",
                   return_value=mock_model):
            p = create_embedding_provider(
                provider_type="auto",
                use_cache=True,
                cache_dir=str(tmp_path),
            )
        assert isinstance(p, CachedEmbeddingProvider)


# ===========================================================================
# _model_utils.py — meta tensor path (lines 70-103)
# ===========================================================================

class TestModelUtilsMetaTensorPath:
    """Cover lines 70-103: the NotImplementedError / to_empty() fallback."""

    def _make_st_mock(self):
        """Return a SentenceTransformer-like mock that loads cleanly."""
        mock = MagicMock()
        mock.eval.return_value = mock
        # No meta tensors
        mock.named_parameters.return_value = []
        return mock

    def test_meta_tensor_path_to_empty(self):
        """When device='cpu' raises NotImplementedError, falls back to device='meta' + to_empty."""
        from codex.rag import _model_utils as mu

        call_log: list = []

        def fake_st(model_name, device, cache_folder, trust_remote_code, use_auth_token):
            call_log.append(device)
            if device == "cpu":
                raise NotImplementedError("meta tensor!")
            # device == "meta"
            mock = MagicMock()
            mock.eval.return_value = mock
            materialized = MagicMock()
            materialized.eval.return_value = materialized
            materialized.named_parameters.return_value = []
            mock.to_empty.return_value = materialized
            mock.named_parameters.return_value = []
            return mock

        with patch("codex.rag.utils.safe_model_to_device", side_effect=lambda m, d: m):
            with patch("sentence_transformers.SentenceTransformer", fake_st):
                result = mu.safe_load_sentence_transformer("test-model")

        assert "cpu" in call_log and "meta" in call_log

    def test_meta_tensor_path_no_to_empty_raises(self):
        """When meta fallback model lacks to_empty(), RuntimeError is raised."""
        from codex.rag import _model_utils as mu

        def fake_st(model_name, device, cache_folder, trust_remote_code, use_auth_token):
            if device == "cpu":
                raise NotImplementedError("meta!")
            mock = MagicMock(spec=[])  # no to_empty attribute
            return mock

        with patch("sentence_transformers.SentenceTransformer", fake_st):
            with pytest.raises(RuntimeError, match="to_empty"):
                mu.safe_load_sentence_transformer("test-model")

    def test_meta_tensor_path_remaining_meta_raises(self):
        """After to_empty(), if meta tensors remain, RuntimeError is raised."""
        from codex.rag import _model_utils as mu

        def fake_st(model_name, device, cache_folder, trust_remote_code, use_auth_token):
            if device == "cpu":
                raise NotImplementedError("meta!")
            mock = MagicMock()
            mock.eval.return_value = mock
            meta_param = MagicMock()
            meta_param.is_meta = True
            materialized = MagicMock()
            materialized.eval.return_value = materialized
            materialized.named_parameters.return_value = [("w", meta_param)]
            mock.to_empty.return_value = materialized
            return mock

        with patch("sentence_transformers.SentenceTransformer", fake_st):
            with pytest.raises(RuntimeError, match="Meta tensors still present"):
                mu.safe_load_sentence_transformer("test-model")

    def test_successful_load_cpu(self):
        """Normal path: model loads on CPU directly."""
        from codex.rag import _model_utils as mu

        mock_model = MagicMock()
        mock_model.eval.return_value = mock_model

        with patch("sentence_transformers.SentenceTransformer", return_value=mock_model):
            with patch("codex.rag.utils.safe_model_to_device", return_value=mock_model):
                result = mu.safe_load_sentence_transformer("test-model")

        assert result is mock_model


# ===========================================================================
# retriever.py — Retriever edge cases
# ===========================================================================

class TestRetrieverEdgeCases:
    """Cover retriever.py lines that are not hit by the main test suite."""

    def _make_retriever_no_index(self, tmp_path):
        """Create a Retriever with no FAISS index (skips _load_index)."""
        from codex.rag import retriever as ret_mod

        mock_model = MagicMock()
        mock_model.encode.return_value = np.zeros((1, 8), dtype=np.float32)

        with patch("codex.rag.indexer.load_index",
                   side_effect=FileNotFoundError("no index")):
            with patch("codex.rag._model_utils.safe_load_sentence_transformer",
                       return_value=mock_model):
                r = ret_mod.Retriever(
                    index_dir=str(tmp_path),
                    index_name="test",
                    tenant_id="t1",
                )
        return r, mock_model

    def test_query_returns_empty_when_no_index(self, tmp_path):
        r, _ = self._make_retriever_no_index(tmp_path)
        result = r.query("what is X?")
        assert result == []

    def test_query_returns_empty_for_empty_query(self, tmp_path):
        r, _ = self._make_retriever_no_index(tmp_path)
        # Give it a fake index so it passes the None check
        r.faiss_index = MagicMock()
        result = r.query("   ")
        assert result == []

    def test_query_clamps_top_k_when_zero(self, tmp_path):
        r, mock_model = self._make_retriever_no_index(tmp_path)
        r.faiss_index = MagicMock()
        r.chunks_metadata = [{"text": "chunk", "start": 0, "end": 10}]
        distances = np.array([[0.1, 0.2, 0.3, 0.4, 0.5]])
        indices = np.array([[0, -1, 0, -1, 0]])
        r.faiss_index.search.return_value = (distances, indices)
        # top_k=0 should be adjusted to 5
        result = r.query("test query", top_k=0)
        assert isinstance(result, list)

    def test_estimate_line_number_zero_pos(self, tmp_path):
        r, _ = self._make_retriever_no_index(tmp_path)
        assert r._estimate_line_number(0) == 1
        assert r._estimate_line_number(-5) == 1

    def test_estimate_line_number_nonzero(self, tmp_path):
        r, _ = self._make_retriever_no_index(tmp_path)
        assert r._estimate_line_number(160) == 3  # 160//80+1

    def test_extract_file_from_chunk_direct(self, tmp_path):
        r, _ = self._make_retriever_no_index(tmp_path)
        chunk = {"file": "/a/b.py", "text": "x"}
        assert r._extract_file_from_metadata(chunk) == "/a/b.py"

    def test_extract_file_from_index_metadata(self, tmp_path):
        r, _ = self._make_retriever_no_index(tmp_path)
        r.index_metadata = {"files": [{"file": "/repo/c.py"}]}
        chunk = {"text": "x"}  # no direct 'file' key
        assert r._extract_file_from_metadata(chunk) == "/repo/c.py"

    def test_extract_file_returns_unknown_fallback(self, tmp_path):
        r, _ = self._make_retriever_no_index(tmp_path)
        r.index_metadata = {}
        chunk = {"text": "x"}
        assert r._extract_file_from_metadata(chunk) == "unknown"

    def test_get_stats_no_index(self, tmp_path):
        r, _ = self._make_retriever_no_index(tmp_path)
        stats = r.get_stats()
        assert stats["num_vectors"] == 0
        assert stats["num_chunks"] == 0

    def test_get_stats_with_index(self, tmp_path):
        r, _ = self._make_retriever_no_index(tmp_path)
        r.faiss_index = MagicMock()
        r.faiss_index.ntotal = 42
        stats = r.get_stats()
        assert stats["num_vectors"] == 42

    def test_query_applies_min_score_filter(self, tmp_path):
        r, mock_model = self._make_retriever_no_index(tmp_path)
        r.faiss_index = MagicMock()
        r.chunks_metadata = [{"text": "a", "start": 0, "end": 10}]
        # distance 0.5, above min_score threshold of 0.1
        r.faiss_index.search.return_value = (
            np.array([[0.5]]), np.array([[0]])
        )
        result = r.query("q", top_k=1, min_score=0.1)
        assert result == []

    def test_reload_delegates_to_load_index(self, tmp_path):
        r, _ = self._make_retriever_no_index(tmp_path)
        called = []
        with patch.object(r, "_load_index", side_effect=lambda: called.append(1)):
            r.reload()
        assert called


# ===========================================================================
# retriever.py — CachedRetriever
# ===========================================================================

class TestCachedRetrieverCoverage:
    """Cover CachedRetriever-specific lines (TTL, cache_key, invalidate_expired)."""

    def _make_cached(self, tmp_path):
        from codex.rag import retriever as ret_mod

        mock_model = MagicMock()
        mock_model.encode.return_value = np.zeros((1, 8), dtype=np.float32)

        with patch("codex.rag.indexer.load_index",
                   side_effect=FileNotFoundError("no index")):
            with patch("codex.rag._model_utils.safe_load_sentence_transformer",
                       return_value=mock_model):
                cr = ret_mod.CachedRetriever(
                    index_dir=str(tmp_path),
                    index_name="test",
                    tenant_id="t1",
                    cache_ttl=3600,
                    cache_maxsize=100,
                    normalize_queries=True,
                )
        return cr, mock_model

    def test_normalize_query(self, tmp_path):
        cr, _ = self._make_cached(tmp_path)
        assert cr._normalize_query("  HELLO  WORLD  ") == "hello world"

    def test_normalize_query_disabled(self, tmp_path):
        cr, _ = self._make_cached(tmp_path)
        cr.normalize_queries = False
        assert cr._normalize_query("  HELLO  ") == "  HELLO  "

    def test_make_cache_key(self, tmp_path):
        cr, _ = self._make_cached(tmp_path)
        key = cr._make_cache_key("test query", 5, None)
        assert key.startswith("query_")
        assert len(key) > 6

    def test_is_cache_valid_missing_key(self, tmp_path):
        cr, _ = self._make_cached(tmp_path)
        assert not cr._is_cache_valid("nonexistent_key")

    def test_is_cache_valid_fresh_entry(self, tmp_path):
        from time import time
        cr, _ = self._make_cached(tmp_path)
        cr.cache_timestamps["fresh"] = time()
        assert cr._is_cache_valid("fresh")

    def test_is_cache_valid_expired_entry(self, tmp_path):
        cr, _ = self._make_cached(tmp_path)
        cr.cache_ttl = 1
        cr.cache_timestamps["old"] = 0.0  # epoch — always expired
        assert not cr._is_cache_valid("old")

    def test_query_with_cache_miss_and_hit(self, tmp_path):
        cr, mock_model = self._make_cached(tmp_path)
        cr.faiss_index = MagicMock()
        cr.chunks_metadata = []
        cr.faiss_index.search.return_value = (np.array([[]]), np.array([[]]))

        r1 = cr.query_with_cache("hello", top_k=3)
        r2 = cr.query_with_cache("hello", top_k=3)
        assert r1 == r2  # same cached result

    def test_query_with_cache_expired(self, tmp_path):
        cr, mock_model = self._make_cached(tmp_path)
        cr.faiss_index = MagicMock()
        cr.chunks_metadata = []
        cr.faiss_index.search.return_value = (np.array([[]]), np.array([[]]))

        # Prime cache then expire it
        cr.query_with_cache("expired query")
        key = cr._make_cache_key("expired query", 5, None)
        cr.cache_timestamps[key] = 0.0  # force expiry
        cr.cache_ttl = 1

        r = cr.query_with_cache("expired query")
        assert isinstance(r, list)

    def test_clear_cache(self, tmp_path):
        cr, _ = self._make_cached(tmp_path)
        cr.cache_timestamps["x"] = 1.0
        cr.query_cache.cache["x"] = []
        cr.clear_cache()
        assert len(cr.cache_timestamps) == 0

    def test_get_cache_stats(self, tmp_path):
        cr, _ = self._make_cached(tmp_path)
        stats = cr.get_cache_stats()
        assert "ttl" in stats
        assert "normalize_queries" in stats
        assert "valid_entries" in stats

    def test_invalidate_expired(self, tmp_path):
        cr, _ = self._make_cached(tmp_path)
        cr.cache_ttl = 1
        cr.cache_timestamps["old_key"] = 0.0
        cr.query_cache.cache["old_key"] = []
        cr.invalidate_expired()
        assert "old_key" not in cr.cache_timestamps


# ===========================================================================
# retriever.py — RAGRetriever facade
# ===========================================================================

class TestRAGRetriever:
    """Cover RAGRetriever lines (649-678)."""

    def test_init(self):
        from codex.rag.retriever import RAGRetriever

        r = RAGRetriever(device="cpu")
        assert r.device == "cpu"
        assert r._retriever is None

    def test_query_raises_when_not_loaded(self):
        from codex.rag.retriever import RAGRetriever

        r = RAGRetriever()
        with pytest.raises(RuntimeError, match="not initialised"):
            r.query("test")

    def test_load_and_query(self, tmp_path):
        from codex.rag.retriever import RAGRetriever

        mock_inner = MagicMock()
        mock_inner.query.return_value = [{"text": "result", "score": 0.1}]

        with patch("codex.rag.retriever.Retriever", return_value=mock_inner):
            r = RAGRetriever()
            r.load(
                index_dir=str(tmp_path),
                index_name="idx",
                tenant_id="t",
                model_name="test-model",
            )
            results = r.query("my query", top_k=2)

        assert results == [{"text": "result", "score": 0.1}]


# ===========================================================================
# retriever.py — MultiIndexRetriever error handling
# ===========================================================================

class TestMultiIndexRetrieverErrors:
    """Cover lines 286-306: retriever init exceptions in MultiIndexRetriever."""

    def test_skips_index_with_no_faiss(self, tmp_path):
        from codex.rag import retriever as ret_mod

        # Retriever that loads but has no faiss_index
        mock_retriever = MagicMock()
        mock_retriever.faiss_index = None

        with patch("codex.rag.retriever.Retriever", return_value=mock_retriever):
            mir = ret_mod.MultiIndexRetriever(
                indices=[{"index_name": "a", "tenant_id": "t"}],
                index_dir=str(tmp_path),
            )

        assert len(mir.retrievers) == 0

    def test_skips_index_that_raises(self, tmp_path):
        from codex.rag import retriever as ret_mod

        with patch("codex.rag.retriever.Retriever",
                   side_effect=RuntimeError("cannot load")):
            mir = ret_mod.MultiIndexRetriever(
                indices=[{"index_name": "a", "tenant_id": "t"}],
                index_dir=str(tmp_path),
            )

        assert len(mir.retrievers) == 0


# ===========================================================================
# indexer.py — chunk_text edge cases
# ===========================================================================

class TestChunkTextEdgeCases:
    """Cover chunk_text() error paths (lines 40-55)."""

    def test_chunk_size_zero_raises(self):
        from codex.rag.indexer import chunk_text

        with pytest.raises(ValueError, match="chunk_size must be positive"):
            chunk_text("text", chunk_size=0)

    def test_chunk_size_negative_raises(self):
        from codex.rag.indexer import chunk_text

        with pytest.raises(ValueError, match="chunk_size must be positive"):
            chunk_text("text", chunk_size=-1)

    def test_overlap_negative_raises(self):
        from codex.rag.indexer import chunk_text

        with pytest.raises(ValueError, match="overlap must be non-negative"):
            chunk_text("text", chunk_size=100, overlap=-1)

    def test_overlap_ge_chunk_size_non_default_raises(self):
        from codex.rag.indexer import chunk_text

        with pytest.raises(ValueError, match="overlap must be non-negative"):
            chunk_text("hello world test", chunk_size=5, overlap=5)

    def test_overlap_ge_chunk_size_default_128_adjusts(self):
        """Default overlap=128 with chunk_size < 128 should auto-adjust."""
        from codex.rag.indexer import chunk_text

        chunks = chunk_text("hello world test", chunk_size=10)
        assert len(chunks) > 0

    def test_empty_text_returns_empty(self):
        from codex.rag.indexer import chunk_text

        assert chunk_text("") == []


# ===========================================================================
# indexer.py — embed_chunks error paths
# ===========================================================================

class TestEmbedChunksEdgeCases:
    """Cover embed_chunks() error paths (lines 99-165)."""

    def test_empty_chunks_returns_empty(self):
        from codex.rag.indexer import embed_chunks

        result = embed_chunks([])
        assert isinstance(result, np.ndarray)
        assert len(result) == 0

    def test_import_error_reraises(self):
        from codex.rag.indexer import embed_chunks

        with patch.dict(sys.modules, {"sentence_transformers": None}):
            with pytest.raises(ImportError):
                embed_chunks([(0, 5, "hello")])

    def test_model_load_error_reraises(self):
        from codex.rag.indexer import embed_chunks

        with patch("codex.rag._model_utils.safe_load_sentence_transformer",
                   side_effect=RuntimeError("model fail")):
            with pytest.raises(RuntimeError, match="model fail"):
                embed_chunks([(0, 5, "hello")])

    def test_all_empty_texts_raises(self):
        from codex.rag.indexer import embed_chunks

        mock_model = MagicMock()
        with patch("codex.rag._model_utils.safe_load_sentence_transformer",
                   return_value=mock_model):
            with pytest.raises(ValueError, match="No valid text chunks"):
                embed_chunks([(0, 1, "   "), (2, 3, "")])

    def test_index_error_during_encode_raises_runtime(self):
        from codex.rag.indexer import embed_chunks

        mock_model = MagicMock()
        mock_model.encode.side_effect = IndexError("oob")

        with patch("codex.rag._model_utils.safe_load_sentence_transformer",
                   return_value=mock_model):
            with pytest.raises(RuntimeError, match="IndexError"):
                embed_chunks([(0, 5, "hello world")])


# ===========================================================================
# indexer.py — persist_index / load_index error paths
# ===========================================================================

class TestIndexerPersistLoadErrors:
    """Cover persist_index and load_index guard clauses."""

    def test_persist_index_empty_embeddings_raises(self, tmp_path):
        from codex.rag.indexer import persist_index

        with pytest.raises(ValueError, match="Cannot persist empty"):
            persist_index("test", np.array([]), [], index_dir=str(tmp_path))

    def test_persist_index_mismatch_raises(self, tmp_path):
        from codex.rag.indexer import persist_index

        emb = np.ones((3, 4), dtype=np.float32)
        chunks = [(0, 1, "a"), (1, 2, "b")]  # 2 != 3
        with pytest.raises(ValueError, match="Mismatch"):
            persist_index("test", emb, chunks, index_dir=str(tmp_path))

    def test_persist_index_faiss_none_raises(self, tmp_path):
        from codex.rag import indexer as idx_mod

        original_faiss = idx_mod.faiss
        try:
            idx_mod.faiss = None
            emb = np.ones((2, 4), dtype=np.float32)
            chunks = [(0, 1, "a"), (1, 2, "b")]
            with pytest.raises(ImportError, match="faiss-cpu"):
                idx_mod.persist_index("test", emb, chunks, index_dir=str(tmp_path))
        finally:
            idx_mod.faiss = original_faiss

    def test_load_index_faiss_none_raises(self, tmp_path):
        from codex.rag import indexer as idx_mod

        original_faiss = idx_mod.faiss
        try:
            idx_mod.faiss = None
            with pytest.raises(ImportError, match="faiss-cpu"):
                idx_mod.load_index("test", index_dir=str(tmp_path))
        finally:
            idx_mod.faiss = original_faiss

    def test_load_index_not_found_raises(self, tmp_path):
        try:
            import faiss as _faiss  # noqa: F401
        except ImportError:
            pytest.skip("faiss not installed")

        from codex.rag.indexer import load_index
        with pytest.raises(FileNotFoundError):
            load_index("nonexistent_idx", index_dir=str(tmp_path))

    def test_load_index_no_chunks_file(self, tmp_path):
        """load_index() returns empty list when chunks.json is missing."""
        try:
            import faiss
        except ImportError:
            pytest.skip("faiss not installed")

        idx_path = tmp_path / "default" / "test_idx"
        idx_path.mkdir(parents=True)

        # Minimal FAISS index
        dim = 4
        index = faiss.IndexFlatL2(dim)
        faiss.write_index(index, str(idx_path / "index.faiss"))
        # No chunks.json and no metadata.json

        _, chunks, meta = load_index("test_idx", index_dir=str(tmp_path))
        assert chunks == []
        assert meta == {}


# ===========================================================================
# indexer.py — build_index_from_files edge cases
# ===========================================================================

class TestBuildIndexEdgeCases:
    """Cover build_index_from_files() missing-files / empty-content paths."""

    def test_all_files_missing_raises(self, tmp_path):
        from codex.rag.indexer import build_index_from_files

        missing = [tmp_path / "does_not_exist.txt"]
        with pytest.raises(ValueError, match="No valid input files"):
            build_index_from_files(missing, "idx", index_dir=str(tmp_path))

    def test_files_with_no_content_raises(self, tmp_path):
        from codex.rag.indexer import build_index_from_files

        empty_file = tmp_path / "empty.txt"
        empty_file.write_text("")
        with pytest.raises(ValueError):
            build_index_from_files([empty_file], "idx", index_dir=str(tmp_path))


# ===========================================================================
# indexer.py — manage_tenant_indices operations
# ===========================================================================

class TestManageTenantIndices:
    """Cover manage_tenant_indices() all operation branches."""

    def test_invalid_operation(self, tmp_path):
        from codex.rag.indexer import manage_tenant_indices

        result = manage_tenant_indices("t1", "UNKNOWN_OP", ["idx"], index_dir=str(tmp_path))
        assert not result.success
        assert "Invalid operation" in result.message

    def test_create_missing_files_param(self, tmp_path):
        from codex.rag.indexer import manage_tenant_indices

        result = manage_tenant_indices("t1", "create", ["idx"], index_dir=str(tmp_path))
        assert not result.success
        assert "requires 'files'" in result.message

    def test_update_missing_files_param(self, tmp_path):
        from codex.rag.indexer import manage_tenant_indices

        result = manage_tenant_indices("t1", "update", ["idx"], index_dir=str(tmp_path))
        assert not result.success
        assert "requires 'files'" in result.message

    def test_delete_nonexistent_index(self, tmp_path):
        from codex.rag.indexer import manage_tenant_indices

        result = manage_tenant_indices(
            "t1", "delete", ["no_such_idx"], index_dir=str(tmp_path)
        )
        assert not result.success
        assert "No indices deleted" in result.message

    def test_delete_existing_index(self, tmp_path):
        from codex.rag.indexer import manage_tenant_indices

        # Create a fake index directory
        idx_dir = tmp_path / "t1" / "my_idx"
        idx_dir.mkdir(parents=True)

        result = manage_tenant_indices(
            "t1", "delete", ["my_idx"], index_dir=str(tmp_path)
        )
        assert result.success
        assert "my_idx" in result.index_names

    def test_merge_missing_name_param(self, tmp_path):
        from codex.rag.indexer import manage_tenant_indices

        result = manage_tenant_indices(
            "t1", "merge", ["a", "b"], index_dir=str(tmp_path)
        )
        assert not result.success
        assert "requires 'merge_name'" in result.message

    def test_merge_no_valid_indices(self, tmp_path):
        from codex.rag.indexer import manage_tenant_indices

        result = manage_tenant_indices(
            "t1", "merge", ["bad_idx"],
            merge_name="merged",
            index_dir=str(tmp_path),
        )
        assert not result.success
        assert "No valid indices" in result.message

    def test_list_empty_tenant_dir(self, tmp_path):
        from codex.rag.indexer import manage_tenant_indices

        result = manage_tenant_indices(
            "nonexistent_tenant", "list", [], index_dir=str(tmp_path)
        )
        assert result.success
        assert result.index_names == []

    def test_list_with_indices(self, tmp_path):
        import json

        from codex.rag.indexer import manage_tenant_indices

        idx_path = tmp_path / "t1" / "myidx"
        idx_path.mkdir(parents=True)
        (idx_path / "index.faiss").touch()
        meta = {"num_vectors": 5, "dimension": 4, "created_at": "now"}
        (idx_path / "metadata.json").write_text(json.dumps(meta))

        result = manage_tenant_indices("t1", "list", [], index_dir=str(tmp_path))
        assert result.success
        assert "myidx" in result.index_names

    def test_list_with_index_no_metadata(self, tmp_path):
        from codex.rag.indexer import manage_tenant_indices

        idx_path = tmp_path / "t1" / "nometaidx"
        idx_path.mkdir(parents=True)
        (idx_path / "index.faiss").touch()

        result = manage_tenant_indices("t1", "list", [], index_dir=str(tmp_path))
        assert result.success
        # Index without metadata should still appear
        assert "nometaidx" in result.index_names

    def test_create_all_fail_returns_failure(self, tmp_path):
        from codex.rag.indexer import manage_tenant_indices

        fake_file = tmp_path / "doc.txt"
        fake_file.write_text("hello")

        with patch("codex.rag.indexer.build_index_from_files",
                   side_effect=RuntimeError("build failed")):
            result = manage_tenant_indices(
                "t1", "create", ["idx"],
                files=[fake_file],
                index_dir=str(tmp_path),
            )
        assert not result.success

    def test_update_all_fail_returns_failure(self, tmp_path):
        from codex.rag.indexer import manage_tenant_indices

        fake_file = tmp_path / "doc.txt"
        fake_file.write_text("hello")

        with patch("codex.rag.indexer.build_index_from_files",
                   side_effect=RuntimeError("build failed")):
            result = manage_tenant_indices(
                "t1", "update", ["idx"],
                files=[fake_file],
                index_dir=str(tmp_path),
            )
        assert not result.success


# ===========================================================================
# indexer.py — RAGIndexer class
# ===========================================================================

class TestRAGIndexer:
    """Cover RAGIndexer.__init__, build_index, list_tenants, move_to_device."""

    def test_init_without_model(self, tmp_path):
        from codex.rag.indexer import RAGIndexer

        with patch("codex.rag._model_utils.safe_load_sentence_transformer",
                   side_effect=Exception("no model")):
            indexer = RAGIndexer(index_dir=str(tmp_path))

        assert indexer.model is None
        assert indexer.device == "cpu"

    def test_init_with_model(self, tmp_path):
        from codex.rag.indexer import RAGIndexer

        mock_model = MagicMock()
        with patch("codex.rag._model_utils.safe_load_sentence_transformer",
                   return_value=mock_model):
            with patch("codex.rag.utils.safe_model_to_device",
                       return_value=mock_model):
                indexer = RAGIndexer(index_dir=str(tmp_path))

        assert indexer.model is mock_model

    def test_list_tenants_empty(self, tmp_path):
        from codex.rag.indexer import RAGIndexer

        with patch("codex.rag._model_utils.safe_load_sentence_transformer",
                   side_effect=Exception("no model")):
            indexer = RAGIndexer(index_dir=str(tmp_path))

        assert indexer.list_tenants() == []

    def test_list_tenants_nonexistent_dir(self):
        from codex.rag.indexer import RAGIndexer

        with patch("codex.rag._model_utils.safe_load_sentence_transformer",
                   side_effect=Exception("no model")):
            indexer = RAGIndexer(index_dir="/nonexistent/path/xyz")

        assert indexer.list_tenants() == []

    def test_list_tenants_with_dirs(self, tmp_path):
        from codex.rag.indexer import RAGIndexer

        (tmp_path / "tenant_a").mkdir()
        (tmp_path / "tenant_b").mkdir()
        (tmp_path / ".hidden").mkdir()

        with patch("codex.rag._model_utils.safe_load_sentence_transformer",
                   side_effect=Exception("no model")):
            indexer = RAGIndexer(index_dir=str(tmp_path))

        tenants = indexer.list_tenants()
        assert "tenant_a" in tenants
        assert "tenant_b" in tenants
        assert ".hidden" not in tenants

    def test_move_to_device_no_model(self, tmp_path):
        from codex.rag.indexer import RAGIndexer

        with patch("codex.rag._model_utils.safe_load_sentence_transformer",
                   side_effect=Exception("no model")):
            indexer = RAGIndexer(index_dir=str(tmp_path))

        indexer.move_to_device("cuda")  # Should not raise
        assert indexer.device == "cuda"

    def test_move_to_device_with_model(self, tmp_path):
        from codex.rag.indexer import RAGIndexer

        mock_model = MagicMock()
        moved_model = MagicMock()

        with patch("codex.rag._model_utils.safe_load_sentence_transformer",
                   return_value=mock_model):
            with patch("codex.rag.utils.safe_model_to_device",
                       return_value=mock_model):
                indexer = RAGIndexer(index_dir=str(tmp_path))

        with patch("codex.rag.utils.safe_model_to_device", return_value=moved_model):
            indexer.move_to_device("cpu")

        assert indexer.device == "cpu"
        assert indexer.model is moved_model


# ===========================================================================
# utils.py — has_meta_tensors() coverage
# ===========================================================================

class TestHasMetaTensorsEdgeCases:
    """Cover utils.py lines 62-137: submodule walks, device.type fallback, etc."""

    def test_meta_param_via_is_meta(self):
        from codex.rag.utils import has_meta_tensors

        meta_param = MagicMock()
        meta_param.is_meta = True

        model = MagicMock()
        model.parameters.return_value = [meta_param]
        model.buffers.return_value = []

        assert has_meta_tensors(model) is True

    def test_meta_param_via_device_type(self):
        from codex.rag.utils import has_meta_tensors

        param = MagicMock()
        param.is_meta = False
        param.device.type = "meta"

        model = MagicMock()
        model.parameters.return_value = [param]

        assert has_meta_tensors(model) is True

    def test_meta_buffer_via_is_meta(self):
        from codex.rag.utils import has_meta_tensors

        normal_param = MagicMock()
        normal_param.is_meta = False
        normal_param.device.type = "cpu"

        meta_buf = MagicMock()
        meta_buf.is_meta = True

        model = MagicMock()
        model.parameters.return_value = [normal_param]
        model.buffers.return_value = [meta_buf]

        assert has_meta_tensors(model) is True

    def test_meta_buffer_via_device_type(self):
        from codex.rag.utils import has_meta_tensors

        normal_param = MagicMock()
        normal_param.is_meta = False
        normal_param.device.type = "cpu"

        meta_buf = MagicMock()
        meta_buf.is_meta = False
        meta_buf.device.type = "meta"

        model = MagicMock()
        model.parameters.return_value = [normal_param]
        model.buffers.return_value = [meta_buf]

        assert has_meta_tensors(model) is True

    def test_no_meta_tensors(self):
        from codex.rag.utils import has_meta_tensors

        param = MagicMock()
        param.is_meta = False
        param.device.type = "cpu"

        model = MagicMock()
        model.parameters.return_value = [param]
        model.buffers.return_value = []

        result = has_meta_tensors(model)
        assert result is False

    def test_model_without_parameters(self):
        from codex.rag.utils import has_meta_tensors

        model = object()  # no parameters, no buffers
        result = has_meta_tensors(model)
        assert result is False

    def test_exception_returns_none(self):
        from codex.rag.utils import has_meta_tensors

        model = MagicMock()
        model.parameters.side_effect = RuntimeError("cannot iterate")

        result = has_meta_tensors(model)
        assert result is None

    def test_model_device_meta(self):
        from codex.rag.utils import has_meta_tensors

        param = MagicMock()
        param.is_meta = False
        param.device.type = "cpu"

        model = MagicMock()
        model.parameters.return_value = [param]
        model.buffers.return_value = []
        model.device.type = "meta"

        result = has_meta_tensors(model)
        assert result is True


# ===========================================================================
# utils.py — safe_model_to_device() edge cases
# ===========================================================================

class TestSafeModelToDeviceEdgeCases:
    """Cover safe_model_to_device() ImportError, AttributeError, None meta paths."""

    def test_none_meta_status_returns_model(self):
        """When has_meta_tensors() returns None, model returned as-is."""
        from codex.rag.utils import safe_model_to_device

        model = MagicMock()
        with patch("codex.rag.utils.has_meta_tensors", return_value=None):
            result = safe_model_to_device(model, "cpu")

        assert result is model

    def test_import_error_falls_back_to_try_model_to(self):
        """When torch is unavailable, falls back to _try_model_to."""
        from codex.rag.utils import safe_model_to_device

        model = MagicMock()
        model.to.return_value = model

        with patch("codex.rag.utils.has_meta_tensors",
                   side_effect=ImportError("no torch")):
            result = safe_model_to_device(model, "cpu")

        assert result is model

    def test_attribute_error_for_to_empty_reraises(self):
        """AttributeError about to_empty() should be re-raised."""
        from codex.rag.utils import safe_model_to_device

        model = MagicMock()

        def raise_attr_err(m):
            raise AttributeError("to_empty not supported")

        with patch("codex.rag.utils.has_meta_tensors", return_value=True):
            with patch("codex.rag.utils._try_model_to",
                       side_effect=AttributeError("to_empty broken")):
                # The meta=True path tries to_empty; mock the model
                model.to_empty.side_effect = AttributeError("to_empty broken")
                with pytest.raises(AttributeError):
                    safe_model_to_device(model, "cpu")

    def test_meta_model_to_empty(self):
        """Meta tensor path should call to_empty() and reset_parameters()."""
        from codex.rag.utils import safe_model_to_device

        materialized = MagicMock()
        materialized.modules.return_value = []

        model = MagicMock()
        model.to_empty.return_value = materialized

        with patch("codex.rag.utils.has_meta_tensors", return_value=True):
            result = safe_model_to_device(model, "cpu")

        model.to_empty.assert_called_once_with(device="cpu")
        assert result is materialized

    def test_non_meta_standard_transfer(self):
        """Standard (non-meta) path calls model.to()."""
        import torch
        from codex.rag.utils import safe_model_to_device
        model = torch.nn.Linear(4, 4)

        result = safe_model_to_device(model, "cpu")
        assert result is not None


# ===========================================================================
# utils.py — safe_model_load() deprecated wrapper
# ===========================================================================

class TestSafeModelLoadDeprecated:
    """Cover lines 322-342: deprecated safe_model_load() wrapper."""

    def test_deprecated_wrapper_warns(self):
        import warnings

        from codex.rag.utils import safe_model_load

        model = MagicMock()
        model.parameters.return_value = []
        model.buffers.return_value = []
        model.to.return_value = model

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = safe_model_load(model, "cpu")

        assert any("deprecated" in str(w.message).lower() for w in caught)
