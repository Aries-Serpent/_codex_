"""
Tests for Vector Store Factory and Registry
"""

import tempfile
import types
from unittest.mock import Mock

import pytest

np = pytest.importorskip("numpy")

from src.codex.retrieval.stores.factory import (
    VectorStoreFactory,
    VectorStoreRegistry,
    VectorStoreType,
    auto_detect_store,
    create_auto_store,
    get_default_store,  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
)

# Check if FAISS is available
try:
    import faiss

    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    # Create mock faiss module for type checking
    faiss = types.SimpleNamespace()
    faiss.IndexFlatL2 = type("IndexFlatL2", (), {})
    faiss.IndexFlatIP = type("IndexFlatIP", (), {})


class TestVectorStoreRegistry:
    """Test VectorStoreRegistry"""

    def test_register_and_get(self):
        """Test registering and getting a store"""
        mock_store = Mock()
        VectorStoreRegistry.register("test_store", mock_store)

        retrieved = VectorStoreRegistry.get("test_store")
        assert retrieved == mock_store, "retrieved is not valid"

    def test_list_types(self):
        """Test listing registered types"""
        types = VectorStoreRegistry.list_types()
        assert isinstance(types, list)
        # FAISS should be registered by default
        assert "faiss" in types, "Condition must be true"

    def test_get_nonexistent(self):
        """Test getting nonexistent store returns None"""
        result = VectorStoreRegistry.get("nonexistent_store")
        assert result is None, "Result must not be empty"

    def test_register_overwrites(self):
        """Test registering same type overwrites"""
        mock_store1 = Mock()
        mock_store2 = Mock()

        VectorStoreRegistry.register("overwrite_test", mock_store1)
        VectorStoreRegistry.register("overwrite_test", mock_store2)

        retrieved = VectorStoreRegistry.get("overwrite_test")
        assert retrieved == mock_store2, "retrieved is not valid"


class TestVectorStoreType:
    """Test VectorStoreType enum"""

    def test_enum_values(self):
        """Test enum values"""
        assert VectorStoreType.FAISS.value == "faiss", "Value must be initialized"
        assert VectorStoreType.PINECONE.value == "pinecone", "Value must be initialized"
        assert VectorStoreType.WEAVIATE.value == "weaviate", "Value must be initialized"
        assert VectorStoreType.CHROMADB.value == "chromadb", "Value must be initialized"


class TestVectorStoreFactory:
    """Test VectorStoreFactory"""

    @pytest.mark.skipif(not FAISS_AVAILABLE, reason="FAISS not available")
    def test_create_faiss_store(self):
        """Test creating FAISS store"""
        store = VectorStoreFactory.create(
            store_type="faiss", index_name="test_index", index_dir=os.path.join(tempfile.gettempdir(), "test_faiss")
        )

        assert store is not None, "store must be initialized"
        assert hasattr(store, "create_index")
        assert hasattr(store, "search")

    def test_create_invalid_type(self):
        """Test creating invalid store type raises error"""
        with pytest.raises(ValueError, match="Unknown vector store type"):
            VectorStoreFactory.create(store_type="invalid_type", index_name="test")

    @pytest.mark.skipif(not FAISS_AVAILABLE, reason="FAISS not available")
    def test_create_from_config(self):
        """Test creating store from config"""
        config = {
            "type": "faiss",
            "index_name": "config_test",
            "dimension": 768,
            "index_dir": os.path.join(tempfile.gettempdir(), "test_config"),
        }

        store = VectorStoreFactory.create_from_config(config)
        assert store is not None, "store must be initialized"

    def test_create_from_config_missing_type(self):
        """Test creating from config without type fails"""
        config = {"index_name": "test", "dimension": 768}

        with pytest.raises(ValueError, match="Config must specify 'type'"):
            VectorStoreFactory.create_from_config(config)

    def test_create_from_config_missing_dimension(self):
        """Test creating from config without dimension fails"""
        config = {"type": "faiss", "index_name": "test"}

        with pytest.raises(ValueError, match="Config must specify 'dimension'"):
            VectorStoreFactory.create_from_config(config)

    def test_create_pinecone_stub(self):
        """Test creating Pinecone store (stub)"""
        # Pinecone should be registered as stub
        if "pinecone" in VectorStoreRegistry.list_types():
            store = VectorStoreFactory.create(
                store_type="pinecone",
                index_name="test_pinecone",
                dimension=768,
                api_key="test_key",
                environment="test-env",
            )
            assert store is not None, "store must be initialized"
            # Stub should raise RuntimeError on operations
            with pytest.raises(RuntimeError, match="not available in offline mode"):
                store.search(np.random.rand(1, 768), top_k=5)

    def test_create_weaviate_stub(self):
        """Test creating Weaviate store (stub)"""
        # Weaviate should be registered
        if "weaviate" in VectorStoreRegistry.list_types():
            store = VectorStoreFactory.create(
                store_type="weaviate",
                index_name="test_weaviate",
                dimension=768,
                url="http://localhost:8080",
            )
            assert store is not None, "store must be initialized"


class TestDefaultStore:
    """Test get_default_store"""

    @pytest.mark.skipif(not FAISS_AVAILABLE, reason="FAISS not available")
    def test_get_default_store(self):
        """Test getting default store"""
        store = get_default_store(dimension=384, index_name="default_test")
        assert store is not None, "store must be initialized"
        assert hasattr(store, "create_index")


class TestAutoDetection:
    """Test auto-detection functionality"""

    def test_auto_detect_faiss(self):
        """Test auto-detect returns FAISS (default)"""
        store_type = auto_detect_store()
        # Should default to FAISS
        assert store_type == "faiss", "store_type is not valid"

    def test_auto_detect_with_pinecone_env(self, monkeypatch):
        """Test auto-detect with Pinecone env var"""
        # FAISS should still be preferred even with Pinecone configured
        monkeypatch.setenv("PINECONE_API_KEY", "test_key")
        store_type = auto_detect_store()
        # FAISS has higher priority
        assert store_type == "faiss", "store_type is not valid"

    def test_auto_detect_with_weaviate_env(self, monkeypatch):
        """Test auto-detect with Weaviate env var"""
        monkeypatch.setenv("WEAVIATE_URL", "http://localhost:8080")
        store_type = auto_detect_store()
        # FAISS has higher priority
        assert store_type == "faiss", "store_type is not valid"

    @pytest.mark.skipif(not FAISS_AVAILABLE, reason="FAISS not available")
    def test_create_auto_store(self):
        """Test creating auto-detected store"""
        store = create_auto_store(index_name="auto_test", dimension=512)
        assert store is not None, "store must be initialized"
        # Should be FAISS by default
        assert hasattr(store, "create_index")

    @pytest.mark.skipif(not FAISS_AVAILABLE, reason="FAISS not available")
    def test_create_auto_store_no_dimension(self):
        """Test creating auto store without dimension"""
        # Should work for FAISS (dimension set during create_index)
        store = create_auto_store(index_name="auto_no_dim")
        assert store is not None, "store must be initialized"


class TestFactoryIntegration:
    """Integration tests for factory"""

    @pytest.mark.skipif(not FAISS_AVAILABLE, reason="FAISS not available")
    def test_factory_with_faiss_operations(self):
        """Test full factory workflow with FAISS"""
        # Create store
        store = VectorStoreFactory.create(
            store_type="faiss", index_name="integration_test", index_dir=os.path.join(tempfile.gettempdir(), "integration")
        )

        # Create index
        embeddings = np.random.rand(10, 128).astype(np.float32)
        documents = [{"id": str(i), "text": f"doc {i}"} for i in range(10)]

        store.create_index(embeddings, documents)

        # Search
        query = np.random.rand(1, 128).astype(np.float32)
        results = store.search(query, top_k=3)

        assert len(results) == 3, "Results must not be empty"
        assert all("id" in r for r in results), "Result must not be empty"
        assert all("score" in r for r in results), "Result must not be empty"

    @pytest.mark.skipif(not FAISS_AVAILABLE, reason="FAISS not available")
    def test_multiple_stores(self):
        """Test creating multiple different stores"""
        store1 = VectorStoreFactory.create(
            store_type="faiss", index_name="store1", index_dir=os.path.join(tempfile.gettempdir(), "store1")
        )

        store2 = VectorStoreFactory.create(
            store_type="faiss", index_name="store2", index_dir=os.path.join(tempfile.gettempdir(), "store2")
        )

        assert store1 is not None, "store1 must be initialized"
        assert store2 is not None, "store2 must be initialized"
        # Should be different instances
        assert store1 != store2, "store1 is not valid"

    @pytest.mark.skipif(not FAISS_AVAILABLE, reason="FAISS not available")
    def test_config_workflow(self):
        """Test complete config-based workflow"""
        config = {
            "type": "faiss",
            "index_name": "config_workflow",
            "dimension": 256,
            "index_dir": os.path.join(tempfile.gettempdir(), "config_workflow"),
        }

        store = VectorStoreFactory.create_from_config(config)

        # Verify store can be used
        embeddings = np.random.rand(5, 256).astype(np.float32)
        documents = [{"id": str(i)} for i in range(5)]

        store.create_index(embeddings, documents)
        health = store.health_check()

        assert health["healthy"] is True, "Condition must be true"
        assert health["num_vectors"] == 5, "Condition must be true"


class TestBackendAvailability:
    """Test backend availability detection"""

    def test_all_backends_registered(self):
        """Test that expected backends are registered"""
        types = VectorStoreRegistry.list_types()

        # At minimum, FAISS should be available
        assert "faiss" in types, "Condition must be true"

        # Stubs should also be registered
        assert "pinecone" in types or "weaviate" in types or "pgvector" in types

    def test_faiss_always_available(self):
        """Test FAISS is always available"""
        store_class = VectorStoreRegistry.get("faiss")
        assert store_class is not None, "store_class must be initialized"
