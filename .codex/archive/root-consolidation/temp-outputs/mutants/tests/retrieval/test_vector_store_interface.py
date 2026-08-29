"""
Tests for VectorStore Interface and FAISS Implementation
"""

import tempfile

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("faiss", reason="faiss-cpu not installed (pip install faiss-cpu)")
from codex.retrieval.stores.base import (
    DimensionMismatchError,
    VectorNotFoundError,
    VectorStore,
)
from codex.retrieval.stores.faiss_store import FAISSStore


class TestVectorStoreInterface:
    """Test that FAISS Store implements VectorStore interface correctly"""

    def test_faiss_implements_interface(self):
        """Test that FAISSStore is a VectorStore"""
        store = FAISSStore()
        assert isinstance(store, VectorStore)

    def test_has_all_required_methods(self):
        """Test that FAISSStore has all required interface methods"""
        store = FAISSStore()

        # Check all required methods exist
        assert hasattr(store, "add")
        assert hasattr(store, "search")
        assert hasattr(store, "delete")
        assert hasattr(store, "get")
        assert hasattr(store, "count")
        assert hasattr(store, "clear")
        assert hasattr(store, "save")
        assert hasattr(store, "load")
        assert hasattr(store, "health_check")

        # Check they're callable
        assert callable(store.add), "Condition must be true"
        assert callable(store.search), "Condition must be true"
        assert callable(store.delete), "Condition must be true"
        assert callable(store.get), "Condition must be true"
        assert callable(store.count), "Count must be greater than zero"
        assert callable(store.clear), "Condition must be true"
        assert callable(store.save), "Condition must be true"
        assert callable(store.load), "Condition must be true"
        assert callable(store.health_check), "Condition must be true"


class TestFAISSStoreAdd:
    """Test vector addition"""

    def test_add_vectors_basic(self):
        """Test adding vectors without IDs"""
        store = FAISSStore()

        vectors = np.random.randn(10, 128).astype(np.float32)
        ids = store.add(vectors)

        assert len(ids) == 10, "Ids must not be empty"
        assert store.count() == 10, "Count must be greater than zero"
        assert all(isinstance(vid, str) for vid in ids)

    def test_add_vectors_with_custom_ids(self):
        """Test adding vectors with custom IDs"""
        store = FAISSStore()

        vectors = np.random.randn(5, 64).astype(np.float32)
        custom_ids = [f"vec-{i}" for i in range(5)]

        ids = store.add(vectors, ids=custom_ids)

        assert ids == custom_ids, "ids is not valid"
        assert store.count() == 5, "Count must be greater than zero"

    def test_add_vectors_with_metadata(self):
        """Test adding vectors with metadata"""
        store = FAISSStore()

        vectors = np.random.randn(3, 32).astype(np.float32)
        metadata = [
            {"text": "hello", "category": "greeting"},
            {"text": "world", "category": "noun"},
            {"text": "test", "category": "verb"},
        ]

        ids = store.add(vectors, metadata=metadata)

        assert len(ids) == 3, "Ids must not be empty"

        # Retrieve and check metadata
        results = store.get(ids[0])
        assert results[0]["metadata"] == metadata[0], "Result must not be empty"

    def test_add_dimension_validation(self):
        """Test that dimension is validated"""
        store = FAISSStore()

        # Add first batch
        vectors1 = np.random.randn(5, 64).astype(np.float32)
        store.add(vectors1)

        # Try to add with wrong dimension
        vectors2 = np.random.randn(3, 32).astype(np.float32)

        with pytest.raises(DimensionMismatchError):
            store.add(vectors2)

    def test_add_invalid_vectors(self):
        """Test adding invalid vectors"""
        store = FAISSStore()

        # Not a numpy array
        with pytest.raises(TypeError):
            store.add([[1, 2, 3]])

        # Wrong shape
        with pytest.raises(ValueError):
            store.add(np.random.randn(10))

        # NaN values
        vectors = np.random.randn(5, 32).astype(np.float32)
        vectors[0, 0] = np.nan
        with pytest.raises(ValueError):
            store.add(vectors)

    def test_add_mismatched_metadata(self):
        """Test that metadata count must match vector count"""
        store = FAISSStore()

        vectors = np.random.randn(5, 32).astype(np.float32)
        metadata = [{"text": "test"}]  # Only 1 metadata for 5 vectors

        with pytest.raises(ValueError, match="must match"):
            store.add(vectors, metadata=metadata)

    def test_add_duplicate_ids(self):
        """Test that duplicate IDs are rejected"""
        store = FAISSStore()

        vectors = np.random.randn(3, 32).astype(np.float32)
        ids = ["id1", "id2", "id3"]

        store.add(vectors, ids=ids)

        # Try to add with duplicate ID
        vectors2 = np.random.randn(1, 32).astype(np.float32)
        with pytest.raises(ValueError, match="Duplicate IDs"):
            store.add(vectors2, ids=["id1"])


class TestFAISSStoreSearch:
    """Test vector search"""

    def test_search_basic(self):
        """Test basic search"""
        store = FAISSStore()

        # Add vectors
        vectors = np.random.randn(20, 64).astype(np.float32)
        store.add(vectors)

        # Search
        query = vectors[0]  # Use first vector as query
        results = store.search(query, top_k=5)

        assert len(results) <= 5, "Results must not be empty"
        assert all("score" in r for r in results), "Result must not be empty"
        assert all("document" in r for r in results), "Result must not be empty"

    def test_search_with_metadata(self):
        """Test search returns metadata"""
        store = FAISSStore()

        vectors = np.random.randn(10, 32).astype(np.float32)
        metadata = [{"text": f"doc-{i}"} for i in range(10)]

        store.add(vectors, metadata=metadata)

        query = vectors[0]
        results = store.search(query, top_k=3)

        assert len(results) > 0, "Results must not be empty"
        assert "metadata" in results[0]["document"], "Result must not be empty"

    def test_search_top_k(self):
        """Test that k parameter works"""
        store = FAISSStore()

        vectors = np.random.randn(50, 64).astype(np.float32)
        store.add(vectors)

        query = np.random.randn(64).astype(np.float32)

        for k in [1, 5, 10]:
            results = store.search(query, top_k=k)
            assert len(results) <= k, "Results must not be empty"

    def test_search_invalid_query(self):
        """Test search with invalid query"""
        store = FAISSStore()

        vectors = np.random.randn(10, 64).astype(np.float32)
        store.add(vectors)

        # Wrong dimension
        query = np.random.randn(32).astype(np.float32)
        with pytest.raises(ValueError, match="dimension"):
            store.search(query)

        # NaN values
        query = np.random.randn(64).astype(np.float32)
        query[0] = np.nan
        with pytest.raises(ValueError):
            store.search(query)


class TestFAISSStoreGetDelete:
    """Test get and delete operations"""

    def test_get_by_id(self):
        """Test retrieving vectors by ID"""
        store = FAISSStore()

        vectors = np.random.randn(5, 32).astype(np.float32)
        ids = store.add(vectors)

        # Get single vector
        results = store.get(ids[0])
        assert len(results) == 1, "Results must not be empty"
        assert results[0]["id"] == ids[0], "Result must not be empty"

        # Get multiple vectors
        results = store.get([ids[0], ids[2]])
        assert len(results) == 2, "Results must not be empty"
        assert results[0]["id"] == ids[0], "Result must not be empty"
        assert results[1]["id"] == ids[2], "Result must not be empty"

    def test_get_nonexistent_id(self):
        """Test getting non-existent ID raises error"""
        store = FAISSStore()

        vectors = np.random.randn(3, 32).astype(np.float32)
        store.add(vectors)

        with pytest.raises(VectorNotFoundError):
            store.get("nonexistent-id")

    def test_delete_by_id(self):
        """Test deleting vectors by ID"""
        store = FAISSStore()

        vectors = np.random.randn(10, 32).astype(np.float32)
        ids = store.add(vectors)

        # Delete single vector
        deleted = store.delete(ids[0])
        assert deleted == 1, "deleted is not valid"
        assert store.count() == 9, "Count must be greater than zero"

        # Verify it's gone
        with pytest.raises(VectorNotFoundError):
            store.get(ids[0])

    def test_delete_multiple(self):
        """Test deleting multiple vectors"""
        store = FAISSStore()

        vectors = np.random.randn(10, 32).astype(np.float32)
        ids = store.add(vectors)

        # Delete multiple
        deleted = store.delete([ids[0], ids[1], ids[2]])
        assert deleted == 3, "deleted is not valid"
        assert store.count() == 7, "Count must be greater than zero"


class TestFAISSStorePersistence:
    """Test save and load operations"""

    def test_save_and_load(self):
        """Test saving and loading index"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and populate store
            store = FAISSStore(index_dir=tmpdir, index_name="test")

            vectors = np.random.randn(20, 64).astype(np.float32)
            metadata = [{"text": f"doc-{i}"} for i in range(20)]
            ids = store.add(vectors, metadata=metadata)

            # Save
            store.save()

            # Create new store and load
            store2 = FAISSStore(index_dir=tmpdir, index_name="test")
            store2.load()

            assert store2.count() == 20, "Count must be greater than zero"
            assert store2.dimension == 64, "dimension is not valid"

            # Verify IDs are preserved
            results = store2.get(ids[0])
            assert results[0]["id"] == ids[0], "Result must not be empty"
            assert results[0]["metadata"] == metadata[0], "Result must not be empty"

    def test_load_nonexistent(self):
        """Test loading non-existent index"""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = FAISSStore(index_dir=tmpdir, index_name="nonexistent")

            with pytest.raises(FileNotFoundError):
                store.load()


class TestFAISSStoreUtilities:
    """Test utility methods"""

    def test_count(self):
        """Test count method"""
        store = FAISSStore()

        assert store.count() == 0, "Count must be greater than zero"

        vectors = np.random.randn(10, 32).astype(np.float32)
        store.add(vectors)

        assert store.count() == 10, "Count must be greater than zero"

    def test_clear(self):
        """Test clear method"""
        store = FAISSStore()

        vectors = np.random.randn(15, 64).astype(np.float32)
        store.add(vectors)

        assert store.count() == 15, "Count must be greater than zero"

        store.clear()

        assert store.count() == 0, "Count must be greater than zero"
        assert store.index is None, "index is not valid"

    def test_health_check(self):
        """Test health check"""
        store = FAISSStore()

        # Empty store
        health = store.health_check()
        assert health["healthy"] is False, "Condition must be true"
        assert health["index_loaded"] is False, "Condition must be true"
        assert health["backend"] == "faiss", "Condition must be true"

        # With data
        vectors = np.random.randn(5, 32).astype(np.float32)
        store.add(vectors)

        health = store.health_check()
        assert health["healthy"] is True, "Condition must be true"
        assert health["index_loaded"] is True, "Condition must be true"
        assert health["num_vectors"] == 5, "Condition must be true"
        assert health["dimension"] == 32, "Condition must be true"


class TestFAISSStoreIntegration:
    """Integration tests for end-to-end workflows"""

    def test_full_workflow(self):
        """Test complete add -> search -> save -> load -> search workflow"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create store and add data
            store = FAISSStore(index_dir=tmpdir, index_name="integration")

            vectors = np.random.randn(100, 128).astype(np.float32)
            metadata = [{"id": i, "text": f"document-{i}"} for i in range(100)]
            store.add(vectors, metadata=metadata)

            # Search
            query = vectors[0]
            results1 = store.search(query, top_k=10)
            assert len(results1) == 10, "Results1 must not be empty"

            # Save
            store.save()

            # Load in new store
            store2 = FAISSStore(index_dir=tmpdir, index_name="integration")
            store2.load()

            # Search again
            results2 = store2.search(query, top_k=10)
            assert len(results2) == 10, "Results2 must not be empty"

            # Results should be similar
            assert results1[0]["document"]["id"] == results2[0]["document"]["id"], "Result must not be empty"

    def test_incremental_additions(self):
        """Test adding vectors incrementally"""
        store = FAISSStore()

        # Add in batches
        for batch in range(5):
            vectors = np.random.randn(10, 64).astype(np.float32)
            metadata = [{"batch": batch, "idx": i} for i in range(10)]
            store.add(vectors, metadata=metadata)

        assert store.count() == 50, "Count must be greater than zero"

        # Search should work across all batches
        query = np.random.randn(64).astype(np.float32)
        results = store.search(query, top_k=20)

        # Check we get results from different batches
        batches = set(r["document"]["metadata"]["batch"] for r in results)
        assert len(batches) > 1, "Batches must not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
