# Expanded Context Workflow - RAG Implementation

This document describes the expanded-context workflow implementation for RAG (Retrieval-Augmented Generation) with vectorstore persistence, embeddings caching, and semantic retrieval at 64k-512k token scale.

## Overview

The expanded context workflow consists of three main components:

1. **Indexer** (`src/codex/rag/indexer.py`) - Text chunking, embedding generation, and FAISS index persistence
2. **Retriever** (`src/codex/rag/retriever.py`) - Semantic search with provenance tracking
3. **Embeddings** (`src/codex/rag/embeddings.py`) - Embedding provider abstraction with caching

## Quick Start

### Installation

Install RAG dependencies:

```bash
pip install -e ".[rag]"
```

Or install directly:

```bash
pip install sentence-transformers faiss-cpu
# Optional: for OpenAI embeddings
pip install openai
```

### Build an Index

Build a FAISS index from documentation:

```bash
# Index all markdown files in docs/
./scripts/local/build_faiss.sh default docs ./docs

# Index entire repository
./scripts/local/build_faiss.sh default docs .

# Index from NDJSON file
./scripts/local/build_faiss.sh default ndjson data/kb.ndjson
```

### Query the Index

```python
from codex.rag.retriever import Retriever

# Initialize retriever
retriever = Retriever(
    index_dir=".codex/tenants",
    index_name="docs",
    tenant_id="default"
)

# Query
results = retriever.query("How do I configure embeddings?", top_k=5)

for result in results:
    print(f"Score: {result['score']:.4f}")
    print(f"File: {result['file']}")
    print(f"Text: {result['text'][:200]}...")
    print()
```

## Architecture

### Indexer Module

The indexer provides functions for building and persisting FAISS indices:

#### Text Chunking

```python
from codex.rag.indexer import chunk_text

chunks = chunk_text(
    text="Your long document text...",
    chunk_size=1000,  # characters
    overlap=128       # overlap between chunks
)
# Returns: [(start_pos, end_pos, chunk_text), ...]
```

Features:
- Smart boundary detection (sentence endings)
- Configurable overlap for context preservation
- Position tracking for provenance

#### Embedding Generation

```python
from codex.rag.indexer import embed_chunks

embeddings = embed_chunks(
    chunks=chunks,
    model_profile={
        "model_name": "sentence-transformers/all-MiniLM-L6-v2",
        "cache_dir": None
    }
)
# Returns: numpy array of shape (num_chunks, embedding_dim)
```

#### Index Persistence

```python
from codex.rag.indexer import persist_index

index_path = persist_index(
    index_name="my_docs",
    embeddings=embeddings,
    chunks=chunks,
    metadata={"source": "documentation"},
    tenant_id="default",
    index_dir=".codex/tenants"
)
```

Persists to `.codex/tenants/{tenant_id}/{index_name}/`:
- `index.faiss` - FAISS index binary
- `chunks.json` - Chunk metadata with provenance
- `metadata.json` - Index metadata

#### Complete Workflow

```python
from codex.rag.indexer import build_index_from_files
from pathlib import Path

files = list(Path("docs").rglob("*.md"))

index_path = build_index_from_files(
    files=files,
    index_name="docs",
    tenant_id="default",
    chunk_size=1000,
    overlap=128
)
```

### Retriever Module

The retriever provides semantic search with provenance:

```python
from codex.rag.retriever import Retriever

retriever = Retriever(
    index_dir=".codex/tenants",
    index_name="docs",
    tenant_id="default",
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Query with provenance
results = retriever.query("semantic search query", top_k=5)

# Each result contains:
# - text: chunk text
# - file: source file path
# - start_line: estimated start line
# - end_line: estimated end line
# - score: L2 distance (lower is better)
# - generated_at: ISO timestamp
# - chunk_id: unique chunk identifier
# - text_hash: chunk content hash
```

#### Multi-Index Retrieval

Query across multiple indices:

```python
from codex.rag.retriever import MultiIndexRetriever

retriever = MultiIndexRetriever(
    indices=[
        {"index_name": "docs", "tenant_id": "default"},
        {"index_name": "code", "tenant_id": "default"},
    ],
    index_dir=".codex/tenants"
)

results = retriever.query("query", top_k=10)
# Returns merged results from all indices, sorted by score
```

### Embeddings Module

Provides embedding provider abstraction with caching:

#### Local Provider

```python
from codex.rag.embeddings import LocalSentenceTransformerProvider

provider = LocalSentenceTransformerProvider(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    cache_dir=None  # Uses HuggingFace default cache
)

embeddings = provider.encode(["text1", "text2"])
```

#### OpenAI Provider

```python
from codex.rag.embeddings import OpenAIEmbeddingProvider
import os

provider = OpenAIEmbeddingProvider(
    model_name="text-embedding-3-small",
    api_key=os.environ["OPENAI_API_KEY"]
)

embeddings = provider.encode(["text1", "text2"])
```

#### Cached Provider

Wrap any provider with caching:

```python
from codex.rag.embeddings import CachedEmbeddingProvider, LocalSentenceTransformerProvider

base_provider = LocalSentenceTransformerProvider()
cached_provider = CachedEmbeddingProvider(
    provider=base_provider,
    cache_dir=".codex/embeddings_cache"
)

# First call: cache miss, generates embeddings
embeddings1 = cached_provider.encode(
    texts=["text1", "text2"],
    cache_key="my_docs",
    metadata={"file_mtime": 1234567890}
)

# Second call: cache hit, loads from cache
embeddings2 = cached_provider.encode(
    texts=["text1", "text2"],
    cache_key="my_docs",
    metadata={"file_mtime": 1234567890}
)

# Check stats
stats = cached_provider.get_stats()
print(f"Hit rate: {stats['hit_rate']:.2%}")
```

#### Factory Function

Convenience function for creating providers:

```python
from codex.rag.embeddings import create_embedding_provider

# Local with caching (default)
provider = create_embedding_provider(
    provider_type="local",
    use_cache=True,
    cache_dir=".codex/embeddings_cache"
)

# OpenAI with caching (if OPENAI_API_KEY is set)
provider = create_embedding_provider(
    provider_type="openai",
    model_name="text-embedding-3-small",
    use_cache=True
)
```

## Storage Layout

```
.codex/
├── tenants/                    # Multi-tenant index storage
│   └── {tenant_id}/           # Tenant-specific directory
│       └── {index_name}/      # Named index
│           ├── index.faiss    # FAISS index binary
│           ├── chunks.json    # Chunk metadata
│           └── metadata.json  # Index metadata
└── embeddings_cache/          # Embedding cache
    ├── {cache_key}.npz        # Cached embeddings
    └── {cache_key}.meta.json  # Cache metadata
```

## Configuration

Environment variables:

- `MSP_EMBEDDING_MODEL` - Default embedding model (default: `sentence-transformers/all-MiniLM-L6-v2`)
- `MSP_FAISS_INDEX_DIR` - Base index directory (default: `.codex/tenants`)
- `OPENAI_API_KEY` - OpenAI API key for OpenAI embeddings
- `CHUNK_SIZE` - Default chunk size (default: `1000`)
- `OVERLAP` - Default chunk overlap (default: `128`)

## Testing

Run tests:

```bash
# Install test dependencies
pip install pytest

# Run RAG tests (requires sentence-transformers and faiss-cpu)
pytest tests/test_rag_indexer.py -v
```

Note: Tests that require downloading models from HuggingFace will be skipped in offline environments.

## Performance

### Scaling Guidelines

- **Small corpus (< 10k chunks)**: Use `IndexFlatL2` (exact search) - current implementation
- **Medium corpus (10k-1M chunks)**: Use `IndexIVFFlat` with training
- **Large corpus (> 1M chunks)**: Use `IndexIVFPQ` with product quantization

### Memory Usage

- Embeddings: ~1.5 KB per chunk (384-dim float32)
- FAISS index: ~1.5 KB per vector (IndexFlatL2)
- Cache: ~1.5 KB per cached chunk

For 100k chunks:
- Embeddings: ~150 MB
- Index: ~150 MB
- Total: ~300 MB

## Provenance Tracking

All retrieval results include provenance information:

- **File**: Source file path
- **Line range**: Estimated start/end lines (based on character positions)
- **Timestamp**: When result was generated
- **Hash**: Content hash for integrity verification
- **Score**: Similarity score (L2 distance - lower is better)

## Next Steps

1. **Implement hierarchical chunking** for better context preservation
2. **Add query rewriting** for improved retrieval
3. **Implement re-ranking** for better result quality
4. **Add hybrid search** (dense + sparse retrieval)
5. **Implement cross-encoder re-ranking** for accuracy
6. **Add metadata filtering** for refined search

## Troubleshooting

### Model Download Issues

If you can't download models from HuggingFace:

1. Download models offline and cache them
2. Use a local model path
3. Configure HuggingFace cache directory

### Memory Issues

For large corpora:

1. Use batch processing
2. Implement streaming index building
3. Use quantized indices (IndexIVFPQ)
4. Process files in batches

### Query Performance

For slow queries:

1. Use IVF indices for faster approximate search
2. Reduce `top_k`
3. Add metadata pre-filtering
4. Use GPU acceleration (faiss-gpu)

## References

- [FAISS Documentation](https://github.com/facebookresearch/faiss/wiki)
- [Sentence Transformers](https://www.sbert.net/)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
