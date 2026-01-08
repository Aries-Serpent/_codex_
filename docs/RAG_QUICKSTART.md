# RAG Quickstart Guide

Welcome to the Codex RAG (Retrieval-Augmented Generation) system! This guide will get you up and running in minutes.

## Overview

The Codex RAG system provides semantic search over your codebase and documentation using FAISS vector indices and sentence embeddings. Perfect for expanded context workflows (64k-512k tokens).

### Key Features

- 🚀 **Fast Semantic Search**: Query code and docs using natural language
- 🏢 **Multi-Tenant**: Isolated workspaces for different projects/customers
- ⚡ **Smart Caching**: 100x faster repeated queries with LRU cache
- 📊 **Full Provenance**: Track every result back to source with line numbers
- 🔒 **No API Keys**: Uses local sentence-transformers (offline-capable)

---

## Installation

### Prerequisites

```bash
# Python 3.8+ required
python --version
# Expected output: Python 3.8.x or higher
# If version is lower, upgrade Python before proceeding

# Install core dependencies
pip install sentence-transformers faiss-cpu numpy
```

### Install Codex RAG

```bash
# From repository root
pip install -e .

# Verify installation
python -c "from codex.rag import Retriever; print('✓ RAG installed')"
```

---

## Quick Start (5 Minutes)

### Step 1: Build Your First Index

```python
from pathlib import Path
from codex.rag import build_index_from_files

# Index your documentation
index_path = build_index_from_files(
    files=[
        Path("README.md"),
        Path("docs/guide.md"),
        Path("docs/api.md")
    ],
    index_name="my_docs",
    tenant_id="quickstart",
    chunk_size=1000,
    overlap=128
)

print(f"✅ Index created at: {index_path}")
```

**Output**:
```
Loading embedding model: sentence-transformers/all-MiniLM-L6-v2
Generating embeddings for 45 chunks
Added 45 vectors to FAISS index
✅ Index created at: .codex/tenants/quickstart/my_docs
```

### Step 2: Query Your Index

```python
from codex.rag import Retriever

# Create retriever
retriever = Retriever(
    index_name="my_docs",
    tenant_id="quickstart"
)

# Search with natural language
results = retriever.query("how to install", top_k=3)

# Display results
for i, result in enumerate(results, 1):
    print(f"\n{i}. {result['file']} (lines {result['start_line']}-{result['end_line']})")
    print(f"   Score: {result['score']:.3f}")
    print(f"   {result['text'][:100]}...")
```

**Output**:
```
1. README.md (lines 15-18)
   Score: 0.423
   ## Installation

   Install Codex RAG with pip:
   ```bash
   pip install -e .
   ```...

2. docs/guide.md (lines 8-12)
   Score: 0.512
   Getting started is easy. First, install the required dependencies...
```

### Step 3: Use Caching for Speed

```python
from codex.rag import CachedRetriever

# Create cached retriever (100x faster for repeated queries!)
cached = CachedRetriever(
    index_name="my_docs",
    tenant_id="quickstart",
    cache_ttl=3600,       # 1 hour cache
    cache_maxsize=1000    # Up to 1000 queries
)

# First query - cache miss (~100-200ms)
results1 = cached.query_with_cache("installation guide")

# Repeated query - cache hit (~1-2ms)
results2 = cached.query_with_cache("installation guide")

# Check cache performance
stats = cached.get_cache_stats()
print(f"Cache hit rate: {stats['hit_rate']:.1%}")
```

---

## Common Use Cases

### Use Case 1: Search Codebase

```python
from codex.rag import build_index_from_files, Retriever
from pathlib import Path
import glob

# Index Python files
python_files = [Path(f) for f in glob.glob("src/**/*.py", recursive=True)]

build_index_from_files(
    files=python_files,
    index_name="codebase",
    tenant_id="myproject"
)

# Search for async functions
retriever = Retriever(index_name="codebase", tenant_id="myproject")
results = retriever.query("async database operations", top_k=5)

for r in results:
    print(f"{r['file']}: {r['text'][:80]}...")
```

### Use Case 2: Multi-Tenant Documentation

```python
from codex.rag import manage_tenant_indices
from pathlib import Path

# Create separate indices for different customers
for customer in ["acme", "globex", "initech"]:
    result = manage_tenant_indices(
        tenant_id=customer,
        operation="create",
        index_names=["docs"],
        files=[Path(f"docs/{customer}/")],
    )
    print(f"✅ Created index for {customer}")

# Query customer-specific docs
retriever_acme = Retriever(index_name="docs", tenant_id="acme")
retriever_globex = Retriever(index_name="docs", tenant_id="globex")

# Completely isolated results
acme_results = retriever_acme.query("API authentication")
globex_results = retriever_globex.query("API authentication")
```

### Use Case 3: Merge Multiple Indices

```python
from codex.rag import manage_tenant_indices

# Create separate indices
manage_tenant_indices(
    tenant_id="project",
    operation="create",
    index_names=["api_docs"],
    files=[Path("docs/api/")]
)

manage_tenant_indices(
    tenant_id="project",
    operation="create",
    index_names=["tutorials"],
    files=[Path("docs/tutorials/")]
)

# Merge for comprehensive search
result = manage_tenant_indices(
    tenant_id="project",
    operation="merge",
    index_names=["api_docs", "tutorials"],
    merge_name="all_docs"
)

print(f"Merged {len(result.index_names)} indices into 'all_docs'")
```

---

## Configuration

### Index Settings

```python
# Custom chunk sizes for different content types
build_index_from_files(
    files=docs,
    index_name="large_docs",
    chunk_size=2000,      # Larger chunks for context
    overlap=256           # More overlap for continuity
)

build_index_from_files(
    files=code,
    index_name="code_snippets",
    chunk_size=500,       # Smaller chunks for precision
    overlap=50
)
```

### Retrieval Settings

```python
# Adjust search parameters
results = retriever.query(
    "error handling patterns",
    top_k=10,              # More results
    min_score=0.7          # Higher similarity threshold
)
```

### Cache Settings

```python
cached = CachedRetriever(
    index_name="docs",
    cache_ttl=7200,        # 2 hours
    cache_maxsize=5000,    # 5000 queries
    normalize_queries=True # Better cache hits
)
```

---

## Monitoring

### Track Performance

```python
from codex.rag.monitoring import get_metrics

# Get global metrics
metrics = get_metrics()

# Track your queries (automatic with CachedRetriever)
retriever.query("example query")

# Get statistics
stats = metrics.get_statistics()
print(f"Average query latency: {stats['query_latency']['mean_ms']:.2f}ms")
print(f"Cache hit rate: {stats['cache']['hit_rate']:.1%}")
```

### Export Metrics

```python
# Prometheus format
prom_metrics = metrics.export_prometheus()
print(prom_metrics)

# CloudWatch format
cw_metrics = metrics.export_cloudwatch()
```

---

## Troubleshooting

### Issue: "Index not found"

```python
# Check if index exists
from pathlib import Path
index_path = Path(".codex/tenants/mytenant/myindex")
if not index_path.exists():
    print("Index doesn't exist. Build it first!")
    build_index_from_files(...)
```

### Issue: Slow queries

```python
# Use CachedRetriever for repeated queries
cached = CachedRetriever(...)

# Or reduce top_k
results = retriever.query("query", top_k=3)  # Faster than top_k=50
```

### Issue: Out of memory

```python
# Reduce chunk size or process files in batches
for batch in file_batches:
    build_index_from_files(
        files=batch,
        index_name=f"batch_{i}",
        chunk_size=500  # Smaller chunks = less memory
    )

# Then merge
manage_tenant_indices(
    operation="merge",
    index_names=[f"batch_{i}" for i in range(num_batches)],
    merge_name="final_index"
)
```

---

## Next Steps

- 📚 **Advanced Guide**: See `docs/RAG_ADVANCED.md` for multi-index, provenance, and advanced caching
- 🤖 **Custom Agents**: Learn about `@rag-index-manager` and `@semantic-search` agents
- 📊 **Monitoring**: Set up Prometheus and Grafana dashboards
- 🧪 **Examples**: Check `examples/rag_workflow.py` for complete workflows

---

## API Reference

### Core Functions

```python
# Indexing
build_index_from_files(files, index_name, tenant_id, chunk_size, overlap)
manage_tenant_indices(tenant_id, operation, index_names, **kwargs)

# Retrieval
Retriever(index_name, tenant_id, model_name, cache_dir)
CachedRetriever(index_name, tenant_id, cache_ttl, cache_maxsize)

# Query
retriever.query(q, top_k, min_score)
cached.query_with_cache(q, top_k, min_score)

# Monitoring
get_metrics()
metrics.track_query_latency(duration_ms, tenant_id, index_name)
metrics.export_prometheus()
metrics.export_cloudwatch()
```

---

## Support

- 📖 Documentation: `docs/`
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions
- 📧 Email: rag-team@example.com

Happy searching! 🔍✨
