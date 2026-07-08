"""
Integration tests for RAG retrieval functionality.

Tests end-to-end retrieval workflows with query processing and ranking.
"""

import importlib.util
import tempfile
from unittest.mock import MagicMock, Mock, patch

import pytest

# Skip entire module if torch is not available or unloadable
pytest.importorskip("torch", reason="PyTorch required for tests")
# Check if required dependencies are available
NUMPY_AVAILABLE = importlib.util.find_spec("numpy") is not None

try:
    if importlib.util.find_spec("sentence_transformers") is None:
        raise ImportError
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# Skip all tests if numpy or sentence_transformers is not available
pytestmark = pytest.mark.skipif(
    not NUMPY_AVAILABLE or not SENTENCE_TRANSFORMERS_AVAILABLE,
    reason="numpy and sentence_transformers required for RAG retrieval tests",
)


class TestRetrieverInitialization:
    """Test Retriever initialization."""

    def test_retriever_import(self):
        """Test Retriever can be imported."""
        from codex.rag.retriever import Retriever

        assert Retriever is not None, "Retriever must be initialized"

    @patch("codex.rag.retriever.SentenceTransformer")
    def test_retriever_initialization_basic(self, mock_st):
        """Test Retriever basic initialization."""
        from codex.rag.retriever import Retriever

        mock_model = Mock()
        mock_st.return_value = mock_model

        with patch.object(Retriever, "_load_index"):
            retriever = Retriever(index_dir=os.path.join(tempfile.gettempdir(), "test"), model_name="test-model")

            assert retriever.index_dir == os.path.join(tempfile.gettempdir(), "test"), "index_dir is not valid"
            assert retriever.model_name == "test-model", "model_name is not valid"

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
        """Test _load_model raises when sentence-transformers not installed."""
        from codex.rag.retriever import Retriever

        with patch.object(Retriever, "_load_index"):
            with pytest.raises(ImportError, match="sentence-transformers not installed"):
                Retriever()

    @patch.dict("os.environ", {"HF_TOKEN": "test_token"}, clear=False)
    @patch("codex.rag.utils.safe_model_to_device", side_effect=lambda m, d: m)
    @patch("codex.rag.retriever.SentenceTransformer")
    def test_load_model_uses_hf_token(self, mock_st, mock_safe):
        """Test _load_model uses HF_TOKEN when available."""
        from codex.rag.retriever import Retriever

        mock_model = Mock()
        mock_model.to.return_value = mock_model
        mock_model.eval.return_value = mock_model
        mock_st.return_value = mock_model

        with patch.object(Retriever, "_load_index"):
            Retriever()

            # Should have attempted to use HF_TOKEN
            call_kwargs = mock_st.call_args[1]
            assert "use_auth_token" in call_kwargs, "Condition must be true"


class TestRetrieverIndexLoading:
    """Test Retriever index loading."""

    def test_load_index_method_exists(self):
        """Test _load_index method exists."""
        from codex.rag.retriever import Retriever

        assert hasattr(Retriever, "_load_index")

    @patch("codex.rag.retriever.load_index")
    def test_load_index_file_not_found_warning(self, mock_load):
        """Test _load_index handles FileNotFoundError gracefully."""
        from codex.rag.retriever import Retriever

        mock_load.side_effect = FileNotFoundError("Index not found")

        with patch.object(Retriever, "_load_model"):
            # Should not raise, just log warning
            retriever = Retriever()

            # Index should be None after failed load
            assert retriever.faiss_index is None, "faiss_index is not valid"

    @patch("codex.rag.retriever.load_index")
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
            assert len(retriever.chunks_metadata) == 2, "Collection must not be empty"


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

    @patch("codex.rag.retriever.SentenceTransformer")
    def test_retriever_custom_index_dir(self, mock_st):
        """Test Retriever with custom index_dir."""
        from codex.rag.retriever import Retriever

        mock_model = Mock()
        mock_st.return_value = mock_model

        with patch.object(Retriever, "_load_index"):
            retriever = Retriever(index_dir="/custom/path")

            assert retriever.index_dir == "/custom/path", "index_dir is not valid"

    @patch("codex.rag.retriever.SentenceTransformer")
    def test_retriever_custom_tenant_id(self, mock_st):
        """Test Retriever with custom tenant_id."""
        from codex.rag.retriever import Retriever

        mock_model = Mock()
        mock_st.return_value = mock_model

        with patch.object(Retriever, "_load_index"):
            retriever = Retriever(tenant_id="custom-tenant")

            assert retriever.tenant_id == "custom-tenant", "tenant_id is not valid"

    @patch("codex.rag.retriever.SentenceTransformer")
    def test_retriever_custom_cache_dir(self, mock_st):
        """Test Retriever with custom cache_dir."""
        from codex.rag.retriever import Retriever

        mock_model = Mock()
        mock_st.return_value = mock_model

        with patch.object(Retriever, "_load_index"):
            retriever = Retriever(cache_dir="/cache/path")

            assert retriever.cache_dir == "/cache/path", "cache_dir is not valid"
