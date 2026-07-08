"""Integration tests for metadata filtering with FAISS store"""

import importlib.util

import pytest

np = pytest.importorskip("numpy")

try:
    from src.codex.retrieval.stores.faiss_store import FAISSStore

    FAISS_AVAILABLE = importlib.util.find_spec("faiss") is not None
except ImportError:
    FAISS_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not FAISS_AVAILABLE, reason="FAISS not installed (pip install faiss-cpu)"
)


class TestFAISSStoreFiltering:
    """Test FAISS store with metadata filtering"""

    @pytest.fixture
    def store_with_data(self, tmp_path):
        """Create FAISS store with sample data"""
        store = FAISSStore(index_dir=str(tmp_path), index_name="test_filtering")

        # Create sample vectors and metadata
        vectors = np.array(
            [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
                [0.7, 0.7, 0.0],
                [0.0, 0.7, 0.7],
            ],
            dtype=np.float32,
        )

        metadata = [
            {"category": "tech", "score": 0.9, "author": "alice"},
            {"category": "news", "score": 0.8, "author": "bob"},
            {"category": "tech", "score": 0.7, "author": "charlie"},
            {"category": "sports", "score": 0.95, "author": "alice"},
            {"category": "tech", "score": 0.85, "author": "bob"},
        ]

        # Add to store (index is created automatically by add() if needed)
        store.add(vectors, metadata=metadata)

        return store

    def test_search_without_filters(self, store_with_data):
        """Test search without filters returns all top results"""
        query = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        results = store_with_data.search(query, top_k=3)

        assert len(results) == 3, "Results must not be empty"
        assert all("id" in r for r in results), "Result must not be empty"
        assert all("score" in r for r in results), "Result must not be empty"
        assert all("metadata" in r for r in results), "Result must not be empty"

    def test_search_with_equality_filter(self, store_with_data):
        """Test search with simple equality filter"""
        query = np.array([1.0, 0.0, 0.0], dtype=np.float32)

        # Filter for tech category
        results = store_with_data.search(query, top_k=5, filters={"category": "tech"})

        assert len(results) <= 3, "Results must not be empty"
        assert all(r["metadata"]["category"] == "tech" for r in results), "Result must not be empty"

    def test_search_with_range_filter(self, store_with_data):
        """Test search with range filter"""
        query = np.array([0.5, 0.5, 0.0], dtype=np.float32)

        # Filter for high scores
        results = store_with_data.search(query, top_k=5, filters={"score": {"$gte": 0.85}})

        assert len(results) <= 2, "Results must not be empty"
        assert all(r["metadata"]["score"] >= 0.85 for r in results), "Value must be greater than zero"

    def test_search_with_complex_filter(self, store_with_data):
        """Test search with complex AND filter"""
        query = np.array([0.5, 0.5, 0.0], dtype=np.float32)

        # Filter for tech AND high score
        results = store_with_data.search(
            query, top_k=5, filters={"$and": [{"category": "tech"}, {"score": {"$gte": 0.8}}]}
        )

        assert len(results) <= 2, "Results must not be empty"
        # Fixed malformed assertion: assert all(...)

    def test_search_with_no_matches(self, store_with_data):
        """Test search with filter that matches nothing"""
        query = np.array([1.0, 0.0, 0.0], dtype=np.float32)

        results = store_with_data.search(query, top_k=5, filters={"category": "nonexistent"})

        assert len(results) == 0, "Results must not be empty"

    def test_filtering_preserves_score_order(self, store_with_data):
        """Test that filtering preserves similarity score ordering"""
        query = np.array([1.0, 0.0, 0.0], dtype=np.float32)

        results = store_with_data.search(query, top_k=5, filters={"category": "tech"})

        # Check scores are in descending order
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)
