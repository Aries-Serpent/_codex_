"""Integration tests for metadata filtering with FAISS store"""
import numpy as np
import pytest
from src.codex.retrieval.stores.faiss_store import FAISSStore


class TestFAISSStoreFiltering:
    """Test FAISS store with metadata filtering"""
    
    @pytest.fixture
    def store_with_data(self, tmp_path):
        """Create FAISS store with sample data"""
        store = FAISSStore(index_dir=str(tmp_path), index_name="test_filtering")
        
        # Create sample vectors and metadata
        vectors = np.array([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [0.7, 0.7, 0.0],
            [0.0, 0.7, 0.7],
        ], dtype=np.float32)
        
        metadata = [
            {"category": "tech", "score": 0.9, "author": "alice"},
            {"category": "news", "score": 0.8, "author": "bob"},
            {"category": "tech", "score": 0.7, "author": "charlie"},
            {"category": "sports", "score": 0.95, "author": "alice"},
            {"category": "tech", "score": 0.85, "author": "bob"},
        ]
        
        # Add to store
        store.create_index(dimension=3)
        store.add(vectors, metadata=metadata)
        
        return store
    
    def test_search_without_filters(self, store_with_data):
        """Test search without filters returns all top results"""
        query = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        results = store_with_data.search(query, top_k=3)
        
        assert len(results) == 3
        assert all("id" in r for r in results)
        assert all("score" in r for r in results)
        assert all("metadata" in r for r in results)
    
    def test_search_with_equality_filter(self, store_with_data):
        """Test search with simple equality filter"""
        query = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        
        # Filter for tech category
        results = store_with_data.search(
            query,
            top_k=5,
            filters={"category": "tech"}
        )
        
        assert len(results) <= 3  # Only 3 tech items
        assert all(r["metadata"]["category"] == "tech" for r in results)
    
    def test_search_with_range_filter(self, store_with_data):
        """Test search with range filter"""
        query = np.array([0.5, 0.5, 0.0], dtype=np.float32)
        
        # Filter for high scores
        results = store_with_data.search(
            query,
            top_k=5,
            filters={"score": {"$gte": 0.85}}
        )
        
        assert len(results) <= 2  # Only 2 items with score >= 0.85
        assert all(r["metadata"]["score"] >= 0.85 for r in results)
    
    def test_search_with_complex_filter(self, store_with_data):
        """Test search with complex AND filter"""
        query = np.array([0.5, 0.5, 0.0], dtype=np.float32)
        
        # Filter for tech AND high score
        results = store_with_data.search(
            query,
            top_k=5,
            filters={
                "$and": [
                    {"category": "tech"},
                    {"score": {"$gte": 0.8}}
                ]
            }
        )
        
        assert len(results) <= 2  # Only 2 tech items with score >= 0.8
        assert all(
            r["metadata"]["category"] == "tech" and r["metadata"]["score"] >= 0.8
            for r in results
        )
    
    def test_search_with_or_filter(self, store_with_data):
        """Test search with OR filter"""
        query = np.array([0.5, 0.5, 0.0], dtype=np.float32)
        
        # Filter for tech OR sports
        results = store_with_data.search(
            query,
            top_k=5,
            filters={
                "$or": [
                    {"category": "tech"},
                    {"category": "sports"}
                ]
            }
        )
        
        assert len(results) <= 4  # 3 tech + 1 sports
        assert all(
            r["metadata"]["category"] in ["tech", "sports"]
            for r in results
        )
    
    def test_search_with_author_filter(self, store_with_data):
        """Test search filtering by author"""
        query = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        
        results = store_with_data.search(
            query,
            top_k=5,
            filters={"author": "alice"}
        )
        
        assert len(results) <= 2  # Only 2 items by alice
        assert all(r["metadata"]["author"] == "alice" for r in results)
    
    def test_search_with_no_matches(self, store_with_data):
        """Test search with filter that matches nothing"""
        query = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        
        results = store_with_data.search(
            query,
            top_k=5,
            filters={"category": "nonexistent"}
        )
        
        assert len(results) == 0
    
    def test_filtering_preserves_score_order(self, store_with_data):
        """Test that filtering preserves similarity score ordering"""
        query = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        
        results = store_with_data.search(
            query,
            top_k=5,
            filters={"category": "tech"}
        )
        
        # Check scores are in descending order
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)
