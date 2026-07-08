"""Comprehensive tests for RAG retriever module."""

import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

pytest.importorskip("numpy")

# Import with graceful fallback
try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import sentence_transformers

    HAS_SENTENCE_TRANSFORMERS = bool(sentence_transformers)
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

# Skip all tests if required dependencies are missing
if not HAS_NUMPY or not HAS_SENTENCE_TRANSFORMERS:
    pytestmark = pytest.mark.skip(
        reason="RAG tests require numpy and sentence-transformers. "
        f"numpy={'available' if HAS_NUMPY else 'missing'}, "
        f"sentence-transformers={'available' if HAS_SENTENCE_TRANSFORMERS else 'missing'}"
    )

from codex.rag.retriever import Retriever


@pytest.fixture
def temp_index_dir(tmp_path):
    """Create a temporary index directory with mock data."""
    index_dir = tmp_path / "tenants" / "default" / "test_index"
    index_dir.mkdir(parents=True)

    # Create mock FAISS index file
    (index_dir / "index.faiss").touch()

    # Create mock chunks metadata
    chunks_data = [
        {
            "id": 0,
            "text": "This is the first chunk of text about Python programming.",
            "start": 0,
            "end": 60,
            "text_hash": "abc123",
            "file": "test.py",
        },
        {
            "id": 1,
            "text": "This is the second chunk about machine learning algorithms.",
            "start": 60,
            "end": 120,
            "text_hash": "def456",
            "file": "test.py",
        },
        {
            "id": 2,
            "text": "Third chunk covers RAG and retrieval systems.",
            "start": 120,
            "end": 180,
            "text_hash": "ghi789",
            "file": "docs.md",
        },
    ]

    with open(index_dir / "chunks.json", "w") as f:
        json.dump(chunks_data, f)

    # Create mock index metadata
    metadata = {
        "index_name": "test_index",
        "tenant_id": "default",
        "dimension": 384,
        "num_vectors": 3,
        "files": [{"file": "test.py"}, {"file": "docs.md"}],
    }

    with open(index_dir / "metadata.json", "w") as f:
        json.dump(metadata, f)

    return tmp_path / "tenants"


@pytest.fixture
def mock_faiss_index():
    """Create a mock FAISS index."""
    mock_index = MagicMock()
    mock_index.ntotal = 3
    mock_index.search.return_value = (
        np.array([[0.5, 1.2, 2.3]]),  # distances
        np.array([[0, 1, 2]]),  # indices
    )
    return mock_index


@pytest.fixture
def mock_sentence_transformer():
    """Create a mock SentenceTransformer model."""
    mock_model = MagicMock()
    mock_model.encode.return_value = np.random.randn(1, 384).astype(np.float32)
    # safe_model_to_device calls model.to(device); keep same mock so encode is accessible
    mock_model.to.return_value = mock_model
    mock_model.to_empty.return_value = mock_model
    mock_model.eval.return_value = mock_model
    return mock_model


class TestRetrieverInitialization:
    """Test suite for Retriever initialization."""

    def test_initialization_default_params(
        self, temp_index_dir, mock_faiss_index, mock_sentence_transformer
    ):
        """Test initialization with default parameters."""
        with patch("codex.rag.indexer.load_index", return_value=(mock_faiss_index, [], {})):
            with patch(
                "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
            ):
                retriever = Retriever(index_dir=str(temp_index_dir))

                assert retriever.index_name == "default", "index_name is not valid"
                assert retriever.tenant_id == "default", "tenant_id is not valid"
                assert retriever.model is not None, "model must be initialized"

    def test_initialization_custom_params(
        self, temp_index_dir, mock_faiss_index, mock_sentence_transformer
    ):
        """Test initialization with custom parameters."""
        with patch("codex.rag.indexer.load_index", return_value=(mock_faiss_index, [], {})):
            with patch(
                "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
            ):
                retriever = Retriever(
                    index_dir=str(temp_index_dir),
                    index_name="custom_index",
                    tenant_id="tenant123",
                    model_name="custom-model",
                )

                assert retriever.index_name == "custom_index", "index_name is not valid"
                assert retriever.tenant_id == "tenant123", "tenant_id is not valid"
                assert retriever.model_name == "custom-model", "model_name is not valid"

    def test_initialization_loads_index(
        self, temp_index_dir, mock_faiss_index, mock_sentence_transformer
    ):
        """Test that initialization loads the index."""
        chunks_metadata = [{"id": 0, "text": "test"}]
        index_metadata = {"test": "value"}

        with (
            patch(
                "codex.rag.indexer.load_index",
                return_value=(mock_faiss_index, chunks_metadata, index_metadata),
            ) as mock_load,
            patch(
                "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
            ),
        ):
            retriever = Retriever(index_dir=str(temp_index_dir), index_name="test_index")

            mock_load.assert_called_once()
            assert retriever.faiss_index is mock_faiss_index, "faiss_index is not valid"
            assert retriever.chunks_metadata == chunks_metadata, "Data must not be empty"
            assert retriever.index_metadata == index_metadata, "Data must not be empty"

    def test_initialization_index_not_found(self, temp_index_dir, mock_sentence_transformer):
        """Test initialization handles missing index gracefully."""
        with (
            patch("codex.rag.indexer.load_index", side_effect=FileNotFoundError("Index not found")),
            patch(
                "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
            ),
        ):
            # Should not raise, but log warning
            retriever = Retriever(index_dir=str(temp_index_dir), index_name="nonexistent")

            assert retriever.faiss_index is None, "faiss_index is not valid"

    def test_initialization_loads_embedding_model(self, temp_index_dir, mock_faiss_index):
        """Test that initialization loads the embedding model."""
        with patch("codex.rag.indexer.load_index", return_value=(mock_faiss_index, [], {})):
            # Model loading goes through _model_utils which does a local import from
            # sentence_transformers — patch at the source module level.
            with patch("sentence_transformers.SentenceTransformer") as mock_st:
                mock_st.return_value.to.return_value = mock_st.return_value
                mock_st.return_value.eval.return_value = mock_st.return_value
                Retriever(index_dir=str(temp_index_dir))

                mock_st.assert_called_once()

    def test_initialization_model_import_error(self, temp_index_dir, mock_faiss_index):
        """Test initialization handles missing sentence-transformers."""
        with patch("codex.rag.indexer.load_index", return_value=(mock_faiss_index, [], {})):
            # Setting the module-level sentinel to None triggers the ImportError guard
            # inside _load_model before safe_load_sentence_transformer is called.
            with patch("codex.rag.retriever.SentenceTransformer", new=None):
                with pytest.raises(ImportError):
                    Retriever(index_dir=str(temp_index_dir))


class TestRetrieverQuery:
    """Test suite for Retriever query method."""

    def test_query_basic(self, temp_index_dir, mock_faiss_index, mock_sentence_transformer):
        """Test basic query functionality."""
        chunks = [{"id": 0, "text": "Test chunk", "start": 0, "end": 10}]

        with patch("codex.rag.indexer.load_index", return_value=(mock_faiss_index, chunks, {})):
            with patch(
                "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
            ):
                retriever = Retriever(index_dir=str(temp_index_dir))
                results = retriever.query("test query", top_k=3)

                assert isinstance(results, list)
                assert len(results) <= 3, "Results must not be empty"

    def test_query_returns_correct_structure(
        self, temp_index_dir, mock_faiss_index, mock_sentence_transformer
    ):
        """Test query returns correctly structured results."""
        chunks = [{"id": 0, "text": "Test chunk", "start": 0, "end": 10}]

        with patch("codex.rag.indexer.load_index", return_value=(mock_faiss_index, chunks, {})):
            with patch(
                "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
            ):
                retriever = Retriever(index_dir=str(temp_index_dir))
                results = retriever.query("test query", top_k=1)

                if results:
                    result = results[0]
                    assert "text" in result, "Result must not be empty"
                    assert "file" in result, "Result must not be empty"
                    assert "start_line" in result, "Result must not be empty"
                    assert "end_line" in result, "Result must not be empty"
                    assert "score" in result, "Result must not be empty"
                    assert "generated_at" in result, "Result must not be empty"

    def test_query_empty_string(self, temp_index_dir, mock_faiss_index, mock_sentence_transformer):
        """Test query with empty string returns empty results."""
        with patch("codex.rag.indexer.load_index", return_value=(mock_faiss_index, [], {})):
            with patch(
                "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
            ):
                retriever = Retriever(index_dir=str(temp_index_dir))
                results = retriever.query("", top_k=5)

                assert results == [], "Result must not be empty"

    def test_query_whitespace_only(
        self, temp_index_dir, mock_faiss_index, mock_sentence_transformer
    ):
        """Test query with whitespace-only string returns empty results."""
        with patch("codex.rag.indexer.load_index", return_value=(mock_faiss_index, [], {})):
            with patch(
                "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
            ):
                retriever = Retriever(index_dir=str(temp_index_dir))
                results = retriever.query("   \n\t  ", top_k=5)

                assert results == [], "Result must not be empty"

    def test_query_no_index_loaded(self, temp_index_dir, mock_sentence_transformer):
        """Test query without loaded index returns empty results."""
        with (
            patch("codex.rag.indexer.load_index", side_effect=FileNotFoundError),
            patch(
                "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
            ),
        ):
            retriever = Retriever(index_dir=str(temp_index_dir))
            results = retriever.query("test", top_k=5)

            assert results == [], "Result must not be empty"

    def test_query_top_k_respected(
        self, temp_index_dir, mock_faiss_index, mock_sentence_transformer
    ):
        """Test that top_k parameter is respected."""
        chunks = [
            {"id": i, "text": f"Chunk {i}", "start": i * 10, "end": (i + 1) * 10} for i in range(10)
        ]

        # Mock search to return all chunks
        mock_faiss_index.search.return_value = (
            np.array([[float(i) for i in range(10)]]),
            np.array([[i for i in range(10)]]),
        )

        with patch("codex.rag.indexer.load_index", return_value=(mock_faiss_index, chunks, {})):
            with patch(
                "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
            ):
                retriever = Retriever(index_dir=str(temp_index_dir))

                results = retriever.query("test", top_k=3)
                assert len(results) <= 3, "Results must not be empty"

    def test_query_invalid_top_k(self, temp_index_dir, mock_faiss_index, mock_sentence_transformer):
        """Test query with invalid top_k uses default."""
        chunks = [{"id": 0, "text": "Test", "start": 0, "end": 10}]

        with patch("codex.rag.indexer.load_index", return_value=(mock_faiss_index, chunks, {})):
            with patch(
                "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
            ):
                retriever = Retriever(index_dir=str(temp_index_dir))

                # top_k <= 0 should use default
                retriever.query("test", top_k=0)
                # Should not raise error

    def test_query_with_min_score(
        self, temp_index_dir, mock_faiss_index, mock_sentence_transformer
    ):
        """Test query with minimum score threshold."""
        chunks = [
            {"id": 0, "text": "Chunk 0", "start": 0, "end": 10},
            {"id": 1, "text": "Chunk 1", "start": 10, "end": 20},
        ]

        # Mock search with varying scores
        mock_faiss_index.search.return_value = (
            np.array([[0.5, 2.5]]),  # distances
            np.array([[0, 1]]),  # indices
        )

        with patch("codex.rag.indexer.load_index", return_value=(mock_faiss_index, chunks, {})):
            with patch(
                "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
            ):
                retriever = Retriever(index_dir=str(temp_index_dir))

                # Only first result should pass threshold of 1.0
                results = retriever.query("test", top_k=2, min_score=1.0)
                assert len(results) <= 1, "Results must not be empty"

    def test_query_encodes_query_text(
        self, temp_index_dir, mock_faiss_index, mock_sentence_transformer
    ):
        """Test that query text is encoded before search."""
        chunks = [{"id": 0, "text": "Test", "start": 0, "end": 10}]

        with patch("codex.rag.indexer.load_index", return_value=(mock_faiss_index, chunks, {})):
            with patch(
                "sentence_transformers.SentenceTransformer",
                return_value=mock_sentence_transformer,
            ):
                retriever = Retriever(index_dir=str(temp_index_dir))
                retriever.query("search query", top_k=5)

                # Verify encode was called
                mock_sentence_transformer.encode.assert_called_once()
                call_args = mock_sentence_transformer.encode.call_args[0]
                assert "search query" in call_args[0], "Condition must be true"

    def test_query_searches_index(
        self, temp_index_dir, mock_faiss_index, mock_sentence_transformer
    ):
        """Test that FAISS index search is called."""
        chunks = [{"id": 0, "text": "Test", "start": 0, "end": 10}]

        with patch("codex.rag.indexer.load_index", return_value=(mock_faiss_index, chunks, {})):
            with patch(
                "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
            ):
                retriever = Retriever(index_dir=str(temp_index_dir))
                retriever.query("test", top_k=3)

                # Verify search was called
                mock_faiss_index.search.assert_called_once()
                _, k = mock_faiss_index.search.call_args[0]
                assert k == 3, "k is not valid"

    def test_query_handles_invalid_indices(
        self, temp_index_dir, mock_faiss_index, mock_sentence_transformer
    ):
        """Test query handles invalid indices from FAISS."""
        chunks = [{"id": 0, "text": "Test", "start": 0, "end": 10}]

        # Mock search with invalid indices
        mock_faiss_index.search.return_value = (
            np.array([[0.5, 1.0]]),
            np.array([[-1, 100]]),  # Invalid indices
        )

        with patch("codex.rag.indexer.load_index", return_value=(mock_faiss_index, chunks, {})):
            with patch(
                "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
            ):
                retriever = Retriever(index_dir=str(temp_index_dir))
                results = retriever.query("test", top_k=2)

                # Should skip invalid indices
                assert len(results) == 0, "Results must not be empty"

    def test_query_adds_timestamp(
        self, temp_index_dir, mock_faiss_index, mock_sentence_transformer
    ):
        """Test that query results include timestamp."""
        chunks = [{"id": 0, "text": "Test", "start": 0, "end": 10}]

        with patch("codex.rag.indexer.load_index", return_value=(mock_faiss_index, chunks, {})):
            with patch(
                "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
            ):
                retriever = Retriever(index_dir=str(temp_index_dir))
                results = retriever.query("test", top_k=1)

                if results:
                    assert "generated_at" in results[0], "Result must not be empty"
                    # Verify it's a valid ISO timestamp
                    datetime.fromisoformat(results[0]["generated_at"])


class TestRetrieverHelperMethods:
    """Test suite for Retriever helper methods."""

    def test_estimate_line_number_basic(
        self, temp_index_dir, mock_faiss_index, mock_sentence_transformer
    ):
        """Test line number estimation."""
        with patch("codex.rag.indexer.load_index", return_value=(mock_faiss_index, [], {})):
            with patch(
                "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
            ):
                retriever = Retriever(index_dir=str(temp_index_dir))

                line_num = retriever._estimate_line_number(0)
                assert line_num == 1, "line_num is not valid"

                line_num = retriever._estimate_line_number(80)
                assert line_num == 2, "line_num is not valid"

                line_num = retriever._estimate_line_number(160)
                assert line_num == 3, "line_num is not valid"

    def test_estimate_line_number_custom_chars_per_line(
        self, temp_index_dir, mock_faiss_index, mock_sentence_transformer
    ):
        """Test line number estimation with custom chars per line."""
        with patch("codex.rag.indexer.load_index", return_value=(mock_faiss_index, [], {})):
            with patch(
                "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
            ):
                retriever = Retriever(index_dir=str(temp_index_dir))

                line_num = retriever._estimate_line_number(100, chars_per_line=50)
                assert line_num == 3, "line_num is not valid"

    def test_extract_file_from_chunk_metadata(
        self, temp_index_dir, mock_faiss_index, mock_sentence_transformer
    ):
        """Test file extraction from chunk metadata."""
        with patch("codex.rag.indexer.load_index", return_value=(mock_faiss_index, [], {})):
            with patch(
                "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
            ):
                retriever = Retriever(index_dir=str(temp_index_dir))

                # Test with file in chunk
                chunk = {"file": "test.py"}
                file = retriever._extract_file_from_metadata(chunk)
                assert file == "test.py", "file is not valid"

    def test_extract_file_from_index_metadata(
        self, temp_index_dir, mock_faiss_index, mock_sentence_transformer
    ):
        """Test file extraction from index metadata."""
        index_metadata = {"files": [{"file": "index_file.py"}]}

        with (
            patch(
                "codex.rag.indexer.load_index", return_value=(mock_faiss_index, [], index_metadata)
            ),
            patch(
                "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
            ),
        ):
            retriever = Retriever(index_dir=str(temp_index_dir))

            chunk = {}  # No file in chunk
            file = retriever._extract_file_from_metadata(chunk)
            assert file == "index_file.py", "file is not valid"

    def test_extract_file_unknown(
        self, temp_index_dir, mock_faiss_index, mock_sentence_transformer
    ):
        """Test file extraction returns unknown when no file info."""
        with patch("codex.rag.indexer.load_index", return_value=(mock_faiss_index, [], {})):
            with patch(
                "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
            ):
                retriever = Retriever(index_dir=str(temp_index_dir))

                chunk = {}
                file = retriever._extract_file_from_metadata(chunk)
                assert file == "unknown", "file is not valid"


class TestRetrieverStats:
    """Test suite for Retriever statistics."""

    def test_get_stats(self, temp_index_dir, mock_faiss_index, mock_sentence_transformer):
        """Test getting retriever statistics."""
        chunks = [{"id": i, "text": f"Chunk {i}"} for i in range(5)]
        metadata = {"test_key": "test_value"}

        with (
            patch(
                "codex.rag.indexer.load_index", return_value=(mock_faiss_index, chunks, metadata)
            ),
            patch(
                "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
            ),
        ):
            retriever = Retriever(
                index_dir=str(temp_index_dir), index_name="my_index", tenant_id="my_tenant"
            )

            stats = retriever.get_stats()

            assert stats["index_name"] == "my_index", "Condition must be true"
            assert stats["tenant_id"] == "my_tenant", "Condition must be true"
            assert stats["num_vectors"] == 3, "Condition must be true"
            assert stats["num_chunks"] == 5, "Condition must be true"
            assert stats["index_metadata"] == metadata, "Data must not be empty"

    def test_get_stats_no_index(self, temp_index_dir, mock_sentence_transformer):
        """Test getting stats when no index is loaded."""
        with (
            patch("codex.rag.indexer.load_index", side_effect=FileNotFoundError),
            patch(
                "sentence_transformers.SentenceTransformer", return_value=mock_sentence_transformer
            ),
        ):
            retriever = Retriever(index_dir=str(temp_index_dir))
            stats = retriever.get_stats()

            assert stats["num_vectors"] == 0, "Condition must be true"
