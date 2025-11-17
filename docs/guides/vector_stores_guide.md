# FAISS Vector Store - User Guide

## Overview

The FAISS Vector Store provides local, CPU-based vector similarity search for embeddings. It includes comprehensive safeguards, validation, and error handling for production use.

## Features

- **Local Operation**: No external dependencies, works offline
- **Safeguards**: Input validation, dimension checking, size limits
- **Persistence**: Save and load indices with checksum validation
- **Health Checks**: Monitor index status and performance
- **High Performance**: FAISS-optimized similarity search

## Installation

```bash
pip install faiss-cpu numpy
```

## Quick Start

### Basic Usage

```python
from src.codex.retrieval.stores.faiss_store import FAISSStore
import numpy as np

# Initialize store
store = FAISSStore(index_dir=".codex/faiss", index_name="my-index")

# Create sample embeddings (10 documents, 128 dimensions)
embeddings = np.random.randn(10, 128).astype(np.float32)
documents = [
    {"id": i, "text": f"Document {i}", "metadata": {"source": "example"}}
    for i in range(10)
]

# Create index
store.create_index(embeddings, documents)

# Save to disk
store.save()

# Search
query = np.random.randn(128).astype(np.float32)
results = store.search(query, top_k=5)

for result in results:
    print(f"Score: {result['score']:.4f}, Doc: {result['document']['text']}")
```

### Loading Existing Index

```python
# Load previously saved index
store = FAISSStore(index_dir=".codex/faiss", index_name="my-index")
store.load()

# Check health
health = store.health_check()
print(f"Status: {health['status']}, Vectors: {health['num_vectors']}")

# Search
results = store.search(query_vector, top_k=10)
```

## Configuration

### Safety Limits

```python
from src.codex.retrieval.stores.faiss_store import MAX_DIMENSION, MAX_VECTORS

# Default limits
MAX_DIMENSION = 4096      # Maximum embedding dimension
MAX_VECTORS = 10_000_000  # Maximum number of vectors

# Custom limits
store = FAISSStore(
    index_dir="./indices",
    index_name="custom",
    max_vectors=100_000,  # Custom limit
    validate_checksums=True
)
```

### Index Naming

Index names must be alphanumeric with dashes/underscores only:

```python
# Valid
store = FAISSStore(index_name="my-index-v1")
store = FAISSStore(index_name="embeddings_2024")

# Invalid - will raise ValueError
store = FAISSStore(index_name="my index")  # spaces not allowed
store = FAISSStore(index_name="index/v1")  # slashes not allowed
```

## API Reference

### FAISSStore

#### `__init__(index_dir, index_name, max_vectors, validate_checksums)`

Initialize vector store.

**Parameters:**
- `index_dir` (str|Path, optional): Directory for indices. Default: `.codex/faiss`
- `index_name` (str): Name of index. Must be alphanumeric with `-_` only.
- `max_vectors` (int, optional): Maximum vectors allowed. Default: 10M
- `validate_checksums` (bool, optional): Validate checksums on load. Default: True

**Raises:**
- `ValueError`: If index_name is invalid
- `ImportError`: If faiss-cpu not installed

#### `create_index(embeddings, documents)`

Create new FAISS index from embeddings.

**Parameters:**
- `embeddings` (np.ndarray): 2D array of shape `[n_docs, dim]`
- `documents` (list[dict]): Document metadata, must match embedding count

**Validation:**
- Embeddings must be 2D numpy array
- Dimension must be 1-4096
- No NaN or Inf values allowed
- Document count must match embedding count
- Total vectors must not exceed max_vectors limit

**Raises:**
- `TypeError`: If embeddings not numpy array
- `ValueError`: If validation fails
- `RuntimeError`: If safety limits exceeded

#### `save()`

Save index and documents to disk with checksum.

Creates three files:
- `{index_name}.index` - FAISS index file
- `{index_name}.docs.jsonl` - Documents in JSONL format
- `{index_name}.meta.json` - Metadata with checksum

**Raises:**
- `RuntimeError`: If no index to save

#### `load()`

Load index and documents from disk.

Validates:
- Index file exists
- Metadata matches index name
- Dimension within limits
- Document count matches vector count

**Raises:**
- `FileNotFoundError`: If index not found
- `ValueError`: If validation fails

#### `search(query_vector, top_k)`

Search for similar vectors.

**Parameters:**
- `query_vector` (np.ndarray): Query embedding, shape `[dim]` or `[1, dim]`
- `top_k` (int, optional): Number of results. Default: 5

**Returns:**
- `list[dict]`: Results with keys:
  - `document`: Document metadata
  - `score`: Cosine similarity score (0-1)
  - `index`: Document index
  - `distance`: L2 distance

**Validation:**
- Query must be numpy array
- Dimension must match index
- No NaN or Inf values
- top_k must be positive (capped at 1000)

**Raises:**
- `RuntimeError`: If index not loaded
- `TypeError`: If query_vector wrong type
- `ValueError`: If validation fails

#### `health_check()`

Check vector store health.

**Returns:**
- `dict`: Health status with keys:
  - `healthy` (bool): Overall health status
  - `index_loaded` (bool): Whether index is loaded
  - `num_vectors` (int): Number of vectors in index
  - `dimension` (int|None): Embedding dimension
  - `num_documents` (int): Number of documents
  - `index_dir_exists` (bool): Whether directory exists
  - `faiss_available` (bool): Whether FAISS is available

## Performance Tuning

### Embedding Normalization

Embeddings are automatically L2-normalized for cosine similarity:

```python
# Automatic normalization happens in create_index()
# No manual normalization needed
store.create_index(raw_embeddings, documents)

# Search also auto-normalizes queries
results = store.search(raw_query)  # normalized internally
```

### Batch Processing

Process large datasets in batches:

```python
BATCH_SIZE = 10000

all_docs = []
all_embeddings = []

for batch_start in range(0, total_docs, BATCH_SIZE):
    batch_end = min(batch_start + BATCH_SIZE, total_docs)
    batch_emb, batch_docs = get_batch(batch_start, batch_end)
    
    all_embeddings.append(batch_emb)
    all_docs.extend(batch_docs)

# Combine and create index
final_embeddings = np.vstack(all_embeddings)
store.create_index(final_embeddings, all_docs)
```

### Memory Management

For large indices:

```python
# Save immediately after creation
store.create_index(embeddings, documents)
store.save()

# Later, load only when needed
store2 = FAISSStore(index_name="large-index")
store2.load()
results = store2.search(query)
```

## Error Handling

### Common Errors

**Dimension Mismatch:**
```python
try:
    results = store.search(wrong_dim_query)
except ValueError as e:
    print(f"Dimension error: {e}")
    # Reshape or re-embed query
```

**Index Not Loaded:**
```python
try:
    results = store.search(query)
except RuntimeError as e:
    print("Loading index...")
    store.load()
    results = store.search(query)
```

**Safety Limit Exceeded:**
```python
try:
    store.create_index(huge_embeddings, huge_docs)
except RuntimeError as e:
    print(f"Too many vectors: {e}")
    # Process in smaller batches or increase max_vectors
```

## Migration from Stubs

### From PGVectorStore Stub

```python
# Old stub code
from src.codex.retrieval.stores.pgvector_store import PGVectorStore
store = PGVectorStore()  # Raises NotImplementedError

# Migrate to FAISS
from src.codex.retrieval.stores.faiss_store import FAISSStore
store = FAISSStore(index_name="migrated-from-pgvector")
store.create_index(embeddings, documents)
store.save()
```

### From Weaviate Stub

```python
# Old stub code
from codex_addons.vector_stores.weaviate_stub import WeaviateStore
# Stub raises ImportError

# Migrate to FAISS
from src.codex.retrieval.stores.faiss_store import FAISSStore
store = FAISSStore(index_name="migrated-from-weaviate")
# ... rest same as above
```

## Best Practices

1. **Always save after creating index:**
   ```python
   store.create_index(embeddings, documents)
   store.save()  # Persist immediately
   ```

2. **Use health checks before operations:**
   ```python
   health = store.health_check()
   if not health["healthy"]:
       store.load()
   ```

3. **Validate embeddings before indexing:**
   ```python
   assert embeddings.ndim == 2
   assert not np.isnan(embeddings).any()
   assert not np.isinf(embeddings).any()
   ```

4. **Handle errors gracefully:**
   ```python
   try:
       results = store.search(query)
   except Exception as e:
       logger.error(f"Search failed: {e}")
       results = []  # Return empty results
   ```

5. **Use descriptive index names:**
   ```python
   # Good
   store = FAISSStore(index_name="product-embeddings-v2")
   
   # Avoid
   store = FAISSStore(index_name="index1")
   ```

## Troubleshooting

### FAISS Not Installed
```bash
pip install faiss-cpu
# Or for GPU support
pip install faiss-gpu
```

### Corrupted Index
```python
# Re-create from source data
store = FAISSStore(index_name="recovered")
store.create_index(original_embeddings, original_documents)
store.save()
```

### Checksum Mismatch
```python
# Disable validation if needed
store = FAISSStore(validate_checksums=False)
store.load()
```

## Examples

See `tests/retrieval/test_faiss_store_enhanced.py` for comprehensive examples.

## Support

For issues or questions:
- Check test suite: `tests/retrieval/test_faiss_store_enhanced.py`
- Review source: `src/codex/retrieval/stores/faiss_store.py`
- File issue in repository
