"""Tests for metadata filtering"""
import pytest
from src.codex.retrieval.filtering import (
    matches_filter,
    apply_filters,
    calculate_fetch_multiplier,
)


class TestMatchesFilter:
    """Test filter matching logic"""
    
    def test_empty_filter(self):
        """Test empty filter matches everything"""
        metadata = {"category": "tech", "score": 0.9}
        assert matches_filter(metadata, {})
        assert matches_filter(metadata, None)
    
    def test_equality_filter(self):
        """Test simple equality filter"""
        metadata = {"category": "tech", "score": 0.9}
        
        # Match
        assert matches_filter(metadata, {"category": "tech"})
        assert matches_filter(metadata, {"score": 0.9})
        
        # No match
        assert not matches_filter(metadata, {"category": "news"})
        assert not matches_filter(metadata, {"score": 0.5})
    
    def test_range_filters(self):
        """Test range operators"""
        metadata = {"score": 0.8}
        
        # Greater than
        assert matches_filter(metadata, {"score": {"$gt": 0.7}})
        assert not matches_filter(metadata, {"score": {"$gt": 0.9}})
        
        # Greater than or equal
        assert matches_filter(metadata, {"score": {"$gte": 0.8}})
        assert matches_filter(metadata, {"score": {"$gte": 0.7}})
        assert not matches_filter(metadata, {"score": {"$gte": 0.9}})
        
        # Less than
        assert matches_filter(metadata, {"score": {"$lt": 0.9}})
        assert not matches_filter(metadata, {"score": {"$lt": 0.7}})
        
        # Less than or equal
        assert matches_filter(metadata, {"score": {"$lte": 0.8}})
        assert matches_filter(metadata, {"score": {"$lte": 0.9}})
        assert not matches_filter(metadata, {"score": {"$lte": 0.7}})
    
    def test_in_filter(self):
        """Test in/not in operators"""
        metadata = {"category": "tech"}
        
        # In
        assert matches_filter(metadata, {"category": {"$in": ["tech", "news"]}})
        assert not matches_filter(metadata, {"category": {"$in": ["sports", "health"]}})
        
        # Not in
        assert matches_filter(metadata, {"category": {"$nin": ["sports", "health"]}})
        assert not matches_filter(metadata, {"category": {"$nin": ["tech", "news"]}})
    
    def test_exists_filter(self):
        """Test exists operator"""
        metadata = {"category": "tech", "score": 0.9}
        
        # Field exists
        assert matches_filter(metadata, {"category": {"$exists": True}})
        assert matches_filter(metadata, {"score": {"$exists": True}})
        
        # Field does not exist
        assert matches_filter(metadata, {"missing": {"$exists": False}})
        assert not matches_filter(metadata, {"category": {"$exists": False}})
    
    def test_logical_and(self):
        """Test logical AND operator"""
        metadata = {"category": "tech", "score": 0.9}
        
        # Both conditions match
        assert matches_filter(metadata, {
            "$and": [
                {"category": "tech"},
                {"score": {"$gte": 0.8}},
            ]
        })
        
        # One condition fails
        assert not matches_filter(metadata, {
            "$and": [
                {"category": "tech"},
                {"score": {"$lt": 0.5}},
            ]
        })
    
    def test_logical_or(self):
        """Test logical OR operator"""
        metadata = {"category": "tech", "score": 0.9}
        
        # One condition matches
        assert matches_filter(metadata, {
            "$or": [
                {"category": "news"},
                {"score": {"$gte": 0.8}},
            ]
        })
        
        # Both conditions match
        assert matches_filter(metadata, {
            "$or": [
                {"category": "tech"},
                {"score": {"$gte": 0.8}},
            ]
        })
        
        # No conditions match
        assert not matches_filter(metadata, {
            "$or": [
                {"category": "news"},
                {"score": {"$lt": 0.5}},
            ]
        })
    
    def test_complex_filter(self):
        """Test complex nested filters"""
        metadata = {"category": "tech", "score": 0.9, "author": "alice"}
        
        # Complex AND/OR combination
        assert matches_filter(metadata, {
            "$and": [
                {
                    "$or": [
                        {"category": "tech"},
                        {"category": "news"},
                    ]
                },
                {"score": {"$gte": 0.8}},
                {"author": "alice"},
            ]
        })
    
    def test_not_equal_operator(self):
        """Test not equal operator"""
        metadata = {"category": "tech"}
        
        assert matches_filter(metadata, {"category": {"$ne": "news"}})
        assert not matches_filter(metadata, {"category": {"$ne": "tech"}})


class TestApplyFilters:
    """Test filter application to results"""
    
    def test_no_filters(self):
        """Test with no filters"""
        results = [
            {"id": "1", "metadata": {"category": "tech"}},
            {"id": "2", "metadata": {"category": "news"}},
        ]
        
        filtered = apply_filters(results, filters=None)
        assert len(filtered) == 2
        assert filtered == results
    
    def test_simple_filter(self):
        """Test simple equality filter"""
        results = [
            {"id": "1", "metadata": {"category": "tech"}},
            {"id": "2", "metadata": {"category": "news"}},
            {"id": "3", "metadata": {"category": "tech"}},
        ]
        
        filtered = apply_filters(results, filters={"category": "tech"})
        assert len(filtered) == 2
        assert all(r["metadata"]["category"] == "tech" for r in filtered)
    
    def test_range_filter(self):
        """Test range filter"""
        results = [
            {"id": "1", "metadata": {"score": 0.9}},
            {"id": "2", "metadata": {"score": 0.6}},
            {"id": "3", "metadata": {"score": 0.8}},
            {"id": "4", "metadata": {"score": 0.4}},
        ]
        
        filtered = apply_filters(results, filters={"score": {"$gte": 0.7}})
        assert len(filtered) == 2
        assert all(r["metadata"]["score"] >= 0.7 for r in filtered)
    
    def test_max_results(self):
        """Test max_results parameter"""
        results = [
            {"id": "1", "metadata": {"category": "tech"}},
            {"id": "2", "metadata": {"category": "tech"}},
            {"id": "3", "metadata": {"category": "tech"}},
        ]
        
        filtered = apply_filters(results, filters={"category": "tech"}, max_results=2)
        assert len(filtered) == 2
    
    def test_complex_filter(self):
        """Test complex filter with multiple conditions"""
        results = [
            {"id": "1", "metadata": {"category": "tech", "score": 0.9}},
            {"id": "2", "metadata": {"category": "news", "score": 0.8}},
            {"id": "3", "metadata": {"category": "tech", "score": 0.6}},
            {"id": "4", "metadata": {"category": "tech", "score": 0.95}},
        ]
        
        filtered = apply_filters(results, filters={
            "$and": [
                {"category": "tech"},
                {"score": {"$gte": 0.85}},
            ]
        })
        
        assert len(filtered) == 2
        assert all(
            r["metadata"]["category"] == "tech" and r["metadata"]["score"] >= 0.85
            for r in filtered
        )
    
    def test_empty_results(self):
        """Test with empty results"""
        filtered = apply_filters([], filters={"category": "tech"})
        assert len(filtered) == 0
    
    def test_no_matches(self):
        """Test when no results match filter"""
        results = [
            {"id": "1", "metadata": {"category": "news"}},
            {"id": "2", "metadata": {"category": "sports"}},
        ]
        
        filtered = apply_filters(results, filters={"category": "tech"})
        assert len(filtered) == 0


class TestCalculateFetchMultiplier:
    """Test fetch multiplier calculation"""
    
    def test_no_filters(self):
        """Test with no filters"""
        assert calculate_fetch_multiplier(None) == 1
        assert calculate_fetch_multiplier({}) == 1
    
    def test_single_condition(self):
        """Test with single filter condition"""
        assert calculate_fetch_multiplier({"category": "tech"}) == 3
    
    def test_two_conditions(self):
        """Test with two filter conditions"""
        assert calculate_fetch_multiplier({
            "category": "tech",
            "score": {"$gte": 0.8}
        }) == 5
    
    def test_complex_filters(self):
        """Test with complex filters"""
        assert calculate_fetch_multiplier({
            "category": "tech",
            "score": {"$gte": 0.8},
            "author": "alice"
        }) == 10
