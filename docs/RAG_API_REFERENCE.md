# RAG Pipeline API Reference

**Last Updated:** 2026-06-22

## Overview

The RAG (Retrieval-Augmented Generation) pipeline provides components for semantic search, document retrieval, and embedding generation.

**Module**: `src.rag.pipelines`
**Version**: 1.0
**Status**: Production Ready

## Core Components

### 1. EmbeddingPipeline

Generate embeddings for documents and queries.

```python
from src.rag.pipelines.embedding import EmbeddingPipeline

pipeline = EmbeddingPipeline(
    model_name='sentence-transformers/all-MiniLM-L6-v2',
    batch_size=32,
    device='cuda'
)
```

**Parameters:**
- `model_name` (str): HuggingFace model identifier
- `batch_size` (int): Batch size for embedding (default: 32)
- `device` (str): 'cuda', 'cpu', or 'auto' (default: 'auto')
- `cache_dir` (str): Cache directory for models (optional)

#### Methods

##### `embed_texts()`

Generate embeddings for a list of texts.

```python
texts = [
    "Machine learning is a subset of AI",
    "Deep learning uses neural networks",
    "Transformers revolutionized NLP"
]

embeddings = pipeline.embed_texts(texts)
# Returns: ndarray of shape (3, embedding_dim)
```

**Parameters:**
- `texts` (List[str]): Texts to embed
- `normalize` (bool): L2 normalize embeddings (default: True)

**Returns:** `np.ndarray` of shape `(len(texts), embedding_dim)`

**Example:**

```python
# Single embedding
embedding = pipeline.embed_texts(["Hello world"])[0]
print(f"Embedding shape: {embedding.shape}")

# Batch embeddings
texts = ["Text 1", "Text 2", "Text 3"]
embeddings = pipeline.embed_texts(texts)
print(f"Batch shape: {embeddings.shape}")  # (3, 384)

# With normalization
embeddings_norm = pipeline.embed_texts(texts, normalize=True)
# L2 norm = 1.0 for each embedding
```

##### `embed_documents()`

Generate embeddings for documents from a file.

```python
embeddings, docs = pipeline.embed_documents(
    'documents.jsonl',
    batch_size=64
)
```

**Parameters:**
- `input_path` (str|Path): Path to JSONL file with documents
- `batch_size` (int): Batch size (default: 32)
- `text_field` (str): Field name containing text (default: 'text')

**Returns:** Tuple of `(embeddings, documents)`

**Example:**

```python
embeddings, docs = pipeline.embed_documents('documents.jsonl')
print(f"Generated {len(embeddings)} embeddings")
print(f"Embedding dimension: {embeddings.shape[1]}")
```

### 2. ChunkingPipeline

Chunk documents into overlapping segments.

```python
from src.rag.pipelines.chunking import ChunkingPipeline

chunker = ChunkingPipeline(
    chunk_size=512,
    overlap=50,
    split_method='sentence'
)
```

**Parameters:**
- `chunk_size` (int): Characters per chunk (default: 512)
- `overlap` (int): Overlap between chunks (default: 50)
- `split_method` (str): 'word', 'sentence', or 'paragraph' (default: 'sentence')
- `min_chunk_size` (int): Minimum chunk size (default: 50)

#### Methods

##### `chunk_text()`

Chunk a single text.

```python
text = "Long document text..."
chunks = chunker.chunk_text(text)
# Returns: List[Dict[str, Any]]
```

**Returns:** List of chunks with metadata

**Example:**

```python
text = """
Machine learning is a subset of artificial intelligence.
It focuses on enabling systems to learn from data.
Deep learning is a more advanced form of machine learning.
"""

chunks = chunker.chunk_text(text)
for i, chunk in enumerate(chunks):
    print(f"Chunk {i}: {chunk['text'][:50]}...")
    print(f"  Start: {chunk['start']}, End: {chunk['end']}")
```

##### `chunk_documents()`

Chunk documents from a file.

```python
documents = chunker.chunk_documents('documents.jsonl')
```

**Parameters:**
- `input_path` (str|Path): Path to JSONL file
- `text_field` (str): Field name with text (default: 'text')

**Returns:** List of chunked documents

### 3. RetrieverPipeline

Retrieve documents based on semantic similarity.

```python
from src.rag.pipelines.retrieval import RetrieverPipeline

retriever = RetrieverPipeline(
    index_path='indexes/documents.faiss',
    documents_path='data/documents.jsonl',
    k=5
)
```

**Parameters:**
- `index_path` (str|Path): Path to FAISS index
- `documents_path` (str|Path): Path to document store
- `k` (int): Number of results to return (default: 5)
- `similarity_threshold` (float): Minimum similarity score (default: 0.0)

#### Methods

##### `retrieve()`

Retrieve documents for a query.

```python
query = "How does transformer architecture work?"
results = retriever.retrieve(query, k=10)

for result in results:
    print(f"Document: {result['document']}")
    print(f"Score: {result['score']:.4f}")
    print(f"Metadata: {result['metadata']}")
```

**Parameters:**
- `query` (str): Query text
- `k` (int, optional): Override default k

**Returns:** List of retrieved documents with scores

**Example:**

```python
query = "machine learning basics"
results = retriever.retrieve(query, k=5)

# Access results
for i, result in enumerate(results, 1):
    print(f"{i}. {result['document']}")
    print(f"   Similarity: {result['score']:.4f}")
```

##### `retrieve_batch()`

Retrieve documents for multiple queries.

```python
queries = [
    "What is machine learning?",
    "How do neural networks work?",
    "What are transformers?"
]

batch_results = retriever.retrieve_batch(queries, k=5)
```

**Parameters:**
- `queries` (List[str]): Query texts
- `k` (int, optional): Override default k

**Returns:** List of result lists

**Example:**

```python
queries = ["ML basics", "Deep learning", "NLP"]
results = retriever.retrieve_batch(queries)

for query, query_results in zip(queries, results):
    print(f"\nQuery: {query}")
    for result in query_results:
        print(f"  - {result['document'][:50]}... ({result['score']:.4f})")
```

##### `build_index()`

Build FAISS index from documents.

```python
retriever.build_index(
    documents_path='documents.jsonl',
    embeddings_path='embeddings.npy'
)
```

**Parameters:**
- `documents_path` (str|Path): Path to documents
- `embeddings_path` (str|Path): Path to embeddings
- `index_type` (str): 'flat', 'ivf', or 'hnsw' (default: 'flat')

### 4. QuantumRetrieval

Advanced retrieval with quantum-inspired probabilistic scoring.

```python
from src.rag.pipelines.quantum_retrieval import QuantumRetrieverPipeline

qretriever = QuantumRetrieverPipeline(
    index_path='indexes/quantum.faiss',
    documents_path='data/documents.jsonl',
    k=5,
    quantum_factor=0.7
)
```

**Parameters:**
- `quantum_factor` (float): Probability scaling (0.0-1.0, default: 0.7)
- Plus all RetrieverPipeline parameters

## Complete Workflow Example

```python
from src.rag.pipelines.embedding import EmbeddingPipeline
from src.rag.pipelines.chunking import ChunkingPipeline
from src.rag.pipelines.retrieval import RetrieverPipeline

# Step 1: Load documents and chunk them
chunker = ChunkingPipeline(chunk_size=512, overlap=50)
documents = chunker.chunk_documents('raw_documents.jsonl')

# Step 2: Generate embeddings
embedder = EmbeddingPipeline(
    model_name='sentence-transformers/all-MiniLM-L6-v2'
)
embeddings = embedder.embed_texts([doc['text'] for doc in documents])

# Step 3: Build retriever index
retriever = RetrieverPipeline(
    index_path='indexes/documents.faiss',
    documents_path='data/documents.jsonl',
    k=5
)
retriever.build_index('documents.jsonl', embeddings)

# Step 4: Search
results = retriever.retrieve("What are transformers?")
for result in results:
    print(f"{result['document'][:100]}... (score: {result['score']:.4f})")
```

## Integration with Language Models

### OpenAI GPT Integration

```python
import openai
from src.rag.pipelines.retrieval import RetrieverPipeline

retriever = RetrieverPipeline(
    index_path='indexes/documents.faiss',
    documents_path='data/documents.jsonl'
)

# Retrieve context
query = "How to optimize machine learning models?"
context_docs = retriever.retrieve(query, k=5)
context = "\n".join([doc['document'] for doc in context_docs])

# Generate answer with context
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
    ]
)

print(response.choices[0].message.content)
```

### Local LLM Integration (Ollama)

```python
import requests
from src.rag.pipelines.retrieval import RetrieverPipeline

retriever = RetrieverPipeline(
    index_path='indexes/documents.faiss',
    documents_path='data/documents.jsonl'
)

# Retrieve context
query = "Explain neural networks"
context_docs = retriever.retrieve(query, k=3)
context = "\n".join([doc['document'] for doc in context_docs])

# Generate with Ollama
response = requests.post('http://localhost:11434/api/generate', json={
    'model': 'mistral',
    'prompt': f"Context:\n{context}\n\nQuestion: {query}",
    'stream': False
})

print(response.json()['response'])
```

## Performance Optimization

### 1. Index Selection

```python
from src.rag.pipelines.retrieval import RetrieverPipeline

# Fast but requires more memory: Flat Index
retriever_flat = RetrieverPipeline(
    index_type='flat'  # O(1) search, O(n) memory
)

# Balanced: IVF (Inverted File)
retriever_ivf = RetrieverPipeline(
    index_type='ivf',
    nlist=100  # Number of clusters
)

# Fast for large datasets: HNSW (Hierarchical)
retriever_hnsw = RetrieverPipeline(
    index_type='hnsw',
    ef_construction=400,
    ef_search=40
)
```

### 2. Batch Processing

```python
# Process documents in batches
from tqdm import tqdm

documents = load_documents('documents.jsonl')
batch_size = 1000

for i in range(0, len(documents), batch_size):
    batch = documents[i:i+batch_size]
    embeddings = embedder.embed_texts([doc['text'] for doc in batch])
    store_embeddings(embeddings, batch)
```

### 3. Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def retrieve_cached(query: str, k: int = 5):
    return retriever.retrieve(query, k=k)

# First call: computes
results = retrieve_cached("machine learning")

# Second call: cached
results = retrieve_cached("machine learning")  # Fast!
```

## Error Handling

```python
try:
    results = retriever.retrieve("query")
except FileNotFoundError:
    print("Index file not found. Build index first.")
except ValueError as e:
    print(f"Invalid query: {e}")
except Exception as e:
    print(f"Retrieval error: {e}")
```

## Troubleshooting

### Q: Retrievals are slow

A: Use HNSW index type for faster searches:
```python
retriever = RetrieverPipeline(
    index_type='hnsw',
    ef_construction=400
)
```

### Q: Results are not relevant

A: Increase chunk overlap and reduce chunk size:
```python
chunker = ChunkingPipeline(
    chunk_size=256,  # Smaller chunks
    overlap=100      # More overlap
)
```

### Q: Index file too large

A: Use IVF with product quantization:
```python
retriever = RetrieverPipeline(
    index_type='ivf_pq',
    nlist=100,
    m=8  # Number of sub-vectors
)
```

## See Also

- [Quickstart Guide](./QUICKSTART.md)
- [Configuration Guide](./CONFIGURATION_GUIDE.md)
- [Ingestion API Reference](./INGESTION_API_REFERENCE.md)
