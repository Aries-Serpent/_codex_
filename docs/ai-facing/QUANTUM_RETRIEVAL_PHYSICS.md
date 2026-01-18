# Quantum Retrieval Physics Principles

**Document Version:** 1.0  
**Author:** Copilot Agent  
**Date:** 2025-12-24  
**Status:** Active

## Overview

This document explains the physics principles underlying the quantum-thermodynamic retrieval scoring system implemented in `src/rag/pipelines/quantum_retrieval.py`. The system applies concepts from quantum mechanics and thermodynamics to enhance document retrieval accuracy in RAG (Retrieval-Augmented Generation) pipelines.

## Table of Contents

1. [Core Physics Principles](#core-physics-principles)
2. [Mathematical Formulation](#mathematical-formulation)
3. [Implementation Details](#implementation-details)
4. [Physics Constants](#physics-constants)
5. [Validation Criteria](#validation-criteria)
6. [References](#references)

---

## Core Physics Principles

### 1. Quantum Superposition

**Principle:** Documents exist in multiple relevance states simultaneously until observed (retrieved).

**Application:** Instead of assigning a single relevance score, we combine multiple scoring methods (semantic similarity, temporal relevance, authority) into a quantum-like superposition state.

**Mathematical Basis:**
```
|Ψ⟩ = α|semantic⟩ + β|temporal⟩ + γ|authority⟩
```

where α, β, γ are weight coefficients that sum to 1.

**Implementation:** The `QuantumRelevanceScorer` combines three independent scoring dimensions:
- **Semantic similarity** (α = 0.6): Cosine similarity between query and document embeddings
- **Temporal decay** (β = 0.25): Exponential decay based on document age
- **Authority weight** (γ = 0.15): Source credibility and citation metrics

### 2. Wave Function Collapse (Born Rule)

**Principle:** Upon measurement (retrieval), the wave function collapses to a definite state with probability determined by the Born rule: P = |Ψ|².

**Application:** The final selection probability of a document is the squared magnitude of its quantum amplitude.

**Mathematical Basis:**
```
Ψ(doc) = √(relevance) × e^(iφ)
P(select) = |Ψ(doc)|² = relevance
```

where φ is the phase determined by the energy state.

**Implementation:**
```python
phase = energy / ℏ_effective
amplitude = √relevance × (cos(phase) + i·sin(phase))
collapse_probability = |amplitude|²
```

### 3. Energy States

**Principle:** Documents have energy levels determined by multiple factors. Lower energy states are generally preferred (more stable).

**Application:** Energy combines topic frequency and temporal factors to represent document "excitation."

**Mathematical Basis:**
```
E = h × frequency(topic) + k × temporal_factor
```

where:
- h is a Planck-like constant (default: 1.0)
- frequency(topic) is the topic occurrence frequency
- k is a temporal constant (default: 0.1)
- temporal_factor = 1 - exp(-β × age/3600)

**Physical Interpretation:**
- **High-frequency topics** → Higher energy (more "excited" state)
- **Older documents** → Higher energy (less stable)
- **Recent, focused documents** → Lower energy (preferred)

### 4. Entropy Minimization (Thermodynamics)

**Principle:** Thermodynamic systems tend toward states of minimum entropy (maximum order). We apply this to select coherent, non-redundant document sets.

**Application:** Optimize document selection to minimize total information entropy while maximizing relevance.

**Mathematical Basis:**

Shannon entropy of a result set:
```
H = -Σ p_i × log(p_i)
```

where p_i is the normalized relevance probability of document i.

**Optimization Strategy:**
```
Score(doc) = relevance(doc) - λ × entropy(doc added to set)
```

This greedy algorithm balances:
- **High relevance** (individual document quality)
- **Low entropy** (set coherence)
- **Diversity** (avoid redundancy)

**Physical Interpretation:**
- **Low entropy** → Coherent, focused result set
- **High entropy** → Diverse, scattered results
- **Equilibrium** → Optimal balance between focus and coverage

### 5. Thermodynamic Equilibrium

**Principle:** Systems evolve toward equilibrium states that balance competing forces.

**Application:** Balance exploration (high entropy, diverse results) vs. exploitation (low entropy, focused results).

**Mathematical Basis:**

The entropy penalty parameter λ controls the exploration-exploitation tradeoff:
```
λ = 0.1  (default)
```

- **λ → 0:** Pure exploitation (select highest relevance, ignore diversity)
- **λ → ∞:** Pure exploration (maximize diversity, ignore relevance)
- **λ = 0.1:** Balanced equilibrium

---

## Mathematical Formulation

### Complete Scoring Function

The full quantum-thermodynamic scoring process:

#### 1. Component Scores

**Semantic Similarity:**
```
sim_semantic = cosine(embedding_query, embedding_doc)
```

**Temporal Decay:**
```
age = current_time - timestamp_doc
sim_temporal = exp(-β × age / 3600)
```

**Authority Weight:**
```
sim_authority = authority_score ∈ [0, 1]
```

#### 2. Combined Relevance

```
relevance = α × sim_semantic + β × sim_temporal + γ × sim_authority
```

Subject to: α + β + γ = 1

#### 3. Energy State

```
E = h × frequency(topic) + k × (1 - sim_temporal)
```

#### 4. Wave Function

```
φ = E / ℏ_effective
Ψ = √relevance × e^(iφ)
  = √relevance × (cos(φ) + i·sin(φ))
```

#### 5. Collapse Probability

```
P_collapse = |Ψ|² = relevance
```

#### 6. Local Entropy

```
if 0 < P_collapse < 1:
    H_local = -P_collapse × log(P_collapse)
else:
    H_local = 0
```

#### 7. Set Optimization

For each candidate document k:
```
Score_k = P_collapse(k) - λ × H_total(set ∪ {k})
```

where H_total is the Shannon entropy of the updated set.

---

## Implementation Details

### Class: `QuantumState`

Represents the quantum state of a single document.

**Attributes:**
- `amplitude: complex` - Wave function amplitude
- `energy: float` - Energy level
- `entropy: float` - Local entropy contribution
- `collapse_probability: float` - Born rule probability |Ψ|²

### Class: `QuantumRelevanceScorer`

Implements the physics-inspired scoring algorithm.

**Key Methods:**

1. **`calculate_quantum_state(chunk, query_embedding, current_time)`**
   - Computes the quantum state for a document
   - Combines semantic, temporal, and authority factors
   - Returns `QuantumState` object

2. **`optimize_entropy(states, max_results)`**
   - Selects documents to minimize total entropy
   - Uses greedy algorithm with entropy penalty
   - Returns indices of selected documents

3. **`_cosine_similarity(vec1, vec2)`**
   - Calculates cosine similarity between vectors
   - Handles edge cases (None, empty, zero vectors)
   - Returns normalized similarity in [0, 1]

### Class: `QuantumEnhancedRetrieval`

Extends `RetrievalPipeline` with quantum scoring.

**Key Methods:**

1. **`retrieve_from_chunks(query, chunks, top_k, current_time)`**
   - Main retrieval method
   - Applies quantum scoring to all chunks
   - Optimizes entropy and returns top-k results

---

## Physics Constants

| Constant | Symbol | Default Value | Units | Description |
|----------|--------|---------------|-------|-------------|
| Semantic weight | α | 0.6 | dimensionless | Weight for semantic similarity |
| Temporal weight | β | 0.25 | dimensionless | Weight for temporal decay |
| Authority weight | γ | 0.15 | dimensionless | Weight for authority score |
| Planck constant | h | 1.0 | arbitrary | Energy scaling factor |
| Temporal constant | k | 0.1 | arbitrary | Temporal energy contribution |
| Entropy threshold | H_max | 2.0 | nats | Maximum acceptable entropy |
| Entropy penalty | λ | 0.1 | dimensionless | Exploration-exploitation balance |

### Tuning Guidelines

**For more recent documents:**
- Increase β (temporal weight)
- Decrease α (semantic weight)

**For higher-quality sources:**
- Increase γ (authority weight)
- Decrease α (semantic weight)

**For more diverse results:**
- Increase λ (entropy penalty)
- Accept higher H_max

**For more focused results:**
- Decrease λ (entropy penalty)
- Set lower H_max

---

## Validation Criteria

### Physics Consistency Checks

1. **Probability Normalization**
   - All collapse probabilities ∈ [0, 1]
   - Sum of weights α + β + γ = 1

2. **Born Rule Compliance**
   - P_collapse = |amplitude|²
   - Verified in tests: `test_born_rule_probability`

3. **Entropy Properties**
   - H ≥ 0 (non-negative)
   - H = 0 for deterministic selection
   - H maximized for uniform distribution

4. **Energy Consistency**
   - E ≥ 0 (non-negative)
   - Lower energy → higher relevance (generally)
   - Energy incorporates frequency and recency

5. **Temporal Decay**
   - Exponential decay: e^(-βt)
   - Recent documents preferred
   - Verified in tests: `test_temporal_decay`

### Expected Behaviors

1. **Superposition Effect**
   - Multiple scoring methods combined coherently
   - No single method dominates (unless weights set that way)

2. **Collapse Determinism**
   - Given same inputs, same outputs (deterministic)
   - Randomness only from input variations

3. **Entropy Optimization**
   - Result sets have lower entropy than random selection
   - Verified in tests: `test_entropy_reduction`

4. **Equilibrium Seeking**
   - System converges to stable selection
   - Balance between relevance and diversity

---

## References

### Quantum Mechanics

1. **Born Rule**: Born, M. (1926). "Zur Quantenmechanik der Stoßvorgänge"
   - Foundation for probability interpretation of wave functions

2. **Wave Function Collapse**: von Neumann, J. (1932). "Mathematical Foundations of Quantum Mechanics"
   - Measurement theory and state reduction

3. **Superposition Principle**: Dirac, P.A.M. (1930). "The Principles of Quantum Mechanics"
   - Linear combination of states

### Thermodynamics

4. **Shannon Entropy**: Shannon, C.E. (1948). "A Mathematical Theory of Communication"
   - Information entropy and uncertainty

5. **Maximum Entropy Principle**: Jaynes, E.T. (1957). "Information Theory and Statistical Mechanics"
   - Entropy minimization for inference

### Quantum Game Theory

6. **Quantum Games**: Eisert, J., Wilkens, M., Lewenstein, M. (1999). "Quantum Games and Quantum Strategies"
   - Application of quantum mechanics to game theory

### Information Retrieval

7. **Vector Space Model**: Salton, G. (1971). "The SMART Retrieval System"
   - Cosine similarity for document retrieval

8. **Temporal Information Retrieval**: Li, X., Croft, W.B. (2003). "Time-based Language Models"
   - Temporal factors in relevance

---

## Appendix: Code Examples

### Basic Usage

```python
from src.rag.pipelines.quantum_retrieval import QuantumEnhancedRetrieval
from src.rag.pipelines.chunking import Chunk

# Create retriever
retriever = QuantumEnhancedRetrieval()

# Prepare chunks with metadata
chunks = [
    Chunk(
        content="Machine learning document",
        start_index=0,
        end_index=25,
        metadata={
            "timestamp": 1703462400.0,
            "authority": 0.8,
            "topic_frequency": 1.5,
            "embedding": [0.1, 0.2, ...],  # 384-dim vector
        }
    ),
    # ... more chunks
]

# Retrieve with quantum scoring
results = retriever.retrieve_from_chunks(
    query="machine learning",
    chunks=chunks,
    top_k=10,
    current_time=1703476800.0
)

# Access quantum metadata
for result in results:
    print(f"Score: {result.score}")
    print(f"Energy: {result.metadata['energy_state']}")
    print(f"Entropy: {result.metadata['entropy_contribution']}")
```

### Custom Physics Parameters

```python
from src.rag.pipelines.quantum_retrieval import (
    QuantumEnhancedRetrieval,
    QuantumRelevanceScorer
)

# Custom scorer with different weights
scorer = QuantumRelevanceScorer(
    alpha=0.5,        # More balanced semantic
    beta=0.3,         # Higher temporal importance
    gamma=0.2,        # Higher authority importance
    planck_constant=2.0,
    temporal_constant=0.2,
    entropy_threshold=1.5  # Stricter entropy requirement
)

# Use custom scorer
retriever = QuantumEnhancedRetrieval()
retriever.quantum_scorer = scorer
```

---

**Document Maintenance:**
- Review annually or when significant changes are made
- Update references as new research emerges
- Validate physics principles against test suite
- Solicit feedback from physics and ML experts

**Related Documents:**
- [Quantum RAG Integration Guide](QUANTUM_RAG_INTEGRATION.md)
- [RAG Pipelines API Documentation](../api/rag_pipelines.md)
- [Advanced Physics Calculators](https://github.com/Aries-Serpent/_codex_/blob/main/agents/advanced_physics_calculators.py)
