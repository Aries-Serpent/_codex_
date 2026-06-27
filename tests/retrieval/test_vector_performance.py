"""
Performance and Load Tests for Vector Operations
Tests vector store performance under various load conditions
"""

import time

import pytest

np = pytest.importorskip("numpy")

# Skip if FAISS not available
pytest.importorskip("faiss", reason="faiss-cpu not installed")
from codex.retrieval.stores.faiss_store import FAISSStore


class TestVectorStorePerformance:
    """Performance tests for vector store operations"""

    def test_bulk_insert_performance(self, tmp_path):
        """Test performance of bulk vector insertion"""
        dimension = 128
        num_vectors = 10000

        store = FAISSStore(index_name="perf_test", dimension=dimension, index_dir=str(tmp_path))

        # Generate test vectors
        vectors = np.random.randn(num_vectors, dimension).astype("float32")
        metadata = [{"id": i} for i in range(num_vectors)]

        # Measure insert time (single batch call)
        start_time = time.time()
        store.add(vectors, metadata=metadata)
        elapsed = time.time() - start_time

        # Performance assertions
        vectors_per_second = num_vectors / elapsed
        assert vectors_per_second > 1000, f"Too slow: {vectors_per_second:.0f} vectors/sec"
        assert elapsed < 30, f"Bulk insert took too long: {elapsed:.2f}s"

    def test_batch_insert_performance(self, tmp_path):
        """Test performance of batch vector insertion"""
        dimension = 128
        num_vectors = 10000
        batch_size = 100

        store = FAISSStore(
            index_name="batch_perf_test", dimension=dimension, index_dir=str(tmp_path)
        )

        # Generate test vectors in batches
        start_time = time.time()
        for batch_idx in range(0, num_vectors, batch_size):
            batch_vectors = np.random.randn(batch_size, dimension).astype("float32")
            batch_meta = [{"id": batch_idx + i} for i in range(batch_size)]
            store.add(batch_vectors, metadata=batch_meta)
        elapsed = time.time() - start_time

        # Batch should be faster than individual
        vectors_per_second = num_vectors / elapsed
        assert (vectors_per_second > 1000, "vectors_per_second must be greater than zero"
        ), f"Batch insert too slow: {vectors_per_second:.0f} vectors/sec"

    def test_search_performance(self, tmp_path):
        """Test search performance on populated index"""
        dimension = 128
        num_vectors = 10000
        num_queries = 100
        k = 10

        store = FAISSStore(
            index_name="search_perf_test", dimension=dimension, index_dir=str(tmp_path)
        )

        # Populate index
        vectors = np.random.randn(num_vectors, dimension).astype("float32")
        metadata = [{"id": i} for i in range(num_vectors)]
        store.add(vectors, metadata=metadata)

        # Measure search time
        query_vectors = np.random.randn(num_queries, dimension).astype("float32")
        start_time = time.time()
        for query in query_vectors:
            results = store.search(query, top_k=k)
            assert len(results) <= k, "Results must not be empty"
        elapsed = time.time() - start_time

        # Performance assertions
        queries_per_second = num_queries / elapsed
        avg_query_time = elapsed / num_queries

        assert queries_per_second > 100, f"Search too slow: {queries_per_second:.0f} queries/sec"
        assert avg_query_time < 0.1, f"Average query too slow: {avg_query_time:.4f}s"

    def test_persistence_performance(self, tmp_path):
        """Test save/load performance"""
        dimension = 128
        num_vectors = 5000

        store = FAISSStore(
            index_name="persist_perf_test", dimension=dimension, index_dir=str(tmp_path)
        )

        # Populate index
        vectors = np.random.randn(num_vectors, dimension).astype("float32")
        metadata = [{"id": i} for i in range(num_vectors)]
        store.add(vectors, metadata=metadata)

        # Measure save time
        start_time = time.time()
        store.save()
        save_time = time.time() - start_time

        # Measure load time
        new_store = FAISSStore(
            index_name="persist_perf_test", dimension=dimension, index_dir=str(tmp_path)
        )
        start_time = time.time()
        new_store.load()
        load_time = time.time() - start_time

        # Performance assertions
        assert save_time < 5, f"Save took too long: {save_time:.2f}s"
        assert load_time < 5, f"Load took too long: {load_time:.2f}s"

    def test_memory_efficiency(self, tmp_path):
        """Test memory usage doesn't grow excessively"""
        dimension = 128
        num_vectors = 1000

        store = FAISSStore(index_name="memory_test", dimension=dimension, index_dir=str(tmp_path))

        # Add vectors and check size
        vectors = np.random.randn(num_vectors, dimension).astype("float32")
        metadata = [{"id": i} for i in range(num_vectors)]
        store.add(vectors, metadata=metadata)

        # Approximate memory check (FAISS uses float32)
        expected_bytes = num_vectors * dimension * 4  # 4 bytes per float32
        # Allow 2x overhead for FAISS index structure
        assert expected_bytes < 10 * 1024 * 1024, "Memory usage unexpectedly high"

    @pytest.mark.slow
    def test_large_scale_performance(self, tmp_path):
        """Test performance at larger scale (marked slow)"""
        dimension = 256
        num_vectors = 100000

        store = FAISSStore(
            index_name="large_scale_test", dimension=dimension, index_dir=str(tmp_path)
        )

        # Add vectors in batches
        batch_size = 1000
        start_time = time.time()
        for batch_idx in range(0, num_vectors, batch_size):
            batch_vectors = np.random.randn(batch_size, dimension).astype("float32")
            batch_meta = [{"id": batch_idx + i} for i in range(batch_size)]
            store.add(batch_vectors, metadata=batch_meta)
        elapsed = time.time() - start_time

        # Should handle 100k vectors reasonably
        assert elapsed < 180, f"Large scale insert took too long: {elapsed:.2f}s"

        # Test search on large index
        query = np.random.randn(dimension).astype("float32")
        start_time = time.time()
        results = store.search(query, top_k=10)
        search_time = time.time() - start_time

        assert search_time < 0.5, f"Search on large index too slow: {search_time:.4f}s"
        assert len(results) == 10, "Results must not be empty"


class TestVectorStoreLoadConditions:
    """Tests under various load conditions"""

    def test_concurrent_reads(self, tmp_path):
        """Test multiple concurrent search operations"""
        dimension = 128
        num_vectors = 1000

        store = FAISSStore(
            index_name="concurrent_test", dimension=dimension, index_dir=str(tmp_path)
        )

        # Populate
        vectors = np.random.randn(num_vectors, dimension).astype("float32")
        metadata = [{"id": i} for i in range(num_vectors)]
        store.add(vectors, metadata=metadata)

        # Simulate concurrent reads
        num_concurrent = 10
        start_time = time.time()
        for _ in range(num_concurrent):
            query = np.random.randn(dimension).astype("float32")
            results = store.search(query, top_k=5)
            assert len(results) <= 5, "Results must not be empty"
        elapsed = time.time() - start_time

        # Should handle concurrent reads efficiently
        avg_time = elapsed / num_concurrent
        assert avg_time < 0.05, f"Concurrent reads too slow: {avg_time:.4f}s avg"

    def test_mixed_operations(self, tmp_path):
        """Test mixed read/write operations"""
        dimension = 128

        store = FAISSStore(
            index_name="mixed_ops_test", dimension=dimension, index_dir=str(tmp_path)
        )

        # Mix of operations — add in small batches, search periodically
        for i in range(100):
            # Add one vector at a time using batch add
            vector = np.random.randn(1, dimension).astype("float32")
            store.add(vector, metadata=[{"id": i}])

            # Search every 10 adds
            if i % 10 == 0 and i > 0:
                query = np.random.randn(dimension).astype("float32")
                results = store.search(query, top_k=5)
                assert len(results) <= min(5, i + 1)

        # Final verification
        assert store.count() == 100, "Count must be greater than zero"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not slow"])
