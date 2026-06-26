"""
Tests for quantum-thermodynamic retrieval scoring.

Author: Copilot Agent
Generated: 2025-12-24
"""

from __future__ import annotations

import math

import pytest

from rag.pipelines.chunking import Chunk
from rag.pipelines.quantum_retrieval import (
    QuantumEnhancedRetrieval,
    QuantumRelevanceScorer,
    QuantumState,
    record_scoring_pattern,
)


class TestQuantumRelevanceScorer:
    """Test quantum relevance scoring."""

    def test_weights_validation(self):
        """Test that weights must sum to 1.0."""
        # Should raise ValueError when weights don't sum to 1
        with pytest.raises(ValueError, match="Weights must sum to 1.0"):
            QuantumRelevanceScorer(alpha=0.5, beta=0.3, gamma=0.1)  # Sum=0.9

        with pytest.raises(ValueError, match="Weights must sum to 1.0"):
            QuantumRelevanceScorer(alpha=0.7, beta=0.2, gamma=0.2)  # Sum=1.1

    def test_valid_weights(self):
        """Test that valid weights are accepted."""
        # Should not raise exception
        scorer = QuantumRelevanceScorer(alpha=0.6, beta=0.25, gamma=0.15)
        assert scorer.alpha == 0.6, "alpha is not valid"
        assert scorer.beta == 0.25, "beta is not valid"
        assert scorer.gamma == 0.15, "gamma is not valid"

        # Exactly 1.0
        scorer2 = QuantumRelevanceScorer(alpha=0.5, beta=0.3, gamma=0.2)
        assert scorer2.alpha == 0.5, "alpha is not valid"

    def test_default_initialization(self):
        """Test scorer initializes with valid defaults."""
        scorer = QuantumRelevanceScorer()
        assert scorer.alpha == 0.6, "alpha is not valid"
        assert scorer.beta == 0.25, "beta is not valid"
        assert scorer.gamma == 0.15, "gamma is not valid"
        assert math.isclose(scorer.alpha + scorer.beta + scorer.gamma, 1.0)

    def test_quantum_state_calculation(self):
        """Test quantum state calculations."""
        scorer = QuantumRelevanceScorer()

        # Create mock chunk with embeddings
        chunk = Chunk(
            content="Test document about machine learning",
            start_index=0,
            end_index=37,
            metadata={
                "timestamp": 1000.0,
                "authority": 0.8,
                "topic_frequency": 1.5,
                "embedding": [0.1] * 384,  # Mock embedding
            },
        )

        # Mock query embedding
        query_embedding = [0.2] * 384

        # Calculate quantum state
        state = scorer.calculate_quantum_state(chunk, query_embedding, current_time=2000.0)

        # Validate state properties
        assert isinstance(state, QuantumState)
        assert isinstance(state.amplitude, complex)
        assert isinstance(state.energy, float)
        assert isinstance(state.entropy, float)
        assert isinstance(state.collapse_probability, float)

        # Collapse probability should be in [0, 1]
        assert 0.0 <= state.collapse_probability <= 1.0, "0 is not valid"

        # Energy should be positive
        assert state.energy >= 0.0, "energy must be greater than zero"

        # Entropy should be non-negative
        assert state.entropy >= 0.0, "entropy must be greater than zero"

    def test_quantum_state_no_embeddings(self):
        """Test quantum state calculation when embeddings are unavailable."""
        scorer = QuantumRelevanceScorer()

        # Chunk without embedding
        chunk = Chunk(
            content="Test document",
            start_index=0,
            end_index=13,
            metadata={
                "timestamp": 1000.0,
                "authority": 0.7,
            },
        )

        state = scorer.calculate_quantum_state(chunk, query_embedding=None, current_time=1500.0)

        # Should still return valid state (with fallback similarity)
        assert isinstance(state, QuantumState)
        assert 0.0 <= state.collapse_probability <= 1.0, "0 is not valid"

    def test_temporal_decay(self):
        """Test that older documents have lower temporal scores."""
        scorer = QuantumRelevanceScorer()

        # Create two identical chunks with different timestamps
        recent_chunk = Chunk(
            content="Test",
            start_index=0,
            end_index=4,
            metadata={
                "timestamp": 1900.0,
                "authority": 0.8,
                "embedding": [0.5] * 384,
            },
        )

        old_chunk = Chunk(
            content="Test",
            start_index=0,
            end_index=4,
            metadata={
                "timestamp": 1000.0,  # Much older
                "authority": 0.8,
                "embedding": [0.5] * 384,
            },
        )

        query_embedding = [0.5] * 384
        current_time = 2000.0

        recent_state = scorer.calculate_quantum_state(recent_chunk, query_embedding, current_time)
        old_state = scorer.calculate_quantum_state(old_chunk, query_embedding, current_time)

        # Recent document should have higher collapse probability
        assert recent_state.collapse_probability >= old_state.collapse_probability, "collapse_probability must be greater than zero"

    def test_authority_weighting(self):
        """Test that authority affects scoring."""
        scorer = QuantumRelevanceScorer()

        # High authority chunk
        high_auth = Chunk(
            content="Test",
            start_index=0,
            end_index=4,
            metadata={
                "timestamp": 1000.0,
                "authority": 0.9,
                "embedding": [0.5] * 384,
            },
        )

        # Low authority chunk
        low_auth = Chunk(
            content="Test",
            start_index=0,
            end_index=4,
            metadata={
                "timestamp": 1000.0,
                "authority": 0.1,
                "embedding": [0.5] * 384,
            },
        )

        query_embedding = [0.5] * 384
        current_time = 2000.0

        high_state = scorer.calculate_quantum_state(high_auth, query_embedding, current_time)
        low_state = scorer.calculate_quantum_state(low_auth, query_embedding, current_time)

        # High authority should have higher collapse probability
        assert high_state.collapse_probability >= low_state.collapse_probability, "collapse_probability must be greater than zero"

    def test_entropy_optimization(self):
        """Test entropy minimization in document selection."""
        scorer = QuantumRelevanceScorer()

        # Create multiple states with varying probabilities
        states = [
            QuantumState(amplitude=0.9 + 0j, energy=1.0, entropy=0.1, collapse_probability=0.81),
            QuantumState(amplitude=0.7 + 0j, energy=1.5, entropy=0.2, collapse_probability=0.49),
            QuantumState(amplitude=0.5 + 0j, energy=2.0, entropy=0.3, collapse_probability=0.25),
            QuantumState(amplitude=0.3 + 0j, energy=2.5, entropy=0.4, collapse_probability=0.09),
            QuantumState(amplitude=0.1 + 0j, energy=3.0, entropy=0.5, collapse_probability=0.01),
        ]

        # Select top 3
        selected = scorer.optimize_entropy(states, max_results=3)

        # Should return 3 indices
        assert len(selected) == 3, "Selected must not be empty"

        # Should be valid indices
        for idx in selected:
            assert 0 <= idx < len(states), "States must not be empty"

        # First selected should be highest probability
        assert selected[0] == 0, "Condition must be true"

    def test_entropy_optimization_empty(self):
        """Test entropy optimization with empty states."""
        scorer = QuantumRelevanceScorer()

        selected = scorer.optimize_entropy([], max_results=10)
        assert selected == [], "selected is not valid"

    def test_entropy_optimization_fewer_than_max(self):
        """Test entropy optimization when we have fewer states than max_results."""
        scorer = QuantumRelevanceScorer()

        states = [
            QuantumState(amplitude=0.9 + 0j, energy=1.0, entropy=0.1, collapse_probability=0.81),
            QuantumState(amplitude=0.7 + 0j, energy=1.5, entropy=0.2, collapse_probability=0.49),
        ]

        # Ask for 10 but only have 2
        selected = scorer.optimize_entropy(states, max_results=10)
        assert len(selected) == 2, "Selected must not be empty"

    def test_cosine_similarity(self):
        """Test cosine similarity calculation."""
        scorer = QuantumRelevanceScorer()

        # Identical vectors
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        assert math.isclose(scorer._cosine_similarity(vec1, vec2), 1.0, rel_tol=0.01)

        # Orthogonal vectors
        vec3 = [1.0, 0.0, 0.0]
        vec4 = [0.0, 1.0, 0.0]
        assert math.isclose(scorer._cosine_similarity(vec3, vec4), 0.0, abs_tol=0.01)

        # Opposite vectors (should clamp to 0)
        vec5 = [1.0, 0.0, 0.0]
        vec6 = [-1.0, 0.0, 0.0]
        similarity = scorer._cosine_similarity(vec5, vec6)
        assert similarity == 0.0, "similarity is not valid"

    def test_cosine_similarity_edge_cases(self):
        """Test cosine similarity edge cases."""
        scorer = QuantumRelevanceScorer()

        # None vectors
        assert scorer._cosine_similarity(None, [1.0]) == 0.0
        assert scorer._cosine_similarity([1.0], None) == 0.0

        # Empty vectors
        assert scorer._cosine_similarity([], [1.0]) == 0.0
        assert scorer._cosine_similarity([1.0], []) == 0.0

        # Zero vectors
        assert scorer._cosine_similarity([0.0, 0.0], [1.0, 1.0]) == 0.0

        # Different lengths
        assert scorer._cosine_similarity([1.0, 0.0], [1.0, 0.0, 0.0]) == 0.0

    def test_collapse_probability_normalization(self):
        """Test that collapse probabilities are properly bounded."""
        scorer = QuantumRelevanceScorer()

        # Create chunk with extreme values
        chunk = Chunk(
            content="Test",
            start_index=0,
            end_index=4,
            metadata={
                "timestamp": 1000.0,
                "authority": 1.5,  # > 1.0, should be clamped
                "topic_frequency": 10.0,
                "embedding": [1.0] * 384,
            },
        )

        query_embedding = [1.0] * 384
        state = scorer.calculate_quantum_state(chunk, query_embedding, current_time=1100.0)

        # Collapse probability must be in [0, 1]
        assert 0.0 <= state.collapse_probability <= 1.0, "0 is not valid"


class TestQuantumEnhancedRetrieval:
    """Test quantum-enhanced retrieval pipeline."""

    def test_initialization(self):
        """Test that quantum retrieval initializes correctly."""
        retriever = QuantumEnhancedRetrieval()
        assert isinstance(retriever.quantum_scorer, QuantumRelevanceScorer)

    def test_retrieve_from_chunks_empty(self):
        """Test retrieval with no chunks."""
        retriever = QuantumEnhancedRetrieval()
        results = retriever.retrieve_from_chunks("test query", chunks=[], top_k=10)
        assert results == [], "Result must not be empty"

    def test_retrieve_from_chunks_basic(self):
        """Test basic retrieval from chunks."""
        retriever = QuantumEnhancedRetrieval()

        # Create test chunks
        chunks = [
            Chunk(
                content="Machine learning is a subset of AI",
                start_index=0,
                end_index=35,
                metadata={
                    "id": "chunk_1",
                    "timestamp": 1000.0,
                    "authority": 0.8,
                    "embedding": [0.5] * 384,
                },
            ),
            Chunk(
                content="Deep learning uses neural networks",
                start_index=0,
                end_index=35,
                metadata={
                    "id": "chunk_2",
                    "timestamp": 1500.0,
                    "authority": 0.9,
                    "embedding": [0.6] * 384,
                },
            ),
            Chunk(
                content="Quantum computing uses qubits",
                start_index=0,
                end_index=30,
                metadata={
                    "id": "chunk_3",
                    "timestamp": 2000.0,
                    "authority": 0.7,
                    "embedding": [0.3] * 384,
                },
            ),
        ]

        results = retriever.retrieve_from_chunks(
            query="machine learning", chunks=chunks, top_k=2, current_time=2500.0
        )

        # Should return 2 results
        assert len(results) == 2, "Results must not be empty"

        # Results should have required fields
        for result in results:
            assert hasattr(result, "id")
            assert hasattr(result, "content")
            assert hasattr(result, "score")
            assert hasattr(result, "metadata")

            # Check quantum-specific metadata
            assert "quantum_amplitude" in result.metadata, "Result must not be empty"
            assert "energy_state" in result.metadata, "Result must not be empty"
            assert "entropy_contribution" in result.metadata, "Result must not be empty"
            assert "scoring_method" in result.metadata, "Result must not be empty"
            assert result.metadata["scoring_method"] == "quantum-thermodynamic", "Result must not be empty"

    def test_retrieve_top_k_bounds(self):
        """Test that top_k is respected."""
        retriever = QuantumEnhancedRetrieval()

        chunks = [
            Chunk(
                content=f"Document {i}",
                start_index=0,
                end_index=11,
                metadata={
                    "id": f"chunk_{i}",
                    "timestamp": 1000.0 + i * 100,
                    "authority": 0.8,
                    "embedding": [0.5 + i * 0.01] * 384,
                },
            )
            for i in range(10)
        ]

        # Request only 3 results
        results = retriever.retrieve_from_chunks(
            query="test", chunks=chunks, top_k=3, current_time=2000.0
        )

        assert len(results) == 3, "Results must not be empty"

    def test_retrieve_sorting(self):
        """Test that results are sorted by score."""
        retriever = QuantumEnhancedRetrieval()

        chunks = [
            Chunk(
                content=f"Document {i}",
                start_index=0,
                end_index=11,
                metadata={
                    "id": f"chunk_{i}",
                    "timestamp": 1000.0,
                    "authority": 0.5 + i * 0.1,
                    "embedding": [0.5] * 384,
                },
            )
            for i in range(5)
        ]

        results = retriever.retrieve_from_chunks(
            query="test", chunks=chunks, top_k=5, current_time=2000.0
        )

        # Check that scores are in descending order
        for i in range(len(results) - 1):
            assert results[i].score >= results[i + 1].score, "score must be greater than zero"


class TestRecordScoringPattern:
    """Test recording of scoring patterns in agent memory."""

    def test_record_pattern_success(self):
        """Test successful pattern recording."""
        scorer = QuantumRelevanceScorer()

        from rag.pipelines.retrieval import RetrievalResult

        results = [
            RetrievalResult(
                id="doc_1",
                content="Test content",
                score=0.85,
                metadata={
                    "entropy_contribution": 0.1,
                    "energy_state": 1.5,
                },
            ),
            RetrievalResult(
                id="doc_2",
                content="More content",
                score=0.75,
                metadata={
                    "entropy_contribution": 0.2,
                    "energy_state": 2.0,
                },
            ),
        ]

        # Should not raise exception even if AgentMemory unavailable
        try:
            record_scoring_pattern(scorer, "test query", results)
        except Exception as e:
            pytest.fail(f"record_scoring_pattern raised exception: {e}")

    def test_record_pattern_empty_results(self):
        """Test pattern recording with empty results."""
        scorer = QuantumRelevanceScorer()

        # Should handle empty results gracefully
        try:
            record_scoring_pattern(scorer, "test query", [])
        except Exception as e:
            pytest.fail(f"record_scoring_pattern raised exception with empty results: {e}")


class TestPhysicsPrinciples:
    """Test that physics principles are correctly applied."""

    def test_superposition_multiple_scoring(self):
        """Test that superposition combines multiple scoring methods."""
        scorer = QuantumRelevanceScorer()

        chunk = Chunk(
            content="Test",
            start_index=0,
            end_index=4,
            metadata={
                "timestamp": 1000.0,
                "authority": 0.8,
                "topic_frequency": 1.5,
                "embedding": [0.5] * 384,
            },
        )

        state = scorer.calculate_quantum_state(
            chunk, query_embedding=[0.5] * 384, current_time=2000.0
        )

        # The collapse probability should reflect all three factors
        # (semantic, temporal, authority) through the weighted combination
        assert state.collapse_probability > 0.0, "collapse_probability must be greater than zero"

    def test_born_rule_probability(self):
        """Test that collapse follows Born rule (|Ψ|² probabilities)."""
        scorer = QuantumRelevanceScorer()

        chunk = Chunk(
            content="Test",
            start_index=0,
            end_index=4,
            metadata={
                "timestamp": 1000.0,
                "authority": 0.8,
                "embedding": [0.5] * 384,
            },
        )

        state = scorer.calculate_quantum_state(
            chunk, query_embedding=[0.5] * 384, current_time=2000.0
        )

        # Collapse probability should equal |amplitude|²
        expected_prob = abs(state.amplitude) ** 2
        assert math.isclose(state.collapse_probability, expected_prob, rel_tol=0.001)

    def test_entropy_reduction(self):
        """Test that result sets have measurably lower entropy."""
        scorer = QuantumRelevanceScorer()

        # Create states with varying probabilities
        states = [
            QuantumState(amplitude=0.9 + 0j, energy=1.0, entropy=0.1, collapse_probability=0.81),
            QuantumState(amplitude=0.5 + 0j, energy=2.0, entropy=0.3, collapse_probability=0.25),
            QuantumState(amplitude=0.3 + 0j, energy=2.5, entropy=0.4, collapse_probability=0.09),
            QuantumState(amplitude=0.2 + 0j, energy=3.0, entropy=0.5, collapse_probability=0.04),
        ]

        # Select top results
        selected = scorer.optimize_entropy(states, max_results=2)

        # Calculate entropy of selected set
        selected_probs = [states[i].collapse_probability for i in selected]
        total = sum(selected_probs)
        normalized = [p / total for p in selected_probs]
        selected_entropy = -sum(p * math.log(p) if p > 0 else 0 for p in normalized)

        # Entropy should be relatively low (less than threshold)
        assert selected_entropy < scorer.entropy_threshold, "selected_entropy is not valid"

    def test_energy_states(self):
        """Test that documents with lower energy are preferred."""
        scorer = QuantumRelevanceScorer()

        # Recent, high-authority document (low energy)
        low_energy_chunk = Chunk(
            content="Test",
            start_index=0,
            end_index=4,
            metadata={
                "timestamp": 1900.0,  # Recent
                "authority": 0.9,
                "topic_frequency": 1.0,
                "embedding": [0.5] * 384,
            },
        )

        # Old, low-authority document (high energy)
        high_energy_chunk = Chunk(
            content="Test",
            start_index=0,
            end_index=4,
            metadata={
                "timestamp": 1000.0,  # Old
                "authority": 0.3,
                "topic_frequency": 2.0,
                "embedding": [0.5] * 384,
            },
        )

        current_time = 2000.0
        query_embedding = [0.5] * 384

        low_state = scorer.calculate_quantum_state(low_energy_chunk, query_embedding, current_time)
        high_state = scorer.calculate_quantum_state(
            high_energy_chunk, query_embedding, current_time
        )

        # Low energy document should be preferred (higher collapse probability)
        assert low_state.collapse_probability > high_state.collapse_probability, "collapse_probability must be greater than zero"


# Integration test placeholder
def test_integration_placeholder():
    """Basic integration smoke test — verifies test file is collectable."""
    # Integration tests for QuantumRetrievalScorer live in separate e2e files.
    # This ensures the module is importable and the test suite collects cleanly.
    assert True, "True is not valid"
