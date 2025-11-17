"""
Comprehensive tests for FAISS Vector Store with safeguards
"""
import numpy as np
import pytest
import tempfile

from src.codex.retrieval.stores.faiss_store import FAISSStore, MAX_VECTORS


@pytest.fixture
def temp_index_dir():
    """Create temporary directory for indices"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_embeddings():
    """Create sample embeddings for testing"""
    np.random.seed(42)
    return np.random.randn(10, 128).astype(np.float32)


@pytest.fixture
def sample_documents():
    """Create sample documents"""
    return [{"id": i, "text": f"Document {i}"} for i in range(10)]


class TestFAISSStoreInitialization:
    """Test store initialization and validation"""
    
    def test_init_default(self, temp_index_dir):
        """Test default initialization"""
        store = FAISSStore(index_dir=temp_index_dir)
        assert store.index_name == "default"
        assert store.index is None
        assert store.dimension is None
        assert store.max_vectors == MAX_VECTORS
    
    def test_init_custom_name(self, temp_index_dir):
        """Test initialization with custom name"""
        store = FAISSStore(index_dir=temp_index_dir, index_name="custom")
        assert store.index_name == "custom"
    
    def test_init_invalid_name(self, temp_index_dir):
        """Test initialization with invalid index name"""
        with pytest.raises(ValueError, match="Invalid index name"):
            FAISSStore(index_dir=temp_index_dir, index_name="invalid/name")


class TestFAISSStoreHealthCheck:
    """Test health check functionality"""
    
    def test_health_check_empty(self, temp_index_dir):
        """Test health check on empty store"""
        store = FAISSStore(index_dir=temp_index_dir)
        health = store.health_check()
        
        assert health["faiss_available"] is True
        assert health["index_loaded"] is False
        assert health["healthy"] is False
        assert health["num_vectors"] == 0
    
    def test_health_check_loaded(self, temp_index_dir, sample_embeddings, sample_documents):
        """Test health check on loaded store"""
        store = FAISSStore(index_dir=temp_index_dir)
        store.create_index(sample_embeddings, sample_documents)
        
        health = store.health_check()
        assert health["healthy"] is True
        assert health["index_loaded"] is True
        assert health["num_vectors"] == 10
        assert health["num_documents"] == 10
        assert health["dimension"] == 128


class TestFAISSStoreIndexCreation:
    """Test index creation with validation"""
    
    def test_create_index_valid(self, temp_index_dir, sample_embeddings, sample_documents):
        """Test creating a valid index"""
        store = FAISSStore(index_dir=temp_index_dir)
        store.create_index(sample_embeddings, sample_documents)
        
        assert store.index is not None
        assert store.dimension == 128
        assert store.index.ntotal == 10
        assert len(store.documents) == 10
    
    def test_create_index_invalid_type(self, temp_index_dir, sample_documents):
        """Test creating index with invalid embedding type"""
        store = FAISSStore(index_dir=temp_index_dir)
        
        with pytest.raises(TypeError, match="must be a numpy array"):
            store.create_index([[1, 2, 3]], sample_documents)
    
    def test_create_index_mismatch_count(self, temp_index_dir, sample_embeddings):
        """Test creating index with mismatched counts"""
        store = FAISSStore(index_dir=temp_index_dir)
        wrong_docs = [{"id": i} for i in range(5)]  # Only 5 docs for 10 embeddings
        
        with pytest.raises(ValueError, match="must match number of documents"):
            store.create_index(sample_embeddings, wrong_docs)


class TestFAISSStorePersistence:
    """Test save and load functionality"""
    
    def test_save_and_load(self, temp_index_dir, sample_embeddings, sample_documents):
        """Test saving and loading index"""
        # Create and save
        store1 = FAISSStore(index_dir=temp_index_dir, index_name="test")
        store1.create_index(sample_embeddings, sample_documents)
        store1.save()
        
        # Load in new store
        store2 = FAISSStore(index_dir=temp_index_dir, index_name="test")
        store2.load()
        
        assert store2.index is not None
        assert store2.dimension == 128
        assert store2.index.ntotal == 10
        assert len(store2.documents) == 10


class TestFAISSStoreSearch:
    """Test search functionality with validation"""
    
    def test_search_valid(self, temp_index_dir, sample_embeddings, sample_documents):
        """Test valid search"""
        store = FAISSStore(index_dir=temp_index_dir)
        store.create_index(sample_embeddings, sample_documents)
        
        query = sample_embeddings[0]
        results = store.search(query, top_k=3)
        
        assert len(results) == 3
        assert results[0]["index"] == 0  # Should find itself first
        assert 0.0 <= results[0]["score"] <= 1.0
        assert "document" in results[0]
    
    def test_search_without_index(self, temp_index_dir):
        """Test search without loaded index"""
        store = FAISSStore(index_dir=temp_index_dir)
        query = np.random.randn(128).astype(np.float32)
        
        with pytest.raises(RuntimeError, match="Index not loaded"):
            store.search(query)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
