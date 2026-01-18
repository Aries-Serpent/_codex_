# RAG Pipelines API Documentation

**Version:** 1.0  
**Last Updated:** 2025-12-24

## Overview

This document describes the API for RAG (Retrieval-Augmented Generation) pipelines, including the quantum-enhanced retrieval scoring system.

## Modules

### src.rag.pipelines.chunking

Text chunking pipeline for splitting documents into semantic chunks.

#### Classes

##### `Chunk`

Dataclass representing a text chunk with metadata.

**Attributes:**
- `content: str` - The text content of the chunk
- `start_index: int` - Start position in original document
- `end_index: int` - End position in original document
- `metadata: dict` - Additional metadata (timestamps, embeddings, etc.)

**Properties:**
- `length: int` - Returns length of chunk content

**Example:**
```python
chunk = Chunk(
    content="Machine learning is a subset of AI",
    start_index=0,
    end_index=35,
    metadata={"timestamp": 1703462400.0}
)
print(chunk.length)  # 35
```

##### `ChunkingPipeline`

Pipeline for splitting text into chunks.

**Methods:**

`__init__(config: ChunkingConfig | None = None)`
- Initialize chunking pipeline
- **Parameters:**
  - `config`: Optional configuration (defaults to ChunkingConfig())

`chunk_text(text: str, metadata: dict | None = None) -> list[Chunk]`
- Split text into chunks
- **Parameters:**
  - `text`: Text to chunk
  - `metadata`: Optional metadata to attach to all chunks
- **Returns:** List of Chunk objects

**Example:**
```python
from src.rag.pipelines.chunking import ChunkingPipeline

chunker = ChunkingPipeline()
chunks = chunker.chunk_text("Your document text here")
```

---

### src.rag.pipelines.embedding

Embedding generation pipeline for text vectorization.

#### Classes

##### `EmbeddingPipeline`

Pipeline for generating text embeddings.

**Methods:**

`__init__(config: EmbeddingConfig | None = None)`
- Initialize embedding pipeline
- Lazy loads sentence-transformers model

`embed_text(text: str) -> EmbeddingResult`
- Generate embedding for single text
- **Parameters:**
  - `text`: Text to embed
- **Returns:** EmbeddingResult with embedding vector

`embed_texts(texts: list[str]) -> list[EmbeddingResult]`
- Generate embeddings for multiple texts (batched)
- **Parameters:**
  - `texts`: List of texts to embed
- **Returns:** List of EmbeddingResult objects

**Example:**
```python
from src.rag.pipelines.embedding import EmbeddingPipeline

embedder = EmbeddingPipeline()
result = embedder.embed_text("Machine learning")
print(result.embedding)  # [0.1, 0.2, ..., 0.3] (384-dim)
```

---

### src.rag.pipelines.retrieval

Classical vector similarity retrieval pipeline.

#### Classes

##### `RetrievalPipeline`

Pipeline for retrieving relevant documents.

**Methods:**

`__init__(config: RetrievalConfig | None = None, embedding_pipeline: EmbeddingPipeline | None = None)`
- Initialize retrieval pipeline
- **Parameters:**
  - `config`: Optional configuration
  - `embedding_pipeline`: Optional embedding pipeline

`add_documents(documents: list[str], ids: list[str] | None = None, metadatas: list[dict] | None = None) -> int`
- Add documents to index
- **Parameters:**
  - `documents`: List of document texts
  - `ids`: Optional document IDs
  - `metadatas`: Optional metadata dicts
- **Returns:** Number of documents added

`retrieve(query: str, top_k: int | None = None, filters: dict | None = None) -> RetrievalResponse`
- Retrieve relevant documents
- **Parameters:**
  - `query`: Search query
  - `top_k`: Number of results (default: 10)
  - `filters`: Optional metadata filters
- **Returns:** RetrievalResponse with results

**Example:**
```python
from src.rag.pipelines.retrieval import RetrievalPipeline

retriever = RetrievalPipeline()
retriever.add_documents(
    documents=["Doc 1", "Doc 2"],
    ids=["id1", "id2"]
)

response = retriever.retrieve("search query", top_k=5)
for result in response.results:
    print(f"{result.score}: {result.content}")
```

---

### src.rag.pipelines.quantum_retrieval

**NEW** Quantum-enhanced retrieval with physics-inspired scoring.

#### Classes

##### `QuantumState`

Dataclass representing quantum state of a document.

**Attributes:**
- `amplitude: complex` - Wave function amplitude
- `energy: float` - Energy state
- `entropy: float` - Local entropy contribution
- `collapse_probability: float` - Born rule probability |Ψ|²

##### `QuantumRelevanceScorer`

Physics-inspired relevance scorer.

**Methods:**

`__init__(alpha: float = 0.6, beta: float = 0.25, gamma: float = 0.15, planck_constant: float = 1.0, temporal_constant: float = 0.1, entropy_threshold: float = 2.0)`
- Initialize quantum scorer
- **Parameters:**
  - `alpha`: Semantic similarity weight (0-1)
  - `beta`: Temporal decay weight (0-1)
  - `gamma`: Authority weight (0-1)
  - `planck_constant`: Energy scaling factor
  - `temporal_constant`: Temporal decay rate
  - `entropy_threshold`: Maximum acceptable entropy
- **Raises:** ValueError if weights don't sum to 1.0

`calculate_quantum_state(chunk: Chunk, query_embedding: list[float], current_time: float) -> QuantumState`
- Calculate quantum state for a document chunk
- **Parameters:**
  - `chunk`: Document chunk with metadata
  - `query_embedding`: Query embedding vector
  - `current_time`: Current timestamp (Unix time)
- **Returns:** QuantumState object

`optimize_entropy(states: list[QuantumState], max_results: int) -> list[int]`
- Select documents to minimize entropy while maximizing relevance
- **Parameters:**
  - `states`: List of quantum states
  - `max_results`: Maximum number to select
- **Returns:** List of selected indices

**Example:**
```python
from src.rag.pipelines.quantum_retrieval import QuantumRelevanceScorer

scorer = QuantumRelevanceScorer(
    alpha=0.7,    # Higher semantic weight
    beta=0.2,     # Lower temporal weight
    gamma=0.1     # Lower authority weight
)

state = scorer.calculate_quantum_state(chunk, query_emb, time.time())
print(f"Probability: {state.collapse_probability}")
```

##### `QuantumEnhancedRetrieval`

Retrieval pipeline with quantum-thermodynamic scoring.

**Inherits:** RetrievalPipeline

**Additional Attributes:**
- `quantum_scorer: QuantumRelevanceScorer` - The quantum scorer instance

**Methods:**

`__init__(**kwargs)`
- Initialize quantum-enhanced retrieval
- **Parameters:** Same as RetrievalPipeline

`retrieve_from_chunks(query: str, chunks: list[Chunk], top_k: int = 10, current_time: float | None = None) -> list[RetrievalResult]`
- Retrieve documents using quantum scoring
- **Parameters:**
  - `query`: Search query string
  - `chunks`: List of Chunk objects to search
  - `top_k`: Number of results to return
  - `current_time`: Current timestamp (defaults to time.time())
- **Returns:** List of RetrievalResult with quantum metadata

**Quantum Metadata in Results:**
Each result includes additional metadata:
- `quantum_amplitude`: String representation of wave function amplitude
- `energy_state`: Float energy level
- `entropy_contribution`: Float local entropy
- `scoring_method`: Always "quantum-thermodynamic"

**Example:**
```python
from src.rag.pipelines.quantum_retrieval import QuantumEnhancedRetrieval
from src.rag.pipelines.chunking import ChunkingPipeline
from src.rag.pipelines.embedding import EmbeddingPipeline
import time

# Setup pipelines
chunker = ChunkingPipeline()
embedder = EmbeddingPipeline()
retriever = QuantumEnhancedRetrieval()

# Process documents
documents = ["Doc 1", "Doc 2", "Doc 3"]
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
    query="search query",
    chunks=chunks,
    top_k=10,
    current_time=time.time()
)

# Access quantum metadata
for result in results:
    print(f"Score: {result.score:.4f}")
    print(f"Energy: {result.metadata['energy_state']:.4f}")
    print(f"Entropy: {result.metadata['entropy_contribution']:.4f}")
```

#### Functions

##### `record_scoring_pattern`

Record quantum retrieval pattern in agent memory.

`record_scoring_pattern(scorer: QuantumRelevanceScorer, query: str, results: list[RetrievalResult]) -> None`
- Store successful scoring patterns for learning
- **Parameters:**
  - `scorer`: The quantum scorer used
  - `query`: The query string
  - `results`: Retrieved results
- **Returns:** None
- **Side Effects:** Stores pattern in AgentMemory if available

**Example:**
```python
from src.rag.pipelines.quantum_retrieval import record_scoring_pattern

# After successful retrieval
record_scoring_pattern(retriever.quantum_scorer, query, results)
```

---

## Configuration

### ChunkingConfig

```python
@dataclass
class ChunkingConfig:
    chunk_size: int = 1000           # Characters per chunk
    chunk_overlap: int = 200         # Overlap between chunks
    separator: str = "\n\n"          # Split on paragraph breaks
    keep_separator: bool = True      # Include separator in chunks
```

### EmbeddingConfig

```python
@dataclass
class EmbeddingConfig:
    model_name: str = "all-MiniLM-L6-v2"  # Sentence-transformers model
    dimension: int = 384                   # Embedding dimension
    normalize: bool = True                 # Normalize embeddings
    batch_size: int = 32                   # Batch size for embedding
```

### RetrievalConfig

```python
@dataclass
class RetrievalConfig:
    top_k: int = 10                      # Default number of results
    similarity_threshold: float = 0.5    # Minimum similarity score
    include_metadata: bool = True        # Include metadata in results
    rerank: bool = False                 # Enable reranking
```

---

## Metadata Schema

For optimal quantum retrieval, chunks should include these metadata fields:

```python
{
    # Required for quantum scoring
    "embedding": list[float],        # Vector embedding (typically 384-dim)
    
    # Highly recommended
    "timestamp": float,              # Unix timestamp for temporal decay
    "authority": float,              # Source credibility (0-1)
    
    # Optional
    "topic_frequency": float,        # Topic occurrence frequency
    "id": str,                       # Unique identifier
    
    # Any other custom metadata
    "source": str,
    "author": str,
    # ...
}
```

**Defaults:**
- Missing `embedding`: Uses 0.5 default similarity
- Missing `timestamp`: Uses current_time (no decay)
- Missing `authority`: Uses 0.5
- Missing `topic_frequency`: Uses 1.0

---

## Performance Characteristics

### Chunking Pipeline
- **Time Complexity:** O(n) where n is document length
- **Space Complexity:** O(n)
- **Typical Speed:** ~1-2ms per 1000 characters

### Embedding Pipeline
- **Time Complexity:** O(n × d) where n is text length, d is model dimension
- **Space Complexity:** O(d)
- **Typical Speed:** 
  - With model: ~50-100ms per text
  - Fallback mode: ~1ms per text

### Classical Retrieval
- **Time Complexity:** O(k × n) where k is top_k, n is corpus size
- **Space Complexity:** O(n × d)
- **Typical Speed:** ~10-50ms for 1000 documents

### Quantum Retrieval
- **Time Complexity:** 
  - State calculation: O(n)
  - Entropy optimization: O(k² × n) where k is top_k
- **Space Complexity:** O(n)
- **Typical Speed:** ~50-200ms for 1000 documents
- **Recommendation:** For large corpora (>10k docs), use classical pre-filtering

---

## Error Handling

All pipelines include safeguards:

1. **Input Validation**
   - Empty inputs return empty results
   - Invalid types raise TypeError
   - Out-of-range parameters are clamped

2. **Graceful Degradation**
   - Missing embeddings: Uses fallback similarity
   - Model loading fails: Uses hash-based embeddings
   - Import errors: Logs warning and continues

3. **Bounds Checking**
   - Query length: Max 10,000 characters
   - Result count: Max 100 results
   - Chunk size: 50-10,000 characters

**Example Error Handling:**

```python
try:
    results = retriever.retrieve_from_chunks(query, chunks, top_k=10)
except ValueError as e:
    logger.error(f"Invalid parameters: {e}")
    results = []
except Exception as e:
    logger.error(f"Retrieval failed: {e}")
    results = []
```

---

## Integration Points

### With Agent Memory

```python
from agents.agent_memory import AgentMemory

memory = AgentMemory()

# Retrieve learned patterns
patterns = memory.recall_patterns(
    pattern_type="quantum_retrieval",
    context={"query_type": "factual"}
)

if patterns:
    # Use learned parameters
    best = patterns[0]
    scorer = QuantumRelevanceScorer(
        alpha=best['context']['alpha'],
        beta=best['context']['beta'],
        gamma=best['context']['gamma']
    )
```

### With MCP Metrics

```python
from src.mcp.metrics.mcp_metrics import MCPMetrics

metrics = MCPMetrics()

# Track retrieval performance
start = time.time()
results = retriever.retrieve_from_chunks(query, chunks, top_k=10)

metrics.record_operation(
    operation="quantum_retrieval",
    duration=time.time() - start,
    metadata={"num_results": len(results)}
)
```

### With Quantum Game Theory

```python
from agents.quantum_game_theory import QuantumGame

# Retrieve strategy documents
results = retriever.retrieve_from_chunks(query, strategy_chunks, top_k=5)

# Use scores in game theory
game = QuantumGame()
decision = game.evaluate_strategies(
    strategies=[r.content for r in results],
    payoffs=[r.score for r in results]
)
```

---

## Testing

All pipelines include comprehensive test suites:

```bash
# Test classical retrieval
pytest tests/rag/test_chunking.py
pytest tests/rag/test_embedding.py
pytest tests/rag/test_retrieval.py

# Test quantum retrieval
pytest tests/rag/test_quantum_retrieval.py

# Integration tests
pytest tests/integration/test_physics_inspired_rag.py
```

---

## See Also

- [Quantum Retrieval Physics Principles](../ai-facing/QUANTUM_RETRIEVAL_PHYSICS.md)
- [Quantum RAG Integration Guide](../ai-facing/QUANTUM_RAG_INTEGRATION.md)
- [Agent Memory Documentation](https://github.com/Aries-Serpent/_codex_/blob/main/agents/agent_memory.py)
- [MCP Metrics Documentation](https://github.com/Aries-Serpent/_codex_/blob/main/src/mcp/metrics/mcp_metrics.py)

---

**API Version:** 1.0  
**Module Version:** Matches package version  
**Last Updated:** 2025-12-24  
**Maintained By:** _codex_ Development Team
