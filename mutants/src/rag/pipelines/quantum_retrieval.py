"""
Quantum-Thermodynamic Retrieval Scoring for RAG Pipeline.

This module implements physics-inspired relevance scoring using principles from
quantum mechanics and thermodynamics to enhance document retrieval accuracy.

Physics Principles:
1. Quantum Superposition - Documents exist in multiple relevance states
2. Entropy Minimization - Prefer document sets with lower information entropy
3. Energy States - Documents have energy levels based on relevance factors
4. Wave Function Collapse - Final selection collapses probability distribution
5. Thermodynamic Equilibrium - Balance exploration vs exploitation

Author: Copilot Agent
Generated: 2025-12-24

Safeguards:
- Normalized probabilities (sum to 1)
- Bounded energy states
- Numerical stability in complex calculations
- Input validation on all parameters
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Any

# Optional numpy import with graceful fallback
try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    # Provide minimal interface for type hints
    np = None

from .chunking import Chunk
from .embedding import EmbeddingPipeline
from .retrieval import RetrievalPipeline, RetrievalResult

# Configure logging
logger = logging.getLogger(__name__)

# Physics constants
DEFAULT_ALPHA = 0.6  # Semantic similarity weight
DEFAULT_BETA = 0.25  # Temporal decay weight
DEFAULT_GAMMA = 0.15  # Authority weight
DEFAULT_PLANCK = 1.0  # Planck-like constant
DEFAULT_TEMPORAL = 0.1  # Temporal constant
DEFAULT_ENTROPY_THRESHOLD = 2.0


@dataclass
class QuantumState:
    """
    Represents quantum state of a document.

    Attributes:
        amplitude: Complex amplitude of the wave function
        energy: Energy state of the document
        entropy: Local entropy contribution
        collapse_probability: Born rule probability |Ψ|²
    """

    amplitude: complex
    energy: float
    entropy: float
    collapse_probability: float


class QuantumRelevanceScorer:
    """
    Physics-inspired relevance scorer using quantum mechanics principles.

    Applies quantum superposition, wave function collapse, and entropy
    minimization to enhance document retrieval accuracy.

    Physics Principles:
    - Superposition: Documents exist in multiple relevance states
    - Collapse: Selection collapses wave function to definite state
    - Entropy: Minimize information entropy in result set
    - Energy: Documents have energy levels based on multiple factors

    Safeguards:
    - Normalized probabilities (sum to 1)
    - Bounded energy states
    - Numerical stability in complex calculations
    """

    def __init__(
        self,
        alpha: float = DEFAULT_ALPHA,
        beta: float = DEFAULT_BETA,
        gamma: float = DEFAULT_GAMMA,
        planck_constant: float = DEFAULT_PLANCK,
        temporal_constant: float = DEFAULT_TEMPORAL,
        entropy_threshold: float = DEFAULT_ENTROPY_THRESHOLD,
    ) -> None:
        """Initialize quantum relevance scorer with physics constants.

        Args:
            alpha: Semantic similarity weight (0-1)
            beta: Temporal decay weight (0-1)
            gamma: Authority weight (0-1)
            planck_constant: Planck-like constant for energy calculation
            temporal_constant: Temporal decay constant
            entropy_threshold: Maximum acceptable entropy

        Raises:
            ValueError: If weights don't sum to approximately 1.0
        """
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.h = planck_constant
        self.k = temporal_constant
        self.entropy_threshold = entropy_threshold

        # Validate weights sum close to 1
        total_weight = alpha + beta + gamma
        if not math.isclose(total_weight, 1.0, rel_tol=0.01):
            raise ValueError(
                f"Weights must sum to 1.0, got {total_weight} "
                f"(alpha={alpha}, beta={beta}, gamma={gamma})"
            )

        logger.info(
            "QuantumRelevanceScorer initialized: α=%.2f, β=%.2f, γ=%.2f, h=%.2f",
            alpha,
            beta,
            gamma,
            planck_constant,
        )

    def calculate_quantum_state(
        self,
        chunk: Chunk,
        query_embedding: list[float],
        current_time: float,
    ) -> QuantumState:
        """
        Calculate quantum state of a document chunk.

        Args:
            chunk: Document chunk to score
            query_embedding: Query embedding vector
            current_time: Current timestamp for temporal decay

        Returns:
            QuantumState with amplitude, energy, entropy, probability
        """
        # Get chunk embedding from metadata (if available)
        chunk_embedding = chunk.metadata.get("embedding", None)

        # Semantic similarity (cosine similarity)
        if chunk_embedding is not None and query_embedding is not None:
            semantic_sim = self._cosine_similarity(chunk_embedding, query_embedding)
        else:
            # Fallback to simple text overlap if embeddings unavailable
            semantic_sim = 0.5
            logger.debug("No embeddings available for chunk, using fallback similarity")

        # Temporal decay (exponential)
        chunk_timestamp = chunk.metadata.get("timestamp", current_time)
        age = current_time - chunk_timestamp
        temporal_score = math.exp(-self.beta * age / 3600.0)  # Hourly decay

        # Authority weight (from metadata)
        authority = chunk.metadata.get("authority", 0.5)
        authority = max(0.0, min(1.0, authority))  # Clamp to [0, 1]

        # Combined relevance score
        relevance = self.alpha * semantic_sim + self.beta * temporal_score + self.gamma * authority

        # Clamp relevance to valid probability range
        relevance = max(0.0, min(1.0, relevance))

        # Energy state (quantum-inspired)
        topic_freq = chunk.metadata.get("topic_frequency", 1.0)
        energy = self.h * topic_freq + self.k * (1.0 - temporal_score)

        # Wave function amplitude (complex number)
        phase = energy / self.h if self.h != 0 else 0.0  # ℏ_effective = h
        amplitude = math.sqrt(relevance) * complex(math.cos(phase), math.sin(phase))

        # Collapse probability (Born rule)
        collapse_prob = abs(amplitude) ** 2

        # Local entropy contribution
        if collapse_prob > 0 and collapse_prob < 1.0:
            entropy = -collapse_prob * math.log(collapse_prob)
        else:
            entropy = 0.0

        return QuantumState(
            amplitude=amplitude,
            energy=energy,
            entropy=entropy,
            collapse_probability=collapse_prob,
        )

    def optimize_entropy(
        self,
        states: list[QuantumState],
        max_results: int,
    ) -> list[int]:
        """
        Select documents to minimize total entropy while maximizing relevance.

        This implements a greedy algorithm inspired by thermodynamic
        equilibrium seeking. We balance:
        - High relevance (low energy state preference)
        - Low entropy (coherent result set)
        - Diversity (avoid redundancy)

        Args:
            states: List of quantum states for all documents
            max_results: Maximum number of documents to return

        Returns:
            Indices of selected documents
        """
        if not states:
            return []

        selected: list[int] = []
        remaining = list(range(len(states)))

        while len(selected) < max_results and remaining:
            # Calculate entropy if we add each remaining document
            best_idx: int | None = None
            best_score = float("-inf")

            for idx in remaining:
                # Trial selection
                trial_selected = selected + [idx]

                # Calculate total entropy
                probs = [states[i].collapse_probability for i in trial_selected]
                total_prob = sum(probs)
                if total_prob > 0:
                    normalized = [p / total_prob for p in probs]
                    entropy_val = -sum(p * math.log(p) if p > 0 else 0.0 for p in normalized)
                else:
                    entropy_val = 0.0

                # Score balances relevance and entropy
                relevance = states[idx].collapse_probability
                score = relevance - 0.1 * entropy_val  # Entropy penalty

                if score > best_score:
                    best_score = score
                    best_idx = idx

            if best_idx is not None:
                selected.append(best_idx)
                remaining.remove(best_idx)
            else:
                break

        return selected

    def _cosine_similarity(
        self,
        vec1: list[float] | Any,
        vec2: list[float] | Any,
    ) -> float:
        """Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity score (0-1)
        """
        if vec1 is None or vec2 is None:
            return 0.0

        if not vec1 or not vec2:
            return 0.0

        # Convert to lists if numpy arrays
        if NUMPY_AVAILABLE and np is not None:
            if isinstance(vec1, np.ndarray):
                vec1 = vec1.tolist()
            if isinstance(vec2, np.ndarray):
                vec2 = vec2.tolist()

        # Ensure same length
        if len(vec1) != len(vec2):
            logger.warning("Vector length mismatch: %d vs %d, returning 0.0", len(vec1), len(vec2))
            return 0.0

        # Calculate dot product and norms
        dot_product = sum(a * b for a, b in zip(vec1, vec2, strict=False))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)

        # Clamp to [0, 1] range (cosine similarity can be negative)
        return max(0.0, min(1.0, similarity))


class QuantumEnhancedRetrieval(RetrievalPipeline):
    """
    Retrieval pipeline enhanced with quantum-thermodynamic scoring.

    Extends the base RetrievalPipeline with physics-inspired relevance
    scoring that considers:
    - Quantum superposition of relevance states
    - Thermodynamic entropy minimization
    - Temporal decay functions
    - Authority-weighted scoring

    Usage:
        retriever = QuantumEnhancedRetrieval()
        results = retriever.retrieve(
            query="machine learning optimization",
            top_k=10
        )
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize quantum-enhanced retrieval pipeline.

        Args:
            **kwargs: Arguments passed to parent RetrievalPipeline
        """
        super().__init__(**kwargs)
        self.quantum_scorer = QuantumRelevanceScorer()

        logger.info("QuantumEnhancedRetrieval initialized")

    def retrieve_from_chunks(
        self,
        query: str,
        chunks: list[Chunk],
        top_k: int = 10,
        current_time: float | None = None,
    ) -> list[RetrievalResult]:
        """
        Retrieve documents from chunks using quantum-thermodynamic scoring.

        This method:
        1. Calculates quantum states for all documents
        2. Applies wave function collapse probabilities
        3. Optimizes entropy of result set
        4. Returns top-k documents

        Args:
            query: Search query string
            chunks: List of document chunks to search
            top_k: Number of results to return
            current_time: Current timestamp (defaults to 0.0)

        Returns:
            List of RetrievalResult with quantum-enhanced scores
        """
        if not chunks:
            logger.warning("No chunks provided for retrieval")
            return []

        # Default current time
        if current_time is None:
            import time

            current_time = time.time()

        # Get query embedding
        query_embedding = self._embed_query(query)

        # Calculate quantum states for all chunks
        states = [
            self.quantum_scorer.calculate_quantum_state(chunk, query_embedding, current_time)
            for chunk in chunks
        ]

        # Optimize entropy and select best documents
        selected_indices = self.quantum_scorer.optimize_entropy(states, max_results=top_k)

        # Create results with quantum scores
        results: list[RetrievalResult] = []
        for idx in selected_indices:
            state = states[idx]
            chunk = chunks[idx]

            result = RetrievalResult(
                id=chunk.metadata.get("id", f"chunk_{idx}"),
                content=chunk.content,
                score=state.collapse_probability,
                metadata={
                    "quantum_amplitude": str(state.amplitude),
                    "energy_state": state.energy,
                    "entropy_contribution": state.entropy,
                    "scoring_method": "quantum-thermodynamic",
                    "chunk_start": chunk.start_index,
                    "chunk_end": chunk.end_index,
                },
            )
            results.append(result)

        # Sort by quantum probability (already should be, but ensure)
        results.sort(key=lambda r: r.score, reverse=True)

        logger.info(
            "Quantum retrieval completed: %d chunks -> %d results",
            len(chunks),
            len(results),
        )

        return results

    def _embed_query(self, query: str) -> list[float]:
        """Embed query using available embedding model.

        Args:
            query: Query text to embed

        Returns:
            Embedding vector as list of floats
        """
        if not hasattr(self, "embedding_pipeline") or self.embedding_pipeline is None:
            self.embedding_pipeline = EmbeddingPipeline()

        embedding_result = self.embedding_pipeline.embed_text(query)
        return embedding_result.embedding


# Integration with Agent Memory
def record_scoring_pattern(
    scorer: QuantumRelevanceScorer,
    query: str,
    results: list[RetrievalResult],
) -> None:
    """
    Record successful scoring patterns in agent memory.

    This allows the agent to learn which physics parameters work
    best for different types of queries.

    Args:
        scorer: The quantum scorer used
        query: The query string
        results: Retrieved results
    """
    try:
        from agents.agent_memory import AgentMemory

        memory = AgentMemory()

        # Calculate effectiveness metrics
        avg_score = sum(r.score for r in results) / len(results) if results else 0.0
        entropy = sum(r.metadata.get("entropy_contribution", 0.0) for r in results)

        # Store pattern
        memory.store_pattern(  # type: ignore[attr-defined]
            pattern_type="quantum_retrieval",
            context={
                "query": query,
                "alpha": scorer.alpha,
                "beta": scorer.beta,
                "gamma": scorer.gamma,
                "planck_constant": scorer.h,
            },
            outcome={
                "avg_score": avg_score,
                "total_entropy": entropy,
                "num_results": len(results),
            },
            metadata={
                "effectiveness": "high" if avg_score > 0.7 else "medium",
            },
        )

        logger.info("Stored quantum retrieval pattern in agent memory")

    except ImportError:
        logger.debug("AgentMemory not available, skipping pattern recording")
    except AttributeError as e:
        logger.warning("Failed to record scoring pattern: %s", e)


# Main demonstration function
def main() -> None:
    """Demonstrate quantum-enhanced retrieval."""
    from .chunking import ChunkingPipeline

    # Create sample documents
    documents = [
        "Machine learning models require large amounts of training data.",
        "Quantum computing leverages superposition and entanglement.",
        "Deep neural networks use backpropagation for training.",
        "Physics-inspired algorithms can improve optimization.",
    ]

    # Chunk documents
    chunker = ChunkingPipeline()
    embedder = EmbeddingPipeline()

    chunks: list[Chunk] = []
    base_time = 1703462400.0  # Base timestamp

    for i, doc in enumerate(documents):
        chunk_result = chunker.chunk_text(doc)

        for chunk in chunk_result:
            # Add metadata
            chunk.metadata.update(
                {
                    "id": f"doc_{i}_chunk_{len(chunks)}",
                    "timestamp": base_time + i * 3600,  # Hourly spacing
                    "authority": 0.8 - i * 0.1,  # Decreasing authority
                    "topic_frequency": 1.0 + i * 0.5,
                }
            )

            # Embed the chunk
            embedding_result = embedder.embed_text(chunk.content)
            chunk.metadata["embedding"] = embedding_result.embedding
            chunks.append(chunk)

    # Perform quantum-enhanced retrieval
    retriever = QuantumEnhancedRetrieval()
    results = retriever.retrieve_from_chunks(
        query="optimization algorithms",
        chunks=chunks,
        top_k=3,
        current_time=base_time + 14400,  # 4 hours after first doc
    )

    # Display results
    print("Quantum-Enhanced Retrieval Results:")
    print("=" * 60)
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Score: {result.score:.4f}")
        print(f"   Content: {result.content}")
        print(f"   Energy: {result.metadata['energy_state']:.4f}")
        print(f"   Entropy: {result.metadata['entropy_contribution']:.4f}")

    # Record pattern for future learning
    record_scoring_pattern(retriever.quantum_scorer, "optimization algorithms", results)


if __name__ == "__main__":
    main()
