# Vector Store Integration Guide

## Overview

The Vector Store integration provides a unified interface for storing, retrieving, and searching vector embeddings. It includes a complete FAISS implementation with metadata support, persistence, and integration with the Inference Server for embedding generation.

## Features

- **Unified Interface**: Abstract `VectorStore` class for consistent API across backends
- **FAISS Implementation**: High-performance local vector storage with FAISS
- **ID-Based Management**: Auto-generated or custom vector IDs
- **Metadata Support**: Store and retrieve arbitrary metadata with vectors
- **Persistence**: Save and load indices with full state preservation
- **Embedding Generation**: Integrated `/embed` endpoint in Inference Server
- **Validation**: Comprehensive input validation and error handling

## Quick Start

### Basic Vector Store Usage

```python
from src.codex.retrieval.stores.faiss_store import FAISSStore
import numpy as np

# Create a vector store
store = FAISSStore(index_dir=".codex/vectors", index_name="my-index")

# Generate some vectors (or get them from embeddings)
vectors = np.random.randn(100, 384).astype(np.float32)

# Add vectors with metadata
metadata = [{"text": f"document-{i}", "category": "test"} for i in range(100)]
ids = store.add(vectors, metadata=metadata)

# Search for similar vectors
query = vectors[0]
results = store.search(query, k=5)

for result in results:
    print(f"Score: {result['score']:.3f}")
    print(f"Metadata: {result['document']['metadata']}")

# Save for later use
store.save()
```text

### Using with Inference Server Embeddings

```python
from src.codex_ml.serving.inference_server import ModelServer, ModelConfig
from src.codex.retrieval.stores.faiss_store import FAISSStore

# Setup model server
config = ModelConfig(model_type="stub")  # or "huggingface"
server = ModelServer(config=config)
server.load_model()

# Generate embeddings
texts = ["Hello world", "Machine learning", "Vector search"]
embeddings = server.embed(texts)

# Store in vector store
store = FAISSStore()
metadata = [{"text": t} for t in texts]
ids = store.add(embeddings, metadata=metadata)

# Search with new text
new_text = ["AI and ML"]
query_embedding = server.embed(new_text)
results = store.search(query_embedding[0], k=2)
```text

## VectorStore Interface

All vector store implementations must implement the `VectorStore` abstract base class:

```python
from src.codex.retrieval.stores.base import VectorStore

class MyVectorStore(VectorStore):
    def add(self, vectors, metadata=None, ids=None):
        # Implementation
        pass
    
    def search(self, query_vector, k=5, filters=None):
        # Implementation
        pass
    
    # ... other required methods
```text

### Required Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `add(vectors, metadata, ids)` | Add vectors to store | List of IDs |
| `search(query_vector, k, filters)` | Search similar vectors | List of results |
| `delete(ids)` | Delete vectors by ID | Number deleted |
| `get(ids)` | Retrieve vectors by ID | List of vectors |
| `count()` | Get total vector count | Integer |
| `clear()` | Remove all vectors | None |
| `save(path)` | Persist to disk | None |
| `load(path)` | Load from disk | None |
| `health_check()` | Get health status | Dict |

## FAISS Store API

### Initialization

```python
from src.codex.retrieval.stores.faiss_store import FAISSStore

store = FAISSStore(
    index_dir=".codex/faiss",      # Directory for index files
    index_name="default",           # Name of this index
    max_vectors=10_000_000,         # Safety limit
    validate_checksums=True         # Validate on load
)
```text

### Adding Vectors

#### Auto-Generated IDs

```python
vectors = np.random.randn(10, 128).astype(np.float32)
ids = store.add(vectors)
# Returns: ['uuid-1', 'uuid-2', ...]
```text

#### Custom IDs

```python
vectors = np.random.randn(10, 128).astype(np.float32)
custom_ids = [f"doc-{i}" for i in range(10)]
ids = store.add(vectors, ids=custom_ids)
# Returns: ['doc-0', 'doc-1', ...]
```text

#### With Metadata

```python
vectors = np.random.randn(10, 128).astype(np.float32)
metadata = [
    {"text": "Hello world", "category": "greeting"},
    {"text": "Machine learning", "category": "tech"},
    # ... more metadata
]
ids = store.add(vectors, metadata=metadata)
```text

### Searching Vectors

```python
# Basic search
query = np.random.randn(128).astype(np.float32)
results = store.search(query, k=5)

# Results structure:
for result in results:
    print(result['id'])           # Vector ID
    print(result['score'])        # Similarity score (0-1)
    print(result['metadata'])     # Associated metadata
    print(result['distance'])     # Raw L2 distance
```text

#### Search Parameters

- `query_vector`: Query embedding (1D or 2D numpy array)
- `k`: Number of results to return (default: 5)
- Top `k` results are returned, sorted by similarity (highest first)

### Retrieving Vectors

```python
# Get by single ID
results = store.get("doc-0")
# Returns: [{"id": "doc-0", "metadata": {...}, "index": 0}]

# Get by multiple IDs
results = store.get(["doc-0", "doc-5", "doc-9"])
# Returns list with 3 items
```text

### Deleting Vectors

```python
# Delete single vector
deleted_count = store.delete("doc-0")
# Returns: 1

# Delete multiple vectors
deleted_count = store.delete(["doc-0", "doc-1", "doc-2"])
# Returns: 3
```text

**Note:** FAISS doesn't support efficient deletion. The store marks vectors as deleted and rebuilds the index when necessary.

### Persistence

#### Saving

```python
# Save to default location
store.save()

# Save to custom location
store.save(path="/custom/path")
```text

Saves three files:
- `{index_name}.index` - FAISS index
- `{index_name}.docs.jsonl` - Documents and IDs
- `{index_name}.meta.json` - Metadata and checksums

#### Loading

```python
# Load from default location
store.load()

# Load from custom location
store.load(path="/custom/path")
```text

Validates:
- Index integrity
- Dimension consistency
- Document count match
- Checksums (if enabled)

### Utility Methods

#### Count

```python
total = store.count()
print(f"Total vectors: {total}")
```text

#### Clear

```python
store.clear()  # Removes all vectors and resets index
```text

#### Health Check

```python
health = store.health_check()
print(health)
# {
#     "healthy": True,
#     "index_loaded": True,
#     "num_vectors": 100,
#     "dimension": 384,
#     "backend": "faiss",
#     ...
# }
```text

## Embedding Generation

### ModelServer.embed() Method

```python
from src.codex_ml.serving.inference_server import ModelServer, ModelConfig

# Setup server
config = ModelConfig(model_type="stub")  # or "huggingface"
server = ModelServer(config=config)
server.load_model()

# Generate embeddings
texts = ["First document", "Second document"]
embeddings = server.embed(texts)

# Returns: numpy array of shape (2, dimension)
# Vectors are L2-normalized
```text

### FastAPI /embed Endpoint

```bash
# Start server
export CODEX_MODEL_TYPE=stub
python -m src.codex_ml.serving.inference_server
```text

```bash
# Make request
curl -X POST http://localhost:8000/embed \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Hello world", "Vector embeddings"]
  }'
```text

Response:
```json
{
  "embeddings": [[0.1, 0.2, ...], [0.3, 0.4, ...]],
  "model_name": "my-model",
  "dimension": 384,
  "num_texts": 2,
  "inference_time_ms": 12.34
}
```text

## Error Handling

### Custom Exceptions

```python
from src.codex.retrieval.stores.base import (
    DimensionMismatchError,
    VectorNotFoundError,
    IndexNotLoadedError,
)

try:
    store.add(wrong_dimension_vectors)
except DimensionMismatchError as e:
    print(f"Dimension error: {e}")

try:
    store.get("nonexistent-id")
except VectorNotFoundError as e:
    print(f"Vector not found: {e}")
```text

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `DimensionMismatchError` | Vector dimension doesn't match index | Ensure all vectors have same dimension |
| `VectorNotFoundError` | Requested ID doesn't exist | Check ID exists before calling get() |
| `ValueError` | Invalid input (NaN, wrong shape, etc.) | Validate inputs before adding |
| `RuntimeError` | Safety limit exceeded | Reduce batch size or increase limit |
| `FileNotFoundError` | Index file missing | Check path exists before loading |

## Complete Example: Text Search System

```python
from src.codex_ml.serving.inference_server import ModelServer, ModelConfig
from src.codex.retrieval.stores.faiss_store import FAISSStore
import numpy as np

# 1. Setup
config = ModelConfig(model_type="stub", model_name="text-embedder")
server = ModelServer(config=config)
server.load_model()

store = FAISSStore(index_dir=".codex/text-search", index_name="documents")

# 2. Index documents
documents = [
    "The quick brown fox jumps over the lazy dog",
    "Machine learning is a subset of artificial intelligence",
    "Python is a popular programming language",
    "Vector databases enable semantic search",
    "Natural language processing powers modern AI",
]

# Generate embeddings
embeddings = server.embed(documents)

# Add to vector store
metadata = [{"text": doc, "idx": i} for i, doc in enumerate(documents)]
ids = store.add(embeddings, metadata=metadata)

# Save index
store.save()

print(f"Indexed {store.count()} documents")

# 3. Search
query = "What is machine learning?"
query_embedding = server.embed([query])

results = store.search(query_embedding[0], k=3)

print(f"\nQuery: {query}\n")
for i, result in enumerate(results, 1):
    print(f"{i}. Score: {result['score']:.3f}")
    print(f"   Text: {result['document']['metadata']['text']}\n")

# 4. Later: Load and continue searching
store2 = FAISSStore(index_dir=".codex/text-search", index_name="documents")
store2.load()

new_query = "programming languages"
new_query_embedding = server.embed([new_query])
new_results = store2.search(new_query_embedding[0], k=2)

print(f"Query: {new_query}\n")
for result in new_results:
    print(f"- {result['document']['metadata']['text']}")
```text

## Performance Considerations

### Vector Dimensions
- **32-128**: Very fast, suitable for small-scale applications
- **384-768**: Good balance of speed and quality (recommended)
- **1024+**: Higher quality but slower, use for large-scale deployments

### Batch Sizes
- **Indexing**: Batch size of 100-1000 vectors recommended
- **Search**: Single query or small batches (<10)
- Larger batches improve throughput but increase latency

### Index Size
- **< 100K vectors**: Loads in memory instantly
- **100K - 1M vectors**: Loads in 1-10 seconds
- **> 1M vectors**: Consider memory-mapped files or distributed setup

### Optimization Tips
1. **Normalize vectors**: Already done automatically in FAISS store
2. **Batch additions**: Add vectors in batches rather than one-by-one
3. **Persist regularly**: Save index after significant additions
4. **Use appropriate k**: Don't retrieve more results than needed

## Limitations

### Current Implementation
- **No filtering**: Metadata filtering not yet implemented
- **No updates**: Vectors can't be updated in-place (delete + add instead)
- **FAISS deletion**: Requires index rebuild (expensive for large indices)
- **Single backend**: Only FAISS supported (more backends in future)

### Not Yet Implemented (Future Work)
- Metadata filtering in search
- Approximate nearest neighbor (ANN) algorithms
- GPU acceleration
- Distributed indices
- Hybrid search (dense + sparse)
- Vector compression/quantization

## Troubleshooting

### Dimension Mismatch
```text
Problem: DimensionMismatchError when adding vectors
Solution: Ensure all vectors have the same dimension as the first batch
```text

### Large Memory Usage
```text
Problem: Index consumes too much memory
Solution: 
- Reduce max_vectors limit
- Save and clear index periodically
- Use memory-mapped files (future feature)
```text

### Slow Search
```text
Problem: Search takes too long
Solution:
- Reduce k (number of results)
- Use smaller vector dimensions
- Consider ANN algorithms (future feature)
```text

### Load Failures
```text
Problem: Cannot load saved index
Solution:
- Check file paths exist
- Verify index_name matches
- Check file permissions
- Validate files aren't corrupted
```text

## Next Steps

1. **Try the basic example** to understand the API
2. **Index your own data** with custom metadata
3. **Experiment with different k values** for search
4. **Integrate with Inference Server** for embedding generation
5. **Save and load indices** to persist your work
6. **Use metadata filtering** to narrow search results

For questions or issues, refer to the test suite in `tests/retrieval/test_vector_store_interface.py` for working examples.

## Metadata Filtering

### Overview

Metadata filtering allows you to filter search results based on metadata fields using MongoDB-style query syntax. This is useful for narrowing search results to specific categories, score ranges, or other criteria.

### Supported Operators

#### Equality
```python
# Simple equality
filters = {"category": "tech"}

# Not equal
filters = {"category": {"$ne": "spam"}}
```text

#### Range Operators
```python
# Greater than
filters = {"score": {"$gt": 0.7}}

# Greater than or equal
filters = {"score": {"$gte": 0.7}}

# Less than
filters = {"score": {"$lt": 0.9}}

# Less than or equal
filters = {"score": {"$lte": 0.9}}

# Combined range
filters = {"score": {"$gte": 0.5, "$lte": 1.0}}
```text

#### List Operators
```python
# In list
filters = {"category": {"$in": ["tech", "news", "sports"]}}

# Not in list
filters = {"category": {"$nin": ["spam", "ads"]}}
```text

#### Field Existence
```python
# Field exists
filters = {"author": {"$exists": True}}

# Field does not exist
filters = {"optional_field": {"$exists": False}}
```text

#### Logical Operators
```python
# AND (all conditions must match)
filters = {
    "$and": [
        {"category": "tech"},
        {"score": {"$gte": 0.8}},
        {"author": "alice"}
    ]
}

# OR (at least one condition must match)
filters = {
    "$or": [
        {"category": "tech"},
        {"category": "news"}
    ]
}

# Complex nested logic
filters = {
    "$and": [
        {
            "$or": [
                {"category": "tech"},
                {"category": "news"}
            ]
        },
        {"score": {"$gte": 0.8}}
    ]
}
```text

### Usage Examples

#### Basic Filtering
```python
from src.codex.retrieval.stores.faiss_store import FAISSStore
import numpy as np

# Create store with data
store = FAISSStore(index_name="filtered-search")
store.create_index(dimension=384)

# Add vectors with metadata
vectors = np.random.randn(1000, 384).astype(np.float32)
metadata = [
    {
        "text": f"document-{i}",
        "category": "tech" if i % 3 == 0 else "news",
        "score": 0.5 + (i % 50) / 100.0,
        "author": ["alice", "bob", "charlie"][i % 3]
    }
    for i in range(1000)
]
store.add(vectors, metadata=metadata)

# Search with category filter
query = np.random.randn(384).astype(np.float32)
results = store.search(
    query,
    top_k=10,
    filters={"category": "tech"}
)

print(f"Found {len(results)} tech articles")
```text

#### Range Filtering
```python
# Find high-quality results
results = store.search(
    query,
    top_k=20,
    filters={"score": {"$gte": 0.8}}
)

# Find results in score range
results = store.search(
    query,
    top_k=20,
    filters={
        "score": {
            "$gte": 0.6,
            "$lte": 0.9
        }
    }
)
```text

#### Multi-Criteria Filtering
```python
# Tech articles with high scores by specific authors
results = store.search(
    query,
    top_k=10,
    filters={
        "$and": [
            {"category": "tech"},
            {"score": {"$gte": 0.75}},
            {"author": {"$in": ["alice", "bob"]}}
        ]
    }
)

# Either high-scoring tech or any news
results = store.search(
    query,
    top_k=10,
    filters={
        "$or": [
            {
                "$and": [
                    {"category": "tech"},
                    {"score": {"$gte": 0.8}}
                ]
            },
            {"category": "news"}
        ]
    }
)
```text

### Performance Considerations

**Post-Filtering Strategy:**
The current implementation uses post-filtering, which means:

1. FAISS returns the top-k results by similarity
2. Results are filtered based on metadata
3. If fewer than k results match the filter, you may get fewer results

**Fetch Multiplier:**
To increase the chance of getting k filtered results, the system automatically fetches more results when filters are present:
- Single condition: fetches 3x
- Two conditions: fetches 5x
- Complex filters: fetches 10x

**Example:**
```python
# Requesting 10 results with a filter
results = store.search(
    query,
    top_k=10,
    filters={"category": "tech"}  # Single condition
)
# Internally fetches top-30, then filters to return up to 10
```text

**Tips for Best Performance:**
1. Use filters with high selectivity (match many documents)
2. Consider using multiple smaller indices for distinct categories
3. For very selective filters, increase `top_k` to get more results
4. Monitor the ratio of filtered to total results

### Limitations

- **No Pre-Filtering**: FAISS doesn't natively support metadata filtering, so all filtering happens after similarity search
- **Result Count**: may return fewer than `top_k` results if few vectors match the filter
- **Performance**: Complex filters on large indices may be slower than simple equality filters

### Future Enhancements

Planned improvements for metadata filtering:
- Auxiliary metadata indices for faster pre-filtering
- Support for text search in metadata fields
- Integration with hybrid search (dense + sparse vectors)
- Custom similarity thresholds per filter

---

## API Reference

### VectorStore (Abstract Base Class)

```python
class VectorStore(ABC):
    def add(vectors: np.ndarray, metadata: Optional[List[Dict]] = None, 
            ids: Optional[List[str]] = None) -> List[str]
    def search(query_vector: np.ndarray, k: int = 5, 
               filters: Optional[Dict] = None) -> List[Dict]
    def delete(ids: Union[str, List[str]]) -> int
    def get(ids: Union[str, List[str]]) -> List[Dict]
    def count() -> int
    def clear() -> None
    def save(path: Optional[str] = None) -> None
    def load(path: Optional[str] = None) -> None
    def health_check() -> Dict[str, Any]
```text

### FAISSStore

Inherits all methods from `VectorStore` plus:

```python
class FAISSStore(VectorStore):
    def __init__(index_dir: Optional[str] = None, 
                 index_name: str = "default",
                 max_vectors: int = 10_000_000,
                 validate_checksums: bool = True)
    
    def create_index(embeddings: np.ndarray, documents: List[Dict])
    # Legacy method, use add() instead
```text

### ModelServer.embed()

```python
def embed(texts: List[str]) -> np.ndarray:
    """Generate embeddings from texts
    
    Args:
        texts: List of input texts
        
    Returns:
        Normalized embeddings (shape: [len(texts), dimension])
    """
```text

## Related Documentation

- [Inference Serving Guide](INFERENCE_SERVING_GUIDE.md) - Model serving and embedding generation
- [FAISS Documentation](https://github.com/facebookresearch/faiss) - FAISS library details
- Test examples in `tests/retrieval/test_vector_store_interface.py`
