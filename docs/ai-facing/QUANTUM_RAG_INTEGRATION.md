# Quantum RAG Integration Guide

**Document Version:** 1.0  
**Author:** Copilot Agent  
**Date:** 2024-12-24  
**Status:** Active

## Overview

This guide explains how to integrate the quantum-thermodynamic retrieval scoring system into existing RAG (Retrieval-Augmented Generation) pipelines and related systems.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Integration Patterns](#integration-patterns)
3. [System Integrations](#system-integrations)
4. [Configuration](#configuration)
5. [Performance Tuning](#performance-tuning)
6. [Troubleshooting](#troubleshooting)
7. [Examples](#examples)

---

## Quick Start

### Installation

The quantum retrieval module is part of the core `_codex_` package:

```bash
pip install -e .
```

### Basic Usage

```python
from src.rag.pipelines.quantum_retrieval import QuantumEnhancedRetrieval
from src.rag.pipelines.chunking import ChunkingPipeline
from src.rag.pipelines.embedding import EmbeddingPipeline

# Initialize pipelines
chunker = ChunkingPipeline()
embedder = EmbeddingPipeline()
retriever = QuantumEnhancedRetrieval()

# Process documents
documents = ["Your document text here", ...]
chunks = []

for doc in documents:
    doc_chunks = chunker.chunk_text(doc)
    for chunk in doc_chunks:
        # Add metadata
        chunk.metadata.update({
            "timestamp": time.time(),
            "authority": 0.8,
            "topic_frequency": 1.0,
        })
        
        # Embed
        emb = embedder.embed_text(chunk.content)
        chunk.metadata["embedding"] = emb.embedding
        
        chunks.append(chunk)

# Retrieve with quantum scoring
results = retriever.retrieve_from_chunks(
    query="your search query",
    chunks=chunks,
    top_k=10,
    current_time=time.time()
)

# Use results
for result in results:
    print(f"Score: {result.score:.4f}")
    print(f"Content: {result.content}")
    print(f"Quantum metadata: {result.metadata}")
```

---

## Integration Patterns

### Pattern 1: Drop-In Replacement

Replace existing `RetrievalPipeline` with `QuantumEnhancedRetrieval`:

```python
# Before
from src.rag.pipelines.retrieval import RetrievalPipeline
retriever = RetrievalPipeline()

# After
from src.rag.pipelines.quantum_retrieval import QuantumEnhancedRetrieval
retriever = QuantumEnhancedRetrieval()

# Use the same way
results = retriever.retrieve_from_chunks(query, chunks, top_k=10)
```

### Pattern 2: Hybrid Approach

Combine classical and quantum scoring:

```python
from src.rag.pipelines.retrieval import RetrievalPipeline
from src.rag.pipelines.quantum_retrieval import QuantumEnhancedRetrieval

classical_retriever = RetrievalPipeline()
quantum_retriever = QuantumEnhancedRetrieval()

# Get both result sets
classical_results = classical_retriever.retrieve(query, top_k=20)
quantum_results = quantum_retriever.retrieve_from_chunks(
    query, chunks, top_k=20
)

# Merge and re-rank
merged = merge_and_rerank(classical_results, quantum_results)
```

### Pattern 3: Conditional Quantum Enhancement

Use quantum scoring only for specific query types:

```python
def smart_retrieve(query, chunks, top_k=10):
    if is_complex_query(query):
        # Use quantum for complex queries
        retriever = QuantumEnhancedRetrieval()
        return retriever.retrieve_from_chunks(query, chunks, top_k)
    else:
        # Use classical for simple queries
        retriever = RetrievalPipeline()
        return retriever.retrieve(query, top_k)
```

---

## System Integrations

### Agent Memory Integration

Record successful quantum retrieval patterns:

```python
from src.rag.pipelines.quantum_retrieval import record_scoring_pattern

# After retrieval
results = retriever.retrieve_from_chunks(query, chunks, top_k=10)

# Record pattern for learning
record_scoring_pattern(
    retriever.quantum_scorer,
    query,
    results
)
```

The agent memory system will:
- Store effective parameter combinations
- Learn query-type specific optimizations
- Enable adaptive tuning over time

**AgentMemory API:**

```python
from agents.agent_memory import AgentMemory

memory = AgentMemory()

# Retrieve patterns for similar queries
patterns = memory.recall_patterns(
    pattern_type="quantum_retrieval",
    context={"query_type": "optimization"}
)

# Use learned parameters
if patterns:
    best_pattern = patterns[0]
    scorer = QuantumRelevanceScorer(
        alpha=best_pattern['context']['alpha'],
        beta=best_pattern['context']['beta'],
        gamma=best_pattern['context']['gamma']
    )
```

### MCP Metrics Integration

Track quantum retrieval performance:

```python
from src.mcp.metrics.mcp_metrics import MCPMetrics

metrics = MCPMetrics()

# Before retrieval
start_time = time.time()

# Perform retrieval
results = retriever.retrieve_from_chunks(query, chunks, top_k=10)

# Record metrics
metrics.record_operation(
    operation="quantum_retrieval",
    duration=time.time() - start_time,
    metadata={
        "num_chunks": len(chunks),
        "num_results": len(results),
        "avg_score": sum(r.score for r in results) / len(results),
        "total_entropy": sum(
            r.metadata.get("entropy_contribution", 0)
            for r in results
        )
    }
)
```

### Quantum Game Theory Integration

Use retrieval scores in strategic decision-making:

```python
from agents.quantum_game_theory import QuantumGame, DecisionState

# Retrieve strategy documents
strategy_chunks = [...]  # Chunks describing strategies
results = retriever.retrieve_from_chunks(
    query="threat mitigation strategies",
    chunks=strategy_chunks,
    top_k=5
)

# Use quantum scores as strategy payoffs
strategies = [r.content for r in results]
payoffs = [r.score for r in results]

# Create quantum game
game = QuantumGame()
decision = game.evaluate_strategies(
    strategies=strategies,
    payoffs=payoffs,
    coherence=0.8
)
```

### Chain of Verification (CoVe) Integration

Verify quantum retrieval results:

```python
from agents.verification import ChainOfVerification

# Retrieve documents
results = retriever.retrieve_from_chunks(query, chunks, top_k=10)

# Verify with CoVe
verifier = ChainOfVerification()

verified_results = []
for result in results:
    verification = verifier.verify_relevance(
        query=query,
        document=result.content,
        score=result.score,
        metadata=result.metadata
    )
    
    if verification.is_valid:
        verified_results.append(result)
```

---

## Configuration

### Physics Parameters

Configure quantum scorer behavior:

```python
from src.rag.pipelines.quantum_retrieval import (
    QuantumEnhancedRetrieval,
    QuantumRelevanceScorer
)

# Create custom scorer
scorer = QuantumRelevanceScorer(
    alpha=0.7,              # Semantic weight (default: 0.6)
    beta=0.2,               # Temporal weight (default: 0.25)
    gamma=0.1,              # Authority weight (default: 0.15)
    planck_constant=1.5,    # Energy scaling (default: 1.0)
    temporal_constant=0.15, # Temporal factor (default: 0.1)
    entropy_threshold=1.8   # Max entropy (default: 2.0)
)

# Use custom scorer
retriever = QuantumEnhancedRetrieval()
retriever.quantum_scorer = scorer
```

### Metadata Requirements

For optimal quantum scoring, provide these metadata fields:

```python
chunk.metadata.update({
    # Required
    "embedding": embedding_vector,  # list[float], typically 384-dim
    
    # Recommended
    "timestamp": unix_timestamp,    # float, for temporal decay
    "authority": 0.0-1.0,           # float, source credibility
    
    # Optional
    "topic_frequency": float,       # how often topic appears
    "id": "unique_id",              # for tracking
})
```

**Fallback Behavior:**
- No `embedding`: Uses 0.5 default similarity
- No `timestamp`: Uses current_time (no decay)
- No `authority`: Uses 0.5 default
- No `topic_frequency`: Uses 1.0 default

---

## Performance Tuning

### For Different Query Types

**Factual Queries** (require authoritative sources):
```python
scorer = QuantumRelevanceScorer(
    alpha=0.5,   # Lower semantic
    gamma=0.35,  # Higher authority
    beta=0.15    # Lower temporal
)
```

**Recent News** (require recency):
```python
scorer = QuantumRelevanceScorer(
    alpha=0.4,   # Lower semantic
    beta=0.45,   # Higher temporal
    gamma=0.15   # Lower authority
)
```

**Conceptual/Tutorial** (require relevance):
```python
scorer = QuantumRelevanceScorer(
    alpha=0.8,   # Higher semantic
    beta=0.1,    # Lower temporal
    gamma=0.1    # Lower authority
)
```

### For Different Result Set Sizes

**Small Result Sets** (top-3):
```python
scorer = QuantumRelevanceScorer(
    entropy_threshold=0.5  # Stricter coherence
)
```

**Large Result Sets** (top-50):
```python
scorer = QuantumRelevanceScorer(
    entropy_threshold=3.0  # Allow more diversity
)
```

### Performance Optimization

**For Large Document Collections:**

1. **Pre-compute embeddings:**
   ```python
   # Embed once, reuse many times
   for chunk in chunks:
       if "embedding" not in chunk.metadata:
           emb = embedder.embed_text(chunk.content)
           chunk.metadata["embedding"] = emb.embedding
   ```

2. **Batch processing:**
   ```python
   # Process chunks in batches
   batch_size = 1000
   all_results = []
   
   for i in range(0, len(chunks), batch_size):
       batch = chunks[i:i+batch_size]
       results = retriever.retrieve_from_chunks(
           query, batch, top_k=10
       )
       all_results.extend(results)
   
   # Re-rank combined results
   all_results.sort(key=lambda r: r.score, reverse=True)
   final_results = all_results[:10]
   ```

3. **Limit entropy optimization:**
   ```python
   # For very large top_k, entropy optimization can be slow
   # Consider classical retrieval + quantum re-ranking
   
   # Classical: Fast, get 100 candidates
   candidates = classical_retriever.retrieve(query, top_k=100)
   
   # Quantum: Re-rank top 100 to top 10
   quantum_results = retriever.retrieve_from_chunks(
       query, candidates, top_k=10
   )
   ```

---

## Troubleshooting

### Issue: Low Retrieval Scores

**Symptoms:** All results have scores near 0.0

**Possible Causes:**
1. Missing or incorrect embeddings
2. Query-document mismatch
3. Overly strict entropy threshold

**Solutions:**
```python
# Check embeddings
for chunk in chunks[:5]:
    emb = chunk.metadata.get("embedding")
    if emb is None:
        print("Missing embedding!")
    elif len(emb) == 0:
        print("Empty embedding!")

# Lower entropy threshold
scorer = QuantumRelevanceScorer(entropy_threshold=3.0)

# Increase semantic weight
scorer = QuantumRelevanceScorer(alpha=0.8, beta=0.1, gamma=0.1)
```

### Issue: Temporal Decay Too Aggressive

**Symptoms:** Only very recent documents returned

**Solution:**
```python
# Reduce temporal weight
scorer = QuantumRelevanceScorer(
    alpha=0.7,
    beta=0.15,  # Reduced from 0.25
    gamma=0.15
)

# Or adjust temporal constant
scorer = QuantumRelevanceScorer(
    temporal_constant=0.05  # Slower decay
)
```

### Issue: Results Too Similar (Low Diversity)

**Symptoms:** All results very similar content

**Solution:**
```python
# Increase entropy penalty
retriever.quantum_scorer.entropy_threshold = 2.5  # Allow more entropy

# Or modify optimize_entropy to use higher λ
# (requires code modification)
```

### Issue: Performance Too Slow

**Symptoms:** Retrieval takes too long

**Solutions:**
```python
# 1. Reduce number of chunks
chunks = chunks[:1000]  # Limit to 1000

# 2. Use smaller top_k
results = retriever.retrieve_from_chunks(query, chunks, top_k=5)

# 3. Pre-filter with classical retrieval
classical_results = classical_retriever.retrieve(query, top_k=100)
quantum_results = retriever.retrieve_from_chunks(
    query, classical_results, top_k=10
)
```

---

## Examples

### Example 1: Research Paper Retrieval

```python
from src.rag.pipelines.quantum_retrieval import QuantumEnhancedRetrieval
import time

# Configure for research papers (authority matters)
retriever = QuantumEnhancedRetrieval()
retriever.quantum_scorer = QuantumRelevanceScorer(
    alpha=0.5,   # Semantic relevance
    beta=0.2,    # Moderate recency
    gamma=0.3    # High authority (citation count)
)

# Prepare paper chunks
papers = load_papers()  # Load from database
chunks = []

for paper in papers:
    chunk = Chunk(
        content=paper.abstract,
        start_index=0,
        end_index=len(paper.abstract),
        metadata={
            "id": paper.id,
            "timestamp": paper.publication_date.timestamp(),
            "authority": paper.citation_count / 1000,  # Normalize
            "topic_frequency": paper.topic_relevance,
            "embedding": paper.embedding_vector
        }
    )
    chunks.append(chunk)

# Retrieve relevant papers
results = retriever.retrieve_from_chunks(
    query="quantum machine learning",
    chunks=chunks,
    top_k=10,
    current_time=time.time()
)

# Display results
for i, result in enumerate(results, 1):
    print(f"\n{i}. Score: {result.score:.4f}")
    print(f"   Paper: {result.id}")
    print(f"   Energy: {result.metadata['energy_state']:.4f}")
    print(f"   Entropy: {result.metadata['entropy_contribution']:.4f}")
```

### Example 2: News Article Retrieval

```python
# Configure for news (recency matters most)
retriever = QuantumEnhancedRetrieval()
retriever.quantum_scorer = QuantumRelevanceScorer(
    alpha=0.4,   # Moderate semantic
    beta=0.45,   # High temporal importance
    gamma=0.15   # Moderate authority
)

# Prepare news chunks
articles = load_news_articles()
chunks = []

for article in articles:
    chunks.extend(
        process_article(article, current_time=time.time())
    )

# Retrieve recent relevant articles
results = retriever.retrieve_from_chunks(
    query="artificial intelligence regulation",
    chunks=chunks,
    top_k=10,
    current_time=time.time()
)
```

### Example 3: Multi-Stage Retrieval

```python
# Stage 1: Fast classical retrieval
classical_retriever = RetrievalPipeline()
classical_retriever.add_documents(documents, ids=doc_ids)
candidates = classical_retriever.retrieve(query, top_k=100)

# Stage 2: Quantum re-ranking
quantum_retriever = QuantumEnhancedRetrieval()

# Convert classical results to chunks
candidate_chunks = [
    Chunk(
        content=result.content,
        start_index=0,
        end_index=len(result.content),
        metadata={
            "id": result.id,
            "embedding": get_embedding(result.content),
            "timestamp": get_timestamp(result.id),
            "authority": get_authority(result.id),
        }
    )
    for result in candidates.results
]

# Re-rank with quantum scoring
final_results = quantum_retriever.retrieve_from_chunks(
    query=query,
    chunks=candidate_chunks,
    top_k=10,
    current_time=time.time()
)
```

---

## Best Practices

1. **Always Provide Embeddings**
   - Pre-compute and store embeddings
   - Use consistent embedding model
   - Handle missing embeddings gracefully

2. **Maintain Accurate Timestamps**
   - Use Unix timestamps for consistency
   - Update timestamps on document changes
   - Consider "freshness" vs "publication date"

3. **Calibrate Authority Scores**
   - Normalize to [0, 1] range
   - Use consistent metrics (citations, views, etc.)
   - Update periodically

4. **Tune for Your Domain**
   - Start with defaults
   - A/B test different configurations
   - Use agent memory to learn optimal settings

5. **Monitor Performance**
   - Track retrieval latency
   - Measure result relevance (human eval)
   - Monitor entropy trends

6. **Validate Physics Principles**
   - Run test suite regularly
   - Verify probability normalization
   - Check entropy bounds

---

## Related Documentation

- [Quantum Retrieval Physics Principles](QUANTUM_RETRIEVAL_PHYSICS.md)
- [RAG Pipelines API](../api/rag_pipelines.md)
- [Agent Memory System](../../agents/agent_memory.py)
- [MCP Metrics](../../src/mcp/metrics/mcp_metrics.py)
- [Quantum Game Theory](../../agents/quantum_game_theory.py)

---

**Document Maintenance:**
- Update with new integration patterns
- Add examples from production use
- Refine tuning recommendations based on feedback
- Keep synchronized with code changes

**Feedback:**
- Report issues to repository maintainers
- Suggest improvements via pull requests
- Share successful integration patterns
