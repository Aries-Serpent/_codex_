"""
Integration tests for RAG retrieval functionality.

Tests end-to-end retrieval workflows with query processing and ranking.
"""

from types import ModuleType
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest


@pytest.fixture
def model_loader():
    """Isolate neural loading at its real boundary; never download model weights."""
    with (
        patch("codex.rag.retriever.SentenceTransformer"),
        patch("aries_serpent_core.rag._model_utils.safe_load_sentence_transformer") as loader,
    ):
        yield loader


class TestRetrieverInitialization:
    """Test Retriever initialization."""

    def test_retriever_import(self):
        """Test Retriever can be imported."""
        from codex.rag.retriever import Retriever

        assert Retriever is not None, "Retriever must be initialized"

    def test_retriever_initialization_basic(self, model_loader, tmp_path):
        """Test Retriever basic initialization."""
        from codex.rag.retriever import Retriever

        with patch.object(Retriever, "_load_index"):
            retriever = Retriever(index_dir=str(tmp_path), model_name="test-model")

        assert retriever.index_dir == str(tmp_path)
        assert retriever.model_name == "test-model"
        assert retriever.model is model_loader.return_value
        model_loader.assert_called_once_with("test-model", None)

    def test_retriever_has_required_attributes(self):
        """Test Retriever has required attributes."""
        from codex.rag.retriever import Retriever

        with patch.object(Retriever, "_load_index"), patch.object(Retriever, "_load_model"):
            r = Retriever()

            assert hasattr(r, "index_dir")
            assert hasattr(r, "index_name")
            assert hasattr(r, "tenant_id")
            assert hasattr(r, "model_name")


class TestRetrieverQuery:
    """Test Retriever query functionality."""

    def test_query_method_exists(self):
        """Test query method exists."""
        from codex.rag.retriever import Retriever

        with patch.object(Retriever, "_load_index"), patch.object(Retriever, "_load_model"):
            retriever = Retriever()

            assert hasattr(retriever, "query")
            assert callable(retriever.query), "Condition must be true"

    def test_query_empty_returns_empty_list(self):
        """Test query with empty string returns empty list."""
        from codex.rag.retriever import Retriever

        with patch.object(Retriever, "_load_index"), patch.object(Retriever, "_load_model"):
            retriever = Retriever()
            retriever.faiss_index = MagicMock()

            result = retriever.query("")

            assert result == [], "Result must not be empty"

    def test_query_no_index_returns_empty_list(self):
        """Test query without index returns empty list."""
        from codex.rag.retriever import Retriever

        with patch.object(Retriever, "_load_index"), patch.object(Retriever, "_load_model"):
            retriever = Retriever()
            retriever.faiss_index = None

            result = retriever.query("test query")

            assert result == [], "Result must not be empty"

    def test_query_invalid_top_k_uses_default(self):
        """Test query with invalid top_k uses default."""
        from codex.rag.retriever import Retriever

        with patch.object(Retriever, "_load_index"), patch.object(Retriever, "_load_model"):
            retriever = Retriever()
            retriever.faiss_index = None

            # Should not crash with invalid top_k
            result = retriever.query("test", top_k=0)
            assert result == [], "Result must not be empty"

            result = retriever.query("test", top_k=-1)
            assert result == [], "Result must not be empty"


class TestRetrieverModelLoading:
    """Test Retriever model loading."""

    def test_load_model_method_exists(self):
        """Test _load_model method exists."""
        from codex.rag.retriever import Retriever

        assert hasattr(Retriever, "_load_model")

    @patch("codex.rag.retriever.SentenceTransformer", None)
    def test_load_model_without_sentence_transformers_raises(self):
        """Without neural dependencies, an empty corpus cannot fit the fallback."""
        from codex.rag.retriever import Retriever

        with patch.object(Retriever, "_load_index"):
            with pytest.raises(ImportError, match="TF-IDF fallback requires chunk text metadata"):
                Retriever()

    def test_load_model_uses_hf_token(self, monkeypatch, tmp_path):
        """Exercise the shared loader and assert the external constructor contract."""
        from codex.rag.retriever import Retriever

        monkeypatch.setenv("HF_TOKEN", "test_token")
        model = Mock(spec=["eval"])
        constructor = Mock(return_value=model)
        dependency = ModuleType("sentence_transformers")
        dependency.SentenceTransformer = constructor
        with (
            patch.dict("sys.modules", {"sentence_transformers": dependency}),
            patch("codex.rag.retriever.SentenceTransformer", constructor),
            patch("aries_serpent_core.rag.utils.safe_model_to_device", return_value=model) as move,
            patch.object(Retriever, "_load_index"),
        ):
            retriever = Retriever(model_name="test-model", cache_dir=str(tmp_path))

        constructor.assert_called_once_with(
            "test-model",
            device="cpu",
            cache_folder=str(tmp_path),
            trust_remote_code=False,
            use_auth_token="test_token",
        )
        move.assert_called_once_with(model, "cpu")
        model.eval.assert_called_once_with()
        assert retriever.model is model

    @patch("codex.rag.retriever.SentenceTransformer", None)
    def test_load_model_without_sentence_transformers_fits_indexed_chunks(self):
        """The supported offline fallback must fit real TF-IDF query embeddings."""
        from aries_serpent_core.rag.embeddings import TfidfEmbeddingProvider
        from codex.rag.retriever import Retriever

        chunks = [{"text": "oranges fruit orchard"}, {"text": "python software code"}]
        with patch(
            "aries_serpent_core.rag.indexer.load_index",
            return_value=(None, chunks, {"dimension": 8}),
        ):
            retriever = Retriever()

        # The provider is imported canonically by the retriever.
        assert isinstance(retriever.model, TfidfEmbeddingProvider)
        embedding = retriever.model.encode(["oranges fruit"])
        assert embedding.shape[0] == 1
        assert np.isfinite(embedding).all()
        assert np.linalg.norm(embedding) > 0
        assert retriever.model.is_fitted


class TestRetrieverIndexLoading:
    """Test Retriever index loading."""

    def test_load_index_method_exists(self):
        """Test _load_index method exists."""
        from codex.rag.retriever import Retriever

        assert hasattr(Retriever, "_load_index")

    @patch("aries_serpent_core.rag.indexer.load_index")
    def test_load_index_file_not_found_warning(self, mock_load, caplog):
        """Test _load_index handles FileNotFoundError gracefully."""
        from codex.rag.retriever import Retriever

        mock_load.side_effect = FileNotFoundError("Index not found")

        with patch.object(Retriever, "_load_model"):
            # Should not raise, just log warning
            retriever = Retriever()

            # Index should be None after failed load
            assert retriever.faiss_index is None, "faiss_index is not valid"
        assert any("Index not found" in message for message in caplog.messages)
        mock_load.assert_called_once_with(
            index_name="default", tenant_id="default", index_dir=".codex/tenants"
        )

    @patch("aries_serpent_core.rag.indexer.load_index")
    def test_load_index_success(self, mock_load):
        """Test _load_index successful loading."""
        from codex.rag.retriever import Retriever

        mock_index = MagicMock()
        mock_metadata = [{"text": "chunk1"}, {"text": "chunk2"}]
        mock_index_meta = {"version": "1.0"}

        mock_load.return_value = (mock_index, mock_metadata, mock_index_meta)

        with patch.object(Retriever, "_load_model"):
            retriever = Retriever()

            assert retriever.faiss_index == mock_index, "faiss_index is not valid"
            assert retriever.chunks_metadata == mock_metadata
            assert retriever.index_metadata == mock_index_meta
        mock_load.assert_called_once_with(
            index_name="default", tenant_id="default", index_dir=".codex/tenants"
        )


class TestRetrieverHelperMethods:
    """Test Retriever helper methods."""

    def test_estimate_line_number_method_exists(self):
        """Test _estimate_line_number method exists."""
        from codex.rag.retriever import Retriever

        with patch.object(Retriever, "_load_index"), patch.object(Retriever, "_load_model"):
            retriever = Retriever()

            assert hasattr(retriever, "_estimate_line_number")

    def test_extract_file_from_metadata_method_exists(self):
        """Test _extract_file_from_metadata method exists."""
        from codex.rag.retriever import Retriever

        with patch.object(Retriever, "_load_index"), patch.object(Retriever, "_load_model"):
            retriever = Retriever()

            assert hasattr(retriever, "_extract_file_from_metadata")


class TestRetrieverConfiguration:
    """Test Retriever configuration options."""

    def test_retriever_custom_index_dir(self, model_loader, tmp_path):
        """Test Retriever with custom index_dir."""
        from codex.rag.retriever import Retriever

        with patch.object(Retriever, "_load_index"):
            retriever = Retriever(index_dir=str(tmp_path))

        assert retriever.index_dir == str(tmp_path)
        model_loader.assert_called_once_with(retriever.model_name, None)

    def test_retriever_custom_tenant_id(self, model_loader):
        """Test Retriever with custom tenant_id."""
        from codex.rag.retriever import Retriever

        with patch.object(Retriever, "_load_index"):
            retriever = Retriever(tenant_id="custom-tenant")

        assert retriever.tenant_id == "custom-tenant"
        model_loader.assert_called_once_with(retriever.model_name, None)

    def test_retriever_custom_cache_dir(self, model_loader, tmp_path):
        """Test Retriever with custom cache_dir."""
        from codex.rag.retriever import Retriever

        with patch.object(Retriever, "_load_index"):
            retriever = Retriever(cache_dir=str(tmp_path))

        assert retriever.cache_dir == str(tmp_path)
        model_loader.assert_called_once_with(retriever.model_name, str(tmp_path))
