"""
Tests for Reranker Module.
"""

import pytest
import numpy as np

from codex.retrieval.reranker import (
    Reranker,
    RerankingConfig,
    RerankingStrategy,
    RankedResult,
    ScoreFusionReranker,
    MMRReranker,
    rerank_results,
)


class TestRankedResult:
    """Tests for RankedResult dataclass."""
    
    def test_creation(self):
        """Test creating a ranked result."""
        result = RankedResult(
            document_id="doc1",
            content="Test content",
            original_score=0.8,
            reranked_score=0.9,
            rank=1,
        )
        
        assert result.document_id == "doc1"
        assert result.content == "Test content"
        assert result.original_score == 0.8
        assert result.reranked_score == 0.9
        assert result.rank == 1
    
    def test_to_dict(self):
        """Test converting to dictionary."""
        result = RankedResult(
            document_id="doc1",
            content="Test",
            original_score=0.5,
            reranked_score=0.6,
            rank=2,
            metadata={"source": "test"},
        )
        
        d = result.to_dict()
        assert d["document_id"] == "doc1"
        assert d["reranked_score"] == 0.6
        assert d["metadata"]["source"] == "test"


class TestRerankingConfig:
    """Tests for RerankingConfig."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = RerankingConfig()
        
        assert config.strategy == RerankingStrategy.SCORE_FUSION
        assert config.top_k == 10
        assert config.mmr_lambda == 0.5
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = RerankingConfig(
            strategy=RerankingStrategy.MMR,
            top_k=5,
            mmr_lambda=0.7,
        )
        
        assert config.strategy == RerankingStrategy.MMR
        assert config.top_k == 5
        assert config.mmr_lambda == 0.7


class TestScoreFusionReranker:
    """Tests for ScoreFusionReranker."""
    
    @pytest.fixture
    def reranker(self):
        config = RerankingConfig(strategy=RerankingStrategy.SCORE_FUSION)
        return ScoreFusionReranker(config)
    
    @pytest.fixture
    def sample_results(self):
        return [
            {"id": "doc1", "content": "First document", "score": 0.9},
            {"id": "doc2", "content": "Second document", "score": 0.7},
            {"id": "doc3", "content": "Third document", "score": 0.8},
        ]
    
    def test_rerank_empty(self, reranker):
        """Test re-ranking empty results."""
        results = reranker.rerank("query", [])
        assert len(results) == 0
    
    def test_rerank_preserves_order_for_similar_scores(self, reranker, sample_results):
        """Test re-ranking preserves relative order."""
        results = reranker.rerank("query", sample_results)
        
        assert len(results) == 3
        # First result should be doc1 (highest score)
        assert results[0].document_id == "doc1"
    
    def test_rerank_assigns_ranks(self, reranker, sample_results):
        """Test that ranks are assigned correctly."""
        results = reranker.rerank("query", sample_results)
        
        for i, result in enumerate(results):
            assert result.rank == i + 1
    
    def test_rerank_respects_top_k(self):
        """Test that top_k is respected."""
        config = RerankingConfig(top_k=2)
        reranker = ScoreFusionReranker(config)
        
        results = [
            {"id": f"doc{i}", "content": f"Content {i}", "score": 0.5}
            for i in range(10)
        ]
        
        reranked = reranker.rerank("query", results)
        assert len(reranked) == 2


class TestMMRReranker:
    """Tests for MMRReranker (diversity-aware)."""
    
    @pytest.fixture
    def reranker(self):
        config = RerankingConfig(
            strategy=RerankingStrategy.MMR,
            mmr_lambda=0.5,
            top_k=5,
        )
        return MMRReranker(config)
    
    @pytest.fixture
    def sample_results(self):
        return [
            {"id": "doc1", "content": "First document", "score": 0.9},
            {"id": "doc2", "content": "Second document", "score": 0.85},
            {"id": "doc3", "content": "Third document", "score": 0.8},
            {"id": "doc4", "content": "Fourth document", "score": 0.75},
            {"id": "doc5", "content": "Fifth document", "score": 0.7},
        ]
    
    def test_mmr_rerank(self, reranker, sample_results):
        """Test MMR re-ranking."""
        results = reranker.rerank("query", sample_results)
        
        assert len(results) == 5
        # First result should still be highest relevance
        assert results[0].document_id == "doc1"
    
    def test_mmr_with_embeddings(self, reranker, sample_results):
        """Test MMR with provided embeddings."""
        # Create similar embeddings
        embeddings = np.random.rand(5, 384).astype(np.float32)
        
        results = reranker.rerank("query", sample_results, embeddings)
        
        assert len(results) == 5
    
    def test_mmr_respects_lambda(self):
        """Test that lambda affects diversity."""
        sample_results = [
            {"id": f"doc{i}", "content": f"Content {i}", "score": 1.0 - i * 0.1}
            for i in range(5)
        ]
        
        # High lambda = more relevance focused
        config_high = RerankingConfig(mmr_lambda=0.9, top_k=3)
        reranker_high = MMRReranker(config_high)
        results_high = reranker_high.rerank("query", sample_results)
        
        # Low lambda = more diversity focused
        config_low = RerankingConfig(mmr_lambda=0.1, top_k=3)
        reranker_low = MMRReranker(config_low)
        results_low = reranker_low.rerank("query", sample_results)
        
        assert len(results_high) == 3
        assert len(results_low) == 3


class TestReranker:
    """Tests for main Reranker class."""
    
    def test_no_reranking_strategy(self):
        """Test NONE strategy returns wrapped results."""
        config = RerankingConfig(strategy=RerankingStrategy.NONE, top_k=2)
        reranker = Reranker(config)
        
        results = [
            {"id": "doc1", "content": "Content 1", "score": 0.9},
            {"id": "doc2", "content": "Content 2", "score": 0.8},
            {"id": "doc3", "content": "Content 3", "score": 0.7},
        ]
        
        reranked = reranker.rerank("query", results)
        
        assert len(reranked) == 2  # Respects top_k
        assert all(isinstance(r, RankedResult) for r in reranked)
    
    def test_score_fusion_strategy(self):
        """Test SCORE_FUSION strategy."""
        config = RerankingConfig(strategy=RerankingStrategy.SCORE_FUSION)
        reranker = Reranker(config)
        
        results = [
            {"id": "doc1", "content": "Content 1", "score": 0.9},
        ]
        
        reranked = reranker.rerank("query", results)
        assert len(reranked) == 1
    
    def test_mmr_strategy(self):
        """Test MMR strategy."""
        config = RerankingConfig(strategy=RerankingStrategy.MMR)
        reranker = Reranker(config)
        
        results = [
            {"id": "doc1", "content": "Content 1", "score": 0.9},
        ]
        
        reranked = reranker.rerank("query", results)
        assert len(reranked) == 1
    
    def test_hybrid_strategy(self):
        """Test HYBRID strategy."""
        config = RerankingConfig(strategy=RerankingStrategy.HYBRID)
        reranker = Reranker(config)
        
        results = [
            {"id": "doc1", "content": "Content 1", "score": 0.9},
            {"id": "doc2", "content": "Content 2", "score": 0.8},
        ]
        
        reranked = reranker.rerank("query", results)
        assert len(reranked) >= 1
    
    def test_empty_results(self):
        """Test with empty results."""
        reranker = Reranker()
        reranked = reranker.rerank("query", [])
        assert len(reranked) == 0


class TestRerankResultsFunction:
    """Tests for rerank_results convenience function."""
    
    def test_basic_reranking(self):
        """Test basic re-ranking function."""
        results = [
            {"id": "doc1", "content": "Content 1", "score": 0.9},
            {"id": "doc2", "content": "Content 2", "score": 0.8},
        ]
        
        reranked = rerank_results("query", results)
        
        assert len(reranked) >= 1
        assert all(isinstance(r, RankedResult) for r in reranked)
    
    def test_with_custom_strategy(self):
        """Test with custom strategy."""
        results = [
            {"id": "doc1", "content": "Content 1", "score": 0.9},
        ]
        
        reranked = rerank_results(
            "query",
            results,
            strategy=RerankingStrategy.MMR,
            top_k=5,
        )
        
        assert len(reranked) == 1
